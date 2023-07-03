import database
import json
import logging
import os
import time
import asyncio
from argparse import ArgumentParser
from flask import Flask, Response, render_template
from flask_cors import CORS, cross_origin
from functools import wraps
import jsonpickle
from datetime import datetime
from models.mgp_models import *


KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9092")
MEMGRAPH_HOST = os.getenv("MEMGRAPH_HOST", "memgraph-mage")
MEMGRAPH_PORT = int(os.getenv("MEMGRAPH_PORT", "7687"))
PATH_TO_INPUT_FILE = os.getenv("PATH_TO_INPUT_FILE", "/")


log = logging.getLogger(__name__)


def init_log():
    logging.basicConfig(level=logging.DEBUG)
    log.info("Logging enabled")
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def parse_args():
    """
    Parse command line arguments.
    """
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0", help="Host address.")
    parser.add_argument("--port", default=5000, type=int, help="App port.")

    parser.add_argument(
        "--debug",
        default=True,
        action="store_true",
        help="Run web server in debug mode.",
    )
    print(__doc__)
    return parser.parse_args()


args = parse_args()

memgraph = None


app = Flask(
    __name__
)
cors = CORS(app)

def parse_node(result):
    node = None
    if "Troll" in result._labels:
        node = {
            "id": result._id,
            "labels": list(result._labels),
            **result._properties
            # "user_screen_name": result._properties.get("user_screen_name"),
            # "user_reported_location": result._properties.get("user_reported_location"),
            # "language": result._properties.get("language"),
            # "follower_count": result._properties.get("follower_count"),
            # "following_count": result._properties.get("following_count")
        }
    elif "User" in result._labels:
        node = {
            "id": result._id,
            "labels": list(result._labels),
            **result._properties
        }
    elif "Tweet" in result._labels:
        node = {
            "id": result._id,
            "labels": list(result._labels),
            "text": result._properties.get("text"),
            "replies_count": result._properties.get("replies_count"),
            "retweets_count": result._properties.get("retweets_count"),
            "quote_count": result._properties.get("quote_count"),
            "like_count": result._properties.get("like_count"),
            "language": result._properties.get("language")
        }
    elif "Source" in result._labels:
        node = {
            "id": result._id,
            "labels": list(result._labels),
            "name": result._properties.get("name")
        }
    elif "Hashtag" in result._labels: 
        node = {
            "id": result._id,
            "labels": list(result._labels),
            "name": result._properties.get("name")
        }
    elif "URL" in result._labels:
        node = {
            "id": result._id,
            "labels": list(result._labels),
            "url": result._properties.get("url")
        }
    return node

# def log_time(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         duration = time.time() - start_time
#         log.info(f"Time for {func.__name__} is {duration}")
#         return result
#     return wrapper


@app.route("/load-data", methods=["GET"])
# log_time
def load_data():
    """Load data into the database."""
    try:
        memgraph.load_data_into_memgraph(PATH_TO_INPUT_FILE)
        return Response(status=200)
    except Exception as e:
        log.info(f"Data loading error: {e}")
        return Response(status=500)


@app.route("/get-graph", methods=["GET"])
# log_time
@cross_origin()
def get_data():
    """Load everything from the database."""
    try:
        results = memgraph.get_graph()

        # Set for quickly check if we have already added the node or the edge
        nodes_set = set()
        links_set = set()
        
        nodes_object_list = []
        links_object_list = []
        for result in results:
            source_id = result["from_id"]
            target_id = result["to_id"]
            link_type = result["r"]._type
            source_node = result["from"]
            # source_node.properties["id"] = source_id
            target_node = result["to"] 
            # target_node.properties["id"] = target_id
            
            
            if source_id not in nodes_set:
                nodes_object_list.append(parse_node(source_node))
            if target_id not in nodes_set:
                nodes_object_list.append(parse_node(target_node))
            
            nodes_set.add(source_id)
            nodes_set.add(target_id)

            if ((source_id, target_id, link_type) not in links_set and
                    (target_id, source_id, link_type) not in links_set):
                links_set.add((source_id, target_id, link_type))


        nodes = [
            node_obj
            for node_obj in nodes_object_list
        ]
        links = [{"source": n_id, "target": m_id, "edge_type": e_type} for (n_id, m_id, e_type) in links_set]

        response = {"nodes": nodes, "links": links}
        return Response(json.dumps(response, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)

@app.route("/get-graph/properties", methods=["GET"])
# log_time
@cross_origin()
def get_graph_properties():
    try:
        result = memgraph.get_full_graph_properties()
        graph_props = result
        sorted_nodes_deg_prop = _[0] if (_:= [x for x in graph_props if x["name"] == "Sorted nodes degree"]) else None
        if sorted_nodes_deg_prop:        
            # Commented out but leaving in for Memgraph review: the Sorted Nodes Degree analysis output 
            # gives a list of (<mgp.Vertex object at xyz memory>, int) tuples... but 
            # because the whole analyze_subgraph procedure outputs all analyses in string form,
            # the Sorted Nodes Degree list of tuples is a string too, not even a directly 
            # accessible and parsable list of Vertex objects. :( I thought I could parse them into client-side
            # Python and then write them out in JSON format, hence the below code, but I can't even do that. 
    
            # sorted_nodes_deg_vals = []
            # for i in sorted_nodes_deg_prop["value"]:
            #     new_node_dg_tuple = (Node.from_vertex(i[0]), i[1])
            #     sorted_nodes_deg_vals.append(new_node_dg_tuple)
            
            graph_props.remove(sorted_nodes_deg_prop)
        
        avg_deg_prop = _[0] if (_:= [x for x in graph_props if x["name"] == "Average degree"]) else None
        if avg_deg_prop:
            log.info("the average degree is found!")
            avg_deg_prop["value"] = round(float(avg_deg_prop["value"]), 5)
            log.info(f"its value is now: {avg_deg_prop['value']}")
        
        log.info(F"Result value for graph properties received: {result}")
        
        return Response(json.dumps({"data": graph_props}, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)

@app.route("/get-graph-no-retweets", methods=["GET"])
# log_time
@cross_origin()
def get_data_no_retweets():
    """Load everything from the database."""
    try:
        results = memgraph.get_graph_without_retweets()

        # Set for quickly check if we have already added the node or the edge
        nodes_set = set()
        links_set = set()
        
        nodes_object_list = []
        links_object_list = []
        for result in results:
            source_id = result["from_id"]
            target_id = result["to_id"]
            link_type = result["r"]._type
            source_node = result["from"]
            # source_node.properties["id"] = source_id
            target_node = result["to"] 
            # target_node.properties["id"] = target_id
            
            
            if source_id not in nodes_set:
                nodes_object_list.append(parse_node(source_node))
            if target_id not in nodes_set:
                nodes_object_list.append(parse_node(target_node))
            
            nodes_set.add(source_id)
            nodes_set.add(target_id)

            if ((source_id, target_id, link_type) not in links_set and
                    (target_id, source_id, link_type) not in links_set):
                links_set.add((source_id, target_id, link_type))


        nodes = [
            node_obj
            for node_obj in nodes_object_list
        ]
        links = [{"source": n_id, "target": m_id, "edge_type": e_type} for (n_id, m_id, e_type) in links_set]

        response = {"nodes": nodes, "links": links}
        return Response(json.dumps(response, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)
    
    
@app.route("/get-graph-no-sources", methods=["GET"])
# log_time
@cross_origin()
def get_data_no_sources():
    """Load everything from the database."""
    try:
        results = memgraph.get_graph_without_sources()

        # Set for quickly check if we have already added the node or the edge
        nodes_set = set()
        links_set = set()
        
        nodes_object_list = []
        links_object_list = []
        for result in results:
            source_id = result["from_id"]
            target_id = result["to_id"]
            link_type = result["r"]._type
            source_node = result["from"]
            # source_node.properties["id"] = source_id
            target_node = result["to"] 
            # target_node.properties["id"] = target_id
            
            
            if source_id not in nodes_set:
                nodes_object_list.append(parse_node(source_node))
            if target_id not in nodes_set:
                nodes_object_list.append(parse_node(target_node))
            
            nodes_set.add(source_id)
            nodes_set.add(target_id)

            if ((source_id, target_id, link_type) not in links_set and
                    (target_id, source_id, link_type) not in links_set):
                links_set.add((source_id, target_id, link_type))


        nodes = [
            node_obj
            for node_obj in nodes_object_list
        ]
        links = [{"source": n_id, "target": m_id, "edge_type": e_type} for (n_id, m_id, e_type) in links_set]

        response = {"nodes": nodes, "links": links}
        return Response(json.dumps(response, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

@app.route("/get-graph-user/<id>", methods=["GET"])
# log_time
@cross_origin()
def get_user(id):
    try:
        #result = memgraph.get_user_by_id_with_props(id)
        result = memgraph.get_node_by_uuid(id, "User")
        log.info(F"Result value for user received: {result}")
        result_data = result["results"]["data"]
        # TODO: change this line once Memgraph Mage supports merging a list into a dictionary within a single clause
        result_data["labels"] = result["results"]["labels"]
        for r in result["results"]["relationships"]:
            result_data[r["rel_name"]] = r["nodes"]
        return Response(json.dumps({"data": result_data}, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)
  
@app.route("/get-tweet/<id>", methods=["GET"])
# log_time
@cross_origin()
def get_tweet(id):
    try:
        result = memgraph.get_node_by_uuid(id, "Tweet")
        log.info(F"Result value for tweet received: {result}")
        result_data = result["results"]["data"]
        for r in result["results"]["relationships"]:
            result_data[r["rel_name"]] = r["nodes"]
        return Response(json.dumps({"data": result_data}, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)
    
    
@app.route("/get-source/<id>", methods=["GET"])
# log_time
@cross_origin()
def get_source(id):
    try:
        result = memgraph.get_node_by_uuid(id, "Source", include_parents=True)
        log.info(F"Result value for source received: {result}")
        result_data = result["results"]["data"]
        for r in result["results"]["relationships"]:
            result_data[r["rel_name"]] = r["nodes"]
        return Response(json.dumps({"data": result_data}, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)
    
@app.route("/get-hashtag/<id>", methods=["GET"])
# log_time
@cross_origin()
def get_hashtag(id):
    try:
        result = memgraph.get_node_by_uuid(id, "Hashtag", include_parents=True)
        log.info(F"Result value for hashtag received: {result}")
        result_data = result["results"]["data"]
        for r in result["results"]["relationships"]:
            result_data[r["rel_name"]] = r["nodes"]
        return Response(json.dumps({"data": result_data}, default=myconverter), status=200, mimetype="application/json")
    except Exception as e:
        log.info(f"Data loading error: {e}")
        log.info(f"Location: {e.__traceback__}")
        return ("", 500)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def main():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        init_log()
        global memgraph
        memgraph = database.Memgraph(MEMGRAPH_HOST,
                                     MEMGRAPH_PORT)
    app.run(host=args.host,
            port=args.port,
            debug=args.debug)


if __name__ == "__main__":
    main()

from platform import node
import time
import logging
from typing import Any, Dict, List
from gqlalchemy import Memgraph as memgraph_connector
from gqlalchemy import match, call


log = logging.getLogger(__name__)


class Memgraph:
    def __init__(self, memgraph_host, memgraph_port):
        self.memgraph_host = memgraph_host
        self.memgraph_port = memgraph_port
        self.memgraph = self.connect_to_memgraph()

    def connect_to_memgraph(self):
        memgraph = memgraph_connector(self.memgraph_host, self.memgraph_port)
        connection_established = False
        while(not connection_established):
            try:
                if (memgraph._get_cached_connection().is_active()):
                    connection_established = True
                    log.info("Connected to Memgraph")
            except:
                log.info("Memgraph probably isn't running")
                time.sleep(4)
        return memgraph

    def load_data_into_memgraph(self, path_to_input_file):
        node = self.memgraph.execute_and_fetch(
            "MATCH (n) RETURN n LIMIT 1;"
        )
        if len(list(node)) == 0:
            self.memgraph.drop_database()
            self.memgraph.execute(
                f"""LOAD CSV FROM "{path_to_input_file}"
                        WITH HEADER AS row
                        MERGE (t:Tweet {{tweet_id: row.tweetid}}) 
                        SET t.created_at=row.tweet_time, 
                        t.text=row.tweet_text, t.replies_count=row.reply_count, 
                        t.quote_count=row.quote_count, t.like_count=row.like_count,
                        t.retweets_count=row.retweet_count, t.language=row.tweet_language,
                        t._hashtags=row.hashtags
                        MERGE (u:User {{user_id: row.userid}})
                        SET u.user_screen_name = row.user_screen_name, 
                        u.account_creation_date=date(row.account_creation_date), u.user_reported_location=row.user_reported_location,
                        u.language=row.account_language, u.following_count = row.following_count, 
                        u.follower_count = row.follower_count
                        MERGE (u)-[:TWEETED]->(t);"""
            )

    def get_graph(self):
        results = self.memgraph.execute_and_fetch(
            f"""MATCH (n)-[r]->(m)
                    RETURN id(n) as from_id, n as from, r, id(m) as to_id, m AS to;"""
        )
        return list(results)
    
    def get_graph_without_retweets(self):
        results = self.memgraph.execute_and_fetch(
            f"""MATCH (n:Troll)-[r]->(m) 
                WHERE NOT n:Retweet AND NOT m:Retweet
                RETURN id(n) as from_id, n as from, r, id(m) as to_id, m AS to;"""
        )
        return list(results)
    
    def get_graph_without_sources(self):
        results = self.memgraph.execute_and_fetch(
            f"""MATCH (n)-[r]->(m) 
                WHERE NOT m:Source
                RETURN id(n) as from_id, n as from, r, id(m) as to_id, m AS to;"""
        )
        return list(results)
    
    # def get_graph_with_filter(self):
    #     query = match(self.memgraph).node(variable="n").to(variable="r").node(variable="m")
    #     filtered = query.where(property, operator, value)
    
    def get_user_by_id_with_props(self, user_id: str):
        # this is gross
        # result = self.memgraph.execute_and_fetch(
        #     """MATCH (u:User {user_id: '""" + user_id + """'})
        #             OPTIONAL MATCH (u)-[r]->(n) 
        #             WITH DISTINCT u, type(r) as rel_type, COLLECT(properties(n)) as nodes
        #             WITH {data: properties(u), relationships: COLLECT({rel_name: rel_type, nodes: nodes} )} as results
        #             RETURN results"""
        # )
        result = match(connection=self.memgraph).node("User", "u", None, **{"user_id": user_id}).match(optional=True).node(variable="u").to(variable="r").node(variable="n").with_({"DISTINCT u": "", "type(r)": "rel_type", "COLLECT(properties(n))": "nodes"}).with_({"{data: properties(u), relationships: COLLECT({rel_name: rel_type, nodes: nodes} )}": "results"}).return_({"results": "results"}).execute()
        user_results = list(result) 
        if (user_results):
            return user_results[0]
        return None
    
    def get_node_by_uuid(self, uuid: str, node_type: str, include_parents: bool = False):
        common_query = match(connection=self.memgraph).node(node_type, "n", None, **{"uuid": uuid}).match(optional=True).node(variable="n").to(variable="r", directed=(not include_parents)).node(variable="m").with_({"DISTINCT n": "", "type(r)": "rel_type", "COLLECT(properties(m))": "nodes"}).with_({"{data: properties(n), relationships: COLLECT({rel_name: rel_type, nodes: nodes} )}": "results"}).return_({"results": "results"}).execute()
        result = list(common_query)
        if (result):
            return result[0]
        return None
    
    # def filter_graph(primary_property, **secondary_properties):
    #     query = match().where()
    
    def get_subgraph_properties(self, vertices: List[str], edges: List[str], analytic_properties: List[str]):
        query = match(connection=self.memgraph).node(variable="n").to(variable="e").node(variable="m").with_({"COLLECT(n)": "nodes_subset", "COLLECT(e)": "edges_subset"}).call("graph_analyzer.analyze", "").yield_().return_().execute()

    def get_full_graph_properties(self):
        # query = match(connection=self.memgraph).node(variable="n").to(variable="e").node(variable="m").with_({"COLLECT(n)": "nodes_subset", "COLLECT(e)": "edges_subset"}).call("graph_analyzer.analyze_subgraph", "nodes_subset, edges_subset").yield_({"name": "", "value": ""}).return_({"name": "", "value": ""}).execute()
        query = self.memgraph.execute_and_fetch(
            """MATCH (n)-[e]->(m)
                    WITH COLLECT(n) AS nodes_subset, COLLECT(e) AS edges_subset
                    CALL graph_analyzer.analyze_subgraph(nodes_subset, edges_subset, ["nodes", "edges", "bridges", "articulation_points", "avg_degree", "sorted_nodes_degree", "is_bipartite", "is_strongly_connected", "strongly_components", "is_dag", "is_eulerian", "is_forest", "is_tree"]) YIELD name, value
                    RETURN name, value"""
        )
        return list(query)

from typing import Any
import mgp
import json
import sys

@mgp.write_proc
def create_hashtags(context: mgp.ProcCtx,
                    created_vertices: mgp.Any,
                    hashtags_lookup_map: mgp.Any
                    ) -> mgp.Record():
    hashtags = []

    for vert in created_vertices:
        # Note to self: when the tweet_dict['hashtags'] data (of type list in the transformation module)
        # is passed to Memgraph in a create/update query, Memgraph does save it into the node's properties,
        # but as a tuple data type rather than the original list data type. 
        if vert.labels[0].name == "Tweet" and "_hashtags" in vert.properties.keys():
            hashtags = vert.properties["_hashtags"]    
            hashtag_vertices_list = [vertex for vertex in context.graph.vertices if any(label == "Hashtag" for label in vertex.labels)]

            if len(hashtags) > 0:
                for i in range(0, len(hashtags)):
                    
                    _ = [x for x in hashtag_vertices_list if x.properties["name"] == hashtags[i]]
                    target_hg = _[0] if len(_) > 0 else None
                    if target_hg is not None:
                        edge = context.graph.create_edge(vert, target_hg, mgp.EdgeType("HAS_TAG"))
                    else:       
                        hg_vertex = context.graph.create_vertex()
                        hg_vertex.add_label("Hashtag")
                        hg_vertex.properties["name"] = hashtags[i]
                        edge = context.graph.create_edge(vert, hg_vertex, mgp.EdgeType("HAS_TAG"))
    return mgp.Record()


@mgp.write_proc
def create_mentions(context: mgp.ProcCtx,
                    created_vertices: mgp.Any) -> mgp.Record():
    for vert in created_vertices:
        if vert.labels[0] == "Tweet" and "_mentions" in vert.properties.keys():
            user_mentions = vert.properties["_mentions"]    
            
            assert isinstance(user_mentions, tuple)
            if len(user_mentions) > 0:
                user_vertices_list = [vertex for vertex in context.graph.vertices if any(label == "User" for label in vertex.labels)]

                for i in range(0, len(user_mentions)):
                    # Note to self: name of the below is walrus operator or assignment expression
                    #target_user = _[0] if (_:= [x for x in user_vertices_list if x.properties["id"] == user_mentions[i]]) else None
                    _ = [x for x in user_vertices_list if x.properties["user_id"] == user_mentions[i]]
                    target_user = _[0] if len(_) > 0 else None
                    if target_user is not None:
                        edge = context.graph.create_edge(vert, target_user, mgp.EdgeType("MENTIONS"))
                    else:
                        target_user_vertex = context.graph.create_vertex()
                        target_user_vertex.add_label("User")
                        target_user_vertex.properties["user_id"] = user_mentions[i]
                        edge = context.graph.create_edge(vert, target_user_vertex, mgp.EdgeType("MENTIONS"))
                        
    return mgp.Record()

@mgp.write_proc
def create_urls(context: mgp.ProcCtx,
                    created_vertices: mgp.Any) -> mgp.Record():
    for vert in created_vertices:
        if "Retweet" not in vert.labels and "_urls" in vert.properties.keys():
            urls = vert.properties["_urls"]    
            
            assert isinstance(urls, tuple)
            if len(urls) > 0:
                url_vertices_list = [vertex for vertex in context.graph.vertices if any(label == "URL" for label in vertex.labels)]

                for i in range(0, len(urls)):
                    # Note to self: name of the below is walrus operator or assignment expression
                    #target_user = _[0] if (_:= [x for x in user_vertices_list if x.properties["id"] == urls[i]]) else None
                    _ = [x for x in url_vertices_list if x.properties["url"] == urls[i]]
                    target_url = _[0] if len(_) > 0 else None
                    if target_url is not None:
                        edge = context.graph.create_edge(vert, target_url, mgp.EdgeType("HAS_LINK"))
                        edge.properties["timestamp"] = vert.properties["created_at"]
                    else:
                        target_url_vertex = context.graph.create_vertex()
                        target_url_vertex.add_label("URL")
                        target_url_vertex.properties["url"] = urls[i]
                        edge = context.graph.create_edge(vert, target_url_vertex, mgp.EdgeType("HAS_LINK"))
                        edge.properties["timestamp"] = vert.properties["created_at"]
                        
    return mgp.Record()


def log_to_stderr_by_force(message: str):
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()
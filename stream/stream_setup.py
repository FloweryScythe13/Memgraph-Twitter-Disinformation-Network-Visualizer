import logging
import time
from gqlalchemy import Memgraph
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable


log = logging.getLogger(__name__)


def connect_to_memgraph(memgraph_host, memgraph_port):
    memgraph = Memgraph(memgraph_host, memgraph_port)
    connection_established = False
    while not connection_established:
        try:
            if memgraph._get_cached_connection().is_active():
                connection_established = True
                log.info("Connected to Memgraph")
        except:
            log.info("Memgraph probably isn't running")
            time.sleep(4)
    return memgraph


def create_stream(memgraph):
    try:
        log.info("Creating stream connections on Memgraph")
        memgraph.execute(
            "CREATE KAFKA STREAM friendship_stream TOPICS friendships TRANSFORM stream.friendship"
        )
        memgraph.execute("START STREAM friendship_stream")
        log.info("Stream creation succeed")
    except:
        log.info("Stream creation failed or streams already exist")

def create_twitter_stream(memgraph):
    try:
        log.info("Creating stream connections for Twitter data on Memgraph")
        memgraph.execute(
            "CREATE KAFKA STREAM twitter_stream TOPICS tweets TRANSFORM twitter.tweets_raw"
        )
        memgraph.execute("START STREAM twitter_stream")
        log.info("Twitter stream creation succeeded")
    except:
        log.info("Twitter stream creation failed or streams already exist")
        
def create_twitter_hashtags_trigger(memgraph):
    try:
        log.info("Creating triggers on Memgraph")
        memgraph.execute(
            '''CREATE TRIGGER created_tweet_trigger_hashtags 
            ON () CREATE AFTER COMMIT EXECUTE 
            MATCH (n :Hashtag)
            WITH COLLECT (n.name, n.id) AS hashtags_lookup_map
            CALL twitter_procs.create_hashtags(createdVertices, hashtags_lookup_map)''')
    except Exception as e:
        log.exception(e)
        
def create_twitter_mentions_trigger(memgraph):
    try:
        log.info("Creating triggers on Memgraph")
        memgraph.execute(
            '''CREATE TRIGGER created_tweet_trigger_mentions
            ON () CREATE AFTER COMMIT EXECUTE
            CALL twitter_procs.create_mentions(createdVertices)'''
        )
    except Exception as e:
        log.exception(e)
        
def create_twitter_urls_trigger(memgraph):
    try:
        log.info("Creating url trigger on Memgraph")
        memgraph.execute(
            '''CREATE TRIGGER created_tweet_trigger_urls
            ON () CREATE AFTER COMMIT EXECUTE 
            CALL twitter_procs.create_urls(createdVertices)
            '''
        )
    except Exception as e:
        log.exception(e)
        
def create_uuid_trigger(memgraph):
    try:
        log.info("Creating uuid trigger on Memgraph")
        memgraph.execute(
            '''CREATE TRIGGER created_node_trigger_uuid
            ON () CREATE BEFORE COMMIT EXECUTE 
            UNWIND createdVertices AS node
            CALL uuid_generator.get() YIELD uuid
            SET node.uuid = uuid
            '''
        )
    except Exception as e:
        log.exception(e)


def get_admin_client(kafka_ip, kafka_port):
    while True:
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=kafka_ip + ":" + kafka_port,
                #client_id="friendship_stream",
                client_id="twitter_stream"
            )
            return admin_client
        except NoBrokersAvailable:
            log.info("Failed to connect to Kafka")
            time.sleep(1)


def create_topic(kafka_ip, kafka_port):
    admin_client = get_admin_client(kafka_ip, kafka_port)
    log.info("Connected to Kafka")

    #topic_list = [NewTopic(name="friendships", num_partitions=1, replication_factor=1)]
    topic_list = [NewTopic(name="tweets", num_partitions=1, replication_factor=1)]
    
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
    except TopicAlreadyExistsError:
        pass
    log.info("Created topics")

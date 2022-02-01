import json
import logging
import os
import stream_setup
from argparse import ArgumentParser
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from time import sleep
import pandas as pd

log = logging.getLogger(__name__)

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9092")
MEMGRAPH_HOST = os.getenv("MEMGRAPH_HOST", "memgraph-mage")
MEMGRAPH_PORT = int(os.getenv("MEMGRAPH_PORT", "7687"))


def parse_args():
    """
    Parse input command line arguments.
    """
    parser = ArgumentParser(
        description="A service that reads a CSV file and streams data to Kafka.")
    parser.add_argument("--file", help="CSV file with data to be streamed.")
    parser.add_argument(
        "--interval",
        type=int,
        help="Interval for sending data in seconds.")
    return parser.parse_args()


def create_kafka_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_HOST + ':' + KAFKA_PORT)
            return producer
        except NoBrokersAvailable:
            print("Failed to connect to Kafka")
            sleep(1)


def main():
    args = parse_args()

    stream_setup.create_topic(KAFKA_HOST, KAFKA_PORT)
    memgraph = stream_setup.connect_to_memgraph(MEMGRAPH_HOST, MEMGRAPH_PORT)
    #stream_setup.create_stream(memgraph)
    streams = [
        stream_row["name"] for stream_row in memgraph.execute_and_fetch("SHOW STREAMS;")
    ]
    if "twitter_stream" not in streams:
        stream_setup.create_twitter_stream(memgraph)
    else:
        print("Twitter Stream already running!")
    
    triggers = [
        trigger_row["trigger name"] for trigger_row in memgraph.execute_and_fetch("SHOW TRIGGERS;")
    ]

    if "created_tweet_trigger_hashtags" not in triggers:
        stream_setup.create_twitter_hashtags_trigger(memgraph)
    if "created_tweet_trigger_mentions" not in triggers:
        stream_setup.create_twitter_mentions_trigger(memgraph)
    if "created_tweet_trigger_urls" not in triggers:
        stream_setup.create_twitter_urls_trigger(memgraph)
    if "created_node_trigger_uuid" not in triggers:
        stream_setup.create_uuid_trigger(memgraph)
        
    producer = create_kafka_producer()
    
    #with open(args.file) as f:
    with pd.read_csv(args.file, chunksize=1) as reader:
        reader
        for row in reader:
            row_json = row.to_json(orient = "records", )
            print(f"Sending data to topic 'tweets'")
            producer.send(topic="tweets", value=row_json.encode('utf8'))
            
            sleep(args.interval)


if __name__ == "__main__":
    main()

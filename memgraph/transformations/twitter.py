import mgp
import json
import logging
import ast
import sys
from datetime import datetime
from dateutil import parser

@mgp.transformation
def tweet(messages: mgp.Messages
          ) -> mgp.Record(query=str, parameters=mgp.Nullable[mgp.Map]):
    result_queries = []

    for i in range(messages.total_messages()):
        message = messages.message_at(i)
        tweet_dict = json.loads(message.payload().decode('utf8'))
        logging.info(tweet_dict)
        if tweet_dict["target_username"]:
            result_queries.append(
                mgp.Record(
                    query=("MERGE (u1:User {username: $source_username}) "
                           "MERGE (u2:User {username: $target_username}) "
                           "MERGE (u1)-[:RETWEETED]-(u2)"),
                    parameters={
                        "source_username": tweet_dict["source_username"],
                        "target_username": tweet_dict["target_username"]}))
        else:
            result_queries.append(
                mgp.Record(
                    query=("MERGE (:User {username: $source_username})"),
                    parameters={
                        "source_username": tweet_dict["source_username"]}))
    return result_queries


@mgp.transformation
def tweets_raw(messages: mgp.Messages
               ) -> mgp.Record(query=str, parameters=mgp.Nullable[mgp.Map]):
    # handlers = [logging.FileHandler('filename.log'), logging.StreamHandler()]
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(asctime)s %(message)s"
    )
    
    result_queries = []
    sys.stderr.write(f"Received stream of tweet messages\n")
    sys.stderr.flush()
    for i in range(messages.total_messages()):
        message = messages.message_at(i)
        tweet_dict = json.loads(message.payload().decode('utf8'))

        # if isinstance(tweet_dict, str):
        #     tweet_dict = ast.literal_eval(tweet_dict)
        if isinstance(tweet_dict, list):
            tweet_dict = tweet_dict[0]

        if (tweet_dict["hashtags"] is not None):
            tweet_dict["hashtags"] = ast.literal_eval(tweet_dict["hashtags"])
        if (tweet_dict["user_mentions"] is not None):
            tweet_dict["user_mentions"] = ast.literal_eval(tweet_dict["user_mentions"])
        if (tweet_dict["urls"] is not None):
            tweet_dict["urls"] = ast.literal_eval(tweet_dict["urls"])

        try:
            result_queries.append(
                mgp.Record(
                    query=(f'''MERGE (t:Tweet{
                            ":Retweet" if tweet_dict["is_retweet"] else ""
                        } {{tweet_id: $tweet_id}}) 
                        ON CREATE SET t.created_at=localdatetime($created_at), 
                        t.text=$text, t.replies_count=$replies_count, 
                        t.retweets_count=$retweets_count, t.quote_count=$quote_count, t.like_count=$like_count,
                        t.language=$tweet_language, t._hashtags=$hashtags,
                        t._mentions=$user_mentions{", t._urls=$tweet_urls" if tweet_dict["is_retweet"] is False and tweet_dict["urls"] else ""}
                        
                        MERGE (u:User:Troll {{user_id: $user_id}}) 
                        ON CREATE SET u.user_screen_name = $user_screen_name, 
                        u.account_creation_date=date($account_creation_date), u.user_reported_location=$user_reported_location,
                        u.language=$account_language, u.following_count = $following_count, 
                        u.follower_count = $follower_count
                        
                        MERGE (u)-[:TWEETED]->(t)      
                        {
                            "MERGE (s:Source {name: $tweet_client_name}) MERGE (t)-[:POSTED_VIA]->(s)" if tweet_dict["tweet_client_name"] else ""
                        }                 
                        {
                            "MERGE (rt:Tweet {tweet_id: $retweet_tweetid}) MERGE (t)-[:RETWEETED]->(rt)" if tweet_dict["is_retweet"] else ""
                        }
                        {
                            "MERGE (rpt:Tweet {tweet_id: $in_reply_to_tweetid}) MERGE (rpu:User {user_id: $in_reply_to_userid}) MERGE (t)-[:IN_REPLY_TO]->(rpt)<-[:TWEETED]-(rpu)" if is_not_null_or_empty(tweet_dict["in_reply_to_tweetid"]) else ""
                        }
                        {
                            "MERGE (qt:Tweet {tweet_id: $quoted_tweet_tweetid}) MERGE (t)-[:QUOTED_TWEET]->(qt)" if is_not_null_or_empty(tweet_dict["quoted_tweet_tweetid"]) else ""
                        }
                        '''),
                    parameters={
                        "tweet_id": str(tweet_dict["tweetid"]),
                        "created_at": parser.parse(tweet_dict["tweet_time"]).isoformat(),
                        "text": tweet_dict["tweet_text"],
                        "replies_count": tweet_dict["reply_count"],
                        "retweets_count": tweet_dict["retweet_count"],
                        "quote_count": tweet_dict["quote_count"],
                        "like_count": tweet_dict["like_count"],
                        "tweet_language": tweet_dict["tweet_language"],
                        "hashtags": tweet_dict["hashtags"],
                        "user_mentions": tweet_dict["user_mentions"],
                        "user_id": tweet_dict["userid"],
                        "user_screen_name": tweet_dict["user_screen_name"],
                        "account_creation_date": tweet_dict["account_creation_date"],
                        "user_reported_location": tweet_dict["user_reported_location"],
                        "account_language": tweet_dict["account_language"],
                        "following_count": tweet_dict["following_count"],
                        "follower_count": tweet_dict["follower_count"],
                        "tweet_client_name": tweet_dict["tweet_client_name"],
                        "retweet_tweetid": str(tweet_dict["retweet_tweetid"]),
                        "in_reply_to_tweetid": str(tweet_dict["in_reply_to_tweetid"]),
                        "in_reply_to_userid": str(tweet_dict["in_reply_to_userid"]),
                        "quoted_tweet_tweetid": str(tweet_dict["quoted_tweet_tweetid"]),
                        "tweet_urls": tweet_dict["urls"]
                        }
                    )
                )
            
            # result_queries.append(
            #     mgp.Record(
            #         query=('''WITH MATCH (t: Tweet {id: $tweet_id }) LIMIT 1
            #                CALL twitter_procs.create_hashtags(t, $hashtags) YIELD *'''), 
            #         parameters={
            #             "tweet_id": str(tweet_dict["tweetid"]),
            #             "hashtags": tweet_dict["hashtags"]
            #         }
            #     )
            # )
            # result_queries.append(
            #     mgp.Record(
            #         query=('''MERGE (u:User {user_id: $user_id}) SET u.user_screen_name = $user_screen_name, 
            #             u.account_creation_date=$account_creation_date, u.user_reported_location=$user_reported_location,
            #             u.language=$account_language, u.following_count = $following_count, 
            #             u.follower_count = $follower_count
                        
            #             MERGE (u)-[:TWEETED]->(t)'''),
            #         parameters={
            #             "user_id": tweet_dict["userid"],
            #             "user_screen_name": tweet_dict["user_screen_name"],
            #             "account_creation_date": tweet_dict["account_creation_date"],
            #             "user_reported_location": tweet_dict["user_reported_location"],
            #             "account_language": tweet_dict["account_language"],
            #             "following_count": tweet_dict["following_count"],
            #             "follower_count": tweet_dict["follower_count"]
            #         }
            #     )
            # )
        except Exception as e:
            logging.info(f"Memgraph loading error: {e}")
            logging.info(f"Tweet_dict: {tweet_dict}")
    print("Populated Cypher queries with transformed values")
    return result_queries




def log_to_stderr_by_force(message: str):
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()
    
def is_not_null_or_empty(s):
    return bool(s and not (s == ""))
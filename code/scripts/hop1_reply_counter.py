import os
from os import path

import json

NEWS_DIR = "../fakenewsnet_dataset/politifact/fake"
news_count = 0

for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):

        news_count += 1
        print(f"{news_count}: {item}")

        news_path = path.join(news_dir_path, "news content.json")
        if path.exists(news_path):

            tweet_dir_path = path.join(news_dir_path, "tweets")
            if path.exists(tweet_dir_path):

                reply_list = []
                tweet_filenames = os.listdir(tweet_dir_path)
                for tweet_filename in tweet_filenames:
                    if tweet_filename == "first_date.json":
                        continue

                    with open(path.join(tweet_dir_path, tweet_filename), "r") as tweet_file:
                        tweet_dict = json.loads(tweet_file.read())

                        replied_tweet_id = tweet_dict["in_reply_to_status_id"]
                        if replied_tweet_id != None and f"{replied_tweet_id}.json" in tweet_filenames:
                            reply_list.append({'replying': tweet_dict['id'], 'replied': replied_tweet_id})

                if len(reply_list) > 0:
                    print(f"news {item} has {len(reply_list)} pairs of replying tweet")

                with open(f"{news_dir_path}/tweet_reply_map.json", "w") as map_file:
                    map_file.write(json.dumps({'count': len(reply_list), 'map': reply_list}))
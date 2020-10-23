import os
from os import path

import json

NEWS_DIR = "../fakenewsnet_dataset/politifact/fake"

source_tweet_count = 0
quote_count = 0
reply_count = 0
for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):

        if not path.exists(f"{news_dir_path}/news content.json"):
            continue
        if not path.exists(f"{news_dir_path}/tweets"):
            continue
        if not path.exists(f"{news_dir_path}/retweets"):
            continue

        source_tweet_count += len(os.listdir(f"{news_dir_path}/tweets"))

        with open(f"{news_dir_path}/tweet_quote_map.json", "r") as map_file:
            mapping = json.loads(map_file.read())
            quote_count += mapping["count"]

        with open(f"{news_dir_path}/tweet_reply_map.json", "r") as map_file:
            mapping = json.loads(map_file.read())
            reply_count += mapping["count"]

print(f"source tweet number: {source_tweet_count}, including {quote_count} quotes and {reply_count} replies")
# source tweet number: 119009, including 131 quotes and 189 replies
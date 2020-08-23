import os
from os import path

import json

NEWS_DIR = "fakenewsnet_dataset/politifact/fake"
RESULT = "fakenewsnet_dataset/politifact/fake/tweet.json"

tweet_count = 0
for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):
        news_path = path.join(news_dir_path, "news content.json")
        if path.exists(news_path):

            tweet_dir_path = path.join(news_dir_path, "tweets")

            if path.exists(tweet_dir_path):
                tweet_count += len(os.listdir(tweet_dir_path))

print(f"total tweets in {NEWS_DIR}: {tweet_count}")

result_file_path = path.abspath( path.join(path.dirname(__file__), RESULT) )

with open(result_file_path, "w") as result_file:
    result_file.write(json.dumps({'tweet_count': tweet_count}, indent=4))
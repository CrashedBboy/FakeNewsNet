import os
from os import path

import json

NEWS_DIR = "../fakenewsnet_dataset/politifact/fake"
RESULT = "../fakenewsnet_dataset/politifact/fake/hop1_quote_list.json"

quote_list = []
for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):
        news_path = path.join(news_dir_path, "news content.json")
        if path.exists(news_path):

            tweet_dir_path = path.join(news_dir_path, "tweets")
            if path.exists(tweet_dir_path):

                for tweet_filename in os.listdir(tweet_dir_path):
                    if tweet_filename == "first_date.json":
                        continue

                    with open(path.join(tweet_dir_path, tweet_filename), "r") as tweet_file:
                        tweet_dict = json.loads(tweet_file.read())

                        if tweet_dict["is_quote_status"] != False:
                            quote_list.append(tweet_dict)

print(f"total quote tweets: {len(quote_list)}")

result_file_path = path.abspath( path.join(path.dirname(__file__), RESULT) )

with open(result_file_path, "w") as result_file:
    result_file.write(json.dumps({'count': len(quote_list), 'quote_tweet': quote_list}, indent=4))
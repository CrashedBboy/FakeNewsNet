###
# Statistics: #fake news
# #fake news having propagation network (having at least one post)
###


import os
from os import path

import json

NEWS_DIR = "../../fakenewsnet_dataset/politifact/fake"
RESULT = "../../fakenewsnet_dataset/politifact/fake/source.json"

total_news_count = 0
exist_news_count = 0
tweeted_news_count = 0
source_dict = {}
for item in os.listdir(NEWS_DIR):
    news_dir_path = path.abspath( path.join(path.dirname(__file__), NEWS_DIR, item) )
    
    if path.isdir(news_dir_path):
        total_news_count += 1
        news_path = path.join(news_dir_path, "news content.json")
        if path.exists(news_path):
            exist_news_count += 1

            with open(news_path, "r") as news_file:
                news_dict = json.loads(news_file.read())

                source = news_dict['source']

                if source in source_dict:
                    source_dict[source] += 1
                else:
                    source_dict[source] = 1

            tweet_dir_path = path.join(news_dir_path, "tweets")
            retweet_dir_path = path.join(news_dir_path, "retweets")
            if path.exists(tweet_dir_path) and path.exists(retweet_dir_path):
                tweeted_news_count += 1

print(f"total news: {total_news_count}, existed news: {exist_news_count}, tweeted news: {tweeted_news_count}")
# total news: 432, existed news: 376, tweeted news: 339

# result_file_path = path.abspath( path.join(path.dirname(__file__), RESULT) )

# with open(result_file_path, "w") as result_file:
#     result_file.write(json.dumps(source_dict, indent=4))
import os
from os import path
import json

import numpy as np
import matplotlib.pyplot as plt


NEWS_DIR = "../fakenewsnet_dataset/politifact/fake"
NEWS_DIR =  path.abspath( path.join(path.dirname(__file__), NEWS_DIR) )

OUTPUT_FILE = "../exported/source_tweet.csv"
OUTPUT_FILE =  path.abspath( path.join(path.dirname(__file__), OUTPUT_FILE) )

def tree_size(root_node):

    node_count  = 1 # itself

    children = [] + root_node["quoted_by"] + root_node["replied_by"] + root_node["retweeted_by"]
    for child in children:
        node_count += tree_size(child)

    return node_count

HEADER = "news_id,source_tweet_id,created_at,text,user_count,tag_count,symbol_count,url_count,cascade_size"

news_count = 0
data_rows = [HEADER]
for item in os.listdir(NEWS_DIR):
    news_dir_path = f"{NEWS_DIR}/{item}"
    
    source_tweet_dir_path = f"{news_dir_path}/tweets"
    
    if path.isdir(news_dir_path):

        print(f"{item}")

        news_count += 1
        # if news_count > 10:
        #     break

        with open(f"{news_dir_path}/cascade.json", "r") as cascade_file:
            cascades = json.loads(cascade_file.read())

            for cas in cascades:

                cascade_size = tree_size(cas)

                with open(f"{source_tweet_dir_path}/{cas['id']}.json", "r", encoding="utf-8") as source_tweet_file:
                    source_tweet = json.loads(source_tweet_file.read())

                    post_text = source_tweet['text'].replace('"', '').replace("\n", "")
                    
                    user_mentioned_count = len(source_tweet['entities']['user_mentions'])
                    hash_tag_count = len(source_tweet['entities']['hashtags'])
                    symbol_count = len(source_tweet['entities']['symbols'])
                    url_count = len(source_tweet['entities']['urls'])

                    tweet_id = source_tweet['id']
                    created_at = source_tweet['created_at']

                    data_rows.append(f'{item},{tweet_id},"{created_at}","{post_text}",{user_mentioned_count},{hash_tag_count},{symbol_count},{url_count},{cascade_size}')

with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
    output_file.write("\n".join(data_rows))
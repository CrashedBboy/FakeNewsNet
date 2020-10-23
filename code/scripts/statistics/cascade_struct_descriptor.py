import os
from os import path
import json

import numpy as np
import matplotlib.pyplot as plt

dataset_dir = "../fakenewsnet_dataset/politifact/fake"
dataset_dir = path.abspath( path.join(path.dirname(__file__), dataset_dir))

# [STATISTICS] results
NEWS_COUNT = 0
POST_PER_CASCADE = []
POST_PER_NEWS = []
TOTAL_POST = 0
CASCADE_PER_NEWS = []
TOTAL_CASCADE = 0

# iterate all news
for item in os.listdir(dataset_dir):

    news_dir_path = f"{dataset_dir}/{item}"

    if not path.isdir(news_dir_path):
        continue

    # check existence of news article
    if not path.exists(f"{news_dir_path}/news content.json"):
        continue

    # check existence of cascade file
    if not path.exists(f"{news_dir_path}/cascade.json"):
        continue
    
    NEWS_COUNT += 1
    print(f"{NEWS_COUNT}: {item}")

    # if NEWS_COUNT > 100:
    #     break

    news_post_count = 0

    with open(f"{news_dir_path}/cascade.json", "r") as cascade_file:
        forest = json.loads(cascade_file.read())

        # [STATISTICS] cascade per news
        CASCADE_PER_NEWS.append(len(forest))

        # [STATISTICS] total cascade
        TOTAL_CASCADE += len(forest)

        for cascade in forest:

            # [STATISTICS] tweets per cascade

            # collect IDs from source tweet, replies, quotes using BFS
            i = 0
            tweet_ids = []
            bfs_queue = [cascade]
            while i < len(bfs_queue):
                traversed = bfs_queue[i]
                tweet_ids.append(traversed['id'])

                if len(traversed['quoted_by']) > 0:
                    bfs_queue += traversed['quoted_by']

                if len(traversed['replied_by']) > 0:
                    bfs_queue += traversed['replied_by']

                i += 1
            # length of bfs_queue is #(source tweet + replies + quites)
            
            cascade_retweet_count = 0
            for id in tweet_ids:
                with open(f"{news_dir_path}/retweets/{id}.json", "r") as retweet_list_file:
                    retweet_list = json.loads(retweet_list_file.read())
                    cascade_retweet_count += len(retweet_list['retweets'])
            
            cascade_retweet_count += len(bfs_queue)

            # [STATISTIC] tweets per news
            news_post_count += cascade_retweet_count

            # [STATISTIC] total post
            TOTAL_POST += cascade_retweet_count

            POST_PER_CASCADE.append(cascade_retweet_count)

    POST_PER_NEWS.append(news_post_count)

# [RESULT]: post per cascade
# count the occurance
POST_PER_CASCADE_FREQUENCY = {occurence: POST_PER_CASCADE.count(occurence) for occurence in set(POST_PER_CASCADE)}

POST_PER_CASCADE = np.array(POST_PER_CASCADE)
print(f"[#post per cascade] min:{POST_PER_CASCADE.min()}, max:{POST_PER_CASCADE.max()}, average:{POST_PER_CASCADE.mean()}, median: {np.median(POST_PER_CASCADE)}")

# plot the occurance
post_number = sorted([int(n) for n in POST_PER_CASCADE_FREQUENCY.keys()])
count = [ POST_PER_CASCADE_FREQUENCY[n] for n in post_number]
count = np.log2(np.array(count))

fig, ax = plt.subplots()
ax.barh(post_number, count, align='center')
ax.set_ylabel('#Tweet'), ax.set_xlabel('log2(#Cascade)')
ax.invert_yaxis()
ax.set_title('#Tweet per Cascade')
plt.show()

# [RESULT]: post per news
POST_PER_NEWS = np.array(POST_PER_NEWS)
print(f"[#post per news] min:{POST_PER_NEWS.min()}, max:{POST_PER_NEWS.max()}, average:{POST_PER_NEWS.mean()}, median:{np.median(POST_PER_NEWS)}")

# [RESULT]: total post
print(f"[#post in total]: {TOTAL_POST}")

# [RESULT]: cascade per news
CASCADE_PER_NEWS = np.array(CASCADE_PER_NEWS)
print(f"[#cascade per news] min:{CASCADE_PER_NEWS.min()}, max:{CASCADE_PER_NEWS.max()}, average:{CASCADE_PER_NEWS.mean()}, median:{np.median(CASCADE_PER_NEWS)}")

# [RESULT]: total cascade
print(f"[#cascade in total]: {TOTAL_CASCADE}")

# [RESULT]: news in total
print(f"[#news in total]: {NEWS_COUNT}")
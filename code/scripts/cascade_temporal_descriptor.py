import os
from os import path
import json
from datetime import date

import numpy as np
import matplotlib.pyplot as plt

dataset_dir = "../fakenewsnet_dataset/politifact/fake"
dataset_dir = path.abspath( path.join(path.dirname(__file__), dataset_dir))

DATE_MAX = date(2095, 12, 31)
DATE_MIN = date(1995, 2, 5)

# convert month string to number
def month_str_to_num(month_string):
    month_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    if month_string in month_dict:
        return month_dict[month_string]
    else:
        return -1

def parse_tweet_date(date_string):

    # example of date string: "Fri Dec 08 17:08:28 +0000 2017"
    y = int(date_string.split(" ")[5])
    m = month_str_to_num(date_string.split(" ")[1])
    assert m >= 1
    d = int(date_string.split(" ")[2])

    return date(y, m, d)

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{:.3f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

# [STATISTICS] results
NEWS_COUNT = 0
LIFESPAN_PER_CASCADE = [] # lifespan of all cascades
LIFESPAN_PER_CASCADE_RT = [] # lifespan of cascades having Replies / Quotes / Retweets
LIFESPAN_PER_NEWS = []

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

    # if NEWS_COUNT > 40:
    #     break

    news_post_count = 0

    with open(f"{news_dir_path}/cascade.json", "r") as cascade_file:
        forest = json.loads(cascade_file.read())

        news_first_date = DATE_MAX
        news_last_date = DATE_MIN

        for cascade in forest:

            cascade_first_date = DATE_MAX
            cascade_last_date = DATE_MIN

            post_count = 0

            # collect IDs from source tweet, replies, quotes using BFS
            i = 0
            tweet_ids = []
            bfs_queue = [cascade]
            while i < len(bfs_queue):
                traversed = bfs_queue[i]
                tweet_ids.append(traversed['id'])

                with open(f"{news_dir_path}/tweets/{traversed['id']}.json", "r") as tweet_file:
                    tweet = json.loads(tweet_file.read())
                    created_at = parse_tweet_date(tweet['created_at'])

                    # update last / first date of cascade / news
                    news_first_date = min(created_at, news_first_date)
                    news_last_date = max(created_at, news_last_date)
                    cascade_first_date = min(created_at, cascade_first_date)
                    cascade_last_date = max(created_at, cascade_last_date)

                if len(traversed['quoted_by']) > 0:
                    bfs_queue += traversed['quoted_by']

                if len(traversed['replied_by']) > 0:
                    bfs_queue += traversed['replied_by']

                i += 1

            # length of tweet_ids is #(source tweet + replies + quites)
            post_count += len(tweet_ids)

            for id in tweet_ids:
                with open(f"{news_dir_path}/retweets/{id}.json", "r") as retweet_list_file:
                    retweet_list = json.loads(retweet_list_file.read())

                    post_count += len(retweet_list['retweets'])
                    for retweet in retweet_list['retweets']:
                        created_at = parse_tweet_date(retweet['created_at'])
                
                        # update last / first date of cascade / news
                        news_first_date = min(created_at, news_first_date)
                        news_last_date = max(created_at, news_last_date)
                        cascade_first_date = min(created_at, cascade_first_date)
                        cascade_last_date = max(created_at, cascade_last_date)

            cascade_lifespan = (cascade_last_date - cascade_first_date).days # calculated in days

            if post_count > 1:
                LIFESPAN_PER_CASCADE_RT.append(cascade_lifespan)

            LIFESPAN_PER_CASCADE.append(cascade_lifespan)

        news_lifespan = (news_last_date - news_first_date).days # calculated in days
        LIFESPAN_PER_NEWS.append(news_lifespan)

#------------------------------------------PRINT RESULT------------------------------------------------

# [RESULT] lifespan per news
LIFESPAN_PER_NEWS = np.array(LIFESPAN_PER_NEWS)
print(f"[lifespan per news] min: {LIFESPAN_PER_NEWS.min()}, max: {LIFESPAN_PER_NEWS.max()}, average: {LIFESPAN_PER_NEWS.mean()}, median: {np.median(LIFESPAN_PER_NEWS)}")

bin_frequency = {
    '1 day': 0 ,
    '1 week': 0,
    '1 month': 0,
    'half year': 0,
    '1 year': 0,
    '> 1 year': 0
}

for n in LIFESPAN_PER_NEWS:
    if n <= 1:
        bin_frequency['1 day'] += 1
    elif n > 1 and n <= 7:
        bin_frequency['1 week'] += 1
    elif n > 7 and n <= 30:
        bin_frequency['1 month'] += 1
    elif n > 30 and n <= 180:
        bin_frequency['half year'] += 1
    elif n > 180 and n <= 365:
        bin_frequency['1 year'] += 1
    else:
        bin_frequency['> 1 year'] += 1

time_lengths = bin_frequency.keys()
news_number = np.array([bin_frequency[n] for n in time_lengths], dtype=np.float)
news_number = news_number / len(LIFESPAN_PER_NEWS)

fig, ax = plt.subplots()
bars = ax.bar(time_lengths, news_number, width=0.8)
autolabel(bars)
ax.set_ylabel('News Number'), ax.set_xlabel('Lifespan')
ax.set_title('Lifespan of News')
plt.show()

# [RESULT] lifespan per cascade
LIFESPAN_PER_CASCADE = np.array(LIFESPAN_PER_CASCADE)
print(f"[lifespan per cascade] min: {LIFESPAN_PER_CASCADE.min()}, max: {LIFESPAN_PER_CASCADE.max()}, average: {LIFESPAN_PER_CASCADE.mean()}, median: {np.median(LIFESPAN_PER_CASCADE)}")

bin_frequency = {
    '1 day': 0 ,
    '3 days': 0,
    '1 week': 0,
    'half month': 0,
    '1 month': 0,
    '> 1 month': 0
}

for n in LIFESPAN_PER_CASCADE:
    if n <= 1:
        bin_frequency['1 day'] += 1
    elif n > 1 and n <= 3:
        bin_frequency['3 days'] += 1
    elif n > 3 and n <= 7:
        bin_frequency['1 week'] += 1
    elif n > 7 and n <= 14:
        bin_frequency['half month'] += 1
    elif n > 14  and n <= 30:
        bin_frequency['1 month'] += 1
    else:
        bin_frequency['> 1 month'] += 1

time_lengths = bin_frequency.keys()
news_number = np.array([bin_frequency[n] for n in time_lengths], dtype=np.float)
news_number = news_number / len(LIFESPAN_PER_CASCADE)
fig, ax = plt.subplots()
bars = ax.bar(time_lengths, news_number, width=0.8)
autolabel(bars)
ax.set_ylabel('Cascade Number'), ax.set_xlabel('Lifespan')
ax.set_title('Lifespan of Cascade')
plt.show()

# [RESULT] lifespan per cascade
LIFESPAN_PER_CASCADE_RT = np.array(LIFESPAN_PER_CASCADE_RT)
print(f"[lifespan per cascade (>= 2 posts)] min: {LIFESPAN_PER_CASCADE_RT.min()}, max: {LIFESPAN_PER_CASCADE_RT.max()}, average: {LIFESPAN_PER_CASCADE_RT.mean()}, median: {np.median(LIFESPAN_PER_CASCADE_RT)}")

bin_frequency = {
    '1 day': 0 ,
    '3 days': 0,
    '1 week': 0,
    'half month': 0,
    '1 month': 0,
    '> 1 month': 0
}

for n in LIFESPAN_PER_CASCADE_RT:
    if n <= 1:
        bin_frequency['1 day'] += 1
    elif n > 1 and n <= 3:
        bin_frequency['3 days'] += 1
    elif n > 3 and n <= 7:
        bin_frequency['1 week'] += 1
    elif n > 7 and n <= 14:
        bin_frequency['half month'] += 1
    elif n > 14  and n <= 30:
        bin_frequency['1 month'] += 1
    else:
        bin_frequency['> 1 month'] += 1

time_lengths = bin_frequency.keys()
news_number = np.array([bin_frequency[n] for n in time_lengths], dtype=np.float)
news_number = news_number / len(LIFESPAN_PER_CASCADE_RT)

fig, ax = plt.subplots()
bars = ax.bar(time_lengths, news_number, width=0.8)
autolabel(bars)
ax.set_ylabel('Cascade Number'), ax.set_xlabel('Lifespan')
ax.set_title('Lifespan of Cascade(#post > 1)')
plt.show()
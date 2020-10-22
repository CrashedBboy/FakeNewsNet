import os
from os import path
import shutil
import json
from datetime import datetime
from functools import cmp_to_key

DATASET_DIR = "../fakenewsnet_dataset"
DATASET_DIR = path.abspath( path.join(path.dirname(__file__), DATASET_DIR) )
NEWS_DIR = f"{DATASET_DIR}/politifact/fake"

def get_index_in_forest(forest, id):
    for index, cascade in enumerate(forest):
        if cascade['id'] == id:
            return index
    return -1

# BFS: to form correct forest
def fold_forest(type, forest, parent_id, child_id):

    child_index = get_index_in_forest(forest, child_id)

    candidates = forest[:]
    visited = 0

    while visited < len(candidates):
        
        if candidates[visited]['id'] == parent_id:
            if type == 'quote':
                candidates[visited]['quoted_by'].append(forest[child_index])
            if type == 'reply':
                candidates[visited]['replied_by'].append(forest[child_index])
            forest.remove(forest[child_index])

            return (True, forest)
        else:
            candidates += candidates[visited]['quoted_by']
            candidates += candidates[visited]['replied_by']

        visited += 1

    return (False, forest)

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

def get_post_datatime(datatime_str):

    # example of date string: "Fri Dec 08 17:08:28 +0000 2017"

    datetime_slices = datatime_str.split(" ")

    year = int(datetime_slices[5])
    month = month_str_to_num(datetime_slices[1])
    assert month >= 1
    day = int(datetime_slices[2])
    hour = int(datetime_slices[3].split(":")[0])
    minute = int(datetime_slices[3].split(":")[1])
    second = int(datetime_slices[3].split(":")[2])

    return datetime(year, month, day, hour, minute, second)

def datetime_to_value(post):
    t = get_post_datatime(post['created_at'])
    return t.timestamp()

# return: whether user1 is followed by user 2
def is_followed_by(uid1, uid2):

    if path.exists(f"{DATASET_DIR}/rt_user_followers/{uid1}.json"):

        with open(f"{DATASET_DIR}/rt_user_followers/{uid1}.json", "r") as follower_list_file:
            follower_list = json.loads(follower_list_file.read())['followers']

            if uid2 in follower_list:
                return True
            else:
                return False

    elif path.exists(f"{DATASET_DIR}/user_followers/{uid1}.json"):

        with open(f"{DATASET_DIR}/user_followers/{uid1}.json", "r") as follower_list_file:
            follower_list = json.loads(follower_list_file.read())['followers']

            if uid2 in follower_list:
                return True
            else:
                return False
    else:
        return False

def append_retweet_to_cascade(cascade_root_id, retweet):

    cascade_root = None
    for cascade in cascade_forest:
        if cascade['id'] == cascade_root_id:
            cascade_root = cascade
            break
    
    assert cascade_root is not None

    latest_parent = cascade_root
    latest_datetime = get_post_datatime(cascade_root['created_at'])
    traversal_queue = [cascade_root]
    idx = 0

    # BFS traversal
    while idx < len(traversal_queue):

        current_post = traversal_queue[idx]

        # check: whether the datetime is newer & they have following relationship
        if is_followed_by(current_post['user'], retweet['user']) and get_post_datatime(current_post['created_at']) > latest_datetime:
            latest_parent = current_post
            latest_datetime = get_post_datatime(current_post['created_at'])

        # BFS traverse
        traversal_queue += current_post['retweeted_by']

        idx += 1

    latest_parent['retweeted_by'].append(retweet)

news_count = 0

for item in os.listdir(NEWS_DIR):
    news_dir_path = f"{NEWS_DIR}/{item}"
    
    if path.isdir(news_dir_path):

        news_count += 1
        print(f"{news_count}: {item}")

        # check whether news article exists
        news_path = path.join(news_dir_path, "news content.json")
        if path.exists(news_path):

            ########
            # create initial forest
            ########

            # check whether tweets/ dir existed
            tweet_dir_path = f"{news_dir_path}/tweets"
            if not path.exists(tweet_dir_path):
                continue

            tweet_filenames = os.listdir(tweet_dir_path)
            cascade_forest = []
            for fn in tweet_filenames:
                with open(f"{tweet_dir_path}/{fn}", "r") as tweet_file:
                    tweet = json.loads(tweet_file.read())
                    cascade_forest.append({
                        'id': tweet['id'],
                        'created_at': tweet['created_at'],
                        'user': tweet['user']['id'],
                        'quoted_by': [],
                        'replied_by': [],
                        'retweeted_by': []
                    })
            tweet_filenames = None


            ########
            # append retweets
            ########

            # check whether retweets/ dir existed
            retweet_dir_path = f"{news_dir_path}/retweets"
            if not path.exists(retweet_dir_path):
                continue

            for tweet_rt_list_fn in os.listdir(f"{news_dir_path}/retweets"):

                tweet_id = int(tweet_rt_list_fn.split(".")[0])

                with open(f"{news_dir_path}/retweets/{tweet_rt_list_fn}", "r") as rt_file:
                    tweet_rt_list = json.loads(rt_file.read())

                    # 1. sort list of retweets by datetime in ASC order
                    tweet_rt_list = [ 
                        {
                            'id': rt['id'],
                            'created_at': rt['created_at'],
                            'user': rt['user']['id'],
                            'quoted_by': [],
                            'replied_by': [],
                            'retweeted_by': []
                        }  for rt in tweet_rt_list['retweets']
                    ]
                    tweet_rt_list = sorted(tweet_rt_list, key = datetime_to_value)

                    # 2. append to latest node in the cascade
                    for rt in tweet_rt_list: 
                        append_retweet_to_cascade(tweet_id, rt)

            ########
            # append quotes & replies under other nodes
            ########

            quote_map, reply_map = None, None
            # read quote mapping file
            with open(f"{news_dir_path}/tweet_quote_map.json", "r") as quote_map_file:
                quote_map = json.loads(quote_map_file.read())

            # read reply mapping file
            with open(f"{news_dir_path}/tweet_reply_map.json", "r") as reply_map_file:
                reply_map = json.loads(reply_map_file.read())

            if quote_map is None or reply_map is None:
                print(f"mapping of news {item} is missing!")
                exit()

            for mapping in quote_map['map']:
                parent_id = mapping['quoted']
                child_id = mapping['quoting']

                # grow cascade tree
                (result, new_cascade_forest) = fold_forest('quote', cascade_forest, parent_id, child_id)

                if result == False:
                    print(f"cannot find parent!! quote, {item}, {parent_id}, {child_id}")
                    print(cascade_forest)
                    print(new_cascade_forest)
                    exit()
                else:
                    cascade_forest = new_cascade_forest

            for mapping in reply_map['map']:
                parent_id = mapping['replied']
                child_id = mapping['replying']

                # grow cascade tree
                (result, new_cascade_forest) = fold_forest('reply', cascade_forest, parent_id, child_id)

                if result == False:
                    print(f"cannot find parent!! reply, {item}, {parent_id}, {child_id}")
                    print(cascade_forest)
                    print(new_cascade_forest)
                    exit()
                else:
                    cascade_forest = new_cascade_forest

            ########
            # export to file
            ########
            with open(f"{news_dir_path}/cascade.json", "w") as cascade_file:
                cascade_file.write(json.dumps(cascade_forest))


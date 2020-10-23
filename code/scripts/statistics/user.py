###
# collect all user IDs in order to download their timeline
# STATISTICS: #users(#source tweet authors, #spreader)
###
import os
from os import path
import json

dataset_dir = "../fakenewsnet_dataset/"
dataset_dir = path.abspath( path.join(path.dirname(__file__), dataset_dir))

all_user_ids = set()

# collect user IDs from user_profiles, rt_user_profiles, and follower_profiles

ids_tweeter = [ int(fn.split(".")[0]) for fn in os.listdir(f"{dataset_dir}/user_profiles")]
ids_tweeter = set(ids_tweeter)
print(f"{len(ids_tweeter)} users in Tweeter folder")

all_user_ids.update(ids_tweeter)
ids_tweeter = None

ids_retweeter = [ int(fn.split(".")[0]) for fn in os.listdir(f"{dataset_dir}/rt_user_profiles") ]
ids_retweeter = set(ids_retweeter)
print(f"{len(ids_retweeter)} users in Retweeter folder")

all_user_ids.update(ids_retweeter)
ids_retweeter = None

print(f"{len(all_user_ids)} users in total who joined news dissemination")

# 73384 users in Tweeter folder
# 76862 users in Retweeter folder
# 143125 users in total who joined news dissemination
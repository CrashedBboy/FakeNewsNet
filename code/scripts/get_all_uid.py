###
# collect all user IDs in order to download their timeline
# STATISTICS: #users(#source tweet authors, #spreader)
###
import os
from os import path
import random
import json
import math
from datetime import date

import numpy as np
import matplotlib.pyplot as plt

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

ids_follower = [ int(fn.split(".")[0]) for fn in os.listdir(f"{dataset_dir}/follower_profiles") ] # sampled followers
ids_follower = set(ids_follower)
print(f"{len(ids_follower)} users in follower folder")

all_user_ids.update(ids_follower)
ids_follower = None

all_user_ids = list(all_user_ids)

print(f"all user number: {len(all_user_ids)}")

split = math.floor(len(all_user_ids) / 3)

with open(f"{dataset_dir}/all_user_id.json", 'w') as id_file:
    id_file.write(json.dumps(all_user_ids))

with open(f"{dataset_dir}/all_user_id.part1.json", 'w') as id_file:
    id_file.write(json.dumps(all_user_ids[ : split * 1]))

with open(f"{dataset_dir}/all_user_id.part2.json", 'w') as id_file:
    id_file.write(json.dumps(all_user_ids[ split * 1 : split * 2 ]))

with open(f"{dataset_dir}/all_user_id.part3.json", 'w') as id_file:
    id_file.write(json.dumps(all_user_ids[ split * 2 : ]))
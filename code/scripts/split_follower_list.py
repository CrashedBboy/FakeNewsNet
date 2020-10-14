import os
from os import path
import random
import json
import shutil
import math
from datetime import date

import numpy as np
import matplotlib.pyplot as plt

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError:  # Guard against race condition
            raise

dataset_dir = "../fakenewsnet_dataset/"
dataset_dir = path.abspath( path.join(path.dirname(__file__), dataset_dir))

with open(f"{dataset_dir}/follower_sample_map.json", "r") as map_file:
    all_sampled_followers = json.loads(map_file.read())


# get all IDs from sample map
all_follower_ids = set()
for li in all_sampled_followers['sample_map'].values():
    follower_set = set(li)
    all_follower_ids.update(follower_set)

# set and create dest dir
print("set and create dest dir")
follower_profiles_folder = f"{dataset_dir}/follower_profiles"
create_dir(follower_profiles_folder)

# check profile duplication
print("check profile duplication")
final_follower_ids = []
skipped_count = 0

all_follower_length = len(all_follower_ids)
for (idx, id) in enumerate(all_follower_ids):

    if idx%1000 == 0:
        print(f"{idx} / {all_follower_length}")

    if path.exists(f"{dataset_dir}/user_profiles/{id}.json"):

        skipped_count += 1
        shutil.copyfile(f"{dataset_dir}/user_profiles/{id}.json", f"{follower_profiles_folder}/{id}.json")
        continue

    if os.path.exists(f"{dataset_dir}/rt_user_profiles/{id}.json"):

        skipped_count += 1
        shutil.copyfile(f"{dataset_dir}/rt_user_profiles/{id}.json", f"{follower_profiles_folder}/{id}.json")
        continue

    final_follower_ids.append(id)

print(f"Total follower profiles to be fetched: {len(final_follower_ids)}, skipped: {skipped_count}")


# export
split_size = math.floor(len(final_follower_ids) / 3)

with open(f"{dataset_dir}/follower_profile_ids.part1.json", "w") as id_list_file:
    id_list_file.write(json.dumps(final_follower_ids[ : split_size * 1]))

with open(f"{dataset_dir}/follower_profile_ids.part2.json", "w") as id_list_file:
    id_list_file.write(json.dumps(final_follower_ids[ split_size * 1 : split_size * 2]))

with open(f"{dataset_dir}/follower_profile_ids.part3.json", "w") as id_list_file:
    id_list_file.write(json.dumps(final_follower_ids[ split_size * 2 : ]))
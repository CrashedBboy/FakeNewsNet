import os
from os import path
import random
import json
from datetime import date

import numpy as np
import matplotlib.pyplot as plt

dataset_dir = "../fakenewsnet_dataset/"
dataset_dir = path.abspath( path.join(path.dirname(__file__), dataset_dir))

K = 10 # sample number

all_sampled_followers = {}

user_followers_dir = f"{dataset_dir}/user_followers"
rter_followers_dir = f"{dataset_dir}/rt_user_followers"

# check dir existence
if not path.exists(user_followers_dir):
    print(f"error! follower list dir doens't exist: {user_followers_dir}")
    exit()

if not path.exists(rter_followers_dir):
    print(f"error! follower list dir doens't exist: {rter_followers_dir}")
    exit()

# get follower IDs from user_followers/
print("get follower IDs from user_followers/")

file_list = os.listdir(user_followers_dir)
file_number = len(file_list)
for idx, fn in enumerate(file_list):

    if idx%1000 == 0:
        print(f"{idx} / {file_number}")

    if idx > 1000:
        break

    uid = int(fn.split(".")[0])

    with open(f"{user_followers_dir}/{fn}", "r") as follower_list_file:
        follower_list = json.loads(follower_list_file.read())['followers']

        follower_number = len(follower_list)
        sampled_followers = None

        if follower_number == 0:
            sampled_followers = []
        elif follower_number >= K:
            # sample without replacement
            sampled_followers = random.sample(follower_list, K)
        elif follower_number < K:
            # sample with replacement (may have repetition)
            sampled_followers = random.choices(follower_list, k = K)

        all_sampled_followers[uid] = sampled_followers

# get follower IDs from rt_user_followers/
print("get follower IDs from rt_user_followers/")

file_list = os.listdir(rter_followers_dir)
file_number = len(file_list)
for idx, fn in enumerate(file_list):

    if idx%1000 == 0:
        print(f"{idx} / {file_number}")

    uid = int(fn.split(".")[0])

    if uid in all_sampled_followers:
        continue

    with open(f"{rter_followers_dir}/{fn}", "r") as follower_list_file:
        follower_list = json.loads(follower_list_file.read())['followers']

        follower_number = len(follower_list)
        sampled_followers = None

        if follower_number == 0:
            sampled_followers = []
        elif follower_number >= K:
            # sample without replacement
            sampled_followers = random.sample(follower_list, K)
        elif follower_number < K:
            # sample with replacement (may have repetition)
            sampled_followers = random.choices(follower_list, k = K)

        all_sampled_followers[uid] = sampled_followers

# save follower sample map back to file
with open(f"{dataset_dir}/follower_sample_map.json", "w") as sample_map_file:
    sample_map_file.write(json.dumps({
        'K': K,
        'sample_map': all_sampled_followers
    }))
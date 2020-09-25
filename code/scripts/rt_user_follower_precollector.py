import os
import json
import shutil
from os import path
import math

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError:  # Guard against race condition
            raise

# dateset root
dateset_dir = '../fakenewsnet_dataset'
dataset_dir = path.abspath( path.join( path.dirname(__file__), dateset_dir ) )

# set up export dir
rt_user_follower_dir = f'{dataset_dir}/rt_user_followers'
create_dir(rt_user_follower_dir)

rt_user_profile_dir = f'{dataset_dir}/rt_user_profiles'
user_follower_dir = f'{dataset_dir}/user_followers'

# collect user IDs that have follower list already
existed_followers = []
not_existed_followers = []
for follower_filename in os.listdir(user_follower_dir):
    existed_followers.append(follower_filename.split(".")[0])

for rt_user_filename in os.listdir(rt_user_profile_dir):
    uid = rt_user_filename.split(".")[0]

    if uid in existed_followers:
        shutil.copyfile(f"{user_follower_dir}/{uid}.json", f"{rt_user_follower_dir}/{uid}.json")
    else:
        not_existed_followers.append(uid)

users_per_worker = math.floor(len(not_existed_followers) / 4)

with open(f"{dataset_dir}/rt_user_ids_1.json", "w") as user_id_file:
    user_id_file.write(json.dumps({ 'users': not_existed_followers[ : users_per_worker * 1] }))

with open(f"{dataset_dir}/rt_user_ids_2.json", "w") as user_id_file:
    user_id_file.write(json.dumps({ 'users': not_existed_followers[users_per_worker * 1 : users_per_worker * 2] }))

with open(f"{dataset_dir}/rt_user_ids_3.json", "w") as user_id_file:
    user_id_file.write(json.dumps({ 'users': not_existed_followers[users_per_worker * 2 : users_per_worker * 3] }))

with open(f"{dataset_dir}/rt_user_ids_4.json", "w") as user_id_file:
    user_id_file.write(json.dumps({ 'users': not_existed_followers[users_per_worker * 3 : ] }))
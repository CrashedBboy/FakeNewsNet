import os
import json
from os import path

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError:  # Guard against race condition
            raise

# set up export dir
rt_user_profile_dir = '../fakenewsnet_dataset/rt_user_profiles'
rt_user_profile_dir = path.abspath( path.join( path.dirname(__file__), rt_user_profile_dir ) )
create_dir(rt_user_profile_dir)

news_list_dir = '../fakenewsnet_dataset/politifact/fake'
news_list_dir = path.abspath( path.join( path.dirname(__file__), news_list_dir ) )

user_ids = []
i = 0
for news_dir in os.listdir(news_list_dir):
    news_dir = path.join(news_list_dir, news_dir)
    if path.isdir(news_dir):
        print(i)
        retweet_dir = path.join(news_dir, 'retweets')

        if path.exists(retweet_dir):
            for retweet_list_filename in os.listdir(retweet_dir):
                with open(path.join(retweet_dir, retweet_list_filename), "r") as retweet_list_file:
                    retweet_list = json.loads(retweet_list_file.read())

                    for rt in retweet_list['retweets']:
                        if rt['user']['id'] not in user_ids:
                            with open(path.join(rt_user_profile_dir, f"{rt['user']['id']}.json"), "w") as profile_file:
                                profile_file.write(json.dumps(rt['user']))
                            user_ids.append(rt['user']['id'])
        i += 1
import json
import logging
import os
import shutil
import random
from pathlib import Path
from twython import TwythonError, TwythonRateLimitError

from util.Constants import GET_USER, GET_USER_TWEETS, USER_ID, FOLLOWERS, GET_FRIENDS_ID, FOLLOWING
from util.TwythonConnector import TwythonConnector
from util.util import Config, is_folder_exists, create_dir, multiprocess_data_collection

from util.util import DataCollector

from util.Constants import GET_FOLLOWERS_ID


def get_user_ids_in_folder(samples_folder):
    user_ids = set()

    for news_id in os.listdir(samples_folder):
        news_dir = f"{samples_folder}/{news_id}"
        tweets_dir = f"{news_dir}/tweets"

        if is_folder_exists(news_dir) and is_folder_exists(tweets_dir):

            for tweet_file in os.listdir(tweets_dir):
                tweet_object = json.load(open("{}/{}".format(tweets_dir, tweet_file)))

                user_ids.add(tweet_object["user"]["id"])

    return user_ids

def get_user_ids_from_profile(dataset_folder):

    user_ids = []

    user_profile_path = f"{dataset_folder}/user_profiles"

    for profile in os.listdir(user_profile_path):
        user_id = int(profile.split(".json")[0])
        user_ids.append(user_id)

    return user_ids

def dump_user_profile_job(user_id, save_location, twython_connector: TwythonConnector):
    profile_info = None

    # Fetch and save user information if the file is not already present
    if not Path("{}/{}.json".format(save_location, user_id)).is_file():
        try:
            profile_info = twython_connector.get_twython_connection(GET_USER).show_user(user_id=user_id)

        except TwythonRateLimitError as ex:
            logging.exception("Twython API rate limit exception")

        finally:
            if profile_info:
                json.dump(profile_info, open("{}/{}.json".format(save_location, user_id), "w"))


def dump_user_recent_tweets_job(user_id, save_location, twython_connector: TwythonConnector):
    profile_info = None

    # Fetch and save user information if the file is not already present
    if not Path("{}/{}.json".format(save_location, user_id)).is_file():
        try:
            profile_info = twython_connector.get_twython_connection(GET_USER_TWEETS).get_user_timeline(user_id=user_id,
                                                                                                       count=200)

        except TwythonRateLimitError as ex:
            logging.exception("Twython API rate limit exception")

        finally:
            if profile_info:
                json.dump(profile_info, open("{}/{}.json".format(save_location, user_id), "w"))


def fetch_user_follower_ids(user_id, twython_connection):
    user_followers = []

    try:
        user_followers = twython_connection.get_followers_ids(user_id=user_id)
        user_followers = user_followers["ids"]
    except:
        logging.exception("Exception in follower_ids for user : {}".format(user_id))

    return user_followers


def fetch_user_friends_ids(user_id, twython_connection):
    user_friends = []

    try:
        user_friends = twython_connection.get_friends_ids(user_id=user_id)
        user_friends = user_friends["ids"]
    except:
        logging.exception("Exception in follower_ids for user : {}".format(user_id))

    return user_friends


def dump_user_followers(user_id, save_location, twython_connector: TwythonConnector):

    # Fetch and save user information if the file is not already present
    if not Path("{}/{}.json".format(save_location, user_id)).is_file():
        try:
            user_followers = fetch_user_follower_ids(user_id, twython_connector.get_twython_connection(GET_FOLLOWERS_ID))

            user_followers_info = {USER_ID: user_id, FOLLOWERS: user_followers}
            json.dump(user_followers_info, open("{}/{}.json".format(save_location, user_id), "w"))

        except:
            logging.exception("Exception in getting follower_ids for user : {}".format(user_id))


def dump_user_following(user_id, save_location, twython_connector: TwythonConnector):

    # Fetch and save user information if the file is not already present
    if not Path("{}/{}.json".format(save_location, user_id)).is_file():
        try:
            user_following = fetch_user_friends_ids(user_id, twython_connector.get_twython_connection(GET_FRIENDS_ID))

            user_following_info = {USER_ID: user_id,FOLLOWING : user_following}
            json.dump(user_following_info, open("{}/{}.json".format(save_location, user_id), "w"))

        except:
            logging.exception("Exception in getting follower_ids for user : {}".format(user_id))



def collect_user_profiles(config: Config, twython_connector: TwythonConnector):
    dump_location = config.dump_location

    all_user_ids = set()

    all_user_ids.update(get_user_ids_in_folder("{}/politifact/fake".format(dump_location)))
    all_user_ids.update(get_user_ids_in_folder("{}/politifact/real".format(dump_location)))
    all_user_ids.update(get_user_ids_in_folder("{}/gossipcop/fake".format(dump_location)))
    all_user_ids.update(get_user_ids_in_folder("{}/gossipcop/real".format(dump_location)))

    user_profiles_folder = "{}/{}".format(dump_location, "user_profiles")
    user_timeline_tweets_folder = "{}/{}".format(dump_location, "user_timeline_tweets")

    create_dir(user_profiles_folder)
    create_dir(user_timeline_tweets_folder)

    multiprocess_data_collection(dump_user_profile_job, all_user_ids, (user_profiles_folder, twython_connector), config)
    multiprocess_data_collection(dump_user_recent_tweets_job, all_user_ids, (user_timeline_tweets_folder,
                                                                             twython_connector), config)


class UserProfileCollector(DataCollector):

    def __init__(self, config):
        super(UserProfileCollector, self).__init__(config)

    def collect_data(self, choices):
        all_user_ids = set()

        for choice in choices:
            all_user_ids.update(get_user_ids_in_folder(
                "{}/{}/{}".format(self.config.dump_location, choice["news_source"], choice["label"])))

        user_profiles_folder = "{}/{}".format(self.config.dump_location, "user_profiles")
        create_dir(user_profiles_folder)

        multiprocess_data_collection(dump_user_profile_job, list(all_user_ids),
                                     (user_profiles_folder, self.config.twython_connector),
                                     self.config)

class FollowerProfileCollector(DataCollector):

    def __init__(self, config):
        super(FollowerProfileCollector, self).__init__(config)

    def collect_data(self, choices):

        # number of sampling
        K = 10

        if os.path.exists(f"{self.config.dump_location}/follower_profile_ids.json"):

            print(f"loads IDs to be fetched from follower_profile_ids.json")

            with open(f"{self.config.dump_location}/follower_profile_ids.json", "r") as id_list_file:
                final_follower_ids = json.loads(id_list_file.read())

            # set and create dest dir
            follower_profiles_folder = f"{self.config.dump_location}/follower_profiles"
            create_dir(follower_profiles_folder)

        else:

            if os.path.exists(f"{self.config.dump_location}/follower_sample_map.json"):

                print(f"loads sampled follower IDs from file follower_sample_map.json")

                with open(f"{self.config.dump_location}/follower_sample_map.json", "r") as map_file:
                    all_sampled_followers = json.loads(map_file.read())
            
            else:

                all_sampled_followers = {}

                user_followers_dir = f"{self.config.dump_location}/user_followers"
                rter_followers_dir = f"{self.config.dump_location}/rt_user_followers"

                # check dir existence
                if not os.path.exists(user_followers_dir):
                    print(f"error! follower list dir doens't exist: {user_followers_dir}")
                    return
                
                if not os.path.exists(rter_followers_dir):
                    print(f"error! follower list dir doens't exist: {rter_followers_dir}")
                    return
            
                # get follower IDs from user_followers/
                print("get follower IDs from user_followers/")
                for fn in os.listdir(user_followers_dir):

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
                for fn in os.listdir(rter_followers_dir):

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
                with open(f"{self.config.dump_location}/follower_sample_map.json", "w") as sample_map_file:
                    sample_map_file.write(json.dumps(all_sampled_followers))

            # set and create dest dir
            print("set and create dest dir")
            follower_profiles_folder = f"{self.config.dump_location}/follower_profiles"
            create_dir(follower_profiles_folder)

            # check profile duplication
            print("check profile duplication")
            all_follower_ids = []
            for li in all_sampled_followers.values():
                all_follower_ids += li
            final_follower_ids = []
            skipped_count = 0

            all_follower_length = len(all_follower_ids)
            for (idx, id) in enumerate(all_follower_ids):

                if idx%100 == 0:
                    print(f"{idx} / {all_follower_length}")

                if os.path.exists(f"{self.config.dump_location}/user_profiles/{id}.json"):

                    skipped_count += 1
                    shutil.copyfile(f"{self.config.dump_location}/user_profiles/{id}.json", f"{follower_profiles_folder}/{id}.json")
                    continue

                if os.path.exists(f"{self.config.dump_location}/rt_user_profiles/{id}.json"):

                    skipped_count += 1
                    shutil.copyfile(f"{self.config.dump_location}/rt_user_profiles/{id}.json", f"{follower_profiles_folder}/{id}.json")
                    continue

                final_follower_ids.append(id)

            print(f"Total follower profiles to be fetched: {len(final_follower_ids)}, skipped: {skipped_count}")

            # save download list back to file
            with open(f"{self.config.dump_location}/follower_download_ids.json", "w") as id_list_file:
                id_list_file.write(json.dumps(final_follower_ids))

        # multiprocess_data_collection(dump_user_profile_job, final_follower_ids,
        #                              (follower_profiles_folder, self.config.twython_connector),
        #                              self.config)

class UserTimelineTweetsCollector(DataCollector):

    def __init__(self, config):
        super(UserTimelineTweetsCollector, self).__init__(config)

    def collect_data(self, choices):
        all_user_ids = set()

        for choice in choices:
            all_user_ids.update(get_user_ids_in_folder(
                "{}/{}/{}".format(self.config.dump_location, choice["news_source"], choice["label"])))

        user_timeline_tweets_folder = "{}/{}".format(self.config.dump_location, "user_timeline_tweets")
        create_dir(user_timeline_tweets_folder)

        multiprocess_data_collection(dump_user_recent_tweets_job, list(all_user_ids), (user_timeline_tweets_folder,
                                                                                       self.config.twython_connector),
                                     self.config)


class UserFollowersCollector(DataCollector):

    def __init__(self, config):
        super(UserFollowersCollector, self).__init__(config)

    def collect_data(self, choices):

        use_id_from_profile = True

        # collect user IDs
        if use_id_from_profile:
            all_user_ids = get_user_ids_from_profile(self.config.dump_location) # List object returned

        else:
            all_user_ids = set()
            for choice in choices:
                choice_dir = f"{self.config.dump_location}/{choice['news_source']}/{choice['label']}"
                all_user_ids.update(get_user_ids_in_folder(choice_dir)) # Set object returned

            all_user_ids = list(all_user_ids)

        # create dir to store user followers
        user_followers_folder = f"{self.config.dump_location}/user_followers"
        create_dir(user_followers_folder)

        multiprocess_data_collection(dump_user_followers, all_user_ids, (user_followers_folder, self.config.twython_connector), self.config)

class RetweetUserFollowersCollector(DataCollector):

    def __init__(self, config):
        super(RetweetUserFollowersCollector, self).__init__(config)

    def collect_data(self, choices):

        # create dir to store user followers
        user_followers_folder = f"{self.config.dump_location}/rt_user_followers"
        create_dir(user_followers_folder)

        user_id_list_path = f"{self.config.dump_location}/rt_user_ids_1.json" # number need to be set

        final_user_id_list = []

        with open(user_id_list_path, "r") as id_file:
            id_list = json.loads(id_file.read())['users']

            for uid in id_list:
                if not os.path.exists(f"{user_followers_folder}/{uid}.json"):
                    final_user_id_list.append(int(uid))

            multiprocess_data_collection(dump_user_followers, final_user_id_list, (user_followers_folder, self.config.twython_connector), self.config)


class UserFollowingCollector(DataCollector):

    def __init__(self, config):
        super(UserFollowingCollector, self).__init__(config)

    def collect_data(self, choices):
        all_user_ids = set()

        for choice in choices:
            all_user_ids.update(get_user_ids_in_folder(
                "{}/{}/{}".format(self.config.dump_location, choice["news_source"], choice["label"])))

        user_friends_folder = "{}/{}".format(self.config.dump_location, "user_following")
        create_dir(user_friends_folder)

        multiprocess_data_collection(dump_user_following, list(all_user_ids), (user_friends_folder,
                                                                                       self.config.twython_connector),
                                     self.config)


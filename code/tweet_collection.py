import json
import logging
from multiprocessing.pool import Pool
import os

from util.TwythonConnector import TwythonConnector
from twython import TwythonError, TwythonRateLimitError

from util.util import create_dir, Config, multiprocess_data_collection

from util.util import DataCollector
from util import Constants

from util.util import equal_chunks


class Tweet:

    def __init__(self, tweet_id, news_id, news_source, label):
        self.tweet_id = tweet_id
        self.news_id = news_id
        self.news_source = news_source
        self.label = label


def dump_tweet_information(tweet_chunk: list, config: Config, twython_connector: TwythonConnector):
    """Collect info and dump info of tweet chunk containing at most 100 tweets"""

    # skip downloading tweets which are already been downloaded
    filtered_tweet_chunk = []
    for tweet in tweet_chunk:
        dump_dir = "{}/{}/{}/{}".format(config.dump_location, tweet.news_source, tweet.label, tweet.news_id)
        tweet_dir = "{}/tweets".format(dump_dir)
        tweet_path = f"{tweet_dir}/{tweet.tweet_id}.json"

        if os.path.exists(tweet_path):
            print(f"[PASSED] source:{tweet.news_source}, label:{tweet.label}, news:{tweet.news_id}")

            # save user profile stored in tweet
            user_profiles_folder = f"{config.dump_location}/user_profiles"

            with open(tweet_path, "r") as tweet_file:
                tweet_dict = json.loads(tweet_file.read())
                user_id = tweet_dict['user']['id']
                user_profile_path = f"{user_profiles_folder}/{user_id}.json"

                if not os.path.exists(user_profile_path):
                    print(f"[NEW] User profile: {user_id}")
                    with open(user_profile_path, "w") as user_profile_file:
                        user_profile_file.write(json.dumps(tweet_dict['user']))

            continue
        else:
            print(f"[NEW] source:{tweet.news_source}, label:{tweet.label}, news:{tweet.news_id}")
            filtered_tweet_chunk.append(tweet)

    tweet_id_list = []
    for tweet in filtered_tweet_chunk:
        dump_dir = "{}/{}/{}/{}".format(config.dump_location, tweet.news_source, tweet.label, tweet.news_id)
        tweet_dir = "{}/tweets".format(dump_dir)
        tweet_path = f"{tweet_dir}/{tweet.tweet_id}.json"
        tweet_id_list.append(tweet.tweet_id)

    try:
        tweet_objects_map = twython_connector.get_twython_connection(Constants.GET_TWEET).lookup_status(id=tweet_id_list,
                                                                                                    include_entities=True,
                                                                                                    map=True)['id']
        for tweet in filtered_tweet_chunk:
            tweet_object = tweet_objects_map[str(tweet.tweet_id)]
            if tweet_object:
                dump_dir = "{}/{}/{}/{}".format(config.dump_location, tweet.news_source, tweet.label, tweet.news_id)
                tweet_dir = "{}/tweets".format(dump_dir)
                tweet_path = f"{tweet_dir}/{tweet.tweet_id}.json"
                create_dir(dump_dir)
                create_dir(tweet_dir)
                json.dump(tweet_object, open(tweet_path, "w"))

                # save user profile stored in tweet
                user_profiles_folder = f"{config.dump_location}/user_profiles"
                user_id = tweet_object['user']['id']
                user_profile_path = f"{user_profiles_folder}/{user_id}.json"

                if not os.path.exists(user_profile_path):
                    print(f"[NEW] User profile: {user_id}")
                    with open(user_profile_path, "w") as user_profile_file:
                        user_profile_file.write(json.dumps(tweet_object['user']))

    except TwythonRateLimitError:
        logging.exception("Twython API rate limit exception")

    except Exception as ex:
        logging.exception("exception in collecting tweet objects")

    return None


def collect_tweets(news_list, news_source, label, config: Config):
    create_dir(config.dump_location)
    # create dir for tweets
    create_dir("{}/{}".format(config.dump_location, news_source))
    create_dir("{}/{}/{}".format(config.dump_location, news_source, label))
    # create dir for user profiles
    create_dir(f"{config.dump_location}/user_profiles")

    tweet_list = []

    for news in news_list:

        # check whether the news is existed
        news_path = f"{config.dump_location}/{news_source}/{label}/{news.news_id}/news content.json"

        if not os.path.exists(news_path):
            # print(f"News {news.news_id} is not existed, skip downloading tweets")
            continue

        for tweet_id in news.tweet_ids:
            tweet_list.append(Tweet(tweet_id, news.news_id, news_source, label))

    tweet_chunks = equal_chunks(tweet_list, 100)
    multiprocess_data_collection(dump_tweet_information, tweet_chunks, (config, config.twython_connector), config)


class TweetCollector(DataCollector):

    def __init__(self, config):
        super(TweetCollector, self).__init__(config)

    def collect_data(self, choices):
        for choice in choices:
            news_list = self.load_news_file(choice)
            collect_tweets(news_list, choice["news_source"], choice["label"], self.config)

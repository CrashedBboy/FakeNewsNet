import csv
import json
import logging
import time

from util.util import Config, News

from news_content_collection import NewsContentCollector
from retweet_collection import RetweetCollector
from cascade_collection import RetweetCascadeCollector
from tweet_collection import TweetCollector
from user_profile_collection import UserProfileCollector, UserTimelineTweetsCollector, UserFollowingCollector, UserFollowersCollector


class DataCollectorFactory:

    def __init__(self, config):
        self.config = config

    def get_collector_object(self, feature_type):

        if feature_type == "news_articles":
            return NewsContentCollector(self.config)
        elif feature_type == "tweets":
            return TweetCollector(self.config)
        elif feature_type == "retweets":
            return RetweetCollector(self.config)
        elif feature_type == "user_profile":
            return UserProfileCollector(self.config)
        elif feature_type == "user_timeline_tweets":
            return UserTimelineTweetsCollector(self.config)
        elif feature_type == "user_following":
            return UserFollowingCollector(self.config)
        elif feature_type == "user_followers":
            return UserFollowersCollector(self.config)
        elif feature_type == "retweet_cascade":
            return RetweetCascadeCollector(self.config)

'''
parse config file into object and dict

[return] config: an object containing all config attributes
[return] data_choices: a list of dict object indicating data sources
[return] data_features_to_collect: a list of string, features to be collected
'''
def init_config():

    # read config file
    json_object = json.load(open("config.json"))

    # save attributes of config into object
    config = Config(json_object["dataset_dir"], json_object["dump_location"], json_object["tweet_keys_file"],
                    int(json_object["num_process"]), int(json_object["cascade_time_limitation"]))

    # list of object, e.g. [{"news_source": "politifact", "label": "fake"}, ... ]
    data_choices = json_object["data_collection_choice"]

    # list of string, e.g. ["news_articles", "tweets", "retweets", "user_profile", "user_timeline_tweets", "user_followers", "user_following"]
    data_features_to_collect = json_object["data_features_to_collect"]

    return config, data_choices, data_features_to_collect

'''
logger setup
'''
def init_logging(config):

    format = '%(asctime)s %(process)d %(module)s %(levelname)s %(message)s'

    # set filename, format, level of logging service
    logging.basicConfig(
        filename='data_collection_{}.log'.format(str(int(time.time()))),
        level=logging.INFO,
        format=format)
    
    # also record log of module 'requests'
    logging.getLogger('requests').setLevel(logging.CRITICAL)


def download_dataset():

    # get values of config option
    config, data_choices, data_features_to_collect = init_config()

    # setup logging service
    init_logging(config)

    
    data_collector_factory = DataCollectorFactory(config)

    for feature_type in data_features_to_collect:
        data_collector = data_collector_factory.get_collector_object(feature_type)
        data_collector.collect_data(data_choices)


if __name__ == "__main__":
    download_dataset()

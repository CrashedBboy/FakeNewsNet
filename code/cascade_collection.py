import json
import logging
import os
from datetime import date
from twython import TwythonError, TwythonRateLimitError

from tweet_collection import Tweet
from util.TwythonConnector import TwythonConnector
from util.util import create_dir, Config, multiprocess_data_collection

from util.util import DataCollector
from util import Constants

def is_date_in_range(cascade_start_date, rt_date, config):
    time_difference = (rt_date - cascade_start_date)
    if time_difference.days <= config.cascade_time_limitation:
        return True
    else:
        return False

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

def parse_tweet_date(date_string):

    # example of date string: "Fri Dec 08 17:08:28 +0000 2017"
    y = int(date_string.split(" ")[5])
    m = month_str_to_num(date_string.split(" ")[1])
    assert m >= 1
    d = int(date_string.split(" ")[2])

    return date(y, m, d)

def dump_retweets_job(tweet: Tweet, config: Config, twython_connector: TwythonConnector):

    hop_index = tweet.hop_index

    news_dir = f"{config.dump_location}/{tweet.news_source}/{tweet.label}/{tweet.news_id}"
    retweet_dir = f"{news_dir}/retweets_{hop_index}"
    retweet_path = f"{retweet_dir}/{tweet.tweet_id}.json"

    if os.path.exists(retweet_path):
        print("[PASSED] news:{}, hop index: {}".format(tweet.news_id, hop_index))
        return
    else:
        print("[NEW] news:{}, hop index: {}".format(tweet.news_id, hop_index))

    retweets = []
    connection = None
    try:
        connection = twython_connector.get_twython_connection("get_retweet")
        retweets = connection.get_retweets(id=tweet.tweet_id, count=100, cursor=-1)

    except TwythonRateLimitError:
        logging.exception(f"Twython API rate limit exception - tweet id : {tweet.tweet_id}")

    except Exception:
        logging.exception(
            "Exception in getting retweets for tweet id %d using connection %s" % (tweet.tweet_id, connection))

    retweet_obj = {"retweets": retweets}

    create_dir(news_dir)
    create_dir(retweet_dir)
    json.dump(retweet_obj, open(retweet_path, "w"))

def collect_retweets(news_list, news_source, label, config: Config, hop_index):

    assert hop_index >= 3

    create_dir(config.dump_location)
    create_dir(f"{config.dump_location}/{news_source}")
    create_dir(f"{config.dump_location}/{news_source}/{label}")

    tweet_id_list = []

    for news in news_list:

        news_dir = f"{config.dump_location}/{news_source}/{label}/{news.news_id}"

        # check whether the news is existed
        news_path = f"{news_dir}/news content.json"

        if not os.path.exists(news_path):
            # print(f"News {news.news_id} is not existed, skip downloading retweets")
            continue

        # get start date of Tweet cascade
        cascade_start_date = None

        first_tweets_dir = f"{news_dir}/tweets"
        if os.path.exists(first_tweets_dir):

            # look for date records created at previous execution 
            if os.path.exists(f"{first_tweets_dir}/first_date.json"):
                with open(f"{first_tweets_dir}/first_date.json") as date_file:
                    date_dict = json.loads(date_file.read())
                    cascade_start_date = date(date_dict['year'], date_dict['month'], date_dict['day'])

            # iterate through all tweets to find the date of earliest Tweet
            else:
                for tweet in os.listdir(first_tweets_dir):
                    with open(f"{first_tweets_dir}/{tweet}", "r") as tweet_file:
                        tweet_dict = json.loads(tweet_file.read())
                        tweet_date = parse_tweet_date(tweet_dict['created_at'])

                        if cascade_start_date == None:
                            cascade_start_date = tweet_date
                        elif tweet_date < cascade_start_date:
                            cascade_start_date = tweet_date
        
        print(cascade_start_date)
        if cascade_start_date == None:
            continue

        # read RTs of previous hop
        if hop_index == 3:
            previous_hop_dir = f"{news_dir}/retweets"
        else:
            previous_hop_dir = f"{news_dir}/retweets_{hop_index - 1}"

        for rt_collection in os.listdir(previous_hop_dir):
            
            with open(f"{previous_hop_dir}/{rt_collection}", "r") as rt_collection_file:
                rt_collection_dict = json.loads(rt_collection_file.read())

                for rt in rt_collection_dict['retweets']:
                    rt_date = parse_tweet_date(rt['created_at'])

                    # is date of parent tweet in time range limitation?
                    if is_date_in_range(rt_date, cascade_start_date, config):
                        tweet_id_list.append(Tweet(rt['id'], news.news_id, news_source, label, hop_index))

    if len(tweet_id_list) == 0:
        print("Return False")
        return False
    else:
        multiprocess_data_collection(dump_retweets_job, tweet_id_list, (config, config.twython_connector), config)

        print("Return True")
        return True

class RetweetCascadeCollector(DataCollector):

    def __init__(self, config):
        super(RetweetCascadeCollector, self).__init__(config)

    # get all retweets in one month
    def collect_data(self, choices):
        for choice in choices:
            news_list = self.load_news_file(choice)
            
            # BFS
            hop_index = 3 # Tweets(hop 1), Retweets(hop 2), <..... our target, hop id starts from 3 ......>
            while True:
                should_continue = collect_retweets(news_list, choice["news_source"], choice["label"], self.config, hop_index)

                if should_continue == False:
                    # there's no retweet in one month anymore
                    break

                hop_index += 1
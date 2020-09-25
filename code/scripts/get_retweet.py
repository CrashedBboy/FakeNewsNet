from os import path
import json

from util.TwythonConnector import TwythonConnector

TWEET_ID = 1309376185340538881

# read config file
config_path = path.abspath( path.join( path.dirname(__file__), '../config.json' ) )
json_object = json.load(open(config_path))
tweet_keys_file = json_object["tweet_keys_file"]

# get twypthon connector
twython_connector = TwythonConnector("localhost:5000", tweet_keys_file)
connection = twython_connector.get_twython_connection("get_retweet")

# request target
retweets = connection.get_retweets(id=TWEET_ID, count=100, cursor=-1)

print(json.dumps(retweets))
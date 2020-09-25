from os import path
import json

from util.TwythonConnector import TwythonConnector
from util import Constants

TWEET_ID_LIST = [
    1309376185340538881
]

# read config file
config_path = path.abspath( path.join( path.dirname(__file__), '../config.json' ) )
json_object = json.load(open(config_path))
tweet_keys_file = json_object["tweet_keys_file"]

# get twypthon connector
twython_connector = TwythonConnector("localhost:5000", tweet_keys_file)
connection = twython_connector.get_twython_connection(Constants.GET_TWEET)

# request target
tweet_objects_map = connection.lookup_status(id=TWEET_ID_LIST, include_entities=True, map=True)['id']

print(json.dumps(tweet_objects_map))
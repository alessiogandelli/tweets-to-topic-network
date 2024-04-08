
from utils import process_json, get_topics, create_network
import sys 
import pandas as pd
import datetime

# get file from command line
file_tweets = 'data/toy.json'
file_user = 'data/toy_users.json'

# get path of the folder 
#path = file_tweets.split('/')[:-1]
#path = '/'.join(path)

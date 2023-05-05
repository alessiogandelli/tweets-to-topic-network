
from utils import process_json, get_topics, create_network
import sys 
import pandas as pd
import datetime

# get file from command line
file_tweets = sys.argv[1]
file_user = sys.argv[2]

# get path of the folder 
#path = file_tweets.split('/')[:-1]
#path = '/'.join(path)

path_cache = path + '/cache'

name = file_tweets.split('/')[-1].split('.')[0]

# process json file
start = datetime.datetime.now()
print('processing json file')

df_tweets = process_json(file_tweets, file_user, path_cache)
df_tweets = df_tweets[df_tweets['lang'] == 'en']
df_original = df_tweets[df_tweets['referenced_id'].isna()]


# filter only retweets and quotes and replies
df_retweets = df_tweets[df_tweets['referenced_type'] == 'retweeted']
df_quotes = df_tweets[df_tweets['referenced_type'] == 'quoted']
df_reply = df_tweets[df_tweets['referenced_type'] == 'replied_to']

# get topics for original tweets and assign the referenced tweet to the others
print('json processed after ', datetime.datetime.now() - start)
print('running topic modeling')
df_original = get_topics(df_original, path_cache)
df_retweets['topic'] = df_retweets['referenced_id']
df_quotes['topic'] = df_quotes['referenced_id']
df_reply['topic'] = df_reply['referenced_id']

df_tweets_retweet = pd.concat([df_original, df_retweets])
df_tweets_quote = pd.concat([df_original, df_quotes])
df_tweets_reply = pd.concat([df_original, df_reply])

print('topic modeling done after ', datetime.datetime.now() - start)
# create network
g_retweet, xr, tr = create_network(df_tweets_retweet, path, filename + '_retweet' )
g_quote, xq, tq = create_network(df_tweets_quote, path, filename + '_quote')
g_reply, xr, tr = create_network(df_tweets_reply, path, filename + '_reply')

print('network created after ', datetime.datetime.now() - start)



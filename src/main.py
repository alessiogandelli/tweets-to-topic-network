#%%
from utils import Pipeline
import sys 

import datetime

# get file from command line
file_tweets = sys.argv[1]
file_user = sys.argv[2]
#%%
#file_tweets = '/Volumes/boot420/Users/data/climate_network/test/sample.json'
#file_user = '/Volumes/boot420/Users/data/climate_network/test/users_cop22.json'

start = datetime.datetime.now()

p = Pipeline(file_tweets, file_user)
p.process_json()
p.get_topics()

p.create_network(p.df_retweets_labeled, 'retweets')
p.create_network(p.df_quotes_labeled, 'quotes')
p.create_network(p.df_reply_labeled, 'reply')






#%%
p.df_retweets_labeled.value_counts('topic')

# %%
file_tweets = '/Volumes/boot420/Users/data/climate_network/test/sample.json'
file_user = '/Volumes/boot420/Users/data/climate_network/test/users_cop22.json'
# %%



def resolve_topic(df, row_id):
    if isinstance(row_id, int): # the topic 
        return int(row_id)
    else: # the pointer 
        try:
            topic = df.loc[row_id, 'topic']
            return get_topic(df, topic)
        except: # if there is not the referenced tweet we discard the tweet
            return None

df['resolved_topic'] = df.apply(lambda x: resolve_topic_name(df, x.topic), axis=1)
df['topic2'] = df.apply(lambda x: get_topic(df, x.topic), axis=1)
# %%

# remove tweets that have 
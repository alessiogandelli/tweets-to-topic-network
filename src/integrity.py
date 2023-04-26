
#%%
import pandas as pd
import numpy as np
import os
import re
import igraph
from igraph import Graph



path = '/Volumes/boot420/Users/data/climate_network/cop22/'
file_user = 'users_cop22.csv'
file_tweets = 'tweets_cop22.pkl'

df_tweets = pd.read_pickle(os.path.join(path,file_tweets))
# %%
df_user = pd.read_csv(os.path.join(path,file_user), index_col=0)
# unnamed: 0 is id 

id_to_users = df_user['username'].to_dict()
users_to_id = {v:k for k,v in id_to_users.items()}

# %%

#df_tweets = pd.read_pickle(os.path.join(path,'tweets_cop21.pkl'))

# cleaning 
df_tweets = df_tweets[~df_tweets['author'].isna()]
df_tweets = df_tweets[df_tweets['author'].apply(lambda x: x.isdigit())]

# remove all author that  dont contains numbers 

df_tweets['mentions']= df_tweets['text'].apply(lambda x: re.findall(r'@(\w+)', str(x)))
df_tweets['mention_id'] = df_tweets['mentions'].apply(lambda x: [users_to_id.get(i) for i in x])
df_tweets['author'] = df_tweets['author'].astype(int)
df_tweets['author_name'] = df_tweets['author'].apply(lambda x: id_to_users.get(int(x)))



# %%
# remove all author that  dont contains numbers using isdigit
author_name = df_tweets['author_name'].isna().sum()/ len(df_tweets)

mentions = df_tweets['mention_id'].to_list()
flatten = [item for sublist in mentions for item in sublist]

none_count = flatten.count(None) / len(flatten)
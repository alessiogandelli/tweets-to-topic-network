#%%
import pandas as pd
import numpy as np
import os
import re
import tweepy
from dotenv import load_dotenv

load_dotenv()



client = tweepy.Client(bearer_token=os.getenv('TOKEN_TWITTER'))

#%%
path = '/Users/alessiogandelli/dev/internship/data'



cop27 = pd.read_csv(os.path.join(path, 'cop27_tw.csv'),  sep='\t',lineterminator='\n')

#%%

# %%
cop27 = cop27[cop27['lang'] == 'en'] # only english
cop27 = cop27[cop27['has_media'] == 'N'] #has media no 
cop27 = cop27[~cop27['text'].str.startswith('RT')]# remove retweets ( if starts euth RT)
cop27 = cop27.drop_duplicates(subset=['text'])# remove text duplicates
cop27['timestamp'] = pd.to_datetime(cop27[['year', 'month', 'day', 'h', 'm', 's']])
cop27 = cop27.sort_values(by='timestamp')
cop27 = cop27.drop(columns=['year', 'day', 'h', 'm', 's'])# remove year month day h m s


cop27=cop27[~cop27['text'].str.contains('\t')] # remove text that contains tab due to importing problems
# %%

cop27['mentions'] = cop27['text'].str.findall(r'@(\w+)') # find mentions
cop27['mentions_id'] = cop27['mentions'].apply(lambda x: [client.get_user(username=i).data.id for i in x]) # find mentions id

# %%
def get_user_id(list_mentions):
    users = []
    
    for username in list_mentions:

        if len(list_mentions) > 0:
            try:
                users.append(client.get_user(username=username).data.id)
            except:
                pass
    return users
# %%

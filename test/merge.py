#%%
"""
process json files and save them in the cache
"""
from tweets_to_topic_network.data import Data_processor 
from tweets_to_topic_network.topic import Topic_modeler
from tweets_to_topic_network.network import Network_creator



cops = ['cop21', 'cop22', 'cop23', 'cop24', 'cop25', 'cop26', 'cop27']

for n_cop in cops:
    print('processing cop: ', n_cop)

    file_tweets = '/Users/alessiogandelli/data/' + n_cop + '/' + n_cop + '.json'
    file_user = '/Users/alessiogandelli/data/' + n_cop + '/users_'+ n_cop+'.json'

    data = Data_processor(file_tweets, n_cop = n_cop)
    data.process_json()



# %%
"""
filter the tweets according to their date and merge them together in a single dataframe
"""
import pandas as pd
from datetime import datetime, timedelta


cop_conferences_date = {
    "cop21": {"start": "2015-11-30", "end": "2015-12-12"},
    "cop22": {"start": "2016-11-07", "end": "2016-11-18"},
    "cop23": {"start": "2017-11-06", "end": "2017-11-17"},
    "cop24": {"start": "2018-12-03", "end": "2018-12-14"},
    "cop25": {"start": "2019-12-02", "end": "2019-12-13"},
    "cop26": {"start": "2021-10-31", "end": "2021-11-12"},
    "cop27": {"start": "2022-11-06", "end": "2022-11-20"}
}
df_merged = pd.DataFrame()

for cop_n, dates in cop_conferences_date.items():
    path_cop =  '/Users/alessiogandelli/data/' + cop_n + '/cache/data/tweets_' + cop_n + '.pkl'
    print(cop_n, dates['start'], '====================')
    start_date = pd.to_datetime(dates['start'],  utc=True) - pd.Timedelta(days=30)
    end_date = pd.to_datetime(dates['end'],  utc=True) + pd.Timedelta(days=30)
    df = pd.read_pickle(path_cop)
    df['date'] = pd.to_datetime(df['date'])
    # get tweets from 30 days before the ocnference and 30 days after
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    df['cop'] = cop_n
    df_merged = pd.concat([df_merged, df])
    print(df.shape)


df_merged.to_pickle('/Users/alessiogandelli/data/cop_merged/cop_merged.pkl')






# %%
# get only original tweets

df_original_merged = df_merged[df_merged['referenced_type'].isnull()]
df_original_merged.to_pickle('/Users/alessiogandelli/data/cop_merged/cop_merged_original.pkl')


# %%
df_english_merged = df_merged[df_merged['lang'] == 'en']
df_english_merged.to_pickle('/Users/alessiogandelli/data/cop_merged/cop_merged_english.pkl')
# %%

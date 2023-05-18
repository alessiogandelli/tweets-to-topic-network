#%%
from utils import Pipeline
import sys 

import datetime

# get file from command line
file_tweets = sys.argv[1]
file_user = sys.argv[2]
#%%


start = datetime.datetime.now()

p = Pipeline(file_tweets, file_user)
p.process_json()
p.get_topics()

p.create_network(p.df_reply_labeled, 'reply')
p.create_network(p.df_quotes_labeled, 'quotes')
p.create_network(p.df_retweets_labeled, 'retweets')







#%%
#p.project_network(path='/Volumes/boot420/Users/data/climate_network/test/networks/sampleretweets.gml', title='retweets')


# %%

#%%
from tweets_to_network import Tweets_to_network
import sys 
import datetime
import pandas as pd


tweets_cop22 = '/Users/alessiogandelli/data/cop22/cop22.json'
users_cop22 = '/Users/alessiogandelli/data/cop22/users_cop22.json'

tweets_cop21 = '/Users/alessiogandelli/data/cop21/cop21.json'
users_cop21 = '/Users/alessiogandelli/data/cop21/users_cop21.json'

tweets_cop26 = '/Users/alessiogandelli/data/cop26/cop26.json'
users_cop26 = '/Users/alessiogandelli/data/cop26/users_cop26.json'

tweets_cop2x = '/Users/alessiogandelli/data/cop2x/cop2x.json'
users_cop2x = '/Users/alessiogandelli/data/cop2x/users_cop2x.json'


#%%


cop26 = Tweets_to_network(tweets_cop26, users_cop26, 'cop26')
cop26.process_json()
cop26.get_topics(name = 'bert')
cop26.label_topics()
cop26.retweet_network_ml()


#%%
cop21 = Tweets_to_network(tweets_cop21, users_cop21, 'cop21')
cop21.process_json()
cop21.get_topics(name = 'bert')
cop21.label_topics()
cop21.retweet_network_ml()
#%%
cop22 = Tweets_to_network(tweets_cop22, users_cop22, 'cop22')
cop21 = Tweets_to_network(tweets_cop21, users_cop21, 'cop21')
cop22.process_json()
cop21.process_json()

cop21.get_topics(name = 'bert')
cop22.get_topics(name = 'bert')




#%%
# except column topics
cop26_tweets= cop26.df_retweets_labeled.drop(columns=['topic'])
cop21_tweets= cop21.df_retweets_labeled.drop(columns=['topic'])
cop22_tweets= cop22.df_retweets_labeled.drop(columns=['topic'])

# %%

# i'm saving these in the cop2x cache so i can artifically create the cache 

cop = pd.concat([cop21.df_original_no_retweets, cop22.df_original_no_retweets, cop26.df_original_no_retweets])
cop.to_pickle('/Users/alessiogandelli/data/cop2x/cache/tweets_original_cop.pkl')

cop_all_tweets = pd.concat([cop21_tweets, cop22_tweets, cop26_tweets])
cop_all_tweets.to_pickle('/Users/alessiogandelli/data/cop2x/cache/tweets_cop2x.pkl')

# %%
cop2x = Tweets_to_network(tweets_cop2x, users_cop2x, 'cop2x')
cop2x.process_json()
cop2x.get_topics(name = 'bert', df=cop2x.df_original_no_retweets)
cop2x.label_topics()
cop2x.retweet_network_ml()


# %%
cop2x.label_topics()
# %%
cop2x.df_retweets_labeled.groupby('topic').count()
# %%
# group by topic and cop 
coptop = cop2x.df_retweets_labeled.groupby(['topic', 'cop'])['author'].count()
# %% remove topic 0 and -1 
coptop = coptop.drop([0, -1])
# plot the number of tweets per topic per cop removing first 2 topics
coptop.unstack.plot(kind='bar', stacked=True)


# x is the cop then a line for each topic
# %%
# group by cop and topic
coptop = cop2x.df_retweets_labeled.groupby(['topic', 'cop',])['author'].count()

#remove topic 0 and -1
coptop = coptop.drop([0, -1])
#drop cop22 
coptop = coptop.drop('cop22', level=1)

coptop.unstack(level=0).plot()







# %%
topics_over_time = cop2x.model.topics_over_time(docs=cop2x.df_original_labeled['text'], timestamps=cop2x.df_original_labeled['date'])

# %%
cop2x.df_original_labeled




#%%
# get tweet from a subset of user from df_retweets_labeled

us = list(cop26.retweet_graph.nodes)

cop26.df_retweets_labeled[cop26.df_retweets_labeled['author'].isin(us)]
# %%

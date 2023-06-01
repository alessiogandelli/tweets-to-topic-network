#%%

#%%
import networkx as nx
import igraph as ig
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



full_network_path = '/Volumes/boot420/Users/data/climate_network/cop22/networks/cop22_retweets.gml'
topics_file = '/Volumes/boot420/Users/data/climate_network/cop22/cache/topics_cop22.csv'
projected_path = '/Volumes/boot420/Users/data/climate_network/cop22/networks/cop22_reply_projected.gml'

test_network = '/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/networks/toy_test.gml'

# load network
g = ig.read(full_network_path, format='gml')

topic_name = pd.read_csv(topics_file)

#%%

# %%
tweets = g.vs.select(bipartite=1)
user = g.vs.select(bipartite=0)
original_tweets = g.vs.select(is_retweet='original')

print('Number of users: ', len(user))
print('Number of tweets: ', len(tweets))
print('number of original tweets: ', len(original_tweets))
print('user that tweeted original tweets: ', len(set(original_tweets['author'])))

#%%
# get in degree for original tweets
original_tweets_indegree = g.degree(original_tweets, mode='in')
df_original_tweets_indegree = pd.DataFrame({'tweet': original_tweets['label'], 'indegree': original_tweets_indegree, 'author': original_tweets['author']})
# indegree -1 and rename to retweets 
df_original_tweets_indegree['indegree'] = df_original_tweets_indegree['indegree'] - 1
df_original_tweets_indegree = df_original_tweets_indegree.rename(columns={'indegree': 'retweets'})
df_rt_user = df_original_tweets_indegree.groupby('author').aggregate({'tweet':'count', 'retweets':'sum'})
df_rt_user['rt_per_tweet'] = round(df_rt_user['retweets'] / df_rt_user['tweet'])
df_rt_user[df_rt_user['retweets'] > 0] # oringal users with 0 retweets 
df_rt_user.sort_values('retweets', ascending=False).head(100)['retweets'].sum()

# plot 

# groupby sum retweets and count tweets 



# check integrity 
sum(df_original_tweets_indegree.groupby('author').sum('retweets').sort_values('retweets')['retweets']) + len(df_original_tweets_indegree)
#%%
# user degree analysis most mentioned users

user_outdegree = g.degree(user, mode='out')
user_indegree = g.degree(user, mode='in')
df_user_degree = pd.DataFrame({'user': user['label'], 'mentions': user_indegree, 'tweets': user_outdegree})
 
df_user_degree.sort_values(by='mentions', ascending=False).head(20)


# plot mentions and tweets distribution
bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10]
xticks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
fig, ax = plt.subplots(1,2, figsize=(10,5))
sns.histplot(df_user_degree['mentions'], ax=ax[0], bins=bins, kde=False, color='blue', stat='probability')
sns.histplot(df_user_degree['tweets'], ax=ax[1], bins=bins, kde=False, color='red', stat='probability')
ax[0].set_xticks(xticks)
ax[1].set_xticks(xticks)
ax[0].set_xlabel('Number of mentions')
ax[1].set_xlabel('Number of tweets')
ax[0].set_ylabel('% of users')
ax[1].set_ylabel('% of users')
# same y axis
ax[1].set_ylim(ax[0].get_ylim())


#%%

# TWEETS DEGREE ANALYSIS

tweets_outdegree = g.degree(tweets, mode='out')
tweets_indegree = g.degree(tweets, mode='in')
df_tweets_degree = pd.DataFrame({'tweet': tweets['label'], 'retweets': tweets_indegree })
# remove one because it is the edge from the user 
df_tweets_degree['retweets'] = df_tweets_degree['retweets'] - 1 

df_tweets_degree.sort_values('retweets', ascending=False).head(20)


bins = [0, 1, 2, 3, 4, 5, 6, 7, 8]
sns.histplot(df_tweets_degree['retweets'], bins=bins, kde=False, color='blue', stat='probability')
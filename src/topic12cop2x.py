#%%

from tweets_to_network import Tweets_to_network
import sys 
import datetime
import pandas as pd
import networkx as nx

# load data 
n_cop = '2x'
n_influencers = 100

folder = '/Users/alessiogandelli/data/cop' + str(n_cop) + '/'


retweet_df_path = folder + 'cache/retweets_labeled_cop'+str(n_cop)+'.pkl'


retweet_df = pd.read_pickle(retweet_df_path)



# %%
# get only topic 12 
topic12 = retweet_df[retweet_df['topic'] == 12]

topic12_21 = topic12[topic12['cop'] == 'cop21']
topic12_26 = topic12[topic12['cop'] == 'cop26']
# %%

p = Tweets_to_network('','', 'cop2x12')

p.df_retweets_labeled = topic12_21

net1221 = p.retweet_network()
# %%
p.df_retweets_labeled = topic12_26

net1226 = p.retweet_network()
# %%


# save the network
nx.write_gml(net1221, folder + 'networks/network1221.gml')
nx.write_gml(net1226, folder + 'networks/network1226.gml')
# %%
# get only topic 12 
topic12 = retweet_df[retweet_df['topic'] == 12]

topic12_21 = topic12[topic12['cop'] == 'cop21']
topic12_26 = topic12[topic12['cop'] == 'cop26']


p = Tweets_to_network('','', 'cop2x12')

p.df_retweets_labeled = topic12_21

net1221 = p.retweet_network()

p.df_retweets_labeled = topic12_26

net1226 = p.retweet_network()

# save the network
nx.write_gml(net1221, folder + 'networks/network1221.gml')
nx.write_gml(net1226, folder + 'networks/network1226.gml')

#%%
# get only topic 1 
topic1 = retweet_df[retweet_df['topic'] == 1]

topic1_21 = topic1[topic1['cop'] == 'cop21']
topic1_26 = topic1[topic1['cop'] == 'cop26']


p = Tweets_to_network('','', 'cop2x1')

p.df_retweets_labeled = topic1_21

net121 = p.retweet_network()

p.df_retweets_labeled = topic1_26

net126 = p.retweet_network()

# save the network
nx.write_gml(net121, folder + 'networks/network121.gml')
nx.write_gml(net126, folder + 'networks/network126.gml')
# %%
# get only topic 3
topic3 = retweet_df[retweet_df['topic'] == 3]

topic3_21 = topic3[topic3['cop'] == 'cop21']
topic3_26 = topic3[topic3['cop'] == 'cop26']


p = Tweets_to_network('','', 'cop2x3')

p.df_retweets_labeled = topic3_21

net321 = p.retweet_network()

p.df_retweets_labeled = topic3_26

net326 = p.retweet_network()

# save the network
nx.write_gml(net321, folder + 'networks/network321.gml')
nx.write_gml(net326, folder + 'networks/network326.gml')


# %%

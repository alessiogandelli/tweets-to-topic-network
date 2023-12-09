#%% 
from tweets_to_network import Tweets_to_network
import sys 
import datetime
import pandas as pd
import uunet.multinet as ml
import networkx as nx
import matplotlib.pyplot as plt


tweets_cop26 = '/Users/alessiogandelli/data/cop26/cop26.json'
users_cop26 = '/Users/alessiogandelli/data/cop26/users_cop26.json'

cop26 = Tweets_to_network(tweets_cop26, users_cop26, 'cop26')
cop26.process_json()
cop26.get_topics(name = 'bert')
cop26.retweet_network()

# %%

cop26.df_original.groupby('author_name').sum().sort_values(by = 'retweet_count', ascending = False)

# %%
l = ml.to_nx_dict(cop26.ml_network)
net =l['1']
adj = nx.adjacency_matrix(l['1'], weight = 'weight')
# %%
plt.spy(adj, markersize=1)
# %%

# draw the graph using the default spring layout
plt.figure(figsize=(10, 10))
nx.draw_networkx(net, node_size=1, alpha=0.5, with_labels=False)
plt.axis('equal')
plt.show()

# %%
# network stats networkx 

net.number_of_nodes()
net.number_of_edges()

# %%
# sum all the lines of the adj matrix to obtain a vector 
# of the degree of each node
degree = adj.sum(axis = 1)

degree = degree.flatten().tolist()

plt.hist(degree, bins = 100)


# %%
len(cop26.df_retweets_labeled['author_name'].unique())
# %%

cop26.retweet_graph.number_of_nodes()
cop26.retweet_graph.number_of_edges()

# %%
rt_count = cop26.df_retweets_labeled.groupby('author')[['author_name', 'retweet_count']].sum()
# %%
indegree = cop26.retweet_graph.in_degree()
# %%
indegree_df = pd.DataFrame(indegree, columns = ['author', 'indegree']).set_index('author').sort_values(by = 'indegree', ascending = False)

# %%
#merge the two df
indegree_df = indegree_df.merge(rt_count, left_index = True, right_index = True)

# %%
top1000 = indegree_df.head(1000).index

#get df_original of top 1000
top1000_df = cop26.df_original[cop26.df_original['author'].isin(top1000)]



# %%

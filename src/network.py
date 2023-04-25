#%%
import pandas as pd
import numpy as np
import os
import re
import igraph
from igraph import Graph
from networkx.algorithms import bipartite
import networkx as nx

path = '/Volumes/boot420/Users/data/climate_network/cop22/'
file_user = 'users_cop22.csv'
file_tweets = 'tweets_cop22.csv'


# create new bipartite graph 


g = nx.Graph()
g.add_nodes_from(sample_df['author_name'].unique(), bipartite=0)
g.add_nodes_from(sample_df.index, bipartite=1)

# list of tuples between author_nname and index 
edges = list(zip(sample_df['author_name'], sample_df.index))
ref_edges = list(zip(sample_df.index, sample_df['referenced_id']))
# remove all none values
ref_edges = [i for i in ref_edges if i[1] is not None]
g.add_edges_from(edges, weight = 10, )
g.add_edges_from(ref_edges, weight = 1)
# add attribute bipartite to all nides without it 
for i in g.nodes:
    if 'bipartite' not in g.nodes[i]:
        g.nodes[i]['bipartite'] = 1

# #remove all nodes 0 that have out degree 1
g.remove_nodes_from([n for n in g if g.degree(n) < 15 and g.nodes[n]['bipartite']==0])
# # remove nodes 1 that have in degree 0
g.remove_nodes_from([n for n in g if g.degree(n) == 0 ])

# %%
# plot graph 
import matplotlib.pyplot as plt
color = [0 if g.nodes[i]['bipartite']==0 else 1 for i in g.nodes]
pos = nx.bipartite_layout(g,sample_df.index)
pos = nx.spring_layout(g, k = 0.07)
#pos = nx.multipartite_layout(g, subset_key='bipartite')
nx.draw(g, with_labels=False, pos = pos, node_size = 4, node_color = color, width = 0.1)
plt.show()

# %%
# %%

# get the biggest degree
max_degree = max(g.degree())
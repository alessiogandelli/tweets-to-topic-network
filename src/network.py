#%%
import pandas as pd
import numpy as np
import os
import re
import igraph
from igraph import Graph
from networkx.algorithms import bipartite
import networkx as nx
import matplotlib.pyplot as plt

path = '/Volumes/boot420/Users/data/climate_network/cop22/'
file_user = 'users_cop22.csv'
file_tweets = 'tweets_cop22.pkl'

# read pickle file
df_tweets = pd.read_pickle(os.path.join(path,file_tweets))


t = {}

#%%

def create_network(df_tweets):

    A = df_tweets['author_name'].unique() # actors
    M = df_tweets.index                   # tweets 
    x = df_tweets['text'].to_dict()

    g = nx.DiGraph()
    g.add_nodes_from(A, bipartite=0) # author of tipe 0
    g.add_nodes_from(M, bipartite=1) # tweets of type 1

    print('nodes added')

    # list of tuples between author_nname and index 
    edges = list(zip(df_tweets['author_name'], df_tweets.index)) # author-> tweet
    ref_edges = list(zip(df_tweets['referenced_id'], df_tweets.index )) # tweet -> tweet
    ref_edges = [i for i in ref_edges if i[0] is not None] # remove all none values
    men_edges = [(i, m) for i in df_tweets.index for m in df_tweets.loc[i]['mentions_name']]


    g.add_edges_from(edges, weight = 10 )
    g.add_edges_from(ref_edges, weight = 1)

    print('edges added')
    # add attribute bipartite to all nides without it, required for the new tweets added with the ref
    for i in g.nodes:
        if 'bipartite' not in g.nodes[i]:
            g.nodes[i]['bipartite'] = 1

    t = {e:df_tweets.loc[e[1]]['date'] for e in g.edges()}
    g.add_edges_from(men_edges)

    for i in g.nodes:
        if 'bipartite' not in g.nodes[i]:
            g.nodes[i]['bipartite'] = 0

    nx.set_edge_attributes(g, t, 'date')
    nx.set_node_attributes(g, x, 'text')


    return (g, x , t)

# #remove all nodes 0 that have out degree 1
#g.remove_nodes_from([n for n in g if g.degree(n) < 15 and g.nodes[n]['bipartite']==0])
# # remove nodes 1 that have in degree 0
#g.remove_nodes_from([n for n in g if g.degree(n) == 0 ])
g,x,t = create_network(df_tweets)
# %%


# degree analysis 

degree = {i:g.degree(i) for i in g.nodes}
degree = pd.DataFrame.from_dict(degree, orient='index')
degree.columns = ['degree']
degree['bipartite'] = [g.nodes[i]['bipartite'] for i in degree.index]
degree['degree'] = degree['degree'].astype(int)
degree['bipartite'] = degree['bipartite'].astype(int)
degree['indegree'] = [g.in_degree(i) for i in degree.index]
degree['outdegree'] = [g.out_degree(i) for i in degree.index]
top_users = degree[degree['bipartite'] == 0].sort_values(['degree', 'bipartite'], ascending=False).head(20) 
top_tweets = degree[degree['bipartite'] == 1].sort_values(['degree', 'bipartite'], ascending=False).head(20)




#%%
# descriptive stats of the graph
# number of nodes
print('number of nodes', g.number_of_nodes())
# number of nodes of bipartite 1 
print('number of tweets', len([i for i in g.nodes if g.nodes[i]['bipartite']==1]))
print('number of users', len([i for i in g.nodes if g.nodes[i]['bipartite']==0]))
# number of retweets
print('number of retweets', g.number_of_edges() - len([i for i in g.nodes if g.nodes[i]['bipartite']==1]))
# average degree
print('average degree', np.mean([g.degree(i) for i in g.nodes]))

# indegree of users 




#%%
gg = g
# #remove all nodes 0 that have out degree 1
gg.remove_nodes_from([n for n in g if g.degree(n) < 15 and g.nodes[n]['bipartite']==0])
# # remove nodes 1 that have in degree 0
gg.remove_nodes_from([n for n in g if g.degree(n) < 2 ])



# plot graph 
color = [0 if g.nodes[i]['bipartite']==0 else 1 for i in g.nodes]
pos = nx.bipartite_layout(g,df_tweets.index)
pos = nx.spring_layout(g, k = 0.07)
#pos = nx.multipartite_layout(g, subset_key='bipartite')
nx.draw(g, with_labels=False, pos = pos, node_size = 4, node_color = color, width = 0.1)
plt.show()


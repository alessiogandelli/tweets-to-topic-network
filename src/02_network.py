#%%
import pandas as pd
import numpy as np
import os
import re
from networkx.algorithms import bipartite
import networkx as nx
import matplotlib.pyplot as plt

path = '/Volumes/boot420/Users/data/climate_network/cop22/'
file_user = 'users_cop22.csv'
file_tweets = 'tweets_cop22.pkl'
file_topic = 'tweets_cop22_topics.pkl'

# read pickle file
df_tweets = pd.read_pickle(os.path.join(path,file_tweets))
#df_labeled = pd.read_pickle(os.path.join(path,file_topic))

#df_tweets['topics'] = df_labeled['topics']


# do reference id is present in the index
df_original = df_tweets[df_tweets['referenced_id'].isna()]
df_retweets = df_tweets[~df_tweets['referenced_id'].isna()]
#df_retweets = df_retweets[~df_retweets['referenced_id'].apply(lambda x: x if x in df_tweets.index else None).isna()]

# fake topic 0 or 1 
df_original['topic'] = [0 if i % 2 == 0 else 1 for i in range(len(df_original))]
df_retweets['topic'] = df_retweets['referenced_id']

df_tweets = pd.concat([df_original, df_retweets])
t = {}

#%%

def create_network(df_tweets):

    A = df_tweets['author_name'].unique() # actors
    M = df_tweets.index                   # tweets 
    x = df_tweets['text'].to_dict()
    topics = df_tweets['topic'].to_dict()

    g = nx.DiGraph()
    g.add_nodes_from(A, bipartite=0) # author of tipe 0
    g.add_nodes_from(M, bipartite=1) # tweets of type 1

    print('nodes added')

    # list of tuples between author_nname and index 
    edges = list(zip(df_tweets['author_name'], df_tweets.index)) # author-> tweet
    ref_edges = list(zip( df_tweets.index, df_tweets['referenced_id'])) # retweet -> tweet
    ref_edges = [i for i in ref_edges if i[1] is not None] # remove all none values
    men_edges = [(row.Index, mention) for row in df_tweets.itertuples() for mention in row.mentions_name]


    g.add_edges_from(edges, weight = 10 )
    g.add_edges_from(ref_edges, weight = 1)

    print('edges added')

    # remove all nodes authomatically addd 

    #add attribute bipartite to all nides without it, required for the new tweets added with the ref
    nodes_to_remove = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
    g.remove_nodes_from(nodes_to_remove)
            # g.nodes[i]['bipartite'] = 1


    date_lookup = {row.Index: row.date for row in df_tweets.itertuples()}

    t = {e: date_lookup[e[1]] for e in g.edges()}
    g.add_edges_from(men_edges)
    print('mentions added')

    # set bipartite = 0 ( so actors) to the new nodes(users) added 
    nodes_to_set = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
    [g.nodes[node].setdefault('bipartite', 0) for node in nodes_to_set]

    print('new nodes added', c)

    nx.set_edge_attributes(g, t, 'date')
    nx.set_node_attributes(g, x, 'text')
    nx.set_node_attributes(g, topics, 'topics')


    return (g, x , t)


g,x,t = create_network(df_tweets)
 
# %%

# get all nodes of type 1 (tweets) that have put degree = 0
# this means that they are not referenced by any other tweet

original = [i for i in g.nodes if g.nodes[i]['bipartite'] == 1 and g.out_degree(i) == 0]
original_text = [x.get(a) for a in original]

# count original_text that continais RT
len([i for i in original_text if 'RT' in i])



orig = df_tweets[df_tweets['referenced_type'].isna()]
pablo = orig[orig['author'] == '52119056']
pablo['text'].str.contains('RT').value_counts()
orig['text'].str.contains('RT').value_counts()

retweets = df_tweets[~df_tweets['referenced_id'].isna()]['referenced_id'].to_list()

referenced = set(retweets)
pd.Series([x.get(t) for t in referenced]).isna().value_counts()
pd.Series([x.get(t) for t in retweets]).isna().value_counts()
#%%
# find referenced id that are also in the index of df_tweets
df_retweets['referenced_id'].apply(lambda x: x if x in df_tweets.index else None)



#%%
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
gg = g.copy()
# #remove all nodes 0 that have out degree 1
gg.remove_nodes_from([n for n in gg if gg.degree(n) < 100 and gg.nodes[n]['bipartite']==0])
# # remove nodes 1 that have in degree 0
gg.remove_nodes_from([n for n in gg if gg.degree(n) < 200 ])


#%%
# plot graph 
color = [0 if gg.nodes[i]['bipartite']==0 else 1 for i in gg.nodes]
pos = nx.bipartite_layout(gg,df_tweets.index)
pos = nx.spring_layout(gg, k = 0.07)
#pos = nx.multipartite_layout(g, subset_key='bipartite')
nx.draw(gg, with_labels=False, pos = pos, node_size = 4, node_color = color, width = 0.1)
plt.show()


# %%
topic = 1

# get only the nodes of the topic

tweets = [i for i in g.nodes if g.nodes[i]['bipartite'] == 1 and g.nodes[i]['topics'] == topic]
users = [i for i in g.nodes if g.nodes[i]['bipartite'] == 0]

sub = g.subgraph(tweets + users)
users = [n for n in sub if sub.degree(n) != 0 and sub.nodes[n]['bipartite']==0]

sub = sub.subgraph(users + tweets)

# remove user nodes with degree 0
# %%

# plot graph
color = [0 if sub.nodes[i]['bipartite']==0 else 1 for i in sub.nodes]
pos = nx.bipartite_layout(sub,df_tweets.index)
pos = nx.spring_layout(sub, k = 0.07)
#pos = nx.multipartite_layout(g, subset_key='bipartite')
nx.draw(sub, with_labels=False, pos = pos, node_size = 4, node_color = color, width = 0.1)
plt.show()

# %%

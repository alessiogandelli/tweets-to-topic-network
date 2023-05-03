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

df_retweets = df_tweets[df_tweets['referenced_type'] == 'retweeted']
df_quotes = df_tweets[df_tweets['referenced_type'] == 'quoted']
df_reply = df_tweets[df_tweets['referenced_type'] == 'replied_to']
#df_retweets = df_retweets[~df_retweets['referenced_id'].apply(lambda x: x if x in df_tweets.index else None).isna()]

# fake topic 0 or 1 
df_original['topic'] = [0 if i % 2 == 0 else 1 for i in range(len(df_original))]
df_retweets['topic'] = df_retweets['referenced_id']
df_quotes['topic'] = df_quotes['referenced_id']
df_reply['topic'] = df_reply['referenced_id']

df_tweets_retweet = pd.concat([df_original, df_retweets])
df_tweets_quote = pd.concat([df_original, df_quotes])
df_tweets_reply = pd.concat([df_original, df_reply])
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


    nx.set_edge_attributes(g, t, 'date')
    nx.set_node_attributes(g, x, 'text')
    nx.set_node_attributes(g, topics, 'topics')


    return (g, x , t)


gr ,xr ,tr = create_network(df_tweets_retweet)
gq ,xq ,tq = create_network(df_tweets_quote)
grt ,xrt ,trt = create_network(df_tweets_retweet)
 
# %%


## export to gml 
nx.write_gml(gr, os.path.join(path,'cop22_retweet.gml'))
nx.write_gml(gq, os.path.join(path,'cop22_quote.gml'))
nx.write_gml(grt, os.path.join(path,'cop22_reply.gml'))

# get all nodes of type 1 (tweets) that have put degree = 0
# this means that they are not referenced by any other tweet


# %%


# %%

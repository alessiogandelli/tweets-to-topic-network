# %%
from dataProcessor.data_processor import Data_processor 
from topicModeler.topic_modeler import Topic_modeler
from networkCreator.network_creator import Network_creator

n_cop = 'cop22'

file_tweets = '/Users/alessiogandelli/data/' + n_cop + '/' + n_cop + '.json'
file_user = '/Users/alessiogandelli/data/' + n_cop + '/users_'+ n_cop+'.json'

# file_tweets = '/Users/alessiogandelli/dev/uni/tweets-to-topic-network/data/toy.json'
# file_user = '/Users/alessiogandelli/dev/uni/tweets-to-topic-network/data/toy_users.json'

#%%
data = Data_processor(file_tweets, file_user, '22')
data.process_json()

tm = Topic_modeler(data.df_original, name = data.name, embedder_name='all-MiniLM-L6-v2', path_cache = data.path_cache)
df_labeled = tm.get_topics()


df_retweet_labeled = data.update_df(df_labeled)

nw = Network_creator(df_retweet_labeled, name = data.name, path = data.folder)
G = nw.create_retweet_network()














# %%
import pandas as pd

# %%

# %%
import numpy as np
import pandas as pd
from networkCreator.network_creator import Network_creator

df = pd.DataFrame({
    'id' : ['tweet1', 'tweet2', 'tweet3', 'tweet4', 'tweet5', 'tweet6', 'tweet7', 'tweet8', 'tweet9'],
    'author': ['a', 'a', 'b', 'b', 'f', 'c', 'd', 'e', 'f'],
    'text': ['tweet1', 'tweet2', 'tweet3', 'tweet4', 'tweet5', 'tweet6', 'tweet7', 'tweet8', 'tweet9'],
    'date': pd.date_range(start='01-01-2022', periods=9).strftime('%Y-%m-%d').tolist(),
    'lang': ['en', 'en', 'en', 'en', 'en', 'en', 'en', 'en', 'en'],
    'referenced_type': ['original', 'original', 'retweet', 'original', 'retweet', 'retweet', 'retweet', 'retweet', 'retweet'],
    'referenced_id': [ None, None, 'tweet2', None, 'tweet3', 'tweet2', 'tweet2', 'tweet2', 'tweet8'],
    'topic' : [1,1,1,1,2,2,2,1,1],
    'mentions_name': [[], [], [], [], [], [], [], [], []]
    
}).set_index('id')

# %%Print the DataFrame
nw = Network_creator(df, name = 'test', path = 'data')
G = nw.create_retweet_network()


ttn = nw.create_ttnetwork()

nw.plot_network(ttn[0])
# %%
import matplotlib.pyplot as plt
import networkx as nx
G = ttn[0]
pos = nx.planar_layout(G)
nx.draw_networkx_nodes(G, pos, node_color=[('red' if node[1]['bipartite'] == 1 else 'blue') for node in G.nodes(data=True)])
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos)
plt.show()
# %%

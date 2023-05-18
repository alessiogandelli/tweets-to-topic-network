# %%


#p.create_multilayer_network()


# %%
# draw graoh nx
import pandas as pd
from utils import Pipeline
import sys 

import datetime
file_tweets = '/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/toy.json'
file_user = '/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/toy_users.json'
# %%
df = pd.DataFrame()
df.index = [1,2,3,4,5,6,7,8,9,10,11]
df['author'] = ['a','c','d','d','e','e','e','f','f','a','c']
df['author_name'] = ['anzio','crizio','danzio','danzio','enzio','enzio','enzio','fanzio','fanzio','anzio','crizio']
df['text'] = 'testo'
df['date'] = str(datetime.datetime.now())
df['referenced_type'] = [None, 'retweeted', None, None, 'retweeted', None, None, 'retweeted', 'retweeted', None, 'retweeted']
df['referenced_id'] = [None, 1, None, None, 4, None, None, 5, 7, None, 10]
df['mentions_id']= [['b'], [], [], ['b'], [], [], ['f'], [], [], [], []]
df['mentions_name']= [['bonzo'], [], [], ['bonzo'], [], [], ['fanzio'], [], [], [], []]
df['topic'] = [1,1,2,2,2,1,1,2,1,1,1]
# reference id int 
df['referenced_id'] = df['referenced_id'].astype('Int64')
p = Pipeline(file_tweets, file_user)

g,a,b = p.create_network(df, 'test')
# %%
import networkx as nx

# draw with node color based on bipartite attribute
color = ['#3498eb' if g.nodes[i]['bipartite']==0 else '#e5eb34' for i in g.nodes]

pos = nx.spring_layout(g, k=4)
pos = nx.planar_layout(g)
#pos = nx.shell_layout(g)
nx.draw(g, with_labels=True,  node_color = color, width = 0.1, pos=pos)


# %%
#nx load gml 
import networkx as nx


g = nx.read_gml('/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/networks/projected/toy_test_prj_1.0.gml')



# %%
# remove self loops
g.remove_edges_from(nx.selfloop_edges(g))
nx.draw(g, with_labels=True, pos=pos)
# %%


from igraph import Graph

path = '/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/networks/toy_test.gml'

g =  Graph.Read_GML(path)


#plot graph 





# %%
import uunet.multinet as ml
import pandas as pd

path = '/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/networks/toy_test_ml.gml'
n = ml.read(path)
# %%
ml.plot(n, vertex_labels_bbox = {"boxstyle":'round4', "fc":'white'})
# %%

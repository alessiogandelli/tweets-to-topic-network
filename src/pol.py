#%%
import pandas as pd
import numpy as np
import os
import re
from networkx.algorithms import bipartite
import networkx as nx

# %%
g = nx.Graph()

g.add_nodes_from(['black russian', 'moscow mule'], bipartite = 0)
g.add_nodes_from(['vodka', 'khalua', 'ginger beer', 'lime'], bipartite=1, stock=1)

g.add_edges_from([('black russian', 'vodka'), ('black russian', 'khalua')])
g.add_edges_from([('moscow mule', 'vodka'), ('moscow mule', 'ginger beer'),('moscow mule', 'lime')])
# %%
def check_availability(g):
    for n in g.nodes():
        if(g.nodes[n]['bipartite'] == 0):
            total = 1
            for e in g.edges(n):
                total = total * g.nodes[e[1]]['stock']
            if total == 1:
                print(n)

check_availability(g)

g.nodes['lime']['stock'] = 0

check_availability(g)

#%%

import matplotlib.pyplot as plt
g = gg.copy()
color = [0 if g.nodes[i]['bipartite']==0 else 1 for i in g.nodes]
pos = nx.bipartite_layout(g,nodes)
#pos = nx.spring_layout(gg, k = 0.07)
#pos = nx.multipartite_layout(g, subset_key='bipartite')
nx.draw(g, with_labels=False, pos = pos, node_size = 10, node_color = color, width = 1)
plt.show()
# %%


#%%
import json 
with open('/Users/alessiogandelli/dev/internship/climate-networks/models/drink.json') as f: # open file
    data = json.load(f) # load json content
    
# %%
# create graph
nodes = []
edges = []
for cock in data:
    nodes.append(cock['name'])
    for i in cock['ingredients']:
        edges.append((cock['name'], i['ingredient']))


gg = nx.Graph()

gg.add_nodes_from(nodes, bipartite = 0)
gg.add_edges_from(edges)

for i in gg.nodes:
    if 'bipartite' not in gg.nodes[i]:
        gg.nodes[i]['bipartite'] = 1
        gg.nodes[i]['stock'] = 1

# %%

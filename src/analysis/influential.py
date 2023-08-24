#%%
import networkx as nx
import igraph as ig
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import uunet.multinet as ml
import json
import matplotlib.pyplot as plt

# prepare data 
folder = '/Users/alessiogandelli/data/cop26/'
cop = 26

full_network_path = folder + '/networks/cop26_retweets.gml'
topics_file = folder + 'cache/topics_cop26.csv'
projected_path = folder + 'networks/cop26_retweets_ml.gml'

test_network = '/Users/alessiogandelli/dev/internship/tweets-to-topic-network/data/networks/toy_test.gml'

# load network
g = ig.read(full_network_path, format='gml') # temporal text networj

mln = ml.read(projected_path)   # multilayer network
topic_name = pd.read_csv(topics_file) 
topic_label = json.load(open(folder + '/cache/labels.json'))



tweets = g.vs.select(bipartite=1) # get only tweets 
user = g.vs.select(bipartite=0)  # get only users
original_tweets = g.vs.select(is_retweet='original') # only original tweets 

#create dataframe of tweets 
df_tweets = pd.DataFrame({'tweets': tweets['label'], 
                          'author': tweets['author'], 
                          'topic': tweets['topics']}
                          )


original_tweets_indegree = g.degree(original_tweets, mode='in')
df_original = pd.DataFrame({'tweets': original_tweets['label'], 
                            'indegree': original_tweets_indegree, 
                            'author': original_tweets['author'],
                            'topic': original_tweets['topics']})

                          # %%

# %%

layers = ml.to_nx_dict(mln) #  dictionary where we have a networkx graph for each layer 


# %%

# find users with highest degrees
deg = ml.degree(mln)
act = ml.actors(mln)

degrees = [ [deg[i], act[i]] for i in range(len(deg)) ]# associate actors and degree
degrees.sort(reverse = True) # sort by degree

# get top 100 actors 
top_actors = []
for el in degrees[0:100]: 
      top_actors.append(el[1])

#%%

layer_deg = dict()
layer_deg["actor"] = top_actors
for layer in ml.layers(mln):
    layer_deg[layer] = ml.degree(mln, actors = top_actors, layers = [layer] )
    
pd.DataFrame.from_dict(layer_deg)
# %%

# compute relevance 

def get_most_relevant():

    layer_rel = dict()
    layer_rel["actor"] = top_actors
    for layer in ml.layers(mln):
        layer_rel[layer] = ml.relevance(mln, actors = top_actors, layers = [layer] )

    df_rel = pd.DataFrame.from_dict(layer_rel)
    df_rel = df_rel.set_index('actor')

    # for each layer find the 3 most relevant 
    #get top 3 actor for each column
    top_actors_rel = {}
    for col in df_rel.columns:
        top_actors_rel[col] = (df_rel[col].sort_values(ascending=False).head(3).index.tolist())

# sort values by index 

df_top_rel = pd.DataFrame.from_dict(top_actors_rel).T
# index int 
df_top_rel.index = df_top_rel.index.astype(float)
df_top_rel = df_top_rel.sort_index()





# %%
# compute xrelevance 
layer_xrel = dict()
layer_xrel["actor"] = top_actors
for layer in ml.layers(mln):
    layer_xrel[layer] = ml.xrelevance(mln, actors = top_actors, layers = [layer] )


df_xrel = pd.DataFrame.from_dict(layer_xrel)
df_xrel = df_xrel.set_index('actor')


top_actors_rel = {}
for col in df_xrel.columns:
    top_actors_rel[col] = (df_xrel[col].sort_values(ascending=False).head(30).index.tolist())


df_top_xrel = pd.DataFrame.from_dict(top_actors_rel).T
df_top_rel.index = df_top_rel.index.astype(float)
df_top_rel = df_top_rel.sort_index()






#%%
#  plot 



nx.draw(layers['60.0'], nodelist=[n for n, d in layers['60.0'].degree() if d > 3], node_size=5, with_labels=False)

# draw only main labels 


# %%
import plotly.graph_objs as go

G = layers['60.0']

pos = nx.spring_layout(layers['60.0'])

   # Create a Scatter trace for nodes
node_trace = go.Scatter(
    x=[pos[node][0] for node in G.nodes()],
    y=[pos[node][1] for node in G.nodes()],
    mode="markers",
    marker=dict(
        size=2,
        color="blue"
    ),
    text=[f"Node {node}" for node in G.nodes()],
    hovertemplate="Node: %{text}<extra></extra>"
)

# Create a Scatter trace for edges
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    mode="lines",
    line=dict(color="gray", width=1),
    hoverinfo="none"
)


fig = go.Figure(data=[edge_trace, node_trace])

# Update layout properties
fig.update_layout(
    title="Interactive Network Visualization",
    showlegend=False,
    hovermode="closest",
    margin=dict(b=20, l=5, r=5, t=40)
)
# %%
fig.write_html("network_visualization.html")
# %%
clust = ml.glouvain(mln)

# %%

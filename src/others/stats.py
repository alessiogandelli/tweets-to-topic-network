#%%
# degree analysis 

g = nx.read_gml(full_network_path)

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


# plot graph
color = [0 if sub.nodes[i]['bipartite']==0 else 1 for i in sub.nodes]
pos = nx.bipartite_layout(sub,df_tweets.index)
pos = nx.spring_layout(sub, k = 0.07)
#pos = nx.multipartite_layout(g, subset_key='bipartite')
nx.draw(sub, with_labels=False, pos = pos, node_size = 4, node_color = color, width = 0.1)
plt.show()


# %%

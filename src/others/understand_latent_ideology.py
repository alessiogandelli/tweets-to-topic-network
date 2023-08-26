#%%
from latent_ideology.latent_ideology_class import latent_ideology as li
import pandas as pd
import networkx as nx
import igraph as ig
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import uunet.multinet as ml
import json
import matplotlib.pyplot as plt
import diptest
import numpy as np
import matplotlib.colors as mcolors


folder = '/Users/alessiogandelli/data/cop26/'
projected_path = folder + 'networks/cop26_retweets_ml.gml'
topic_label = json.load(open(folder + '/cache/labels.json'))
topic_label = {int(k): v for k, v in topic_label.items()}# key float to int

mln = ml.read(projected_path)   # multilayer network

layers = ml.to_nx_dict(mln) # dictionary where we have a networkx graph for each layer
layers = {int(float(k)): v for k, v in layers.items()} # key float to int

# %%
net = layers[4]
n_influencers = 30

degree = net.degree()
sorted_degree = sorted(degree, key=lambda x: x[1], reverse=True)
influencers = [s[0] for s in sorted_degree[:n_influencers]]
users = [s[0] for s in sorted_degree[n_influencers:]]



connection_df = pd.DataFrame(columns=['influencer','user'])
for i in influencers:
    # get all in edges of node i
    edges = net.in_edges(i)

    for e in edges:
        connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':i, 'user':e[0]}, index=[0])], ignore_index=True)

li_matrix = li(connection_df)

#%%


connection_df = pd.DataFrame(columns=['influencer','user'])
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'i', 'user':'a'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'i', 'user':'b'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'i', 'user':'c'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'j', 'user':'a'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'j', 'user':'i'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'j', 'user':'c'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'k', 'user':'c'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'k', 'user':'b'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'l', 'user':'b'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'l', 'user':'f'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'l', 'user':'d'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'l', 'user':'e'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'l', 'user':'g'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'m', 'user':'g'}, index=[0])], ignore_index=True)
connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':'m', 'user':'e'}, index=[0])], ignore_index=True)

lim = li(connection_df)


#%%
df_filtered, df_adjacency = lim.make_adjacency(n=2,targets='user', sources='influencer', filtered_df=True)

A = df_adjacency.to_numpy(dtype = int) #for row scores
row_scores = lim.calculate_scores(A)


#%%
P = (1/np.sum(A))*A
#P = (1/np.sum(B))*B
# %% prepare standardization
round(P, 3)


n_col = np.shape(P)[1] # get number of columns
n_row = np.shape(P)[0] # get number of rows

r = np.matmul(P, np.ones((n_col,))) # sum row
c = np.matmul(np.ones((n_row,)), P) # sum column

r2 = r**(-0.5) # power -1/2
c2 = c**(-0.5) # power -1/2

Dr2 = np.diag(r2) # put r2 in the diagonals 
Dc2 = np.diag(c2) # put c2 in the diagonals

r_t = np.array([r]).transpose() # trnaspose r
c_new = np.array([c])
# %%
S = np.matmul(np.matmul(Dr2, P - np.matmul(r_t,c_new)),Dc2)

# %%
from sklearn.utils.extmath import randomized_svd

U, sig, Vt = randomized_svd(S, n_components=1, n_iter=5, random_state=None)

# %%
X_dim1 = np.matmul(Dr2,U)
# %%
scores = (-1 + 2 * (X_dim1-np.min(X_dim1))/np.ptp(X_dim1)) #scaled

# %%
scores_list = [float(l) for l in scores]
data_metodo = {'target':df_adjacency.index,'score':scores_list}
df_scores_target = pd.DataFrame(data_metodo)
# %%
df_final = df_filtered.set_index('target').join(df_scores_target.set_index('target'))
df_final['target'] = df_final.index
df_final = df_final.reset_index(drop=True).copy()
# %%
groups_dict = df_final[['source','score']].set_index('score').groupby(by=['source']).groups
keys_list = list(groups_dict.keys()) #los influencers (son keys)
mean_scores = []
for key in keys_list:
    score_list = list(groups_dict[key]) #lista de scores
    mean_scores.append(np.mean(score_list))
# %%

data_new = {'source':[str(key) for key in keys_list], 'score':mean_scores} #Create dataframe
df_scores_source = pd.DataFrame(data_new).sort_values(by=['score'], ascending=False).reset_index(drop=True)


# %%

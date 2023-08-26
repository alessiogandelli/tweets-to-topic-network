
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



# %% prepare data 


folder = '/Users/alessiogandelli/data/cop26/'
projected_path = folder + 'networks/cop26_retweets_ml.gml'
topic_label = json.load(open(folder + '/cache/labels.json'))
topic_label = {int(k): v for k, v in topic_label.items()}# key float to int

mln = ml.read(projected_path)   # multilayer network

layers = ml.to_nx_dict(mln) # dictionary where we have a networkx graph for each layer
layers = {int(float(k)): v for k, v in layers.items()} # key float to int

# %%


def get_influencers(net, n_influencers):
    degree = net.degree()
    sorted_degree = sorted(degree, key=lambda x: x[1], reverse=True)
    influencers = [s[0] for s in sorted_degree[:n_influencers]]
    users = [s[0] for s in sorted_degree[n_influencers:]]
    

    return influencers, users


def get_polarization_by_layer(n_influencers = 30, n = 2):
    res = {}

    for l in layers:
        net = layers[l]

        # number of edges and nodes 
        print('Layer: ', l)
        print('Number of nodes: ', net.number_of_nodes())
        print('Number of edges: ', net.number_of_edges())


        # get n influencers with highest degree 
        influencers, _ = get_influencers(net, n_influencers)


        # create connection df between influencers and users 
        connection_df = pd.DataFrame(columns=['influencer','user'])
        for i in influencers:
            # get all in edges of node i
            edges = net.in_edges(i)

            for e in edges:
                connection_df = pd.concat([connection_df, pd.DataFrame({'influencer':i, 'user':e[0]}, index=[0])], ignore_index=True)


        # create matrix and apply latent ideology
        try:
            li_matrix = li(connection_df)
            df1, df2 = li_matrix.apply_method(n=n,targets='user', sources='influencer')
        except:
            print('Layer ', l, ' has too few data to be analyzed with latent ideology')
            continue


        # perform dip test on scores
        test = df1['score'].to_numpy()

        dip_res = diptest.diptest(test)
        
        if dip_res[1] < 0.05 and l != -1:
            res[l] = (dip_res, df1, df2)
            res = {int(float(k)): v for k, v in res.items()}
        else:
            print('Layer ', l, ' has too few data to be analyzed with dip test')

    
    return res

def plot_dip_test(res):

    # keys float to int

    #sort the result of the diptest 
    diptest = [(r[0], r[1][0][0]) for r in res.items()]
    diptest_s = sorted(diptest, key=lambda x: x[1], reverse=True)


    plt.figure(figsize=(12,4))
    plt.bar([str(d[0]) for d in diptest_s], [d[1] for d in diptest_s])

    # write xticks on top of the bar 
    plt.xticks([str(d[0]) for d in diptest_s], rotation=90)


    # add mean
    plt.axhline(y=np.mean([d[1] for d in diptest_s]), color='r', linestyle='-')
    # add x label
    plt.xlabel('Layer')
    # add y label
    plt.ylabel('Dip test')
    plt.show()


    # print the most and least polarized topics according to this test 

    # sort topic label according to diptest_s mantain keys
    sorted_topic_label = [(k, topic_label[k]) for k, v in diptest_s]

    # print 10 most and least polarized topics one per line
    print('Most polarized topics:')
    for i in range(10):
        print(sorted_topic_label[i][0], sorted_topic_label[i][1])
    print('')
    print('Least polarized topics:')

    for i in range(1,9):
        print(sorted_topic_label[-i][0], sorted_topic_label[-i][1])

    return sorted_topic_label
    # plot sorted topic label

def draw_network(topic, ax, only_influencers=False):
    # get network and df of correspondence analysis of the users 
    net = layers[topic]
    df1 = res[topic][1]
    df2 = res[topic][2]

    # merge dataframe of users 
    df1.rename(columns={'target':'user'}, inplace=True)
    df2.rename(columns={'source':'user'}, inplace=True)
    df = pd.concat([df1, df2], ignore_index=True)
    df.set_index('user', inplace=True)

    # add score to network
    nx.set_node_attributes(net, df['score'].to_dict(), 'score')




    influencers, users = get_influencers(net, 30)


    # remove self loops
    net.remove_edges_from(nx.selfloop_edges(net))

    net = net.subgraph(influencers) if only_influencers else net.subgraph(influencers + users)

    net = net.to_undirected()

    # delete node when score does not exist, because it's a user that never interacted with an influencer
    for node in net.copy():
        if 'score' not in net.nodes[node]:
            net.remove_node(node)

    # gradient color depending on the score 
    cmap = plt.get_cmap('spring')
    scores = [d['score'] for n, d in net.nodes(data=True)]
    norm = mcolors.Normalize(vmin=min(scores), vmax=max(scores))
    colors = [cmap(norm(score)) for score in scores]


    # remove edges that do not involve a influencer
    edges = list(net.edges())
    for e in edges:
        if e[0] not in influencers and e[1] not in influencers:
            net.remove_edge(e[0], e[1])





    size_map = [100 if node in influencers else 5 for node in net]

    x_noise = 0.0 if only_influencers else 0.01

    # use score for position but add noise in the other dimension
    pos = {n: [d['score'] + np.random.normal(0, x_noise), np.random.normal(0, 0.1)] for n, d in net.nodes(data=True)}


    # add title to plot
    plt.title('Topic: ' + str(topic) + ' - ' + topic_label[topic])


    nx.draw(net, pos=pos ,node_color=colors, with_labels=False, node_size=size_map, width=0.3, ax=ax)

    return ax

def create_plots(topics, title,only_influencers=False):
    fig, axs = plt.subplots(len(topics), figsize=(10, 10))
    # add title 
    fig.suptitle(title, fontsize=25)


    for i, topic in enumerate(topics):
        ax = axs[i]
        ax.set_title('Topic: ' + str(topic) + ' - ' + topic_label[topic])
        draw_network(topic, ax, only_influencers=only_influencers)
    plt.tight_layout()
    plt.show()
# %%



n_influencers = 100

res = get_polarization_by_layer(n_influencers = n_influencers, n=3)
sorted_topic_label = plot_dip_test(res)

#%%
# Example usage
topics_pol = [t[0] for t in sorted_topic_label[:5]]
topics_not_pol = [t[0] for t in sorted_topic_label[-5:]]
topics_not_pol.reverse()

create_plots(topics_pol, 'most polarized topics' + ' - ' + str(n_influencers) + ' influencers')
create_plots(topics_pol,'most polarized topics' + ' - ' + str(n_influencers) + ' influencers',only_influencers=True)
create_plots(topics_not_pol, 'least polarized topics' + ' - ' + str(n_influencers) + ' influencers')
create_plots(topics_not_pol,'least polarized topics'+' - ' + str(n_influencers) + ' influencers', only_influencers=True)

# %%





#%%

# %%



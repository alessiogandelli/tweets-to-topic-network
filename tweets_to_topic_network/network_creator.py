import os
import networkx as nx
import uunet.multinet as ml
from igraph import Graph 
import igraph as ig

class Network_creator:

    def __init__(self, df, name, path):
      
        self.df = df
        self.name = name
        self.path = path
        self.graph_dir = os.path.join(self.path, 'networks')

        self.ttn = None
        self.retweet_network = None
        self.retweet_network_ml = None
        self.proj_graphs = {}
        self.ml_network = ml.empty()
        

    def create_retweet_network(self):
        """
        create a retweet network from the dataframe of tweets and save it in a gml file
        """
        print('create retweet network')
        G = nx.DiGraph() # directed graph
        
        authors = self.df['author'].unique()
        G.add_nodes_from(authors)

        for i, row in self.df.iterrows(): # for each tweet
            ref_id = row['referenced_id']

            if ref_id is not None:  # if the tweet is a retweet
            # if the edge already exists add 1 to the weight
                if G.has_edge(row['author'], self.df.loc[str(ref_id)]['author']):
                    G[row['author']][self.df.loc[str(ref_id)]['author']]['weight'] += 1
                else:
                    G.add_edge(row['author'], self.df.loc[str(ref_id)]['author'], weight=1)
            
        self.retweet_network = G

        self._save_graph(G, 'retweet')

        return G
    
    def create_ttnetwork(self, project = True):
        """
        Create a temporal text network from the dataframe of tweets and save it in a gml file

        Parameters
        ----------
        project : bool
            if true project the network into multiple one mode network, one for each topic, saved in a dict 
            using networkx
        """
        # if author name is none put author id 
        

        print('create network ' + self.name)
        
        A = self.df['author'].unique()            # actors
        M = self.df.index                         # tweets 
        x = self.df['text'].to_dict()             # dict mapping text and nodes 
        topics = self.df['topic'].to_dict()       # dict mapping topics and nodes
        author = self.df['author'].to_dict() # dict mapping author and nodes
        is_retweet = self.df['referenced_type'].to_dict() # dict mapping is_retweet and nodes
        # none to 'original
        is_retweet = {k: 'original' if v is None else v for k, v in is_retweet.items()}

        g = nx.DiGraph() # we use a directed and bipartite graph

        # add nodes
        g.add_nodes_from(A, bipartite=0) # author of tipe 0
        g.add_nodes_from(M, bipartite=1) # tweets of type 1

        # add edges 
        edges = list(zip(self.df['author'], self.df.index))        # author-> tweet
        ref_edges = list(zip( self.df.index, self.df['referenced_id'])) # retweet -> tweet
        ref_edges = [i for i in ref_edges if i[1] is not None]          # remove all none values
        men_edges = [(row.Index, mention) for row in self.df.itertuples() for mention in row.mentions_name] # tweet -> user

        g.add_edges_from(edges, weight = 10 )
        g.add_edges_from(ref_edges, weight = 1)


        # remove all nodes automatically ad
        nodes_to_remove = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
        g.remove_nodes_from(nodes_to_remove)
                # g.nodes[i]['bipartite'] = 1


        date_lookup = {row.Index: row.date for row in self.df.itertuples()}

        t = {e: date_lookup[e[1]] for e in g.edges()}
        g.add_edges_from(men_edges)

        # set bipartite = 0 (so actors) to the new nodes(users) added 
        nodes_to_set = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
        [g.nodes[node].setdefault('bipartite', 0) for node in nodes_to_set]


        nx.set_edge_attributes(g, t, 'date')
        nx.set_node_attributes(g, x, 'text')
        nx.set_node_attributes(g, topics, 'topics')
        nx.set_node_attributes(g, author, 'author')
        nx.set_node_attributes(g, is_retweet, 'is_retweet')


        filename = self._save_graph(g, 'ttt')

        if project:
            self._project_network(path = filename , title = self.name)

        self.text = x
        self.ttn = (g, x, t)

        return (g, x, t)
    
    def create_retweet_ml(self):
        """
        Create a multilayer network from the projected networks, one layer is the retweet network of a specific topic
        """
        topics = self.df['topic'].unique()

        # remove -1
        topics = topics[topics != -1]

        ml_network = ml.empty()

        for topic in topics:
            G = nx.DiGraph()
            df_tmp = self.df[self.df['topic'] == topic]
            G.add_nodes_from(df_tmp['author'].unique())
            print('topic', topic, 'nodes', len(df_tmp['author'].unique()))

            for i, row in df_tmp.iterrows():
                    ref_id = row['referenced_id']
                    try:
                        if ref_id is not None:
                        # if the edge already exists add 1 to the weight
                            if G.has_edge(row['author'], df_tmp.loc[str(ref_id)]['author']):
                                G[row['author']][df_tmp.loc[str(ref_id)]['author']]['weight'] += 1
                            else:
                                G.add_edge(row['author'], df_tmp.loc[str(ref_id)]['author'], weight=1)
                    except:
                        print(ref_id)
                        
            ml.add_nx_layer(ml_network, G , str(topic))

        self.retweet_network_ml = ml_network

        
        
        # save GML file
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

        filename = os.path.join(self.graph_dir,self.name+'_retweet_network_ml.gml')
        ml.write(ml_network, file = filename)

        self.retweetml2 = ml_network


        return ml_network
    
    def _project_network(self, path = None, nx_graph = None, title = None):
        """
        Project a network from a gml file into multiple networks based on the topic of the tweets
        """

        def recursive_explore(graph, node,start_node, previous_node = None , edges = None, topic= None, depth = 0):

            neighbors = graph.neighborhood(node, mode='out') 
            
            # if it is the first we initialize the edges
            if edges is None:
                edges = {}
            
            # it is a user
            if node['bipartite'] == 0.0 :
                # if there is only one node in the middle it is a mention
                if depth == 2 :
                    edges.setdefault(topic, []).append((start_node['label'], node['label']))
                    return
                # in this  case we have a retweet  
                elif depth > 2 :
                    edges.setdefault(topic, []).append((start_node['label'], previous_node['author']))
                    return
            # it is a tweet
            else:
                if topic is None:
                    topic = node['topics']
                # end of the chain it is a retweet without mention
                if (len(neighbors) == 1):
                    edges.setdefault(topic, []).append((start_node['label'], node['author']))
                    return

            # explore all the neighbors
            for neighbor in neighbors[1:]:
                new_node = g.vs[neighbor]
                recursive_explore(graph, node = new_node, previous_node = node, start_node = start_node, depth = depth+1, edges= edges, topic= topic)

            return edges

        if path is not None:
            g =  Graph.Read_GML(path)
            
        elif nx_graph is not None:
            g = Graph.from_networkx(nx_graph)
            g.vs['label'] = g.vs['_nx_name']
            
        else:
            print('provide a graph of a gml file o a networkx graph')
            return None

        edges = {}

        # for each user
        for n in g.vs.select(bipartite=0):
            # get all neighbors of g
            visited = set()
            result = recursive_explore(g, n, start_node = n)
            #print(result)
            edges = {key: edges.get(key, []) + result.get(key, []) for key in set(edges) | set(result)}

        edges = {e: set(edges[e]) for e in edges }
        edges.pop(None, None)
        # drop key 
        print('projected network created')

        self._save_projected(edges)

        # prj_dir = os.path.join(self.graph_dir, 'projected')

        # if not os.path.exists(prj_dir):
        #     os.makedirs(prj_dir)
       
        # for t, e in edges.items():
        #     print(t, len(e))
        #     if t != 'NaN':
        #         self.proj_graphs[t] = nx.from_edgelist(e, create_using=nx.DiGraph())
        #         nx.write_gml(self.proj_graphs[t], os.path.join(prj_dir, self.name+'_'+title+'_prj_'+str(t)+'.gml'))
        #         ml.add_nx_layer(ml_network, self.proj_graphs[t], str(t))
        
        # ml.write(ml_network, file = os.path.join(self.graph_dir, self.name+'retweet_ml.gml'))
        # save file 
       # Graph.write_gml(g, os.path.join(self.graph_dir, self.name+title+'_prj.gml'))

        
        return self.proj_graphs

    def _save_projected(self, edges):
        prj_dir = os.path.join(self.graph_dir, 'projected')

        if not os.path.exists(prj_dir):
            os.makedirs(prj_dir)


       
        for t, e in edges.items():
            print(t, len(e))
            if t != 'NaN':
                self.proj_graphs[t] = nx.from_edgelist(e, create_using=nx.DiGraph())
                nx.write_gml(self.proj_graphs[t], os.path.join(prj_dir, self.name+'__prj_'+str(t)+'.gml'))
                ml.add_nx_layer(self.ml_network, self.proj_graphs[t], str(t))

        ml.write(self.ml_network, file = os.path.join(self.graph_dir, self.name+'_retweet_ml.gml'))

    def _save_graph(self, G, title):
        """
        Save a network in a gml file and creates the networks directory if needed 

        Parameters
        ----------
        G : networkx.Graph
            network to save
        title : str
            title of the network
        """
        print('save graph', title)
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

        filename = os.path.join(self.graph_dir,self.name+'_'+title+'.gml')
        nx.write_gml(G, filename)
        print('network created at', filename)
        # create a png of the network
        return filename
    
    def plot_network(self, G):
        print('plot network')
        import matplotlib.pyplot as plt
        pos = nx.kamada_kawai_layout(G)
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos)
        plt.show()

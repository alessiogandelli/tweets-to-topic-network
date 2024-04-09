import os
import networkx as nx


class Network_creator:

    def __init__(self, df, name, path):
      
        self.df = df
        self.name = name
        self.path = path
        self.graph_dir = os.path.join(self.path, 'networks')
        self.text = None
        self.retweet_graph = None
        

    def create_retweet_network(self):
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
            
        self.retweet_graph = G

        self._save_graph(G, 'retweet')

        return G
    
    def _save_graph(self, G, title):
        print('save graph', title)
        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

        filename = os.path.join(self.graph_dir,self.name+'_'+title+'.gml')
        nx.write_gml(G, filename)
        print('network created at', filename)

    def plot_network(self, G):
        print('plot network')
        import matplotlib.pyplot as plt
        pos = nx.kamada_kawai_layout(G)
        nx.draw_networkx_nodes(G, pos)
        nx.draw_networkx_edges(G, pos)
        nx.draw_networkx_labels(G, pos)
        plt.show()

    def create_ttnetwork(self, project = True):
        """
        Create a temporal text network from the dataframe of tweets and save it in a gml file

        Parameters
        ----------
        df_tweets : pandas.DataFrame
            dataframe of tweets including, author, text, topic, author_name, referenced_type, referenced_id, mentions_name
        title : str
            title of the network
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

        #self.graph_dir = os.path.join(self.path, 'networks')

        if not os.path.exists(self.graph_dir):
            os.makedirs(self.graph_dir)

        filename = os.path.join(self.graph_dir,self.name+'_'+self.name+'.gml')
        nx.write_gml(g, filename)
        print('network created at', filename)

        # if project:
        #     self.project_network(path = filename , title = self.name)

        self.text = x

        return (g, x, t)
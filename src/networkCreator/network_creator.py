
class Network_creator:

    def create_ttnetwork(self, df_tweets, title, project = True):
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
        

        print('create network ' + title)
        
        A = df_tweets['author_name'].unique() # actors
        M = df_tweets.index                   # tweets 
        x = df_tweets['text'].to_dict()       # dict mapping text and nodes 
        topics = df_tweets['topic'].to_dict() # dict mapping topics and nodes
        author = df_tweets['author_name'].to_dict() # dict mapping author and nodes
        is_retweet = df_tweets['referenced_type'].to_dict() # dict mapping is_retweet and nodes
        # none to 'original
        is_retweet = {k: 'original' if v is None else v for k, v in is_retweet.items()}

        g = nx.DiGraph() # we use a directed and bipartite graph

        # add nodes
        g.add_nodes_from(A, bipartite=0) # author of tipe 0
        g.add_nodes_from(M, bipartite=1) # tweets of type 1


        # add edges 
        edges = list(zip(df_tweets['author_name'], df_tweets.index)) # author-> tweet
        ref_edges = list(zip( df_tweets.index, df_tweets['referenced_id'])) # retweet -> tweet
        ref_edges = [i for i in ref_edges if i[1] is not None] # remove all none values
        men_edges = [(row.Index, mention) for row in df_tweets.itertuples() for mention in row.mentions_name] # tweet -> user


        g.add_edges_from(edges, weight = 10 )
        g.add_edges_from(ref_edges, weight = 1)


        # remove all nodes authomatically ad
        nodes_to_remove = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
        g.remove_nodes_from(nodes_to_remove)
                # g.nodes[i]['bipartite'] = 1


        date_lookup = {row.Index: row.date for row in df_tweets.itertuples()}

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

        filename = os.path.join(self.graph_dir,self.name+'_'+title+'.gml')
        nx.write_gml(g, filename)
        print('network created at', filename)

        if project:
            self.project_network(path = filename , title = title)

        self.text = x

        return (g, x, t)
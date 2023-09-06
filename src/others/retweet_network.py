
def retweet_network(self, df = None):
    if df is None:
        df = self.df_retweets_labeled
    

    topics = df['topic'].unique()

    ml_network = ml.empty()

    for topic in topics:
        G = nx.Graph()
        df_tmp = df[df['topic'] == topic]
        G.add_nodes_from(df_tmp['author'].unique())

        for i, row in df_tmp.iterrows():
            ref_id = row['referenced_id']

            if ref_id is not None:
            # if the edge already exists add 1 to the weight
                if G.has_edge(row['author'], df_tmp.loc[str(ref_id)]['author']):
                    G[row['author']][df_tmp.loc[str(ref_id)]['author']]['weight'] += 1
                else:
                    G.add_edge(row['author'], df_tmp.loc[str(ref_id)]['author'], weight=1)
                    
        ml.add_nx_layer(ml_network, G , str(topic))
    
    return ml_network
#%%
import jsonlines
import pandas as pd
import os
import numpy as np
import re
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from networkx.algorithms import bipartite
import networkx as nx




def process_json(file, file_user):
    print('processing json')
    users = {}
    with jsonlines.open(file_user) as reader: # open file
        for obj in reader:
            users[obj['id']] = {'username': obj['username'], 'tweet_count': obj['public_metrics']['tweet_count'], 'followers' : obj['public_metrics']['followers_count'], 'following' : obj['public_metrics']['following_count']}
        

    df_user = pd.DataFrame(users).T



    tweets = {}
    with jsonlines.open(file) as reader: # open file
        for obj in reader:
            tweets[obj['id']] = {'author': obj['author_id'], 
                                'author_name': users[obj['author_id']]['username'],
                                'text': obj['text'], 
                                'date': obj['created_at'],
                                'lang':obj['lang'] ,
                                'reply_count': obj['public_metrics']['reply_count'], 
                                'retweet_count': obj['public_metrics']['retweet_count'], 
                                'like_count': obj['public_metrics']['like_count'], 
                                'quote_count': obj['public_metrics']['quote_count'],
                                'impression_count': obj['public_metrics']['impression_count'],
                                'conversation_id': obj['conversation_id'] if 'conversation_id' in obj else None,
                                'referenced_type': obj['referenced_tweets'][0]['type'] if 'referenced_tweets' in obj else None,
                                'referenced_id': obj['referenced_tweets'][0]['id'] if 'referenced_tweets' in obj else None,
                                'mentions_name': [ann.get('username') for ann in obj.get('entities',  {}).get('mentions', [])],
                                'mentions_id': [ann.get('id') for ann in obj.get('entities',  {}).get('mentions', [])],
                                'context_annotations': [ann.get('entity').get('name') for ann in obj.get('context_annotations', [])]}


    df_tweets = pd.DataFrame(tweets).T
    #df_user.to_csv(os.path.join(path,'users_cop22.csv'))
    #df_tweets.to_csv(os.path.join(path,'tweets_cop22.csv'))
    #df_tweets.to_pickle(os.path.join(path,'tweets_cop22.pkl'))

    return df_tweets



def get_topics(df_cop):
    docs = df_cop['text'].tolist()

    docs = [re.sub(r"http\S+", "", doc) for doc in docs]



    vectorizer_model = CountVectorizer(stop_words="english")
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    model = BERTopic( 
                        vectorizer_model =   vectorizer_model,
                        ctfidf_model      =   ctfidf_model,
                        nr_topics        =  'auto',
                        min_topic_size   =   100,
                    )

    topics ,probs = model.fit_transform(docs)
    df_cop['topic'] = topics

    #cop.to_pickle(os.path.join(path,'tweets_cop22_topics.pkl'))
    #model.get_topic_info().to_csv(os.path.join(path,'topics_cop22.csv'))



    return df_cop


def create_network(df_tweets, path, name):

    A = df_tweets['author_name'].unique() # actors
    M = df_tweets.index                   # tweets 
    x = df_tweets['text'].to_dict()
    topics = df_tweets['topic'].to_dict()

    g = nx.DiGraph()
    g.add_nodes_from(A, bipartite=0) # author of tipe 0
    g.add_nodes_from(M, bipartite=1) # tweets of type 1

    print('nodes added')

    # list of tuples between author_nname and index 
    edges = list(zip(df_tweets['author_name'], df_tweets.index)) # author-> tweet
    ref_edges = list(zip( df_tweets.index, df_tweets['referenced_id'])) # retweet -> tweet
    ref_edges = [i for i in ref_edges if i[1] is not None] # remove all none values
    men_edges = [(row.Index, mention) for row in df_tweets.itertuples() for mention in row.mentions_name]


    g.add_edges_from(edges, weight = 10 )
    g.add_edges_from(ref_edges, weight = 1)

    print('edges added')

    # remove all nodes authomatically addd 

    #add attribute bipartite to all nides without it, required for the new tweets added with the ref
    nodes_to_remove = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
    g.remove_nodes_from(nodes_to_remove)
            # g.nodes[i]['bipartite'] = 1


    date_lookup = {row.Index: row.date for row in df_tweets.itertuples()}

    t = {e: date_lookup[e[1]] for e in g.edges()}
    g.add_edges_from(men_edges)
    print('mentions added')

    # set bipartite = 0 ( so actors) to the new nodes(users) added 
    nodes_to_set = [node for node in g.nodes if 'bipartite' not in g.nodes[node]]
    [g.nodes[node].setdefault('bipartite', 0) for node in nodes_to_set]


    nx.set_edge_attributes(g, t, 'date')
    nx.set_node_attributes(g, x, 'text')
    nx.set_node_attributes(g, topics, 'topics')

    nx.write_gml(g, os.path.join(path,name))


    return (g, x , t)
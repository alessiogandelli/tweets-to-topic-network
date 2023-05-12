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
os.environ['TOKENIZERS_PARALLELISM'] = 'false' # to avoid a warning 

#%%
class Pipeline:
    """
    A class used to represent the entire pipeline from json to graph

    ...
    Attributes
    ----------
    file_tweets : str
        path to the json file containing the tweets
    file_user : str
        path to the json file containing the users
    path : str
        path to the folder containing the json files
    path_cache : str
        path to the folder containing the cache files
    name : str
        name of the folder
    df_tweets : pandas.DataFrame
        dataframe containing all the tweets
    df_original : pandas.DataFrame
        dataframe containing all the tweets that are not retweets, quotes or replies
    df_original_labeled : pandas.DataFrame
        dataframe containing all the tweets that are not retweets, quotes or replies and are labeled with the topic
    df_retweets : pandas.DataFrame
        dataframe containing all the retweets
    df_retweets_labeled : pandas.DataFrame
        dataframe containing all tweets and retweets and are labeled with the topic 
    df_quotes : pandas.DataFrame
        dataframe containing all the quotes
    df_quotes_labeled : pandas.DataFrame
        dataframe containing all tweets and quotes and are labeled with the topic
    df_reply : pandas.DataFrame
        dataframe containing all the replies
    df_reply_labeled : pandas.DataFrame
        dataframe containing all tweets and replies and are labeled with the topic

    Methods
    -------
    process_json()
        process the json files and create the dataframes
    get_topics()
        get the topics of the original tweets
    create_network(df -> pandas.DataFrame, title -> str)
        create the network of the given dataset and save in gml format in the network folder

    """

    def __init__(self,  file_tweets, file_user):
        """

        Parameters
        ----------
        file_tweets : str
            path to the json file containing the tweets
        file_user : str
            path to the json file containing the users
        """

        self.file_user = file_user
        self.file_tweets = file_tweets
        self.path = file_tweets.split('/')[:-1]
        self.path = '/'.join(self.path)
        self.path_cache = os.path.join(self.path, 'cache')
        self.name = self.file_tweets.split('/')[-1].split('.')[0]
        self.df_tweets = None
        self.df_original = None
        self.df_original_labeled = None
        self.df_retweets = None
        self.df_retweets_labeled = None
        self.df_quotes = None
        self.df_quotes_labeled = None
        self.df_reply = None
        self.df_reply_labeled = None





    def process_json(self):
        """
        Process the json files and create the dataframes

        """
        file = os.path.join(self.path_cache,'tweets_'+self.name+'.pkl')

        # if pkl file tweets_cop22 exists, load it
        if os.path.exists(file):
            print('using cached file for json processing')
            df_tweets = pd.read_pickle(file)
            
        else:
            print('looking into users json file')
            users = {}
            with jsonlines.open(self.file_user) as reader: # open file
                for obj in reader:
                    users[obj['id']] = {'username': obj['username'], 'tweet_count': obj['public_metrics']['tweet_count'], 'followers' : obj['public_metrics']['followers_count'], 'following' : obj['public_metrics']['following_count']}

            df_user = pd.DataFrame(users).T

            print('looking into tweets json file')
            tweets = {}
            with jsonlines.open(self.file_tweets) as reader: # open file
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
                                       # 'context_annotations': [ann.get('entity').get('name') for ann in obj.get('context_annotations', [])]
                                       }


            df_tweets = pd.DataFrame(tweets).T

            # create cache folder if not exists and then
            if not os.path.exists(self.path_cache):
                os.makedirs(self.path_cache)
            # save file in the cache folder both csv and pkl format
            df_user.to_csv(os.path.join(self.path_cache,'users_'+self.name+'.csv'))
            df_tweets.to_csv(os.path.join(self.path_cache,'tweets_'+self.name+'.csv'))
            df_tweets.to_pickle(file)
        
        df_tweets = df_tweets[df_tweets['lang'] == 'en'] # consider only english tweets
        
        # create the dataframes, devide the tweets in original, retweets, quotes and replies
        self.df_tweets = df_tweets
        self.df_original = df_tweets[df_tweets['referenced_type'].isna()]
        self.df_retweets = df_tweets[df_tweets['referenced_type'] == 'retweeted']
        self.df_quotes = df_tweets[df_tweets['referenced_type'] == 'quoted']
        self.df_reply = df_tweets[df_tweets['referenced_type'] == 'replied_to']


        return df_tweets



    def get_topics(self):
        """
        Get the topics of the original tweets
           
        """

        file = os.path.join(self.path_cache, 'tweets_'+self.name+'_topics.pkl')

        # if the original dataframe is not created, run process_json
        if(self.df_original is None):
            self.process_json()

        # if pkl file tweets_cop22_topics exists, load it
        if os.path.exists(file):
            print('using cached topics')
            df_cop = pd.read_pickle(file)
        else:
            print('running topic modeling')

            df_cop = self.df_original
            # prepare documents for topic modeling
            docs = df_cop['text'].tolist()
            docs = [re.sub(r"http\S+", "", doc) for doc in docs]

            # topic modeling
            vectorizer_model = CountVectorizer(stop_words="english")
            ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
            model = BERTopic( 
                                vectorizer_model =   vectorizer_model,
                                ctfidf_model      =   ctfidf_model,
                                nr_topics        =  'auto',
                                min_topic_size   =   max(int(len(docs)/100),10),
                            )
            topics ,probs = model.fit_transform(docs)
            df_cop['topic'] = topics            

            try:
                topics ,probs = model.fit_transform(docs)
                df_cop['topic'] = topics            
                model.get_topic_info().to_csv(os.path.join(self.path_cache,'topics_cop22.csv'))

            except Exception as e:
                print(e)
                print('error in topic modeling')
                df_cop['topic'] = -1

            # create cache folder if not exists 
            if not os.path.exists(self.path_cache):
                os.makedirs(self.path_cache)

            # save file in the cache folder 
            df_cop.to_pickle(file)

        # add topics label to the originaldataframe and for the not original tweet put the reference of the original tweet in that field 
        self.df_original_labeled = df_cop
        self.df_retweets['topic'] = self.df_retweets['referenced_id']
        self.df_quotes['topic'] = self.df_quotes['referenced_id']
        self.df_reply['topic'] = self.df_reply['referenced_id']

        # merge the dataframes
        self.df_retweets_labeled = pd.concat([self.df_original_labeled, self.df_retweets])
        self.df_quotes_labeled = pd.concat([self.df_original_labeled, self.df_quotes])
        self.df_reply_labeled = pd.concat([self.df_original_labeled, self.df_reply])

        def resolve_topic(df, row_id):
            if isinstance(row_id, int): # the topic 
                return int(row_id)
            else: # the pointer 
                try:
                    topic = df.loc[row_id, 'topic']
                    return resolve_topic(df, topic)
                except: # if there is not the referenced tweet we discard the tweet
                    return None
        
        self.df_retweets_labeled['topic'] = self.df_retweets_labeled.apply(lambda row: resolve_topic(self.df_retweets_labeled, row['topic']), axis=1)
        self.df_quotes_labeled['topic'] = self.df_quotes_labeled.apply(lambda row: resolve_topic(self.df_quotes_labeled, row['topic']), axis=1)
        self.df_reply_labeled['topic'] = self.df_reply_labeled.apply(lambda row: resolve_topic(self.df_reply_labeled, row['topic']), axis=1)



        return df_cop




    def create_network(self, df_tweets, title):
        """
        Create a network from the dataframe of tweets and save it in a gml file
        """


        print('create network ' + title)
       
        A = df_tweets['author_name'].unique() # actors
        M = df_tweets.index                   # tweets 
        x = df_tweets['text'].to_dict()
        topics = df_tweets['topic'].to_dict()
        author = df_tweets['author_name'].to_dict()

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
        nx.set_node_attributes(g, author, 'author')

        graph_folder = os.path.join(self.path, 'networks')

        if not os.path.exists(graph_folder):
            os.makedirs(graph_folder)

        nx.write_gml(g, os.path.join(graph_folder,self.name+title+'.gml'))
        print('network created at', os.path.join(graph_folder,self.name+title+'.gml'))

        return (g, x , t)
# %%

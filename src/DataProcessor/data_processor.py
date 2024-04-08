
import os
import jsonlines
import pandas as pd
import datetime


class Data_processor:
    def __init__(self, file_tweets, file_user, n_cop):

        # input files
        self.file_user = file_user
        self.file_tweets = file_tweets
        self.n_cop = None

        # paths and name
        self.name = self.file_tweets.split('/')[-1].split('.')[0]

        self.folder = '/'.join(file_tweets.split('/')[:-1])
        self.path_cache = os.path.join(self.folder, 'cache')
        self.tweets_file = os.path.join(self.path_cache,'tweets_'+self.name)
        self.users_file = os.path.join(self.path_cache,'users_'+self.name)

        # dataframes
        self.df_tweets = None
        self.df_original = None
        self.df_original_influencers = None
        self.df_retweets = None
        self.df_quotes = None
        self.df_reply = None


    def process_json(self):
    
        
        # df_tweets and df_users are the cleaned dataframe is a tabular form btu before other data preprocessing
        if self._is_cached():
            print('loading files from the cache ', self.path_cache)
            self.df_tweets = pd.read_pickle(self.tweets_file+'.pkl')
            self.df_users = pd.read_pickle( self.users_file+'.pkl')
        else:
            df_tweets, df_user = self._load_json()

            print('saving files in the cache ', self.path_cache)
            df_user.to_csv(self.users_file+'.csv')
            df_tweets.to_csv(self.tweets_file+'.csv')
            df_user.to_pickle(self.users_file+'.pkl')
            df_tweets.to_pickle(self.tweets_file+'.pkl')
            self.df_tweets = df_tweets
            self.df_users = df_user
        
        #miss preprocessing here
        self._create_dataframes()
        self._log_info()


    def _create_dataframes(self):
        """
        Create dataframes by dividing tweets into original, retweets, quotes, and replies.
        """
        print('creating dataframes')
        df_tweets = self.df_tweets
        self.df_original = df_tweets[df_tweets['referenced_type'].isna()] # The handwritten tweets
        self.df_retweets = df_tweets[df_tweets['referenced_type'] == 'retweeted']
        self.df_quotes = df_tweets[df_tweets['referenced_type'] == 'quoted']
        self.df_reply = df_tweets[df_tweets['referenced_type'] == 'replied_to']
    
    def _is_cached(self):
       
        if not os.path.exists(self.path_cache):
            os.makedirs(self.path_cache)

        return os.path.exists(self.tweets_file+'.pkl') and os.path.exists(self.users_file+'.pkl')

    def _load_json(self):
        
        df_user = self._load_users_json()
        df_tweets = self._load_tweets_json(df_user)

       

        return df_tweets, df_user
    
    def _load_users_json(self):
        print('looking into users json file')
        users = {}
        with jsonlines.open(self.file_user) as reader: # open file
            for obj in reader:
                users[obj['id']] = {'username': obj['username'], 'tweet_count': obj['public_metrics']['tweet_count'], 'followers' : obj['public_metrics']['followers_count'], 'following' : obj['public_metrics']['following_count']}

        df_user = pd.DataFrame(users).T
        return df_user

    def _load_tweets_json(self, users):
        print('looking into tweets json file')
        tweets = {}
        attachments = 0
        with jsonlines.open(self.file_tweets) as reader: # open file
            for obj in reader:
                if obj.get('attachments') is  None : # avoid tweets with attachments (should be analyzed with )
                    tweets[obj.get('id', 0)] = {'author': obj['author_id'], 
                                                    'author_name': users.get(obj['author_id'], {}).get('username'),
                                                    'text': obj.get('text', ''), 
                                                    'date': obj.get('created_at', ''),
                                                    'lang':obj.get('lang', ''),
                                                    'reply_count': obj.get('public_metrics', {}).get('reply_count', 0), 
                                                    'retweet_count': obj.get('public_metrics', {}).get('retweet_count', 0), 
                                                    'like_count': obj.get('public_metrics', {}).get('like_count', 0), 
                                                    'quote_count': obj.get('public_metrics', {}).get('quote_count', 0),
                                                    #'impression_count': obj['public_metrics']['impression_count'],
                                                    'conversation_id': obj.get('conversation_id', None),
                                                    'referenced_type': obj.get('referenced_tweets', [{}])[0].get('type', None),
                                                    'referenced_id': obj.get('referenced_tweets', [{}])[0].get('id', None),
                                                    'mentions_name': [ann.get('username', '') for ann in obj.get('entities',  {}).get('mentions', [])],
                                                    'mentions_id': [ann.get('id', '') for ann in obj.get('entities',  {}).get('mentions', [])],
                                                    'cop':  self.n_cop
                                                # 'context_annotations': [ann.get('entity').get('name') for ann in obj.get('context_annotations', [])]
                                                }
                else:
                    attachments+=1

            print('discarded ',attachments ,'tweets with attachments')

        df_tweets = pd.DataFrame(tweets).T
        return df_tweets
    
    def _log_info(self):
        print('Data processed')
        print('Tweets:', self.df_tweets.shape[0])
        print('Original tweets:', self.df_original.shape[0])
        print('Retweets:', self.df_retweets.shape[0])
        print('Quotes:', self.df_quotes.shape[0])
        print('Replies:', self.df_reply.shape[0])
        print('Users:', self.df_users.shape[0])

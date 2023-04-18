#%%
import jsonlines
import pandas as pd
path = '/Volumes/boot420/Users/data/climate_network/cop21/'


# %%
file_user = 'users_cop21.json'
file = 'cop21.json'
users = {}

with jsonlines.open(os.path.join(path,file_user)) as reader: # open file
    for obj in reader:
        users[obj['id']] = {'username': obj['username'], 'tweet_count': obj['public_metrics']['tweet_count'], 'followers' : obj['public_metrics']['followers_count'], 'following' : obj['public_metrics']['following_count']}
    
# %%

df_user = pd.DataFrame(users).T
# %%
df_user.to_csv(os.path.join(path,'users_cop21.csv'))
# %%
file_user = 'users_cop21.json'
file = 'cop21.json'

#%%

tweets = {}
with jsonlines.open(os.path.join(path,file)) as reader: # open file
    for obj in reader:
        tweets[obj['id']] = {'author': obj['author_id'], 
                            'text': obj['text'], 
                            'date': obj['created_at'],
                            'lang':obj['lang'] ,
                            'reply_count': obj['public_metrics']['reply_count'], 
                            'retweet_count': obj['public_metrics']['retweet_count'], 
                            'like_count': obj['public_metrics']['like_count'], 
                            'quote_count': obj['public_metrics']['quote_count'],
                            'conversation_id': obj['conversation_id'] if 'conversation_id' in obj else None,
                            'referenced_type': obj['referenced_tweets'][0]['type'] if 'referenced_tweets' in obj else None,
                            'referenced_id': obj['referenced_tweets'][0]['id'] if 'referenced_tweets' in obj else None}
# %%
df_tweets = pd.DataFrame(tweets).T
# %%
df_tweets.to_csv(os.path.join(path,'tweets_cop21.csv'))
# %%

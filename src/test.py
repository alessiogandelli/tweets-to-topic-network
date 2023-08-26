#%%
from utils import Pipeline
import sys 
import datetime


# file_tweets = '/Volumes/boot420/Users/data/climate_network/test/sample.json'
# file_user = '/Volumes/boot420/Users/data/climate_network/test/users_cop22.json'

# file_tweets = '/Volumes/boot420/Users/data/climate_network/cop22/cop22.json'
# file_user = '/Volumes/boot420/Users/data/climate_network/cop22/cop22_user.json'

file_tweets = '/Users/alessiogandelli/data/cop26/cop26.json'
file_user = '/Users/alessiogandelli/data/cop26/users_cop26.json'

start = datetime.datetime.now()

p = Pipeline(file_tweets, file_user)
p.process_json()
print('json processed in ', datetime.datetime.now()-start)
p.get_topics(name = 'bert')
print('topics extracted in ', datetime.datetime.now()-start)


p.create_network(p.df_retweets_labeled, 'retweets')

# %%


# if author name is none put author id 
p.df_retweets_labeled['author_name'] = p.df_retweets_labeled['author_name'].fillna(p.df_retweets_labeled['author_id'])






# %%



import re 

name = 'openai'
df_cop = p.df_original

df_cop['n_words'] = df_cop['text'].apply(lambda x: len(x.split()))




# prepare documents for topic modeling
docs = df_cop['text'].tolist()

stats = docs_stats(docs)

docs = [re.sub(r"http\S+", "", doc) for doc in docs]
#docs = [re.sub(r"@\S+", "", doc) for doc in docs] #  remove mentions 
#docs = [re.sub(r"#\S+", "", doc) for doc in docs] #  remove hashtags
docs = [re.sub(r"\n", "", doc) for doc in docs] #  remove new lines
#strip 
docs = [doc.strip() for doc in docs]



#%%
if(name == 'openai'):
    embs = openai.Embedding.create(input = docs, model="text-embedding-ada-002")['data']
    embedder = None
    embeddings = np.array([np.array(emb['embedding']) for emb in embs])
else:
    embedder = SentenceTransformer(self.name)
    embeddings = self.embedder.encode(self.docs)
# %%

# statistics about docs 
print('number of docs: ', len(docs))
print('number of unique docs: ', len(set(docs)))

# %%
import pandas as pd
pd.Series(docs).value_counts().head(10)
# %%

# give me the longest word

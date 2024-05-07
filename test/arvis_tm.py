#%%
import pandas as pd
from tweets_to_topic_network.topic import Topic_modeler



file_tweets = '/Users/alessiogandelli/data/cop23/cache/data/tweets_cop23.pkl'      

df = pd.read_pickle(file_tweets)

df = df[df['referenced_type'].isna()]

# %%

tm = Topic_modeler(df, name = 'cop23', embedder_name='all-MiniLM-L6-v2', path_cache = '/Users/alessiogandelli/data/cop23/cache')
df_labeled = tm.get_topics()

# %%
tm = Topic_modeler(df, name = 'cop23', embedder_name='paraphrase-MiniLM-L3-v2', path_cache = '/Users/alessiogandelli/data/cop23/cache')
df_labeled = tm.get_topics()

# %%

tm = Topic_modeler(df, name = 'cop23', embedder_name='text-embedding-3-small', path_cache = '/Users/alessiogandelli/data/cop23/cache')
df_labeled = tm.get_topics()


# %%
# tm.docs is a list of strings get the lenght of each 

len_docs = [len(doc) for doc in tm.docs]
# %%

from openai import OpenAI
openai_client = OpenAI()
import numpy as np


batch_size = 1000
num_batches = len(tm.docs) // batch_size + (len(tm.docs) % batch_size != 0)
tm.embeddings = []

for i in range(num_batches):
    print(f'         batch {i+1}/{num_batches}')
    batch = tm.docs[i*batch_size:(i+1)*batch_size]
    print(batch[:5])
    embs = openai_client.embeddings.create(input = batch, model=tm.embedder_name).data
    tm.embeddings.extend([np.array(emb.embedding) for emb in embs])
# %%

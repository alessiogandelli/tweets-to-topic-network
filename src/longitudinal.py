#%%
from tweets_to_network import Tweets_to_network
import sys 
import datetime
import pandas as pd


tweets_cop22 = '/Users/alessiogandelli/data/cop22/cop22.json'
users_cop22 = '/Users/alessiogandelli/data/cop22/users_cop22.json'

tweets_cop21 = '/Users/alessiogandelli/data/cop21/cop21.json'
users_cop21 = '/Users/alessiogandelli/data/cop21/users_cop21.json'

tweets_cop26 = '/Users/alessiogandelli/data/cop26/cop26.json'
users_cop26 = '/Users/alessiogandelli/data/cop26/users_cop26.json'

tweets_cop2x = '/Users/alessiogandelli/data/cop2x/cop2x.json'
users_cop2x = '/Users/alessiogandelli/data/cop2x/users_cop2x.json'


#%%

network_cop22 = Tweets_to_network(tweets_cop22, users_cop22, 'cop22')
network_cop21 = Tweets_to_network(tweets_cop21, users_cop21, 'cop21')
network_cop26 = Tweets_to_network(tweets_cop26, users_cop26, 'cop26')

cop22 = network_cop22.process_json()
cop21 = network_cop21.process_json()
cop26 = network_cop26.process_json()

# %%

# merge the three df
cop = pd.concat([cop22, cop21, cop26])

#save csv 
cop.to_pickle('/Users/alessiogandelli/data/cop2x/cache/tweets_cop.pkl')


cop_original = cop[cop['referenced_type'].isna()]
# %%
cop2x = Tweets_to_network(tweets_cop2x, users_cop2x, 'cop2x')
cop2x.process_json()
# %%
cop2x.get_topics(name = 'bert')
# %%

from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import IncrementalPCA
from bertopic.vectorizers import OnlineCountVectorizer
from bertopic import BERTopic


def online_topic_modeling(df):

    print('running online topic modeling')

    df_cop = df.df_original
    # prepare documents for topic modeling
    docs = df_cop['text'].tolist()
    docs = [re.sub(r"http\S+", "", doc) for doc in docs]
    docs = [re.sub(r"@\S+", "", doc) for doc in docs] #  remove mentions 
    docs = [re.sub(r"#\S+", "", doc) for doc in docs] #  remove hashtags
    docs = [re.sub(r"\n", "", doc) for doc in docs] #  remove new lines
    docs = [doc.strip() for doc in docs]#strip 
    docs = [doc.lower() for doc in docs]#lowercase

    doc_chunks = [docs[i:i + 10000] for i in range(0, len(docs), 10000)]

    umap_model = IncrementalPCA(n_components=5)
    cluster_model = MiniBatchKMeans(n_clusters=50, random_state=0)
    vectorizer_model = OnlineCountVectorizer(stop_words="english", decay=.01)

    # Create the topic model

    topic_model = BERTopic(
        umap_model=umap_model,
        hdbscan_model=cluster_model,
        vectorizer_model=vectorizer_model)

    all_topics = []
    # Update the topic model with the documents
    for chunk in doc_chunks:
        print('processing chunk n ', doc_chunks.index(chunk))
        topics = topic_model.partial_fit(chunk)
        print(topics.topics_)
        # add topics to the df 

        all_topics.append(topics.topics_) 

    all_topics = [item for sublist in all_topics for item in sublist]
    df_cop['topics'] = all_topics


    
    return topic_model, df_cop


topic_model = online_topic_modeling(df = network_cop22)





        

# %%

# %%

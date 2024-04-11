import os
import pandas as pd
import numpy as np
import datetime
import re
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
import openai
from qdrant_client import QdrantClient, models

os.environ['TOKENIZERS_PARALLELISM'] = 'false' # to avoid a warning 
openai.api_key = os.getenv("OPENAI_API_KEY")    
client = QdrantClient(os.getenv("QDRANT_URL")) # vector database saved in memory

collection_name = 'cop'


class Topic_modeler:

    def __init__(self, df, embedder_name = 'all-MiniLM-L6-v2', path_cache = '/cache', name = 'cop') -> None:
        self.df = df
        self.path_cache = path_cache
        self.embedder_name = embedder_name
        self.name = name

        self.df_labeled_path = os.path.join(self.path_cache, 'tweets_'+self.name+'_topics.pkl')
        self.model_path = os.path.join(self.path_cache, 'model_'+self.name+'.pkl')
        self.model = None
        self.embeddings = None
        

    def get_topics(self):
        """
        Main function of the class, get the topics of the original tweets and updates the dataframe with the topics and topic probabilities. 
        then save the embeddings in qdrant and save the labeled dataframe in the cache folder.

        """
        # start time and create cache folder
        time = datetime.datetime.now()
        if not os.path.exists(self.path_cache):
            os.makedirs(self.path_cache)

        
        # if pkl file of the labeled df exists, load it from the cache
        if os.path.exists(self.df_labeled_path):
            print('using cached topics')
            self.df = pd.read_pickle(self.df_labeled_path)
            self.model = BERTopic.load(self.model_path)
        else:
            print('running topic modeling')
    
            docs = self._preprocess()
            print( '    ',datetime.datetime.now() - time, ' for preprocessing')
            self._get_embeddings(docs)
            print( '    ',datetime.datetime.now() - time, ' for embeddings')
            self._use_BERTopic(docs)
            print( '    ',datetime.datetime.now() - time, ' for bertopic')
            self._save_embeddings(docs)
            print( '    ',datetime.datetime.now() - time, ' for saving embeddings')
            self._save_files()
            print( '    ',datetime.datetime.now() - time, ' for saving files')
        

        print('topics created in ', datetime.datetime.now() - time)

        return self.df

        # add topics label to the originaldataframe and for the not original tweet put the reference of the original tweet in that field 

    def _preprocess(self):
        docs = self.df['text'].tolist()
        docs = [re.sub(r"http\S+", "", doc) for doc in docs] #  remove urls
        docs = [re.sub(r"@\S+", "", doc) for doc in docs] #  remove mentions 
        docs = [re.sub(r"#\S+", "", doc) for doc in docs] #  remove hashtags
        docs = [re.sub(r"\n", "", doc) for doc in docs] #  remove new lines
        docs = [doc.strip() for doc in docs] #strip 
        return docs

    def _get_embeddings(self, docs):
        if(self.embedder_name == 'text-embedding-ada-002'):
            embs = openai.Embedding.create(input = docs, model="text-embedding-ada-002")['data']
            self.embedder = None
            self.embeddings = np.array([np.array(emb['embedding']) for emb in embs])
        elif(self.embedder_name == 'text-embedding-3-large'):
            embs = openai.Embedding.create(input = docs, model="text-embedding-3-large")['data']
            self.embedder = None
            self.embeddings = np.array([np.array(emb['embedding']) for emb in embs])
        
        elif(self.embedder_name == 'text-embedding-3-small'):
            embs = openai.Embedding.create(input = docs, model="text-embedding-3-small")['data']
            self.embedder = None
            self.embeddings = np.array([np.array(emb['embedding']) for emb in embs])
        else:
            print(self.embedder_name, docs[:2])
            self.embedder = SentenceTransformer(self.embedder_name)
            self.embeddings = self.embedder.encode(docs)

    def _use_BERTopic(self, docs):
        vectorizer_model = CountVectorizer(stop_words="english") 
        # we can also change some parameter of the cTFIDF model https://maartengr.github.io/BERTopic/getting_started/ctfidf/ctfidf.html#reduce_frequent_words
        ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
        model = BERTopic( 
                            vectorizer_model =   vectorizer_model,
                            ctfidf_model      =   ctfidf_model,
                            nr_topics        =  'auto',
                            min_topic_size   =   max(int(len(docs)/800),10),
                            embedding_model  = self.embedder,
                        )
        
        try:
            topics ,probs = model.fit_transform(docs, embeddings = self.embeddings)
            self.df['topic'] = topics    
            self.df['topic_prob'] = probs   
            print('topics created')
            #df_cop['embedding'] = embeddings   
            model.get_topic_info().to_csv(os.path.join(self.path_cache,'topics_cop22.csv'))
            self.model = model          
            print('model saved')

        except Exception as e:
            print(e)
            print('error in topic modeling')
            self.df['topic'] = -1

    def _save_embeddings(self,docs):
        ids = self.df.index.tolist()
        vectors = self.embeddings.tolist()
        topics = self.df['topic'].tolist()
        probs = self.df['topic_prob'].tolist()

        try:
            client.create_collection(
                collection_name= self.name,
                vectors_config=models.VectorParams(size=len(self.embeddings[0]), distance=models.Distance.COSINE),
            )
        except:
            print('collection already exists')


        try:
            points = [
                models.PointStruct(
                    id = int(idx),
                    vector = vector,
                    payload = {"text": text, "topic": topic, "prob": prob}
            
                )
                for idx, vector, text, topic, prob in zip(ids, vectors, docs, topics, probs)
            ]
            client.upload_points(self.name, points)
            

        except(Exception) as e:
            print(e)
            print('error in saving vectors in qdrant')

    def _save_files(self):
        self.df.to_pickle(self.df_labeled_path)
        self.model.save(self.model_path, serialization="safetensors", save_ctfidf=True)

    def label_topics(self):
        pass
       
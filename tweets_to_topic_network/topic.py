import os
import pandas as pd
import numpy as np
import datetime
import re
from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from bertopic.vectorizers import ClassTfidfTransformer
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding
import pickle 

from langchain import PromptTemplate
from langchain.llms import OpenAI as LLMOpenAI
from bertopic.representation import OpenAI as BERTOpenAI

from langchain.chains import LLMChain
from openai import OpenAI

try:
    from cuml.cluster import HDBSCAN
    from cuml.manifold import UMAP
    umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.0)
    hdbscan_model = HDBSCAN(min_samples=10, gen_min_span_tree=True, prediction_data=True)
except:
    from umap import UMAP
    print('cuml not found')

try:
    openai_client = OpenAI()
except:
    openai_client = None



os.environ['TOKENIZERS_PARALLELISM'] = 'false' # to avoid a warning 
qdrant_client = QdrantClient(os.getenv("QDRANT_URL")) # vector database saved in memory
collection_name = 'cop'


class Topic_modeler:

    def __init__(self, df, embedder_name = 'all-MiniLM-L6-v2', path_cache = '/cache', name = 'cop') -> None:
        self.df = df
        self.path_cache = path_cache
        self.embedder_name = embedder_name
        self.name = name

        self.tm_path = os.path.join(self.path_cache,'tm', self.embedder_name)
        self.df_labeled_path = os.path.join(self.tm_path,'tweets_'+self.name+'_labeled.pkl')
        self.model_path = os.path.join( self.tm_path, 'model_'+self.name)
        self.embeddings_path = os.path.join( self.tm_path ,'embeddings_'+self.name+'.pkl')
        self.topic_path = os.path.join( self.tm_path ,'topics_'+self.name+'.csv')

        self.model = None
        self.embeddings = None
        self.docs = None
        

    def get_topics(self, min_topic_size = 50, nr_topics = 'auto', umap_model = None, hdbscan_model = None, representation_model = None):
        """
        Main function of the class, get the topics of the original tweets and updates the dataframe with the topics and topic probabilities. 
        then save the embeddings in qdrant and save the labeled dataframe in the cache folder.

        """
        # start time and create cache folder
        time = datetime.datetime.now()
        if not os.path.exists(self.path_cache):
            os.makedirs(self.path_cache)
        
        if not os.path.exists(self.tm_path):
            os.makedirs(self.tm_path)

        
        # if pkl file of the labeled df exists, load it from the cache
        if os.path.exists(self.df_labeled_path) and os.path.exists(self.model_path) :
            print('using cached topics')
            self.df = pd.read_pickle(self.df_labeled_path)
            self.model = BERTopic.load(self.model_path)
            self.docs = self.df['new_text'].tolist()
        else:
            print('running topic modeling')
    
            docs = self._preprocess()
            print( '    ',datetime.datetime.now() - time, ' for preprocessing')
            if os.path.exists(self.embeddings_path):
                print('   loading embeddings from cache')
                self.embeddings = pickle.load(open(self.embeddings_path, 'rb'))
            else:
                self._get_embeddings(docs)
            print( '    ',datetime.datetime.now() - time, ' for embeddings')
            self._use_BERTopic(docs, nr_topics, min_topic_size, umap_model, hdbscan_model, representation_model)
            print( '    ',datetime.datetime.now() - time, ' for bertopic')
            self._save_embeddings(docs)
            print( '    ',datetime.datetime.now() - time, ' for saving embeddings')
            self._save_files()
            print( '    ',datetime.datetime.now() - time, ' for saving files')
        

        print('topics created in ', datetime.datetime.now() - time)

        return self.df

        # add topics label to the originaldataframe and for the not original tweet put the reference of the original tweet in that field 

    def _preprocess(self):

        self.df['new_text'] = self.df['text']
        self.df['new_text'] =  self.df['new_text'].str.replace(r"http\S+", "")
        self.df['new_text'] =  self.df['new_text'].str.replace(r"@\S+", "")
        self.df['new_text'] =  self.df['new_text'].str.replace(r"\n", "")
        self.df['new_text'] =  self.df['new_text'].str.strip()

        # if new text is empty delete the row
        self.df = self.df[self.df['new_text'] != '']

        docs = self.df['new_text'].tolist()
        self.docs = docs

        
        return docs

    def _get_embeddings(self, docs):


        if os.path.exists(self.embeddings_path):
            try:
                self.embeddings = pickle.load(open(self.embeddings_path, 'rb'))
                return
            except Exception as e:
                print(f"Error loading embeddings from cache: {e}")

        print('     Embeddings not found in cache, using' + self.embedder_name + ' to get embeddings')


        if(self.embedder_name.startswith('text-embedding')):
            print('         using openai')

            batch_size = 1000
            num_batches = len(self.docs) // batch_size + (len(self.docs) % batch_size != 0)
            self.embeddings = []

            for i in range(num_batches):
                print(f'         batch {i+1}/{num_batches}')
                batch = self.docs[i*batch_size:(i+1)*batch_size]
                print(batch[:5])
                embs = openai_client.embeddings.create(input = batch, model=self.embedder_name).data
                self.embeddings.extend([np.array(emb.embedding) for emb in embs])

            self.embedder = None
            self.embeddings = np.array(self.embeddings)
        else:
            self.embedder = SentenceTransformer(self.embedder_name)
            self.embeddings = self.embedder.encode(docs)
        
                #save embeddings to pickle file
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings, f)

    def _use_BERTopic(self, docs, nr_topics = 'auto', min_topic_size = 50, umap_model = None, hdbscan_model = None, representation_model = None):
        vectorizer_model = CountVectorizer(stop_words="english") 
        # we can also change some parameter of the cTFIDF model https://maartengr.github.io/BERTopic/getting_started/ctfidf/ctfidf.html#reduce_frequent_words
        ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

        try:
            representation_model = BERTOpenAI(openai_client, model="gpt-3.5-turbo", chat=True)
        except:
            representation_model = None
            print('representation model not found')

        model = BERTopic( 
                            vectorizer_model =   vectorizer_model,
                            ctfidf_model      =   ctfidf_model,
                            nr_topics        =  nr_topics,
                            min_topic_size   =   min_topic_size,
                            umap_model=umap_model,
                            hdbscan_model=hdbscan_model,
                            representation_model = representation_model
                        )
        print('         model created')
        
        try:
            topics ,probs = model.fit_transform(docs, embeddings = self.embeddings)
            self.df['topic'] = topics    
            self.df['topic_prob'] = probs   
            print('         model fitted')

            #df_cop['embedding'] = embeddings   
            model.get_topic_info().to_csv(self.topic_path)
            self.model = model          
            print('         model saved')

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
            qdrant_client.create_collection(
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
            qdrant_client.upload_points(self.name, points)
            

        except(Exception) as e:
            print(e)
            print('error in saving vectors in qdrant')

    def _save_files(self):
        self.df.to_pickle(self.df_labeled_path)
        self.model.save(self.model_path, serialization="safetensors", save_ctfidf=True, save_embedding_model=self.embedder_name)

    def label_topics(self):
        template = """
        I have a topic that contains the following documents: 
        [{DOCUMENTS}]
        The topic is described by the following keywords: [{KEYWORDS}]

        Based on the information above, extract a short topic label in the following format:
        topic: <topic label>
        """
        llm = LLMOpenAI(temperature=0.3)

        prompt = PromptTemplate(
            input_variables=["DOCUMENTS", 'KEYWORDS'],
            template=template
        )

        chain = LLMChain(llm=llm, prompt=prompt)


        pass
    
    def visualize_topics(self):
        return self.model.visualize_topics()
    
    def visualize_hierarchical_topics(self):
        hierarchical_topics =  self.model.hierarchical_topics(self.docs)
        self.model.visualize_hierarchy()

    def get_topic_tree(self):
        hierarchical_topics =  self.model.hierarchical_topics(self.docs)
        return self.model.get_topic_tree(hierarchical_topics)
    
    def visualize_docs(self):
        # Reduce dimensionality of embeddings, this step is optional but much faster to perform iteratively:
        reduced_embeddings = UMAP(n_neighbors=10, n_components=2, min_dist=0.0, metric='cosine').fit_transform(self.embeddings)
        return self.model.visualize_documents(self.docs, reduced_embeddings=reduced_embeddings)
    
    def visualize_topic_similarity(self):
        return self.model.visualize_heatmap()
    
    def visualize_terms(self):
        return self.model.visualize_barchart()
    




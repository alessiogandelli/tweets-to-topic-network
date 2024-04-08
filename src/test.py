# %%
from dataProcessor.data_processor import Data_processor 
from topicModeler.topic_modeler import Topic_modeling

file_tweets = '/Users/alessiogandelli/data/cop22/cop22.json'
file_user = '/Users/alessiogandelli/data/cop22/users_cop22.json'

#%%
data = Data_processor(file_tweets, file_user, '22')
data.process_json()

tm = Topic_modeling(data.df_original, name = data.name, embedder_name='all-MiniLM-L6-v2', path_cache = data.path_cache)
df = tm.get_topics()
# %%

# %%
from DataProcessor.data_processor import Data_processor 

file_tweets = '/Users/alessiogandelli/data/cop22/cop22.json'
file_user = '/Users/alessiogandelli/data/cop22/users_cop22.json'

#%%
data = Data_processor(file_tweets, file_user, '22')
data.process_json()
# %%

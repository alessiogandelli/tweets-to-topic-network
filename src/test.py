#%%
from utils import Pipeline
import sys 
import datetime



file_tweets = '/Volumes/boot420/Users/data/climate_network/test/sample.json'
file_user = '/Volumes/boot420/Users/data/climate_network/test/users_cop22.json'


start = datetime.datetime.now()

p = Pipeline(file_tweets, file_user)
p.process_json()
print('json processed in ', datetime.datetime.now()-start)
p.get_topics()
print('topics extracted in ', datetime.datetime.now()-start)

# %%
import jsonlines
att = []
not_att = []
with jsonlines.open(file_tweets) as reader: # open file
    for obj in reader:
        if obj.get('attachments') is  None :
            att.append(obj['attachments'])
        else:
            not_att.append(obj)
# %%

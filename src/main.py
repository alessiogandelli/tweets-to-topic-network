#%%
from utils import Pipeline
import sys 
import datetime

# get file from command line
file_tweets = sys.argv[1]
file_user = sys.argv[2]

#file_tweets = '/Volumes/boot420/Users/data/climate_network/cop22/cop22.json'
#file_user = '/Volumes/boot420/Users/data/climate_network/cop22/cop22_user.json'
 #%%


start = datetime.datetime.now()

p = Pipeline(file_tweets, file_user)
p.process_json()
print('json processed in ', datetime.datetime.now()-start)
p.get_topics()
print('topics extracted in ', datetime.datetime.now()-start)


p.label_topics()

#%%
p.create_network(p.df_reply_labeled, 'reply')
print('reply network created in ', datetime.datetime.now()-start)
p.create_network(p.df_quotes_labeled, 'quotes')
print('quotes network created in ', datetime.datetime.now()-start)
p.create_network(p.df_retweets_labeled, 'retweets')
print('retweets network created in ', datetime.datetime.now()-start)







#%%
#p.project_network(path='/Volumes/boot420/Users/data/climate_network/test/networks/sampleretweets.gml', title='retweets')


# %%

#%%
from tweets_to_network import Tweets_to_network
import sys 
import datetime



tweets_cop22 = '/Users/alessiogandelli/data/cop22/cop22.json'
users_cop22 = '/Users/alessiogandelli/data/cop22/users_cop22.json'

tweets_cop21 = '/Users/alessiogandelli/data/cop21/cop21.json'
users_cop21 = '/Users/alessiogandelli/data/cop21/users_cop21.json'

tweets_cop26 = '/Users/alessiogandelli/data/cop26/cop26.json'
users_cop26 = '/Users/alessiogandelli/data/cop26/users_cop26.json'


#%%

network_cop22 = Tweets_to_network(tweets_cop22, users_cop22, 'cop22').process_json()
network_cop21 = Tweets_to_network(tweets_cop21, users_cop21, 'cop21').process_json()
network_cop26 = Tweets_to_network(tweets_cop26, users_cop26, 'cop26').process_json()
# %%

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

cop22 = Tweets_to_network(tweets_cop22, users_cop22, 'cop22')
cop21 = Tweets_to_network(tweets_cop21, users_cop21, 'cop21')
cop26 = Tweets_to_network(tweets_cop26, users_cop26, 'cop26')

cop22.process_json()
cop21.process_json()
cop26.process_json()

cop22.get_topics(name = 'bert')
cop21.get_topics(name = 'bert')
#cop26.get_topics(name = 'bert')

cop22.retweet_network()
cop21.retweet_network()
#cop26.retweet_network()
#%%
inf_cop22 = cop22.get_n_influencers()
inf_cop21 = cop21.get_n_influencers()
inf_cop26 = cop26.get_n_influencers()



#%%


# %%

# merge the three df
cop = pd.concat([inf_cop22, inf_cop21, inf_cop26])

#save csv 
cop.to_pickle('/Users/alessiogandelli/data/cop2x/cache/tweets_original_cop.pkl')



# %%
cop2x = Tweets_to_network(tweets_cop2x, users_cop2x, 'cop2x')
cop2x.process_json()


#%%
cop2x.get_topics(name = 'bert', df=cop2x.df_original_influencers)


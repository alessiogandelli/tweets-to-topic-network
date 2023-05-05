# tweets-to-network
This repository contains the code to create a temporal text network from a set of tweets in json format (as they come from the api), labeling each tweet according to its topic. The network is saved in gml format.

#  example

````
from utils import Pipeline
p = Pipeline(file_tweets, file_user)
p.process_json()
p.get_topics()

p.create_network(p.df_retweets_labeled, 'retweets')
p.create_network(p.df_quotes_labeled, 'quotes')
p.create_network(p.df_reply_labeled, 'reply')

````


# How to run 

open a terminal and run, tweet file is the user file is the file with the users information


```
make run tweet_file=url user_file=url
```


# data
First step was to transform the json in csv removing all non necessary information and saving much more space and having the possibility to use tabular data.
This process is in the data file, the output is a csv with the users and one with the tweets. Moreover the tweet file has been also saved in a pickle file to be able to load it faster.

# topic modeling 
The topic modeling is done using Bertopic

# network 
starting from the tabular file we have just created we can create the temporal text network created according to https://appliednetsci.springeropen.com/articles/10.1007/s41109-018-0082-3.

It is a bipartite network with nodes that can be or users or tweets.
edges: 
- user-tweet: if the user has tweeted the tweet
- tweet-user: if the tweet mention the user 
- tweet-tweet: if the tweet retweets the other

the create_network function gets as input a dataframe loaded from the csv file and returns:
- a directed graph 
- dictionary x which maps the tweet id to its text 
- dictionary t which maps the couple (user, tweet) to the time of the tweet

note that the content of this dictionary is also present as nodes and edges attributes 

TODO
topic modeling and multilayer network 

one layer per topic 

# to understand 

cop22 
number of tweets = 768174
number of tweets that are not retweets =  180926
number of tweets that are not retweets but contains RT in the text = 12019
number of tweets that are not retweets but contains RT from pablorodas = 6639


number of retweets = 587248
number of referenced tweets = 104368
number of refereenced tweets that we do not have =  14403
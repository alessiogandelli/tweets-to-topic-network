# climate-networks

# data
first step was to transform the json in csv removing all non necesary information and saving much more space and having the possibility to use tabular data.
This process is in the data file, the output is a csv with the users and one with the tweets. Moreover the tweet file has been also saved in a pickle file to be able to load it faster.

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
# tweets-to-network
This repository contains the code to create a temporal text network from a set of tweets in json format (as they come from the api), labeling each tweet according to its topic. The network is saved in gml format.

Optionally from the temporal text network we can create a projected multilayer network where each layer is a topic and the nodes are the users.

#  Quickstart
## with python
```python
from utils import Pipeline
p = Pipeline(file_tweets, file_user)
p.process_json()
p.get_topics()

p.create_network(p.df_retweets_labeled, 'retweets')
p.create_network(p.df_quotes_labeled, 'quotes')
p.create_network(p.df_reply_labeled, 'reply')

```

##  with terminal

open a terminal and run, tweet file is the user file is the file with the users information


```
make run tweet_file=url user_file=url
```


# input 
Th input is in [jsonl](https://jsonlines.org/) format, so one json per line representing or a user or a tweet depending on the file. You can find an example in [this](https://github.com/alessiogandelli/tweets-to-topic-network/tree/main/data) folder. This format is the one you can get querying the twitter api.
## json tweets file 
The json tweets file contains information about all tweets involved in the conversation. Each tweet is represented as a json object with the following fields:

- `author`: The ID of the tweet author.
- `author_name`: The username of the tweet author.
- `text`: The content of the tweet.
- `created_At`: The timestamp when the tweet was created.
- `lang`: The language of the tweet.
- `reply_count`: The number of replies to the tweet.
- `retweet_count`: The number of retweets of the tweet.
- `like_count`: The number of likes on the tweet.
- `quote_count`: The number of quotes of the tweet.
- `impression_count`: The number of impressions (times the tweet was displayed) of the tweet.
- `conversation_id`: The ID of the conversation the tweet belongs to (if available).
- `referenced_type`: The type of the referenced tweet (if available).
- `referenced_id`: The ID of the referenced tweet (if available).
- `mentions_name`: A list of usernames mentioned in the tweet.
- `mentions_id`: A list of IDs of users mentioned in the tweet.


## json users file
The json users file contains information about all users involved in the conversation. Each user is represented as a json object with the following fields:

- `id`: The ID of the user.
- `username`: The username of the user.
- `tweet_count`: The number of tweets posted by the user.
- `followers`: The number of followers the user has.
- `following`: The number of accounts the user is following.


# Workflow

## init
The first step is to initialize the pipeline class giving the two files as input.

```python
from utils import Pipeline
p = Pipeline(file_tweets, file_user)
```
## process json
Then we can process the json files, this creates a pandas dataframe contaning all the tweets in english. Moreover the dataframe is also stored in a pickle and csv for caching it, in fact the next rime you run the pipeline it loads the file instead of processing it every time.

```python  
p.process_json()
```
## topic modeling 
Then we can get the topics of the tweets using BERTopic, this creates a new column in the dataframe with the topic of the tweet. The topics are saved in a pickle file for caching.

```python
p.get_topics()
```

## create network
Finally we can create the network, the  `create_network()` function takes as input the dataframe created in the previous stage, but you can use your own if you need it, and the title of the network.

The function creates a [temporal text network](https://appliednetsci.springeropen.com/articles/10.1007/s41109-018-0082-3) and two dictionaries that map the tweet id to its text and the couple (user, tweet) to the time of the tweet. The network is saved in gml format in the `networks` folder.



```python
p.create_network(p.df_retweets_labeled, 'retweets')
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
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
In this example we can see how a network is built, the small nodes are the tweets, while the other are the authors. The color of the tweets corresponds to the topic of the tweet. The edges are of three types:
- user-tweet: if the user has tweeted the tweet
- tweet-user: if the tweet mention the user
- tweet-tweet: if the tweet retweets the other

![full network](https://github.com/alessiogandelli/tweets-to-topic-network/blob/main/data/full_network.png)


## network projection
Now we have two sets of nodes and we want only one: the authors. To achieve this i used an hybrid approach between iteration and recursion. First it iterates over all the users, so for each user the goal now is to create all the edges between this user and others. 
For each user we iterate over all its tweets recursively searching for the end of the chain. There are few cases:
- It is an original tweet with no mentions: do nothing 
- It is an original tweet mentioning other users: create an edge between the user and the mentioned users
- It is a retweet: create an edge between the user and the author of the original tweet

In this process is also involved the topics of the tweets, so while projecting it is created a network for each topic, and the edges are added to the corresponding network. The networks are saved in gml format in the `networks/projected` folder.

The path is the path of the gml file of the full network.

```python
p.project_network(path)
```


## create multilayer network
The multilayer network is created using the `create_multilayer_network()` function which uses the [multinet](https://github.com/uuinfolab/py_multinet) library developed by the infolab in Uppsala university. 

This step is made inside the projection function, so you don't need to run it again.

```python
p.create_multilayer_network()
```

This is an example of how it looks like 

![multilayer network](https://github.com/alessiogandelli/tweets-to-topic-network/blob/main/data/projected_topics_ml.png)

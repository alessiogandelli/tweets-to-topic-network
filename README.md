# tweets-to-network
```bash
pip install tweets-to-topic-network
```

This repository contains the code to 
- create networks from a set of tweets in json format (as they come from the API (RIP))
- label each tweet with a topic using BERTopic

from a set of tweets it is possibile to generate multiple networks:
- *retweet network*:  a network where the nodes are the users and the edges are the retweets
- *retweet network multilayer*: a network where the nodes are the users and the edges are the retweets, but the edges are divided in layers based on the topic of the tweet
- *temporal text network*: a bipartite network where the nodes are the tweets and the users and the edges are the interactions between them

#  Quickstart

```python
data = Data_processor(file_tweets, file_user, '22')
data.process_json() # this process the data and creates several dataframes useful for the next steps

tm = Topic_modeler(data.df_original, name = data.name, embedder_name='all-MiniLM-L6-v2', path_cache = data.path_cache)
df_labeled = tm.get_topics() # this creates a new column in the dataframe with the topic of the tweet


df_retweet_labeled = data.update_df(df_labeled) # this updates the dataframe with the labeled topics

nw = Network_creator(df_retweet_labeled, name = data.name, path = data.folder)
nw.create_retweet_network() # this creates the retweet network
nw.create_ttnetwork()   # this creates the temporal text network
nw.create_retweet_ml()  # this creates the multilayer network

```


# Input 
Th input is in [jsonl](https://jsonlines.org/) format, so one JSON per line representing or a user or a tweet depending on the file. You can find an example in [this](https://github.com/alessiogandelli/tweets-to-topic-network/blob/main/data/toy.json) file. This format is the one you can get querying the Twitter API.
## JSON tweets file 
The JSON tweets file contains information about all tweets involved in the conversation. Each tweet is represented as a JSON object with the following fields:

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


## JSON users file
The user's file contains information about all users involved in the conversation. Each user is represented as a JSON object with the following fields:

- `id`: The ID of the user.
- `username`: The username of the user.
- `tweet_count`: The number of tweets posted by the user.
- `followers`: The number of followers the user has.
- `following`: The number of accounts the user is following.


# Classes
The pipeline is divided into three classes, each of them is independent and can be used separately.

- dataProcessor: takes the two json files and creates a pandas dataframe with all the tweets in english. It also creates a cache of the dataframe in csv and pickle format.

- TopicModeler: takes a dataframe and labels the tweets with a topic using BERTopic. It also creates a cache of the labeled dataframe in csv and pickle format.

- NetworkCreator: takes a dataframe of tweets and creates a network from it. It can create a retweet network, a temporal text network, and a multilayer network. The networks are saved in gml format.


## Data Processor
The first step is to initialize the pipeline class giving the two files as input and the name of the COP.

```python
data = Data_processor(file_tweets, file_user, name)
data.process_json()

```
### Under the hood
Let's see what happen when you run the process_json() function, firstly, if the files are present in the cache folder, it loads them, otherwise, it follows this pipeline:.
- load_users_json: loads the json file of the users into a dataframe 
- load_tweets_json: loads the json file of the tweets into a dataframe discarding the tweets with attachments
- save dataframes: both in pickle (for machines) and csv(for humans) format in the cache folder

### after the topic modeling
There is the possibility to update the dataframe with the labeled topic, so that the object data contains all the data needed, it gets the labeled dataframe of the original tweets ( the topic modeling is not run on retweets to save save time and energy), and propagate the topic also to the retweets of the original tweets.

```python  
df_retweet_labeled = data.update_df(df_labeled)

```
## Topic Modeler
Then we can get the topics of the tweets using BERTopic, this creates a new column in the dataframe with the topic of the tweet. The topics are saved in a pickle file for caching. In [this](https://github.com/alessiogandelli/topic-modeling-evaluation) repository I conclude that BERTopic is the best topic modeling algorithm for this scenario. You can choose the embedder you prefer

```python
tm = Topic_modeler(data.df_original, name = data.name, embedder_name='all-MiniLM-L6-v2', path_cache = data.path_cache)
df_labeled = tm.get_topics()


```
### label topics 
we use openai gpt3.5turbo model to label the topic using the putput of the cTFIDF and some representative tweets. 

## Network Creator
Finally we can create the networks using the full dataframe with topic labels. there are 3 possible types of network you can create

```python
nw = Network_creator(df_retweet_labeled, name = data.name, path = data.folder)
```
### Temporal Text Network
The function creates a [temporal text network](https://appliednetsci.springeropen.com/articles/10.1007/s41109-018-0082-3) and two dictionaries that map the tweet id to its text and the couple (user, tweet) to the time of the tweet. The network is saved in gml format in the `networks` folder.

```python
nw.create_ttnetwork(project = True)
```

In this example we can see how a network is built, the small nodes are the tweets, while the other are the authors. The color of the tweets corresponds to the topic of the tweet. The edges are of three types:
- user-tweet: if the user has tweeted the tweet
- tweet-user: if the tweet mention the user
- tweet-tweet: if the tweet retweets the other

![full network](https://github.com/alessiogandelli/tweets-to-topic-network/blob/main/data/full_network.png)



#### Network projection
if the project parameter is set to True the network is also projected into a retweet network (this is redundant, you can create a retweets network without passing from the ttn) and a network of retweets for each topic :

In the temporal text network, we have two sets of nodes and we want only one: the authors. To achieve this I used a hybrid approach between iteration and recursion. First, it iterates over all the users, so for each user, the goal now is to create all the edges between this user and others. 

For each user, we iterate over all its tweets recursively searching for the end of the chain. There are a few cases:
- It is an original tweet with no mentions: do nothing 
- It is an original tweet mentioning other users: create an edge between the user and the mentioned users
- It is a retweet: create an edge between the user and the author of the original tweet.

In this process are also involved the topics of the tweets, so while projecting it, a network is created for each topic, and the edges are added to the corresponding network. The networks are saved in gml format in the `networks/projected` folder.

The TTN is a very powerful tool, but it requires a lot of computational power and time. so if you do not need all the information contained, you can create the simple retweet network using the `retweet_network()` or the  `retweet_network_ml()` depending if you are interested in the multilayer network or not.

### Retweet Network

In this network the nodes are the users and the edges are the retweets, the network is saved in gml format in the `networks` folder.

```python
nw.create_retweet_network()
```

### Retweet Network Multilayer


multiples retweets network created at topic level stacked together

This is an example of how it looks like 

![multilayer network](https://github.com/alessiogandelli/tweets-to-topic-network/blob/main/data/projected_topics_ml.png)





#  How to run it

suggestion: create a folder for each set of tweets you want to process, in our case one for each COP. Inside this folder there should be the two jsonl files, one for the tweets and one for the users. After running the main script( either using make or just running main.py) in that folder you will find the following folders:

- `cache`: contains the csv and pickle files of the intermediate steps of the pipeline, from the cleaned dataset in csv to the label of the topics.

- `networks`: contains the gml files of the temporal text network




# A Real Example

Processing around 400k tweets with the hashtag #cop22, this took around 3 hours on 2018 macbook air.

- json tweets: 878 MB
- csv/pkl tweets: 236 MB
- retweet gml network: 234 MB
- projected gml network: 19 MB

## cop 26 
macbook pro 14 

- json tweets: 14.3 GB (requires a lot of ram)
- csv/pkl tweets: 1.79 GB
- temporal text network: 900 MB
- projected multilayer: 84 MB

2 h for processing the json file 
4 h for extracting topics 
18 h for creating the networks 

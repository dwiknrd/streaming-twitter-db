import tweepy
import time
import sqlite3
from decouple import config


'''
===Authenticating the Twitter API===
- Create an OAuthHandler instance that handles the authentication:
  -- Need to pass the API key, API secret key, Access token and Access Token Secret Key.
- Create API object by passing in the authentication information
'''

api_key = config('api_key') # api_key
api_secret_key = config('api_secret_key') # api_secret_key
access_token = config('access_token') # access_token
access_token_secret = config('access_token_secret') # access_token_secret

# authorize the API Key
authentication = tweepy.OAuthHandler(api_key, api_secret_key)

# authorization to user's access token and access token secret
authentication.set_access_token(access_token, access_token_secret)

# call the api
api = tweepy.API(authentication)

'''
===Streaming Tweets in Real-Time using StreamListener===
- Obtaining a large number of tweets
- Streaming API returns data in JSON
- Use tweepy.StreamListener to stream real-time tweets
'''

class MyStreamListener(tweepy.StreamListener):
    
    def __init__(self, time_limit=300):
        self.start_time = time.time()
        self.limit = time_limit
        super(MyStreamListener, self).__init__()
    
    def on_connect(self):
        print("Connected to Twitter API.")
        
    def on_status(self, status):
        
        
        # Tweet ID
        tweet_id = status.id
        
        # User ID
        user_id = status.user.id

        # fetching the user
        user = api.get_user(user_id)
  
        # fetching the username/screen name
        username = user.screen_name

        # Create time
        create_time = str(status.created_at) 
        
        # Tweet
        if status.truncated == True:
            tweet = status.extended_tweet['full_text']
            hashtags = status.extended_tweet['entities']['hashtags']
        else:
            tweet = status.text
            hashtags = status.entities['hashtags']
        
        # Read hastags
        hashtags = read_hashtags(hashtags)            
        
        # # Retweet count
        # retweet_count = status.retweet_count

        # Language
        lang = status.lang
        
        
        # If tweet is not a retweet and tweet is in English
        if not hasattr(status, "retweeted_status") and lang=="en":
            # Connect to database
            insert_to_db(tweet_id, username, tweet, create_time, hashtags)
            
        if (time.time() - self.start_time) > self.limit:
            
            print(time.time(), self.start_time, self.limit)
            return False
            
    def on_error(self, status_code):
        if status_code == 420:
            # Returning False in on_data disconnects the stream
            return False

def read_hashtags(tag_list):
    hashtags = []
    for tag in tag_list:
        hashtags.append(tag['text'])
    return hashtags

def insert_to_db(tweet_id, username, tweet_text, date, hashtag):
    con = sqlite3.connect('streaming_tweets.db')
    cur = con.cursor()

    command = f'''INSERT INTO tweets VALUES ("{tweet_id}","{username}","{tweet_text}","{date}","{hashtag}")'''
    print(command)
    # insert user information
    try:
        cur.execute(command)
    except:
        print("there is error occur")
    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener,
                        tweet_mode="extended")
myStream.filter(track=['covid','Covid','COVID','covid19','Covid19','COVID19','covid-19','Covid-19','COVID-19'])
# myStream.filter(track=['PPKM', 'ppkm'])


import sqlite3

conn = sqlite3.connect('streaming_tweets.db')
cur = conn.cursor()

# Create table
cur.execute('''CREATE TABLE tweets
               (tweet_id text, username text, tweet_text text, date text, hashtag text)''')

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

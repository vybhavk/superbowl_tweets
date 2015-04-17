import pandas as pd
import sqlite3
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

con = sqlite3.connect("../dbs/tweets.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
sunday_12_NYC = pd.to_datetime('2015-02-01 05:00:00',format="%Y-%m-%d %H:%M:%S")
df['hour_offset'] = (df.created_at - sunday_12_NYC)/np.timedelta64(1,'h')
print "total number of tweets: ",len(df)
df = df.loc[(df.hour_offset>18.5)&(df.hour_offset<22.)]
print "number of tweets during game: ",len(df)
df['content'] = df.content.str.lower()

#remove breaking bad and breakingbad from esurance ads, as they can skew the sentiment
df.loc[['esurance' in entry for entry in df.content],'content'] = df[['esurance' in entry for entry in df.content]].content.str.replace('breaking bad','').str.replace('breakingbad','')
sentiment = df.content.apply(lambda x: pd.Series(TextBlob(x).sentiment))
df[['polarity','subjectivity']] = sentiment

con = sqlite3.connect("../dbs/tweets_v2.db")
df.to_sql("tweets", con,  flavor='sqlite')

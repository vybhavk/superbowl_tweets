from collections import Counter
import re
import sqlite3
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

con = sqlite3.connect("../dbs/tweets.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
sunday_12_NYC = pd.to_datetime('2015-02-01 05:00:00',format="%Y-%m-%d %H:%M:%S")
df['hour_offset'] = (df.created_at - sunday_12_NYC)/np.timedelta64(1,'h')
print "total number of tweets: ",len(df)
df = df.loc[(df.hour_offset>18.5)&(df.hour_offset<22.)]
print "number of tweets during game: ",len(df)
df['content'] = df.content.str.lower()

hashtags = re.findall('#\w+',' '.join(df.content).lower())
counter = Counter(hashtags)
hashtag_arr = []
count_arr = []
KeepNum = 50
for hashtag_count in counter.most_common(KeepNum):
    hashtag_arr.append(hashtag_count[0])
    count_arr.append(hashtag_count[1])

def word_in_text(word,text):
        word = word.lower()
        text = text.lower()
        match = re.search(word,text)
        if match:
            return True
        return False

def trend_measure(df,hashtag):
    histvals = np.histogram(df[[hashtag in entry for entry in df.content]].hour_offset.values,bins=21)[0]
    return (histvals.max()-histvals.min())/np.float(histvals.max())

trend_measure_array = []
for hashtag in hashtag_arr:
    tm = trend_measure(df,hashtag)
    trend_measure_array.append(tm)

hashtag_df = pd.DataFrame({ 'hashtag' :hashtag_arr, 'tweet_count':count_arr,"trend_measure":trend_measure_array })
trending_hashtag_df = hashtag_df[hashtag_df.trend_measure>.999].sort('tweet_count',ascending=False).set_index('hashtag')
trending_hashtag_df.drop('trend_measure',axis=1).iloc[0:5].plot(kind='bar')#,figsize=(6,5))
plt.tight_layout()
plt.savefig("../png/trending.png")

#mindy refers to a nationwide insurance commercial
#superbowlrally refers to an NFL ad
#reunited refers to britney spears meeting up with Steven Tyler at the game
#spongebobmovie refers to an ad for an upcoming Spongebob movie
#missyelliott refers to her appearance during the halftime show

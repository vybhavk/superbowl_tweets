# The following script makes some exploratory plots

import pandas as pd
import sqlite3
import re
import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter
from scipy.signal import argrelextrema

con = sqlite3.connect("tweets.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
sunday_12_NYC = pd.to_datetime('2015-02-01 05:00:00',format="%Y-%m-%d %H:%M:%S")
df['hour_offset'] = (df.created_at - sunday_12_NYC)/np.timedelta64(1,'h')
df = df.loc[(df.hour_offset>18.5)&(df.hour_offset<22.)]
len(df)

def word_in_text(word,text):
        word = word.lower()
        text = text.lower()
        match = re.search(word,text)
        if match:
            return True
        return False
        
plt.figure(figsize=(8, 8))
plt.hist(df[df.content.apply(lambda x: word_in_text('touchdown',x))].hour_offset.values,bins=100,alpha=.25,label='touchdown')
plt.hist(df[df.content.apply(lambda x: word_in_text('budweiser',x))].hour_offset.values,bins=100,alpha=.25,label='budweiser')
plt.hist(df[df.content.apply(lambda x: word_in_text('snickers',x))].hour_offset.values,bins=100,alpha=.25,label='snickers')
plt.hist(df[df.content.apply(lambda x: word_in_text('fiat',x))].hour_offset.values,bins=100,alpha=.25,label='fiat')
plt.xlabel("hour")
plt.ylabel("counts")
plt.legend(loc='best')
plt.savefig("hist.png")

df['one_minute'] = np.floor(df.hour_offset*60.)
game_rate = df[df.content.apply(lambda x: word_in_text('game',x))].groupby('one_minute').size()
buy_rate = df[df.content.apply(lambda x: word_in_text('buy',x))].groupby('one_minute').size()
plt.figure(figsize=(8, 8))
plt.scatter(game_rate,buy_rate)
plt.xlabel("tweets containing 'game'")
plt.ylabel("tweets containing 'buy'")
plt.savefig("scatter.png")

touchdown_tweets = df[df.content.apply(lambda x: (word_in_text('touchdown',x)) )]
touchdown_boston = touchdown_tweets[touchdown_tweets.location.apply(lambda x: word_in_text('boston', x))]
touchdown_seattle = touchdown_tweets[touchdown_tweets.location.apply(lambda x: word_in_text('seattle', x))]
boston_touchdown_count = np.zeros(300)
seattle_touchdown_count = np.zeros(300)
for minute_count in touchdown_boston.one_minute:
    boston_touchdown_count[minute_count - 1110] +=1
for minute_count in touchdown_seattle.one_minute:
    seattle_touchdown_count[minute_count - 1110] +=1

s_td_smooth = gaussian_filter((seattle_touchdown_count - boston_touchdown_count).clip(min=0),2)
b_td_smooth = gaussian_filter((boston_touchdown_count - seattle_touchdown_count).clip(min=0),2)

def find_peaks_above_thresh(array,thresh):
    maxes = argrelextrema(array,np.greater)[0]
    return maxes[np.where(array[maxes]>thresh)[0]]

seattle_peaks = find_peaks_above_thresh(s_td_smooth,2.)
boston_peaks = find_peaks_above_thresh(b_td_smooth,2.)
print "seattle scored ",len(seattle_peaks),"touchdowns"
print "boston scored ",len(boston_peaks),"touchdowns"

plt.figure(figsize=(8, 8))
plt.plot(s_td_smooth, label = 'Seattle',color="blue")
plt.plot(b_td_smooth, label = 'Boston',color = "green")
for i in seattle_peaks:
    plt.plot((i, i), (0, 2), color='blue',linewidth=3.0)
for i in boston_peaks:
    plt.plot((i, i), (0, 2), color='green',linewidth=3.0)
plt.xlim(25,225)
plt.xlabel("minutes after kickoff")
plt.legend(loc='best')
plt.savefig("touchdowns.png")

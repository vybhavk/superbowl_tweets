import pandas as pd
import sqlite3
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob

con = sqlite3.connect("../dbs/tweets_v2.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
df['content'] = df.content.str.lower()

con = sqlite3.connect("../dbs/usatoday_ads.db")
df_ads = pd.read_sql("SELECT * from ads", con)

def get_sentiment_ratio(keyword,tmin,tmax):
    df_window = df[[tmin<time<tmax for time in df.hour_offset]]
    thresh = 0.01
    df_keyword = df_window[[keyword in entry for entry in df_window.content]]
    return TextBlob(' '.join(df_keyword.content.values)).sentiment.polarity

def get_keyword_count(keyword,tmin,tmax):
    df_window = df[[tmin<time<tmax for time in df.hour_offset]]
    df_keyword = df_window[[keyword in entry for entry in df_window.content]]
    count = df_keyword.content.count()
    return count

counts = []
for i in df_ads[['keyword','tmin','tmax']].values:
    count = get_keyword_count(i[0],i[1],i[2])
    counts.append(count)
df_ads['count'] = counts

df_ads_popular = df_ads[df_ads['count']>2000]

sentiment_ratios = []
for i in df_ads_popular[['keyword','tmin','tmax']].values:
    sentiment_ratio_value = get_sentiment_ratio(i[0],i[1],i[2])
    sentiment_ratios.append(sentiment_ratio_value)
df_ads_popular['sentiment_ratio'] = np.array(sentiment_ratios)

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
linreg = LinearRegression()
linreg.fit(np.array(pd.DataFrame(df_ads_popular['sentiment_ratio'])),df_ads_popular['rating'])
print "R2: ", linreg.score(np.array(pd.DataFrame(df_ads_popular['sentiment_ratio'])),df_ads_popular['rating'])

plt.scatter(df_ads_popular[df_ads_popular['quarter']=='First Quarter']['sentiment_ratio'],df_ads_popular[df_ads_popular['quarter']=='First Quarter']['rating'],color='b')
plt.scatter(df_ads_popular[df_ads_popular['quarter']=='Second Quarter']['sentiment_ratio'],df_ads_popular[df_ads_popular['quarter']=='Second Quarter']['rating'],color='b')
plt.scatter(df_ads_popular[df_ads_popular['quarter']=='Third Quarter']['sentiment_ratio'],df_ads_popular[df_ads_popular['quarter']=='Third Quarter']['rating'],color='b')
plt.scatter(df_ads_popular[df_ads_popular['quarter']=='Fourth Quarter']['sentiment_ratio'],df_ads_popular[df_ads_popular['quarter']=='Fourth Quarter']['rating'],color='b')
plt.scatter(df_ads_popular[df_ads_popular['quarter']=='Halftime']['sentiment_ratio'],df_ads_popular[df_ads_popular['quarter']=='Halftime']['rating'],color='b')
plt.plot(np.arange(-1.,1.,.1),np.arange(-1.,1.,.1)*linreg.coef_ + linreg.intercept_, color='k' )
plt.xlim(-.3,.5)
plt.ylim(3,9)

plt.xlabel('sentiment score')
plt.ylabel('usa today score')
plt.savefig("../png/ad_correlation.png")

from sklearn.feature_extraction import DictVectorizer as DV

vectorizer = DV( sparse = False )
period_aired = vectorizer.fit_transform( [{entry:1} for entry in df_ads_popular.quarter] )
df_period = pd.DataFrame(period_aired,index=df_ads_popular.index,columns=vectorizer.get_feature_names())
df_for_fitting = df_ads_popular.join(df_period)

X = df_for_fitting[['First Quarter','Second Quarter', 'Halftime', 'Third Quarter', 'Fourth Quarter','sentiment_ratio']]
X['interaction_1q'] = X['First Quarter']*X['sentiment_ratio']
X['interaction_2q'] = X['Second Quarter']*X['sentiment_ratio']
X['interaction_3q'] = X['Third Quarter']*X['sentiment_ratio']
X['interaction_4q'] = X['Fourth Quarter']*X['sentiment_ratio']
X['interaction_h'] = X['Halftime']*X['sentiment_ratio']
y = df_for_fitting['rating']

linreg_v2 = LinearRegression()
linreg_v2.fit(X,y)
print "R^2 including extra features: ",linreg_v2.score(X,y)

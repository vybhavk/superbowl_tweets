import pandas as pd
import sqlite3
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
import urllib2
from bs4 import BeautifulSoup

url = "http://admeter.usatoday.com/results/2015"
raw_page = urllib2.urlopen(url).read()
soup = BeautifulSoup(raw_page)
parents = soup.find_all('header',attrs={'class':'ranking_header'}) #Find (at most) *one*
parents

ad_list = []
for parent in parents:
    advertiser = parent.find('span',attrs={'class':'ranking_advertiser'}).get_text().strip().lower()
    title = parent.find('h3',attrs={'class':'ranking_title'}).get_text().strip().lower()
    rating = float(parent.find('span',attrs={'class':'ranking_average'}).get_text().strip().split()[2])
    quarter = parent.find('span',attrs={'class':'ranking_quarter'}).get_text().strip()
    ad_list.append(pd.Series({'advertiser':advertiser,'title':title,'rating':rating,'quarter':quarter}))
df_ads = pd.DataFrame(ad_list)
#get rid of always and nfl ads because they are too difficult to distinguish in tweets
df_ads = df_ads[df_ads['advertiser']!='always']
df_ads = df_ads[df_ads['advertiser']!='nfl']
df_ads['keyword'] = df_ads['advertiser']
df_ads['tmin'] = [18.5]*len(df_ads)
df_ads['tmax'] = [22.]*len(df_ads)
df_ads.ix[0,'advertiser'] = 'budweiser_1'
df_ads.ix[0,'tmin'] = 18.5
df_ads.ix[0,'tmax'] = 20.5
df_ads.ix[36,'advertiser'] = 'budweiser_2'
df_ads.ix[36,'tmin'] = 20.5
df_ads.ix[36,'tmax'] = 22.
df_ads.ix[3,'advertiser'] = 'microsoft_1'
df_ads.ix[3,'tmin'] = 18.5
df_ads.ix[3,'tmax'] = 20.5
df_ads.ix[26,'advertiser'] = 'microsoft_2'
df_ads.ix[26,'tmin'] = 20.5
df_ads.ix[26,'tmax'] = 22.
df_ads.ix[4,'advertiser'] = 'doritos_1'
df_ads.ix[4,'tmin'] = 18.5
df_ads.ix[4,'tmax'] = 20.5
df_ads.ix[10,'advertiser'] = 'doritos_2'
df_ads.ix[10,'tmin'] = 20.5
df_ads.ix[10,'tmax'] = 22.
df_ads.ix[6,'advertiser'] = 'toyota_1'
df_ads.ix[6,'tmin'] = 19.5
df_ads.ix[6,'tmax'] = 22.
df_ads.ix[21,'advertiser'] = 'toyota_2'
df_ads.ix[21,'tmin'] = 18.5
df_ads.ix[21,'tmax'] = 19.5
df_ads.ix[20,'advertiser'] = 'nationwide_1'
df_ads.ix[20,'tmin'] = 18.5
df_ads.ix[20,'tmax'] = 19.4
df_ads.ix[45,'advertiser'] = 'nationwide_2'
df_ads.ix[45,'tmin'] = 19.4
df_ads.ix[45,'tmax'] = 22.
df_ads.ix[23,'advertiser'] = 'esurance_1'
df_ads.ix[23,'tmin'] = 19.5
df_ads.ix[23,'tmax'] = 22.
df_ads.ix[46,'advertiser'] = 'esurance_2'
df_ads.ix[46,'tmin'] = 18.5
df_ads.ix[46,'tmax'] = 19.5
df_ads = df_ads.set_index('advertiser')

con = sqlite3.connect("../dbs/usatoday_ads.db")
df_ads.to_sql("ads", con,  flavor='sqlite')

con = sqlite3.connect("../dbs/usatoday_ads.db")
df_ads = pd.read_sql("SELECT * from ads", con)

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

#remove ad title
for i in df_ads.index:
    this_keyword = df_ads.loc[i].keyword
    this_title = df_ads.loc[i].title
    where_keyword = [this_keyword in entry for entry in df.content]
    df.loc[where_keyword,'content'] = df[where_keyword].content.str.replace(this_title,'')

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

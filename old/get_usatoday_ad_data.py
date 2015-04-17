import pandas as pd
import urllib2
from bs4 import BeautifulSoup
import sqlite3

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
df_ads.ix[0,'tmin'] = 20.5
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

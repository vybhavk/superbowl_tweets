import pandas as pd
import urllib2
from bs4 import BeautifulSoup
import sqlite3
import numpy as np

con = sqlite3.connect("../dbs/tweets.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
sunday_12_NYC = pd.to_datetime('2015-02-01 05:00:00',format="%Y-%m-%d %H:%M:%S")
df['hour_offset'] = (df.created_at - sunday_12_NYC)/np.timedelta64(1,'h')
print "total number of tweets: ",len(df)
df = df.loc[(df.hour_offset>18.5)&(df.hour_offset<22.)]
print "number of tweets during game: ",len(df)
df['content'] = df.content.str.lower()

url = "http://simple.wikipedia.org/wiki/List_of_U.S._states_by_population"
raw_page = urllib2.urlopen(url).read()
soup = BeautifulSoup(raw_page)
parent_table = soup.find_all('table') #Find (at most) *one*
blah = parent_table[0].find_all('tr')[1:]

state_pops = dict([(state.find('a').get_text(),int(state.find('td',attrs={'align':'right'}).get_text().replace(',',''))) for state in blah])
state_pops['DC'] = 658893

states = [
('Alabama','AL'),
('Montana','MT'),
('Alaska','AK'),
('Nebraska','NE'),
('Arizona','AZ'),
('Nevada','NV'),
('Arkansas','AR'),
('New Hampshire','NH'),
('California','CA'),
('New Jersey','NJ'),
('Colorado','CO'),
('New Mexico','NM'),
('Connecticut','CT'),
('New York','NY'),
('Delaware','DE'),
('North Carolina','NC'),
('Florida','FL'),
('North Dakota','ND'),
('Georgia','GA'),
('Ohio','OH'),
('Hawaii','HI'),
('Oklahoma','OK'),
('Idaho','ID'),
('Oregon','OR'),
('Illinois','IL'),
('Pennsylvania','PA'),
('Indiana','IN'),
('Rhode Island','RI'),
('Iowa','IA'),
('South Carolina','SC'),
('Kansas','KS'),
('South Dakota','SD'),
('Kentucky','KY'),
('Tennessee','TN'),
('Louisiana','LA'),
('Texas','TX'),
('Maine','ME'),
('Utah','UT'),
('Maryland','MD'),
('Vermont','VT'),
('Massachusetts','MA'),
('Virginia','VA'),
('Michigan','MI'),
('Washington','WA'),
('Minnesota','MN'),
('West Virginia','WV'),
('Mississippi','MS'),
('Wisconsin','WI'),
('Missouri','MO'),
('Wyoming','WY'),
('DC','DC')
]

def get_state(location):
    state =  [state[1] for state in states if state[0].lower() in location.lower() or state[1] in location]
    if state:
        return state[0]
    else:
        return False 
df['state'] = df.location.apply(get_state)

df_state = df[df.state!=False]
df_state['fiveminute'] = np.floor((df_state.hour_offset-18.5)*12)
df_state_touchdown = df_state[['touchdown' in entry for entry in df_state.content.str.lower()]]
touchdown_by_fiveminute_by_state = pd.crosstab(df_state_touchdown.fiveminute,df_state_touchdown.state)

state_dict = dict([(y,x) for x,y in states])

def set_floor(x):
    if x<6.:
        return 0
    else:
        return x

for col in touchdown_by_fiveminute_by_state:
    touchdown_by_fiveminute_by_state[col] = touchdown_by_fiveminute_by_state[col].apply(set_floor)
    touchdown_by_fiveminute_by_state[col] = 1.e6 * touchdown_by_fiveminute_by_state[col]/state_pops[state_dict[col]]

touchdown_by_fiveminute_by_state.to_csv(path_or_buf='../data/touchdown_fivemin_state.tsv',sep='\t')


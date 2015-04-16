import numpy as np
import pandas as pd
import json
import sqlite3
import re
import matplotlib.pyplot as plt

def nvd3_array(df,colnames,colors):
    output = []
    for j in np.arange(len(colnames)):#name in colnames:
        values = []
        for i in df.index:
            values.append({'x':df['time'][i],'y':df[colnames[j]][i]})
        output.append({
        'key':colnames[j],
        'color':colors[j],
        'values':values
    })
    return output

con = sqlite3.connect("../dbs/tweets.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
sunday_12_NYC = pd.to_datetime('2015-02-01 05:00:00',format="%Y-%m-%d %H:%M:%S")
df['hour_offset'] = ((df.created_at - sunday_12_NYC)/np.timedelta64(1,'h')-18.5)*60.
df = df.loc[(df.hour_offset>0.)&(df.hour_offset<210.)]

microsoft_hist = plt.hist(df[['microsoft' in entry for entry in df.content.str.lower()]].hour_offset.values,range=(0.,210),bins=105,alpha=.25,label='touchdown')
budweiser_hist = plt.hist(df[['budweiser' in entry for entry in df.content.str.lower()]].hour_offset.values,range=(0.,210),bins=105,alpha=.25,label='budweiser')
doritos_hist = plt.hist(df[['doritos' in entry for entry in df.content.str.lower()]].hour_offset.values,range=(0.,210),bins=105,alpha=.25,label='snickers')
fiat_hist = plt.hist(df[['fiat' in entry for entry in df.content.str.lower()]].hour_offset.values,range=(0.,210),bins=105,alpha=.25,label='fiat')
 
df_hist = pd.DataFrame({'time' : microsoft_hist[1][1:],
                    'microsoft' : microsoft_hist[0]/2,
                    'budweiser' : budweiser_hist[0]/2,
                    'doritos' : doritos_hist[0]/2,
                    'fiat' : fiat_hist[0]/2 
                    })

with open('../data/hist_data.json', 'w') as outfile:
    json.dump(nvd3_array(df_hist,['microsoft','budweiser','doritos','fiat'],['red','blue','green','magenta']), outfile)

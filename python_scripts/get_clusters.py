import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans,DBSCAN
import seaborn as sns
import nltk

con = sqlite3.connect("../dbs/tweets_v2.db")
df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
df['content'] = df.content.str.lower()
df['content'] = df.content.apply(lambda x: x.replace('katy perry','katyperry'))
df['content'] = df.content.apply(lambda x: x.replace('missy elliot','missyelliot'))
df['content'] = df.content.apply(lambda x: x.replace('missy elliott','missyelliot'))
df['content'] = df.content.apply(lambda x: x.replace('super bowl','superbowl'))
df['content'] = df.content.apply(lambda x: x.replace('half time show','halftimeshow'))
df['content'] = df.content.apply(lambda x: x.replace('half time','halftime'))
df['content'] = df.content.apply(lambda x: x.replace('new england','newengland'))
df['content'] = df.content.apply(lambda x: x.replace('commercials','commercial'))
df['content'] = df.content.apply(lambda x: x.replace('watching','watch'))

#Find the Score

df['second'] = np.floor((df.hour_offset - 18.5)*60*60)
df_td = df[[('touchdown' in entry or 'touch down' in entry) and not ('fieldgoal' in entry or 'field goal' in entry) for entry in df.content]]
df_td = df_td[[('boston' in entry or 'newengland' in entry or 'patriots' in entry or 'seattle' in entry or 'seahawks' in entry) for entry in df_td.content]]
df_td = df_td[[not(('boston' in entry or 'newengland' in entry or 'patriots' in entry) and ('seattle' in entry or 'seahawks' in entry)) for entry in df_td.content]]
df_td['fan'] = [0.0]*len(df_td)
df_td.loc[[('boston' in entry or 'newengland' in entry or 'patriots' in entry) and 'seattle' not in entry and 'seahawks' not in entry for entry in df_td.content],'fan'] = 10000.
df_td.loc[[('seattle' in entry or 'seahawks' in entry ) and 'patriots' not in entry and 'newengland' not in entry and 'boston' not in entry for entry in df_td.content],'fan'] = -10000.

df_fg = df[[('fieldgoal' in entry or 'field goal' in entry) and not ('touchdown' in entry or 'touch down' in entry) for entry in df.content]]
df_fg = df_fg[[('boston' in entry or 'newengland' in entry or 'patriots' in entry or 'seattle' in entry or 'seahawks' in entry) for entry in df_fg.content]]
df_fg = df_fg[[not(('boston' in entry or 'newengland' in entry or 'patriots' in entry) and ('seattle' in entry or 'seahawks' in entry)) for entry in df_fg.content]]
df_fg['fan'] = [0.0]*len(df_fg)
df_fg.loc[[('boston' in entry or 'newengland' in entry or 'patriots' in entry) and 'seattle' not in entry and 'seahawks' not in entry for entry in df_fg.content],'fan'] = 10000.
df_fg.loc[[('seattle' in entry or 'seahawks' in entry ) and 'patriots' not in entry and 'newengland' not in entry and 'boston' not in entry for entry in df_fg.content],'fan'] = -10000.

X_td = df_td[['second','fan']]
X_fg = df_fg[['second','fan']]

db_td = DBSCAN(eps=360, min_samples=300)
db_fg = DBSCAN(eps=360, min_samples=50)

X_td = X_td.values
X_fg = X_fg.values

db_td.fit(X_td)
db_fg.fit(X_fg)


core_samples_mask = np.zeros_like(db_td.labels_, dtype=bool)
core_samples_mask[db_td.core_sample_indices_] = True
labels = db_td.labels_

# Number of clusters in labels, ignoring noise if present.
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
unique_labels = set(labels)
colors = ['red','blue','green','magenta']
b_index = 0
s_index = 0
td_time_actual = [40.53,60.4,75.02,85.47,141.65,174.33,194.27]
fig, ax = plt.subplots(1)
td_time_calc = []
td_time_delay = []
td_fan = []
for k in unique_labels:
    if k != -1:
        
        class_member_mask = (labels == k)

        xy = X_td[class_member_mask & core_samples_mask]
        cluster_fan = int(np.median(xy[:,1])/10000)
        cluster_num = len(xy)
        td_time_calc.append(np.percentile(xy[:,0],5)/60.)
        td_time_delay.append(np.percentile(xy[:,0],5)/60. - td_time_actual[k])
        #print np.median(xy[:,0])/60.,np.percentile(xy[:,0],5)/60.,td_actual[k],np.percentile(xy[:,0],5)/60.-td_actual[k], cluster_fan, cluster_num
        if cluster_fan==1:
            color = colors[b_index]
            plt.hist(xy[:,0]/60.,alpha=0.2,color=color)
            b_index +=1
            td_fan.append('Boston')
        else:
            if cluster_fan==-1:
                color = colors[s_index]
                plt.hist(xy[:,0]/60.,alpha=1.0,color=color)
                s_index +=1
                td_fan.append('Seattle')

        plt.plot([td_time_actual[k],td_time_actual[k]],[0,10000],color='yellow')
        

#blue_patch = mpatches.Patch(label='Patriots')
#green_patch = mpatches.Patch(label='Seahawks')

#plt.legend(handles=[green_patch,blue_patch])
plt.xlabel('minutes since kickoff')
plt.title('"touchdown" tweets')
# these are matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='white', alpha=0.5)

# place a text box in upper left in axes coords
ax.text(0.05, 0.95, 'dark colors: Seahawks\nlight colors: Patriots', transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)
plt.ylim(0,1500)
plt.savefig("../png/td_cluster_hist.png")

core_samples_mask = np.zeros_like(db_fg.labels_, dtype=bool)
core_samples_mask[db_fg.core_sample_indices_] = True
labels = db_fg.labels_

n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
unique_labels = set(labels)
colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

fg_time_actual = [125.83]
fg_time_calc = []
fg_time_delay = []
fg_fan = []
fig, ax = plt.subplots(1)
for k in unique_labels:
    if k != -1:
        
        class_member_mask = (labels == k)

        xy = X_fg[class_member_mask & core_samples_mask]
        cluster_fan = int(np.median(xy[:,1])/10000)
        cluster_num = len(xy)
        fg_time_calc.append(np.percentile(xy[:,0],5)/60.)
        fg_time_delay.append(np.percentile(xy[:,0],5)/60. - fg_time_actual[k])
        if cluster_fan==1:
            color = 'blue'
            plt.hist(xy[:,0]/60.,alpha=0.2,range=(0,250),bins=250,color=color)
            fg_fan.append('Boston')
        else:
            if cluster_fan==-1:
                color = 'green'
                plt.hist(xy[:,0]/60.,alpha=1.0,range=(0,250),bins=250,color=color)
                fg_fan.append('Seattle')

        #print np.median(xy[:,0])/60.,np.percentile(xy[:,0],25)/60.,  cluster_fan, cluster_num
        plt.plot([fg_time_actual[k],fg_time_actual[k]],[0,10000],color='yellow')

 # these are matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='white', alpha=0.5)

# place a text box in upper left in axes coords
ax.text(0.05, 0.95, 'dark colors: Seahawks\nlight colors: Patriots', transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=props)
       
#plt.legend(handles=[green_patch,blue_patch])
plt.xlabel('minutes since kickoff')
plt.title('"field goal" tweets')
plt.ylim(0,80)
plt.savefig("../png/fg_cluster_hist.png")

td_measurements = pd.DataFrame({'calculated time':td_time_calc,'actual time':td_time_actual,'team':td_fan,'time delay':td_time_delay})
fg_measurements = pd.DataFrame({'calculated time':fg_time_calc,'actual time':fg_time_actual,'team':fg_fan,'time delay':fg_time_delay})

print td_measurements.to_html()
print fg_measurements.to_html()

vectorizer = TfidfVectorizer(max_features=10,
                             stop_words=nltk.corpus.stopwords.words('english') + ['superbowl','sb49','http','rt','co'])
X = vectorizer.fit_transform(df.content)
vectorizer.get_feature_names()

# Do the actual clustering
true_k = 4
km = KMeans(n_clusters=true_k, init='k-means++', max_iter=1000, n_init=1,verbose=False,random_state=50)

print("Clustering sparse data with %s" % km)
km.fit(X)

print()

print("Top terms per cluster:")
order_centroids = km.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
terms.append('time')
for i in range(true_k):
    print("Cluster %d:" % i)#, end='')
    for ind in order_centroids[i, :15]:
        print(' %s' % terms[ind],km.cluster_centers_[i,ind])#, end='')
    print()

for i in [0,2,3]:
    label = ', '.join([terms[j] for j in order_centroids[i,:] if km.cluster_centers_[i,j]>.15])
    plt.hist((df[km.predict(X)==i].hour_offset.values-18.5)*60,bins=105,alpha=0.5,label=label)#terms[order_centroids[i, 0]])
plt.legend()
plt.xlabel('minutes since kickoff')
plt.savefig("../png/cluster_hist.png")

basis_vectors = np.array([center / np.linalg.norm(center) for center in km.cluster_centers_])
projected = basis_vectors.dot(X.toarray().transpose())

from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(8,6))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(projected[0,km.predict(X)==0],projected[1,km.predict(X)==0],projected[3,km.predict(X)==0],color='red',marker='.',s=20,depthshade=False,label='seahawks/patriots')
ax.scatter(projected[0,km.predict(X)==1],projected[1,km.predict(X)==1],projected[3,km.predict(X)==1],color='blue',marker='.',s=20,depthshade=False,label='commercials')
ax.scatter(projected[0,km.predict(X)==3],projected[1,km.predict(X)==3],projected[3,km.predict(X)==3],color='green',marker='.',s=20,depthshade=False,label='katyperry/halftime')

ax.view_init(35, 55)
ax.set_xlim(0,1.)
ax.set_ylim(0,1.)
ax.set_zlim(0,1.)
ax.set_xlabel('half time show')
ax.set_ylabel('seahawks/patriots')
ax.set_zlabel('commercials')
plt.legend()
plt.savefig("../png/cluster_3d.png")

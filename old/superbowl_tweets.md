

    import pandas as pd
    import sqlite3
    import re
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.ndimage.filters import gaussian_filter
    from scipy.signal import argrelextrema

I have downloaded tweets using the Twitter Streaming API, and stored them tweets
in a database. I used a filter so that I only capture tweets containing the word
"superbowl". Fortunately, pandas makes it incredibly easy to load the data and
start playing with it using one simple query. I add one new column named
'hour_offset' which is simply the number of hours which have elapsed since
midnight in New York. This is done to make histogramming easier. I also restrict
the database to tweets that occured during the game itself. After doing this, I
am left with about 1.5 million tweets.


    con = sqlite3.connect("tweets.db")
    df = pd.read_sql("SELECT * from tweets", con, parse_dates=['created_at'])
    sunday_12_NYC = pd.to_datetime('2015-02-01 05:00:00',format="%Y-%m-%d %H:%M:%S")
    df['hour_offset'] = (df.created_at - sunday_12_NYC)/np.timedelta64(1,'h')
    df = df.loc[(df.hour_offset>18.5)&(df.hour_offset<22.)]
    len(df)




    1498142



Now, I plot histograms of the occurence of various words in tweets by time. We
can easily pick out the occurance of each of the 7 touchdowns by eye, as well as
the spikes caused by commercials. I have chosen to show tweets containing
"budweiser", "snickers", and "fiat" as examples. We can also see the gap
corresponding to the half-time show. This highlights the importance of ads in
the superbowl. It indicates that by some measures, commercials can capture more
attention of viewers than some touchdowns. The budweiser commercial seems to
have been particularly engaging for people.


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
    legend(loc='best')
    plt.savefig("hist.png")
    plt.show()


![png](superbowl_tweets_files/superbowl_tweets_4_0.png)


One can think about how peoples priorities can vary over the course of the game.
In particular, I want to compare people's interest in "buying things" vs. their
interest in the game. I plot the counts in each minute bin for tweets containing
the word "buy" vs counts for the word "game". If they maintened a constant level
of interest in each, you would expect to see one cluster only. Instead, you also
see two distinct branches toward both the "buy" axis and the "game" axis. This
shows that the context of what is happening can shift people's priorities to
either buying the things, or paying attention to the game itself. This is
expected, as people's attention is forced to switch between game play and
commercial breaks, but a closer analysis may reveal other interesting
influential factors, such as the score, minutes remaining in quarter, which down
is being played, etc. I leave these questions for a future analysis.


    df['one_minute'] = np.floor(df.hour_offset*60.)
    game_rate = df[df.content.apply(lambda x: word_in_text('game',x))].groupby('one_minute').size()
    buy_rate = df[df.content.apply(lambda x: word_in_text('buy',x))].groupby('one_minute').size()
    plt.figure(figsize=(8, 8))
    plt.scatter(game_rate,buy_rate)
    plt.xlabel("tweets containing 'game'")
    plt.ylabel("tweets containing 'buy'")
    plt.savefig("scatter.png")
    plt.show()


![png](superbowl_tweets_files/superbowl_tweets_6_0.png)


Just for fun, let's see if we can infer the number of touchdowns scored by each
team, just based on twitter data. We select out tweets by people who identify
themselves as living in either Boston or Seattle and count the number of times
they tweet the word "touchdown" each minute. In each minute bin, we take the
count difference for each group and set a floor on the result at 0. This
accounts for the fact that some people also tweet "touchdown" when the opposing
team scores, and we don't want to be confused by this. We then use a gaussian
filter to smooth these curves, and count the number of local maxima above a
given threshold. Lo and behold, we get the correct number of touchdowns for each
team.


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
    legend(loc='best')
    plt.savefig("touchdowns.png")
    plt.show()

    seattle scored  3 touchdowns
    boston scored  4 touchdowns



![png](superbowl_tweets_files/superbowl_tweets_8_1.png)


Let's see if we can find "trending" hashtags from the data itself. We are most
interested in topics which see a sharp rise in tweet counts. We find the 50 most
popular hashtags, then we count the frequency of each hashtag in ten minute
intervals. We then consider topics for which the count frequency is very close
to zero for at least one time interval. This is very useful because it can alert
us to bursts of interest that we would not have otherwise been aware of.


    from collections import Counter
    hashtags = re.findall('#\w+',' '.join(df.content).lower())
    counter = Counter(hashtags)
    hashtag_arr = []
    count_arr = []
    KeepNum = 50
    for hashtag_count in counter.most_common(KeepNum):
        hashtag_arr.append(hashtag_count[0])
        count_arr.append(hashtag_count[1])


    def trend_measure(df,hashtag):
        histvals = np.histogram(df[df.content.apply(lambda x: word_in_text(hashtag,x))].hour_offset.values,bins=21)[0]
        return (histvals.max()-histvals.min())/np.float(histvals.max())
    
    trend_measure_array = []
    for hashtag in hashtag_arr:
        #hashtag = hashtag_count[0]
        tm = trend_measure(df,hashtag)
        trend_measure_array.append(tm)


    hashtag_df = pd.DataFrame({ 'hashtag' :hashtag_arr, 'tweet_count':count_arr,"trend_measure":trend_measure_array })
    trending_hashtag_df = hashtag_df[df2.trend_measure>.999].sort('tweet_count',ascending=False).set_index('hashtag')
    trending_hashtag_df.drop('trend_measure',axis=1).iloc[0:5].plot(kind='bar',figsize=(8,8))




    <matplotlib.axes._subplots.AxesSubplot at 0x1e34f0650>




![png](superbowl_tweets_files/superbowl_tweets_12_1.png)


- \#invisiblemindy refers to a nationwide insurance commercial
- \#superbowlrally refers to an NFL ad
- \#reunited refers to britney spears meeting up with Steven Tyler at the game
- \#spongebobmovie refers to an ad for an upcoming Spongebob movie
- \#missyelliott refers to her appearance during the halftime show


    

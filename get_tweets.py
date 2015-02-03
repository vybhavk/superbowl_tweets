# The Following Script will download the twitter stream
# and store it in a SQLite database which has already been created 
import tweepy

# database interface
import sqlite3
conn = sqlite3.connect('tweets.db')
curs = conn.cursor()
 
class StreamWatcherHandler(tweepy.StreamListener):
    """ Handles all incoming tweets as discrete tweet objects.
    """
 
    def on_status(self, status):
        """Called when status (tweet) object received.
        """
        try:
            tid = status.id_str
            usr = status.author.screen_name.strip()
            lang = status.lang.strip()
            txt = status.text.strip()
            location = status.user.location.strip()
            src = status.source.strip()
            cat = status.created_at
 
            # Now that we have our tweet information, let's stow it away in our 
            # sqlite database
            curs.execute("insert into tweets (tid, username, created_at, lang, content, location, source) values(?, ?, ?, ?, ?, ?, ?)",
                          (tid, usr, cat, lang, txt, location, src))
            conn.commit()
        except Exception as e:
            # Most errors we're going to see relate to the handling of UTF-8 messages (sorry)
            print(e)
 
    def on_error(self, status_code):
       print('An error has occured! Status code = %s' % status_code)
       return True
 
def main():
    # establish stream
    consumer_key = 'NZXsujOR8eHwTzYJFYDbf3P1Q'
    consumer_secret ='DzrtX5Dmp9Z0WFD4gsQV5ER5RWgkD2ALwumG77tyvIjOMusgnp'
    access_token = '175184025-o5n3pfUTGihIU5b549HmGyOEo3MHLlG4mWgjQx1o'
    access_token_secret = 'zpJEOQPZLPgcUTLkwaKIOBe3cYW2R7C7UFlyiqOBrWsHG'

    auth1 = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
    auth1.set_access_token(access_token, access_token_secret)
 
    def start_stream():
    	while True:
        	try:
            		print "Establishing stream...",
            		stream = tweepy.Stream(auth1, StreamWatcherHandler(), timeout=None)
            		print "Done"
            		keywords = ['superbowl']
			stream.filter(track=keywords,languages=["en"])
        	except: 
            		continue
    start_stream()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Disconnecting from database... ",
        conn.commit()
        conn.close()
        print "Done"

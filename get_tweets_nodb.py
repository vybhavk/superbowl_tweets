# twitter client
import tweepy

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
	    
	    sep = ',,sep,,'
	    print tid, sep, usr, sep, lang, sep, txt, sep, location, sep, src, sep, cat
 
        except Exception as e:
            # Most errors we're going to see relate to the handling of UTF-8 messages (sorry)
            print(e)
 
    def on_error(self, status_code):
       print('An error has occured! Status code = %s' % status_code)
       return True
 
def main():
    # establish stream
    consumer_key = '38Wa8qLF8ZdVFjvbeJ4trOADX'
    consumer_secret ='mCJS44ZvTmSfw0fnUHQOLscjYkJMXn1bRig6PK7CcHZIb4ZdjO'
    access_token = '175184025-lIvJcE1mEzDC4cwFzidl0dJadTl4ePoKL0HRcjxd'
    access_token_secret = 'LTVgd6OTabVynjkaBhLDMmCHqyqJ9WzU1h6ra6trYwde9'

    auth1 = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
 
    #access_token = "ACCESS_TOKEN"
    #access_token_secret = "ACCESS_TOKEN_SECRET"
    auth1.set_access_token(access_token, access_token_secret)
 
    #print "Establishing stream...",
    #stream = tweepy.Stream(auth1, StreamWatcherHandler(), timeout=None)
    #print "Done"
 
    # Start pulling our sample streaming API from Twitter to be handled by StreamWatcherHandler
    #stream.sample()

    #keywords = ['super','bowl','superbowl','superbowlXLIX','XLIX','katy','perry','sunday','superbowlsunday','boston','patriots','newengland','new england','seattle','seahawks','commercial','commercials','ads','ad','fast furious','kardashian','superbowlcommercials','nfl','carls','deflategate','ballghazi','pizza','wings','beer','avocado','guacamole','mcdonalds','bmw','kia','Priceline','Snickers','SquareSpace','Toyota','T Mobile','nachos','touchdown','football']

    #stream.filter(track=keywords,languages=["en"])

    def start_stream():
    	while True:

        	try:
            		print "Establishing stream...",
            		stream = tweepy.Stream(auth1, StreamWatcherHandler(), timeout=None)
            		print "Done"
            		#keywords = ['super','bowl','superbowl','superbowlXLIX','XLIX','katy','perry','sunday','superbowlsunday','boston','patriots','newengland','new england','seattle','seahawks','commercial','commercials','ads','ad','fast furious','kardashian','superbowlcommercials','nfl','carls','deflategate','ballghazi','pizza','wings','beer','avocado','guacamole','mcdonalds','bmw','kia','Priceline','Snickers','SquareSpace','Toyota','T Mobile','nachos','sb49']
            		keywords = ['superbowl']
			stream.filter(track=keywords,languages=["en"])
            
            		#sapi = tweepy.streaming.Stream(auth, CustomStreamListener(api))
            		#sapi.filter(track=["Samsung", "s4", "s5", "note" "3", "HTC", "Sony", "Xperia", "Blackberry", "q5", "q10", "z10", "Nokia", "Lumia", "Nexus", "LG", "Huawei", "Motorola"])
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

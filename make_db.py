# The Following script creates the database where we will store tweets
import sqlite3
conn = sqlite3.connect('tweets.db')
curs = conn.cursor()
curs.execute("CREATE TABLE tweets (tid integer, username text, created_at text, lang txt, content text, location text, source text)")


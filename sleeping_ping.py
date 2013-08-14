from time import time, sleep
from SQL_Alchemy import *
import feedparser

#function that pings all urls in db at a certain time interval
# query Feed db table for all feed_urls
# go out to feed_urls and look for new content

feed_info = Feed.query.all()
posts = Feed()
print "FEED_INFO", feed_info

# while there are feeds in the DB
# can also just say while True
while feed_info is not None:
	# loop over all the feed objects saved in the Feed table
	for feed_object in feed_info:			
		# check for set of post titles in the DB based on that specific feed_id
		post_set = feed_object.check_posts()
		print "POST SET", post_set
		#retrieve parsed feed info based on the feed_link
		feed_data = feedparser.parse(feed_object.feed_link)

		# compared post_titles to determine if there are new posts 
		if feed_data.entries[0].title not in post_set:
			print "ENTRY TITLE", feed_data.entries[0].title
			for entry in feed_data.entries:
				# insert new posts into post table as appropriate based on comparison
				if entry.title not in post_set:
					post = make_post(entry, feed_object.feed_id)
					session.add(post)
				else: 
					break
		# set a certain time to elapse		
		session.commit()
		print "WHILE LOOP HAS RUN"
	sleep(30)

		


from time import time, sleep, strptime, strftime, mktime
from SQL_Alchemy_LXML import *
from lxml import etree
import urllib2
from dateutil import parser as du_parser

#function that pings all urls in db at a certain time interval
# query Feed db table for all feed_urls
# go out to feed_urls and look for new content
# import pdb; pdb.set_trace()

feed_info = Feed.query.all()

# while there are feeds in the DB
# can also just say while True
while feed_info is not None:
	# loop over all the feed objects saved in the Feed table
	for feed_object in feed_info:			

		# check for set of post titles in the DB based on that specific feed_id
		post_set = feed_object.check_posts()
		
		#retrieve parsed feed info based on the feed_link
		feed_data = etree.parse(feed_object.feed_link)

		# compared post_titles to determine if there are new posts 
		for each_item in feed_data.xpath(".//item"):
			# insert new posts into post table as appropriate based on comparison
			# each_item is only the title so trying to access additional info is not possible
			if each_item.find(".//title").text not in post_set:
			
				# for element in use_this_to_populate:
				# using xpath returns a list even if its only a single element within the list
				# this is why you need the [0] or replace .xpath() with .find()
				title = each_item.xpath(".//title/text()")[0]
				# add author with ratchet meow trixieness
				content = each_item.xpath(".//description/text()")[0]
				timestamp = str(each_item.xpath(".//pubDate/text()")[0])
				datetime_timestamp = du_parser.parse(timestamp)
				no_UTC = datetime_timestamp.replace(tzinfo=None) 

				post = Post(feed_id=feed_object.feed_id, title = title,  content = content, timestamp = no_UTC)
				session.add(post)

			else: 
				break
		# set a certain time to elapse		
		session.commit()
		print "WHILE LOOP HAS RUN"
	sleep(30)

		


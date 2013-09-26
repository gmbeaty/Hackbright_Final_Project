from SQL_Alchemy_LXML import *
from lxml import etree
import urllib2
from dateutil import parser as du_parser

#function that pings all urls in db at a certain time interval
# query Feed db table for all feed_urls
# go out to feed_urls and look for new content
# import pdb; pdb.set_trace()

def create_post(item, feed):
    post = Post(feed_id=feed.feed_id)

    post.title = item.xpath(".//title/text()")[0]
    creators = item.xpath(".//creator/text()")
    if creators:
        post.author = unicode(creators[0])

    post.content = item.xpath(".//description/text()")[0]

    timestamp = str(item.xpath(".//pubDate/text()")[0])
    post.timestamp = du_parser.parse(timestamp).replace(tzinfo=None)

    post.url = str(item.xpath(".//link/text()")[0])

    return post

def main():
    feed_info = Feed.query.all()

    # while there are feeds in the DB
    # can also just say while True
    while feed_info is not None:
        # loop over all the feed objects saved in the Feed table
        for feed_object in feed_info:

            # check for set of post titles in the DB based on that specific feed_id
            post_set = feed_object.check_posts()

            #retrieve parsed feed info based on the feed_link
            just_link = feed_object.feed_link

            feed_data = etree.parse(just_link)
            feed_data_test = feed_data.xpath(".//channel")

            # compared post_titles to determine if there are new posts
            if feed_data_test != []:
                contents = urllib2.urlopen(just_link).read().replace('dc:','')
                post_str = etree.fromstring(contents)
                all_posts = post_str.xpath(".//channel/item")

                for each_item in all_posts:
                    # insert new posts into post table as appropriate based on comparison
                    if each_item.find(".//title").text not in post_set:
                        _post = create_post(each_item, feed_object)
                        session.add(create_post(each_item, feed_object))
                    else:
                        break

                session.commit()
                print "WHILE LOOP HAS RUN"


            else:
                post_str = str(just_link)
                post_data_tree = lxml.html.parse(post_str)
                all_entries = post_data_tree.xpath(".//entry")

                for each_entry in all_entries:
                    # insert new posts into post table as appropriate based on comparison
                    if each_entry.find(".//title").text not in post_set:

                        # using xpath returns a list even if its only a single element within the list
                        # this is why you need the [0] or replace .xpath() with .find()
                        if each_entry.xpath(".//title/text()") != []:
                            title = unicode(each_entry.xpath(".//title/text()")[0])

                        if each_entry.xpath(".//creator/text()") != []:
                            author = unicode(each_entry.xpath(".//creator/text()")[0])

                        content = each_entry.xpath(".//content/text()")[0]
                        timestamp = str(each_entry.xpath(".//published/text()")[0])
                        datetime_timestamp = du_parser.parse(timestamp)
                        pub_Date = datetime_timestamp.replace(tzinfo=None)

                        _url = str(each_entry.xpath("//link[@rel='alternate']/@href")[0])

                        try:
                            _post = Post(feed_id=feed_object.feed_id, title = title,  author = author, content = content, timestamp = pub_Date, url = _url)

                        except:
                            _post = Post(feed_id=feed_object.feed_id, title = title, content = content, timestamp = pub_Date, url = _url)

                        session.add(_post)

                    else:
                        break

                session.commit()
                print "WHILE LOOP HAS RUN"

        yield

if __name__ == '__main__':
    import time

    for _ in main():
        time.sleep(90)

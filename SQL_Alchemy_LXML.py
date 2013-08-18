from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from sqlalchemy import ForeignKey
from lxml import etree
import lxml.html
import urllib2
import datetime 
from time import strptime, strftime
from dateutil import parser as du_parser

engine = create_engine("sqlite:///rss.db", echo=True)
session = scoped_session(sessionmaker(bind=engine,autocommit=False,autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

# Convert datetime into the format to use in the database, for example:
# 2013-02-09 14:06:33

def published_parsed_to_db_format(string):
    d = string.split(" +")[0]
    print "THIS IS THE DATE", d
    # make_int = int(strptime(d, '%a, %d %b %Y %H:%M:%S'))
    #two equivalent ways to format it:
    #dStr = d.isoformat(' ')
    #or
    # Sun, 28 Jul 2013 02:54:44 +0000
    # return d.strftime('%a, %d %b %Y %H:%M:%S')
    return strptime(d, '%a, %d %b %Y %H:%M:%S')

# def make_post(post, feed_id=None):
#     timestamp = published_parsed_to_db_format(str(post.xpath(".//pubDate/text()")[0]))
#     kwargs = {
#         "title" : unicode(post.xpath(".//title/text()")[0]),
#         "content" : unicode(post.xpath(".//description/text()")[0]),
#         "timestamp" : timestamp
#         }

#     if hasattr(entry, "author"):
#         kwargs["author"] = unicode(post.xpath(".//creator/text()")[0])

#     if feed_id is not None:
#         kwargs["feed_id"] = feed_id

#     return Post(**kwargs)

### Class declarations go here

class User(Base):
    print "User table is running"
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key = True)
    user_name = Column(String(64), nullable = True)
    email = Column(String(64), nullable = True)
    password = Column(String(64), nullable = True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id 

    feeds = relationship("User_Feed", backref=backref("users", order_by=user_id), uselist=True)

class User_Feed(Base):
    print "User/Feeds FTW"
    __tablename__ = "user_feeds"

    user_feed_id = Column(Integer, primary_key = True)
    feed_id = Column(Integer, ForeignKey("feeds.feed_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    last_post_read_id = Column(Integer, nullable = True)

    user_feed = relationship("Feed", backref=backref("user_feeds", order_by=user_feed_id))

class Feed(Base):
    print "Feed - is a go!"
    __tablename__ = "feeds"

    feed_id = Column(Integer, primary_key = True)
    feed_title = Column(String(64), nullable = True)
    feed_subtitle = Column(String(512), nullable = True)
    feed_link = Column(String(128), nullable=True)

    def populate_metadata(self):
        data = self.feed_link
        # import pdb; pdb.set_trace()
        # read_data = urllib2.urlopen(data).read()

        # USE THIS ROUTE FOR RSS
        try:
            data_tree = etree.parse(data)
            self.feed_title = str(data_tree.xpath(".//channel/title/text()")[0])
            self.feed_subtitle = str(data_tree.xpath(".//channel/description/text()")[0])


        # USE THIS ROUTE FOR ATOM FEEDS
        except:
            str_data = str(data)
            data_tree = lxml.html.parse(str_data)
            self.feed_title = str(data_tree.xpath(".//feed/title/text()")[0])
            self.feed_subtitle = str(data_tree.xpath(".//feed/subtitle/text()")[0])

    def get_current_posts(self):
        post_link = self.feed_link
        post_tree = etree.parse(post_link)
        post_title_test = post_tree.xpath(".//channel")
        # import pdb; pdb.set_trace()

        # USE THIS ROUTE FOR RSS
        # ratchet meow
        if post_title_test != []:
            contents = urllib2.urlopen(post_link).read().replace('dc:','')
            post_str = etree.fromstring(contents)
            all_posts = post_str.xpath(".//channel/item") 

            for post in all_posts:
                _title = unicode(post.xpath(".//title/text()")[0])
                _author = unicode(post.xpath(".//creator/text()")[0])
                _description = unicode(post.xpath(".//description/text()")[0])
                timestamp = str(post.xpath(".//pubDate/text()")[0])
                datetime_timestamp = du_parser.parse(timestamp)
                _pubDate = datetime_timestamp.replace(tzinfo=None) 
                _url = str(post.xpath(".//link/text()")[0])

                _post = Post(title = _title, author = _author, content = _description, timestamp = _pubDate, url = _url)

                self.posts.append(_post)

            # Add this in later     
            # single_post = make_post(post)
            # p_img = Post(title = post.image.url)
            # self.posts.image.append(p_img) 
            
            # p_url = Post(url = post.description.link)
            # self.posts.append(p_url)

        # END RSS USECASE BLOCK
        #START ATOM USE CASE BLOCK
        else:
            post_str = str(post_link)
            post_data_tree = lxml.html.parse(post_str) 
            all_entries = post_data_tree.xpath(".//entry")
            # import pdb; pdb.set_trace()

            for entry in all_entries:
                print "<<<SINGLE ENTRY>>>", entry
                print type(entry)
                # blogger blogs are not playing nice with this xpath call
                # list index error is happening
                _title = unicode(entry.xpath(".//title/text()")[0])
                # print "YUNOTITLING", _title
                _author = unicode(entry.xpath(".//author/name/text()")[0])
                # print "ZEEEEE AUTHOR", _author
                _description = unicode(entry.xpath(".//content/text()")[0])
                # print "THE POST SAYS THIS", _description
                timestamp = str(entry.xpath(".//published/text()")[0])
                datetime_timestamp = du_parser.parse(timestamp)
                _pubDate = datetime_timestamp.replace(tzinfo=None) 
                _url = str(entry.xpath("//link[@rel='alternate']/@href")[0])

                _post = Post(title = _title, author = _author, content = _description, timestamp = _pubDate, url=_url)

                self.posts.append(_post)

        # END ATOM BLOCK

        return self.posts
       
    def check_posts(self):
        # feed_posts = self.posts
        # print feed_posts
        # print "DA TYPE", type(feed_posts)

        # post_title = self.feed_title
        # the above returns the title of the blog (ie. "What's new for Terry Tao")
        all_posts = self.posts

        post_title_list = []
        for post in all_posts:
            post_title = post.title
            post_title_list.append(post_title)

        # print "POST TITLE", post_title_list
        # most_recent_post = post_title_list[0]
        # print "LAST POST", most_recent_post

        return set(post_title_list)

class Post(Base):
    print "All zee posts"
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key = True)
    feed_id = Column(Integer, ForeignKey("feeds.feed_id"))
    title = Column(String(256), nullable = True)
    author = Column(String(64), nullable = True)
    content = Column(String(1024), nullable = True)
    image = Column(String(256), nullable = True)
    url = Column(String(128), nullable = True)
    timestamp = Column(Integer, nullable = True)

    feed = relationship("Feed", backref=backref("posts", order_by=post_id))

### End class declarations

def main():
    pass

if __name__ == "__main__":
    main()
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey
from lxml import etree
import lxml.html
import urllib2
import datetime
from time import strptime, strftime
from dateutil import parser as du_parser

Base = declarative_base()

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

        # USE THIS ROUTE FOR RSS
        try:
            data_tree = etree.parse(data)
            self.feed_title = str(data_tree.xpath(".//channel/title/text()")[0])
            self.feed_subtitle = str(data_tree.xpath(".//channel/description/text()")[0])


        # USE THIS ROUTE FOR ATOM FEEDS
        except:
            str_data = str(data)
            data_tree = lxml.html.parse(str_data)
            if data_tree.xpath(".//feed/title/text()") != []:
                self.feed_title = str(data_tree.xpath(".//feed/title/text()")[0])
            if data_tree.xpath(".//feed/subtitle/text()") != []:
                self.feed_subtitle = str(data_tree.xpath(".//feed/subtitle/text()")[0])

    def get_current_posts(self):
        post_link = self.feed_link
        post_tree = etree.parse(post_link)
        post_title_test = post_tree.xpath(".//channel")
        # import pdb; pdb.set_trace()

        # USE THIS ROUTE FOR RSS
        # removing the dc: to be able to access the author in RSS
        if post_title_test != []:
            contents = urllib2.urlopen(post_link).read().replace('dc:','')
            post_str = etree.fromstring(contents)
            all_posts = post_str.xpath(".//channel/item")

            for post in all_posts:
                _title = unicode(post.xpath(".//title/text()")[0])

                if post.xpath(".//creator/text()") != []:
                    _author = unicode(post.xpath(".//creator/text()")[0])

                _description = unicode(post.xpath(".//description/text()")[0])

                timestamp = str(post.xpath(".//pubDate/text()")[0])
                datetime_timestamp = du_parser.parse(timestamp)
                _pubDate = datetime_timestamp.replace(tzinfo=None)
                _url = str(post.xpath(".//link/text()")[0])


                try:
                    _post = Post(title = _title, author = _author, content = _description, timestamp = _pubDate, url = _url)

                except:
                    _post = Post(title = _title, content = _description, timestamp = _pubDate, url = _url)

                self.posts.append(_post)

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
                if entry.xpath(".//title/text()") != []:
                    _title = unicode(entry.xpath(".//title/text()")[0])

                _author = unicode(entry.xpath(".//author/name/text()")[0])

                _description = unicode(entry.xpath(".//content/text()")[0])

                timestamp = str(entry.xpath(".//published/text()")[0])
                datetime_timestamp = du_parser.parse(timestamp)
                _pubDate = datetime_timestamp.replace(tzinfo=None)

                _url = str(entry.xpath("//link[@rel='alternate']/@href")[0])

                try:
                    _post = Post(title = _title, author = _author, content = _description, timestamp = _pubDate, url = _url)

                except:

                    _post = Post(author = _author, content = _description, timestamp = _pubDate, url=_url)

                self.posts.append(_post)

        # END ATOM BLOCK

        return self.posts

    def check_posts(self):
        all_posts = self.posts

        post_title_list = []
        for post in all_posts:
            post_title = post.title
            post_title_list.append(post_title)

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

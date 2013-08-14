from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from sqlalchemy import ForeignKey
import feedparser 
import datetime 

engine = create_engine("sqlite:///rss.db", echo=True)
session = scoped_session(sessionmaker(bind=engine,autocommit=False,autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

# Convert datetime into the format to use in the database, for example:
# 2013-02-09 14:06:33

def published_parsed_to_db_format(tup):
    d = datetime.datetime(*(tup[0:6]))
    #two equivalent ways to format it:
    #dStr = d.isoformat(' ')
    #or
    return d.strftime('%Y-%m-%d %H:%M:%S')

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
        metadata = feedparser.parse(self.feed_link)
        self.feed_title = metadata.feed.title
        self.feed_subtitle = metadata.feed.subtitle 

    def get_current_posts(self):
        all_posts = feedparser.parse(self.feed_link)

        for post in all_posts.entries:
            timestamp = published_parsed_to_db_format(post.published_parsed)
            
            if hasattr(post, "author"):
                single_post = Post(title = post.title, author = post.author, content = post.description, timestamp = timestamp)
                
            else:
                single_post = Post(title = post.title, content = post.description, timestamp = timestamp)

            # p_url = Post(url = post.description.link)
            # self.posts.append(p_url)

            self.posts.append(single_post)
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
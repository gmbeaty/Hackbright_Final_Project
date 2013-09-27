from StringIO import StringIO
import unittest
import urllib2

import dateutil
from lxml import etree
import mox
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import SQL_Alchemy_LXML
from SQL_Alchemy_LXML import Base, Post, Feed
import startengine

import add_atom

class TestAddAtom(unittest.TestCase):
    def test_create_post_with_author(self):
        item = etree.Element('root')
        etree.SubElement(item, 'title').text = 'Title'
        etree.SubElement(item, 'creator').text = 'Author'
        etree.SubElement(item, 'description').text = 'Description'
        etree.SubElement(item, 'pubDate').text = 'January 1, 2013'
        etree.SubElement(item, 'link').text = 'http://www.fake.com/feed'

        feed = Feed(feed_id=1)

        post = add_atom.create_post(item, feed)

        self.assertEqual(post.feed_id, 1)
        self.assertEqual(post.title, 'Title')
        self.assertEqual(post.author, 'Author')
        self.assertEqual(post.content, 'Description')
        timestamp = dateutil.parser.parse('January 1, 2013').replace(tzinfo=None)
        self.assertEqual(post.timestamp, timestamp)
        self.assertEqual(post.url, 'http://www.fake.com/feed')

    def test_create_post_without_author(self):
        item = etree.Element('root')
        etree.SubElement(item, 'title').text = 'Title'
        etree.SubElement(item, 'description').text = 'Description'
        etree.SubElement(item, 'pubDate').text = 'January 1, 2013'
        etree.SubElement(item, 'link').text = 'http://www.fake.com/feed'

        feed = Feed(feed_id=1)

        post = add_atom.create_post(item, feed)

        self.assertEqual(post.feed_id, 1)
        self.assertEqual(post.title, 'Title')
        self.assertEqual(post.author, None)
        self.assertEqual(post.content, 'Description')
        timestamp = dateutil.parser.parse('January 1, 2013').replace(tzinfo=None)
        self.assertEqual(post.timestamp, timestamp)
        self.assertEqual(post.url, 'http://www.fake.com/feed')

class TestAddAtomFullLoop(unittest.TestCase):
    @staticmethod
    def create_feed_xml(*posts):
        return '<rss><channel>' + ''.join(posts) + '</channel></rss>'

    def setUp(self):
        self.mox = mox.Mox()

        engine = create_engine('sqlite://')
        self.session = startengine.create_session(engine)
        Post.metadata.create_all(engine)
        Feed.metadata.create_all(engine)

        self.feed_link = 'http://fake-feed/'
        self.posts = [
'''<item>
  <title>Title</title>
  <description>Description</description>
  <pubDate>January 1, 2013</pubDate>
  <link>http://fake-feed/post1/</link>
</item>''',
]

    def tearDown(self):
        self.session.remove()
        self.mox.UnsetStubs()
        self.mox.VerifyAll()

    def test_main_loop(self):
        # Stub out etree.parse to return an element tree structure without
        # hitting the network
        feed_xml = self.create_feed_xml(self.posts[0])
        self.mox.StubOutWithMock(etree, 'parse')
        etree.parse(self.feed_link).AndReturn(etree.fromstring(feed_xml))

        # Stub out urllib2.urlopen to return the xml for the page without
        # hitting the network
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen(self.feed_link).AndReturn(StringIO(feed_xml))

        # Prepare the mocks to be called on
        self.mox.ReplayAll()

        # Create a row in the feed table, after running the main function once,
        # a row should be added to the post table
        self.session.add(Feed(feed_link=self.feed_link))
        self.session.commit()

        main = add_atom.main(self.session)
        main.next()
        self.assertEqual(len(Post.query.all()), 1)

    def test_main_loop_with_added_feed(self):
        # Stub out etree.parse to return an element tree structure without
        # hitting the network
        feed_xml = self.create_feed_xml(self.posts[0])
        self.mox.StubOutWithMock(etree, 'parse')
        etree.parse(self.feed_link).AndReturn(etree.fromstring(feed_xml))

        # Stub out urllib2.urlopen to return the xml for the page without
        # hitting the network
        self.mox.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen(self.feed_link).AndReturn(StringIO(feed_xml))

        # Prepare the mocks to be called on
        self.mox.ReplayAll()

        # Run the main loop once without any rows in the feed table and there
        # should be no rows in the post table
        main = add_atom.main(self.session)
        main.next()
        self.assertEqual(len(Post.query.all()), 0)

        # Create a row in the feed table in the database, after running the main
        # loop again, a row should be added to the post table
        self.session.add(Feed(feed_link=self.feed_link))
        self.session.commit()

        main.next()
        self.assertEqual(len(Post.query.all()), 1)

if __name__ == '__main__':
    unittest.main()

import unittest

import dateutil
from lxml import etree
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

from SQL_Alchemy_LXML import Post, Feed

import add_atom

class TestAddAtom(unittest.TestCase):
    # engine = create_engine('sqlite://')

    # def setUp(self):
    #     self.session = sessionmaker(bind=engine)()
    #     Post.metadata.create_all(self.engine)

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

if __name__ == '__main__':
    unittest.main()

import dateutil
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from SQL_Alchemy_LXML import Post

from fakes import FakeModel, FakeObject
import add_atom

class TestAddAtom(unittest.TestCase):
    # engine = create_engine('sqlite://')

    # def setUp(self):
    #     self.session = sessionmaker(bind=engine)()
    #     Post.metadata.create_all(self.engine)

    def test_create_post_with_author(self):
        item = FakeModel({
            './/title/text()': ['Title'],
            './/creator/text()': ['Author'],
            './/description/text()': ['Description'],
            './/pubDate/text()': ['January 1, 2013'],
            './/link/text()': ['http://www.fake.com/feed'],
        })

        feed_object = FakeObject()
        feed_object.feed_id = 1

        post = add_atom.create_post(item, feed_object)

        self.assertEqual(post.feed_id, 1)
        self.assertEqual(post.title, 'Title')
        self.assertEqual(post.author, 'Author')
        self.assertEqual(post.content, 'Description')
        self.assertEqual(post.timestamp,
                         dateutil.parser.parse('January 1, 2013').replace(tzinfo=None))
        self.assertEqual(post.url, 'http://www.fake.com/feed')

    def test_create_post_without_author(self):
        item = FakeModel({
            './/title/text()': ['Title'],
            './/creator/text()': [],
            './/description/text()': ['Description'],
            './/pubDate/text()': ['January 1, 2013'],
            './/link/text()': ['http://www.fake.com/feed'],
        })

        feed_object = FakeObject()
        feed_object.feed_id = 1

        post = add_atom.create_post(item, feed_object)

        self.assertEqual(post.feed_id, 1)
        self.assertEqual(post.title, 'Title')
        self.assertEqual(post.author, None)
        self.assertEqual(post.content, 'Description')
        self.assertEqual(post.timestamp,
                         dateutil.parser.parse('January 1, 2013').replace(tzinfo=None))
        self.assertEqual(post.url, 'http://www.fake.com/feed')

if __name__ == '__main__':
    unittest.main()


from crawler import crawler
import unittest

class test_crawler(unittest.TestCase):

    def setUp(self):
        self.bot = crawler(None, '')

    # def test_word_id(self):

        # insert a few words into the lexicon,
        # and check that _word_id_cache and _revert_word_id
        # map each word to its word_id correctly

        self.assertEqual(self.bot.word_id('apple'), 1)
        self.assertEqual(self.bot.word_id('lemon'), 2)
        self.assertEqual(self.bot.word_id('mango'), 3)
        self.assertEqual(self.bot.word_id('melon'), 4)
        self.assertEqual(self.bot.word_id('peach'), 5)

        self.assertEqual(self.bot._word_id_cache['apple'], 1)
        self.assertEqual(self.bot._word_id_cache['lemon'], 2)
        self.assertEqual(self.bot._word_id_cache['mango'], 3)
        self.assertEqual(self.bot._word_id_cache['melon'], 4)
        self.assertEqual(self.bot._word_id_cache['peach'], 5)

        self.assertEqual(self.bot._revert_word_id[1], 'apple')
        self.assertEqual(self.bot._revert_word_id[2], 'lemon')
        self.assertEqual(self.bot._revert_word_id[3], 'mango')
        self.assertEqual(self.bot._revert_word_id[4], 'melon')
        self.assertEqual(self.bot._revert_word_id[5], 'peach')

    # def test_doc_id(self):

        # insert a few URLs into the document index,
        # and check that _doc_id_cache and _revert_doc_id
        # map each URL to its doc_id correctly

        self.assertEqual(self.bot.document_id('google.com'), 1)
        self.assertEqual(self.bot.document_id('facebook.com'), 2)
        self.assertEqual(self.bot.document_id('instagram.com'), 3)

        self.assertEqual(self.bot._doc_id_cache['google.com'], 1)
        self.assertEqual(self.bot._doc_id_cache['facebook.com'], 2)
        self.assertEqual(self.bot._doc_id_cache['instagram.com'], 3)

        self.assertEqual(self.bot._revert_doc_id[1], 'google.com')
        self.assertEqual(self.bot._revert_doc_id[2], 'facebook.com')
        self.assertEqual(self.bot._revert_doc_id[3], 'instagram.com')

    # def test_add_words_to_document(self):

        # pretend that crawl() has just visited the web page,
        # and now insert words that are found to the document

        self.bot._curr_doc_id = 1
        self.bot._curr_words = [(1, 1), (2, 1), (3, 1)]
        self.bot._add_words_to_document()

        self.bot._curr_doc_id = 2
        self.bot._curr_words = [(2, 1), (3, 1), (4, 1)]
        self.bot._add_words_to_document()

        self.bot._curr_doc_id = 3
        self.bot._curr_words = [(3, 1), (4, 1), (5, 1)]
        self.bot._add_words_to_document()

    # def test_doc_index(self):

        expected_doc_index = {
            1: set([1, 2, 3]),
            2: set([2, 3, 4]),
            3: set([3, 4, 5]),
        }
        self.assertEqual(expected_doc_index, self.bot.get_doc_index())

    # def test_inverted_index(self):

        expected_inverted_index = {
            1: set([1]),
            2: set([1, 2]),
            3: set([1, 2, 3]),
            4: set([2, 3]),
            5: set([3]),
        }
        self.assertEqual(expected_inverted_index, self.bot.get_inverted_index())

    # def test_resolved_inverted_index(self):

        expected_resolved_inverted_index = {
            'apple': set(['google.com']),
            'lemon': set(['google.com', 'facebook.com']),
            'mango': set(['google.com', 'facebook.com', 'instagram.com']),
            'melon': set(['facebook.com', 'instagram.com']),
            'peach': set(['instagram.com'])
        }
        self.assertEqual(expected_resolved_inverted_index, self.bot.get_resolved_inverted_index())

if __name__ == '__main__':
    unittest.main()

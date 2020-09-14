import unittest
import os, json, datetime, shutil
import extractor
import pdb

class TestTwitterExtractor(unittest.TestCase):

    def setUp(self):
        extractor.raw2date("test/test_tweet_lines.txt",
                           "test/tweets",
                           "test_tweet")

    def test_retweeted(self):
        #pdb.set_trace()
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            mentions=False)
        print("tweet list: ", tweet_list)
        retweeter_ids = []
        for tweet in tweet_list:
            id_str = tweet[0]
            retweeter_ids.append(id_str)
        self.assertTrue("1" in retweeter_ids,
                         'id 1 should be in retweeters')
        self.assertTrue("2" in retweeter_ids,
                         'id 2 should be in retweeters')
        self.assertTrue("4" in retweeter_ids,
                         'id 4 should be in retweeters')
        self.assertTrue("7" in retweeter_ids,
                         'id 7 should be in retweeters')

    def tearDown(self):
        shutil.rmtree("test/tweets")

if __name__ == '__main__':
    unittest.main()


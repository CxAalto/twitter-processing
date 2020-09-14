import unittest
import os, json, datetime, shutil
import extractor
import pdb

class TestTwitterExtractor(unittest.TestCase):

    def setUp(self):
        extractor.raw2date("test/test_tweet_lines.txt",
                           "test/tweets",
                           "test_tweet")

    def test_retweets(self):
        #pdb.set_trace()  # for debugging
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            mentions=False)
        retweeter_ids = []
        retweet_times =[]
        for tweet in tweet_list:
            id_str = tweet[0]
            timestamp = tweet[2]
            retweeter_ids.append(id_str)
            retweet_times.append(timestamp)
        self.assertTrue("1" in retweeter_ids,
                         'id 1 should be in retweeters')
        self.assertTrue("2" in retweeter_ids,
                         'id 2 should be in retweeters')
        self.assertTrue("4" in retweeter_ids,
                         'id 4 should be in retweeters')
        self.assertTrue("7" in retweeter_ids,
                         'id 7 should be in retweeters')
        self.assertTrue("1599845613000" in retweet_times,
                        "Tweet with id 12 should be in retweets")
        # the non-retweet has timestamp "1599838215000"
        self.assertTrue("1599838215000" not in retweet_times,
                        "Tweet with id 1 should not be in retweets")

    def test_retweeters(self):
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            senders_rt=["1"],
                                            mentions=False)
        retweeter_ids = []
        for tweet in tweet_list:
            id_str = tweet[0]
            retweeter_ids.append(id_str)
        self.assertTrue("1" in retweeter_ids,
                        "Retweeter with id 1 should be included")
        self.assertTrue("2" not in retweeter_ids,
                        "Retweeter with id 2 should not be included")


    def test_retweeteds(self):
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            receivers_rt=["5"],
                                            mentions=False)
        retweeted_ids = []
        for tweet in tweet_list:
            id_str = tweet[1]
            retweeted_ids.append(id_str)
        self.assertTrue("5" in retweeted_ids,
                        "Retweeted with id 5 should be included")
        self.assertTrue("6" not in retweeted_ids,
                        "Retweeted with id 6 should not be included")


    def test_languages(self):
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            languages=["fi"],
                                            mentions=False)
        timestamps = []
        for tweet in tweet_list:
            time = tweet[2]
            timestamps.append(time)
        self.assertTrue("1599841875000" in timestamps,
                        "Tweet with id 10 should be included")
        self.assertTrue("1599845613000" not in timestamps,
                        "Tweet with id 12 should not be included")

    def test_keywords(self):
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            mentions=False,
                                            keywords=[
                                                "climate",
                                                "ilmastonmuutos"
                                            ])
        timestamps = []
        for tweet in tweet_list:
            time = tweet[2]
            timestamps.append(time)
        self.assertTrue("1599838275000" in timestamps,
                        "Tweet with id 2 should be included")
        self.assertTrue("1599819010000" in timestamps,
                        "Tweet with id 6 should be included")
        self.assertTrue("1599838275000" in timestamps,
                        "Tweet with id 8 should be included")
        self.assertTrue("1599841875000" in timestamps,
                        "Tweet with id 10 should be included")
        self.assertTrue("1599845613000" in timestamps,
                        "Tweet with id 12 should be included")
        self.assertTrue("1599838876000" not in timestamps,
                        "Tweet with id 4 should not be included")

    def test_dates(self):
        tweet_list = extractor.make_network("test/tweets",
                                            retweets=True,
                                            mentions=False,
                                            dates=[
                                                "20190813",
                                                "20200911"
                                            ])
        timestamps = []
        for tweet in tweet_list:
            time = tweet[2]
            timestamps.append(time)
        self.assertTrue("1599838275000" in timestamps,
                        "Tweet with id 2 should  be included")
        self.assertTrue("1599819010000" in timestamps,
                        "Tweet with id 6 should  be included")
        self.assertTrue("1599838275000" in timestamps,
                        "Tweet with id 8 should  be included")
        self.assertTrue("1599841875000" in timestamps,
                        "Tweet with id 10 should  be included")
        self.assertTrue("1599845613000" in timestamps,
                        "Tweet with id 12 should  be included")
        self.assertTrue("1565804013000" in timestamps,
                        "Tweet with id 13 should  be included")
        self.assertTrue("1565544813000" not in timestamps,
                        "Tweet with id 15 should not be included")

    def tearDown(self):
        shutil.rmtree("test/tweets")

if __name__ == '__main__':
    unittest.main()


# twitter-processing
Code to process and work with Twitter data.
## Testing
The `test` directory includes unit tests in `test_extractor.py` and a made up Twitter data file `test_tweets_lines.txt` for tests.
### Test tweets
The tested tweets may include the following fields:
| Field                                | Type                                          | Example                          |
|--------------------------------------|-----------------------------------------------|----------------------------------|
| created_at                           | string                                        | "Thu Apr 06 15:24:15 +0000 2017" |
| user                                 | object                                        | {}                               |
| user:id_str                          | int in string                                 | "1239376816101613568"            |
| retweeted_status                     | object                                        | {}                               |
| retweeted_status:user:id_str         | int in string                                 | "1239376816101613568"            |
| retweeted_status:lang                | string                                        | "en"                             |
| retweeted_status:truncated           | boolean                                       | false                            |
| retweeted_status:text                | string                                        | "Hello world!"                   |
| retweeted_status:extended_tweet      | object                                        | {}                               |
| retweeted_status:extended_tweet:text | string                                        | "Hi there!"                      |
| timestamp_ms                         | int in string, milliseconds since Jan 1, 1970 | "1584325447282"                  |

Test cases for tweets:
| Filter to test | Resulting tweets                         | Tweet id | Retweeter id | Retweeted id | Time        |
|----------------|------------------------------------------|----------|--------------|--------------|-------------|
| retweets       | should include retweets                  |        2 |            1 |            2 | Sep 11 2020 |
|                |                                          |        4 |            2 |            3 | Sep 11 2020 |
|                |                                          |        8 |            4 |            6 | Sep 11 2020 |
|                |                                          |       10 |            7 |            8 | Sep 11 2020 |
|                |                                          |       12 |            7 |            9 | Sep 11 2020 |
| retweets       | should not include non-retweets          |        1 |            1 |         None | Sep 11 2020 |
| retweeters     | should include given retweeters          |        2 |            1 |            2 | Sep 11 2020 |
| retweeters     | should not include other than given      |        4 |            2 |            3 | Sep 11 2020 |
| retweeteds     | should include given retweeteds          |        6 |            4 |            5 | Sep 11 2020 |
| retweeteds     | should not include others than given     |        8 |            4 |            6 | Sep 11 2020 |
| languages      | should include tweets in given languages |       10 |            7 |            8 | Sep 11 2020 |
| languages      | should not include languages not given   |       12 |            7 |            8 | Sep 11 2020 |
| keywords       | should include retweets with given words |        2 |            1 |            2 | Sep 11 2020 |
|                |                                          |        6 |            4 |            7 | Sep 11 2020 |
|                |                                          |        8 |            4 |            6 | Sep 11 2020 |
|                |                                          |       10 |            7 |            8 | Sep 11 2020 |
|                |                                          |       12 |            7 |           11 | Sep 11 2020 |
| keywords       | should not have ones without given words |        4 |            2 |            3 | Sep 11 2020 |
| hashtags       | should include tweets with hashtags      |        2 |            1 |            2 | Sep 11 2020 |
|                |                                          |       19 |           18 |           19 | Sep 12 2020 |
| hashtags       | should not include tweets without        |        6 |            4 |            5 | Sep 11 2020 |
| dates          | should be inside the date range          |        2 |            1 |            2 | Sep 11 2020 |
|                |                                          |        6 |            4 |            7 | Sep 11 2020 |
|                |                                          |        8 |            4 |            6 | Sep 11 2020 |
|                |                                          |       10 |            7 |            8 | Sep 11 2020 |
|                |                                          |       12 |            7 |           11 | Sep 11 2020 |
|                |                                          |       13 |           12 |           13 | Aug 14 2019 |
| dates          | should not be outside the date range     |       15 |           14 |           15 | Aug 11 2019 |
| truncated      | include without 'truncated' field        |       17 |           16 |           17 | Sep 11 2020 |
| oneline files  | deal with files where all is in one line |          |              |              |             |
| unions         | tweeter or tweeted should be a given     |        2 |            1 |            2 | Sep 11 2020 |
|                |                                          |        4 |            2 |            3 | Sep 11 2020 |
| list           | in a list format                         |          |              |              |             |
| dict           | in a dictionary format                   |          |              |              |             |

# Code to extract information from raw twitter data
import os, json, datetime
from inspect import getsource


# top level function
def raw2date(file, outfolder, filename):
		"""Converts raw tweet file to separate files by date.
		Parameters
		----------
		file : str
		File to be parsed into seperate files.
		outfolder : str
		Name of directory to save separate files.
		filename : str
		Base name for output files; date will be appended.
		"""
		os.makedirs(outfolder, exist_ok = True)
		with open(file, 'r') as infile:
				for line in infile:
						status = json.loads(line)
						if "created_at" in status:
								created = status["created_at"]
								dt = datetime.datetime.strptime(created, '%a %b %d %X %z %Y').strftime('%Y%m%d')
								out = filename + '_' + dt + '.txt'
								with open(os.path.join(outfolder, out), 'a', encoding = 'utf-8') as outfile:
										outfile.write(line)


# arguments: 1) file location; 2) time period; 3) subsets; 4) output?
def parse_retweet(tweet, **filters):
		"""Parse twitter json for retweet data; intended for internal use."""
		if "retweeted_status" in tweet:
				if filters.get('senders_rt') != None and tweet['user']['id_str'] not in filters.get('senders_rt'):
						return None
				if filters.get('receivers_rt') != None and tweet['retweeted_status']['user']['id_str'] not in filters.get('receivers_rt'):
						return None
				if filters.get('languages') != None and tweet['retweeted_status']['lang'] not in filters.get('languages'):
						return None
				if not tweet['retweeted_status']['truncated']:
						text = tweet['retweeted_status']['extended_tweet']['full_text'].lower()
				else:
						text = tweet['retweeted_status']['text'].lower()
				if filters.get('keywords') != None:
						for keyword in filters.get('keywords'):
								if keyword.lower() in text:
										edge = (tweet['user']['id_str'],
												tweet['retweeted_status']['user']['id_str'],
												tweet['timestamp_ms'])
										return(edge)
						return None
				else:
						edge = (tweet['user']['id_str'],
								tweet['retweeted_status']['user']['id_str'],
								tweet['timestamp_ms'])
						return(edge)


def update_retweet_parser(kw, sndr, rcvr, lng):
	    """Remove filtering conditions in retweet parser; intended for internal use."""
	    parse_retweet_source = getsource(parse_retweet)
	    parse_retweet_source = parse_retweet_source.replace('def parse_retweet(', 'def parse_retweet_conditions(')
	    if sndr == None:
		        parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'user\'][\'id_str\'] not in filters.get(\'senders_rt\'):\n\t\t\treturn None', '')
	    if rcvr == None:
		        parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'retweeted_status\'][\'user\'][\'id_str\'] not in filters.get(\'receivers_rt\'):\n\t\t\treturn None', '')
	    if lng == None:
		        parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'retweeted_status\'][\'lang\'] not in filters.get(\'languages\'):\n\t\t\treturn None', '')
	    if kw == None:
		        parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'retweeted_status\'][\'truncated\']:\n\t\t\ttext = tweet[\'retweeted_status\'][\'extended_tweet\'][\'full_text\'].lower()\n\t\telse:\n\t\t\ttext = tweet[\'retweeted_status\'][\'text\'].lower()\n\t\tfor keyword in filters.get(\'keywords\'):\n\t\t\tif keyword.lower() in text:\n\t\t\t\tedge = (tweet[\'user\'][\'id_str\'], tweet[\'retweeted_status\'][\'user\'][\'id_str\'], tweet[\'timestamp_ms\'])\n\t\t\t\treturn(edge)\n\t\treturn None', '')
	    return(parse_retweet_source)


def make_network(folder, **filters):
		"""Creates networks with specified filters.
		Parameters
		----------
	    folder : str
		Path containing all raw, dated files.
	    output : str
		Format of network. If 'edges', returns list of edges; if 'dict', returns dict object.
	    **filters :
		dates : list of two strings with start and end dates ('%Y%m%d'); or else all files in directory.
		retweets : logical of whether to include retweets in the network.
		mentions : logical of whether to include mentions in the network.
		keywords : list of all substrings to be matched; or else no filtering.
		senders_rt : list of retweeting accounts; or else all accounts included.
		receivers_rt : list of retweeted accounts; or else all accounts included.
		senders_at : list of mentioning accounts; or else all accounts included.
		receivers_at : list of all mentioned accounts; or else all accounts included.
		languages : list of languages to include; or else all languages included.
	    Returns
		-------
		list
		"""
		edges = []
		files = sorted([file for file in os.listdir(folder) if not file.startswith('.')])
		# Filter by date:
		dates = filters.get('dates')
		if dates != None:
				dates = [datetime.datetime.strptime(date, '%Y%m%d') for date in dates]
				date_range = [(dates[0] + datetime.timedelta(n)).strftime('%Y%m%d') for n in range(int ((dates[1] - dates[0]).days + 1))]
				files = [file for file in files if file[-12:-4] in date_range]
		# Redefine retweet and mention parsers to satisfy specified filters
		""" Remove this because of bugs that cannot be debugged
		if filters.get('retweets'):
				new_retweet_parser = update_retweet_parser(filters.get('keywords'),
														   filters.get('senders_rt'),
														   filters.get('receivers_rt'),
														   filters.get('languages'))
				exec(new_retweet_parser, globals())
		"""
		if filters.get('mentions'):
				pass
		for file in files:
				with open(os.path.join(folder, file), 'r', encoding = 'utf-8') as infile:
						for line in infile:
								tweet = json.loads(line)
								if filters.get('retweets'):
										parsed_rt = parse_retweet(tweet, **filters)
								if parsed_rt != None:
										edges.append(parsed_rt)
								if filters.get('mentions'):
										pass # For now does not parse mentions
		edges = list(set(edges)) # Removing duplicated edges (currently does not differentiate between retweets and mentions)
		return(edges)


def create_retweet_set_and_dict(dir_name,
                                hashtags_to_search,
                                hashtags_optional: bool, # are hashtags optional
                                strings_in_text,         # TODO
                                strings_optional: bool,  # are strings optional
                                set_of_tweeters,         # set of accounts to include; include all if empty
                                both_needed: bool, # do both retweeter and retweeted need to be in the set_of_tweeters
                                tweet_per_line = False): # Set to True, if each Tweet is on their own line.
    """
    Parameters: "dir_name" is the directory containing files tweets in json format.
                "hashtags_to_search" is a collection of hashtags as strings
                "hashtags_optional" if True, a tweet does not have to have one of the hashtags_to_search to be included,
                                    but will be included if the tweet has one the hashtags_to_search
                "strings_in_text" is a collection of strings
                "strings_optional" if True, a tweet does not have to have one of the strings in its contents to be included,
                                    but will be included if the tweet has one the strings
                "set_of_tweeters" is a collection of Twitter accounts that will be included in the set and dict; if empty, no limitation
                "both_in_set" if True, both retweeted and retweeter need to be in "set_of_tweeters" to be included
    "

    Returns: a set of retweet-related accounts,
             and a dictionary with a tuple of an account edge as a key and number of retweets as a value.
    """
    edge_dict = {} # key: (vertex1, vertex2), value: number_of_retweets
    accounts = set() # the set of tuples (accountId, accountName)
    set_of_tweeters_empty = not bool(set_of_tweeters)
    def add_tweet_to_dict(tweet_json):
        if "retweeted_status" in tweet_json:
                    retweeter = tweet_json["user"]["id"]
                    retweeter_name = tweet_json["user"]["screen_name"]
                    retweeted = tweet_json["retweeted_status"]["user"]["id"]
                    retweeted_name = tweet_json["retweeted_status"]["user"]["screen_name"]
                    try:
                        hashtags = tweet_json["retweeted_status"]["hashtags"]
                    except KeyError:
                        hashtags = []
                    in_set = False
                    in_hash = False
                    in_string = False
                    if set_of_tweeters_empty:
                        in_set = True
                    elif both_needed and (retweeter in set_of_tweeters) and (retweeted in set_of_tweeters):
                        in_set = True
                    elif (not both_needed) and ((retweeter in set_of_tweeters) or (retweeted in set_of_tweeters)):
                        in_set = True
                    else:
                        in_set = False
                    if in_set:
                        for hashtag in hashtags_to_search:
                            if hashtag in hashtags:
                              in_hash = True
                              break
                    # TODO search for strings in tweet text
                    if in_set and (in_hash or hashtags_optional) and (in_string or strings_optional):
                        if (retweeted, retweeter) in edge_dict:
                            old_weigth = edge_dict[(retweeted, retweeter)]
                            edge_dict.update({(retweeted,retweeter):old_weigth+1})
                        else:
                            edge_dict.update({(retweeted,retweeter):1})
                            # adding an account to a set two times results in only one instance in the set
                            accounts.add((retweeted,retweeted_name))
                            accounts.add((retweeter,retweeter_name))
    filenames = os.listdir(dir_name)
    for filename in filenames:
        json_file = open(dir_name+'/'+filename)
        for line in json_file:
            contents = json.loads(line)
            if tweet_per_line:
                add_tweet_to_dict(contents)
            else:
                for tweet_json in contents:
                    add_tweet_to_dict(tweet_json)
        json_file.close()
    return accounts, edge_dict



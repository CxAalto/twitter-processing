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
		if tweet['user']['id_str'] not in filters.get('senders_rt'):
			return None
		if tweet['retweeted_status']['user']['id_str'] not \
		   in filters.get('receivers_rt'):
			return None
		if tweet['retweeted_status']['lang'] not in filters.get('languages'):
			return None
		if 'truncated' in tweet['retweeted_status'] and \
		   not tweet['retweeted_status']['truncated']:
			text = tweet['retweeted_status']['extended_tweet']['full_text'].lower()
		else:
			text = tweet['retweeted_status']['text'].lower()
		for keyword in filters.get('keywords'):
			if keyword.lower() in text:
				edge = (tweet['user']['id_str'],
					tweet['retweeted_status']['user']['id_str'],
					tweet['timestamp_ms'])
				return(edge)
		return None
		edge = (tweet['user']['id_str'],
			tweet['retweeted_status']['user']['id_str'],
			tweet['timestamp_ms'])
		return(edge)
	else:
		return None

def update_retweet_parser(kw, sndr, rcvr, lng):
	"""Remove filtering conditions in retweet parser; intended for
	internal use."""
	parse_retweet_source = getsource(parse_retweet)
	parse_retweet_source = parse_retweet_source.replace('def parse_retweet(', 'def parse_retweet_conditions(')
	if sndr == None:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'user\'][\'id_str\'] not in filters.get(\'senders_rt\'):\n\t\t\treturn None', '')
	if rcvr == None:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'retweeted_status\'][\'user\'][\'id_str\'] not \\\n\t\t   in filters.get(\'receivers_rt\'):\n\t\t\treturn None', '')
	if lng == None:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'retweeted_status\'][\'lang\'] not in filters.get(\'languages\'):\n\t\t\treturn None', '')
	if kw == None:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tif \'truncated\' in tweet[\'retweeted_status\'] and \\\n\t\t   not tweet[\'retweeted_status\'][\'truncated\']:\n\t\t\ttext = tweet[\'retweeted_status\'][\'extended_tweet\'][\'full_text\'].lower()\n\t\telse:\n\t\t\ttext = tweet[\'retweeted_status\'][\'text\'].lower()\n\t\tfor keyword in filters.get(\'keywords\'):\n\t\t\tif keyword.lower() in text:\n\t\t\t\tedge = (tweet[\'user\'][\'id_str\'],\n\t\t\t\t\ttweet[\'retweeted_status\'][\'user\'][\'id_str\'],\n\t\t\t\t\ttweet[\'timestamp_ms\'])\n\t\t\t\treturn(edge)\n\t\treturn None', '')
	return(parse_retweet_source)


def make_network(folder,
		 output="edges",
		 tweet_per_line=False,
		 no_truncated_tweets=False,
		 **filters):
	"""Creates networks with specified filters.
	Parameters
	----------
	folder : str
		Path containing all raw, dated files.
	output : str
		Format of network. If 'edges', returns list of edges; if 'dictionary',
		returns dict object.
	tweet_per_line : logical of whether there is one tweet (JSON object) per
		line.
	no_truncated_tweets: logical of whether there is a key 'truncated' in JSON
	**filters :
	dates : list of two strings with start and end dates ('%Y%m%d'); or else
		all files in directory.
	retweets : logical of whether to include retweets in the network.
	mentions : logical of whether to include mentions in the network.
	keywords : list of all substrings to be matched; or else no filtering.
	senders_rt : list of retweeting accounts; or else all accounts included.
	receivers_rt : list of retweeted accounts; or else all accounts included.
	senders_at : list of mentioning accounts; or else all accounts included.
	receivers_at : list of all mentioned accounts; or else all accounts
		included.
	languages : list of languages to include; or else all languages included.
	Returns
	-------
	list of edges or
	a dict where keys are tuples of linked accounts
	"""
	edges = []
	dictionary = {}
	files = sorted([file for file in os.listdir(folder) if not file.startswith('.')])
	# Filter by date:
	dates = filters.get('dates')
	if dates != None:
		dates = [datetime.datetime.strptime(date, '%Y%m%d') for date in dates]
		date_range = [(dates[0] + datetime.timedelta(n)).strftime('%Y%m%d') for n in range(int ((dates[1] - dates[0]).days + 1))]
		files = [file for file in files if file[-12:-4] in date_range]
	# Redefine retweet and mention parsers to satisfy specified filters
	if filters.get('retweets'):
		new_retweet_parser = update_retweet_parser(filters.get('keywords'),
								filters.get('senders_rt'),
								filters.get('receivers_rt'),
								filters.get('languages')
							)
		exec(new_retweet_parser, globals())
	if filters.get('mentions'):
		pass
	def filter_tweet_to_collection(tweet, **filters):
		parsed_rt = parse_retweet_conditions(tweet, **filters)
		if parsed_rt != None:
			if output == "edges":
				edges.append(parsed_rt)
			else:
				key = (parsed_rt[0], parsed_rt[1])
				dictionary.update({key:tweet})
	for file in files:
		with open(os.path.join(folder, file), 'r', encoding = 'utf-8') as infile:
			for line in infile:
				contents = json.loads(line)
				parsed_rt = None
				if filters.get('retweets'):
					if tweet_per_line:
						filter_tweet_to_collection(contents, **filters)
					else:
						for tweet_json in contents:
							filter_tweet_to_collection(contents, **filters)
				if filters.get('mentions'):
					pass # For now does not parse mentions
	if output == "edges":
		# Removing duplicated edges
		# (currently does not differentiate between retweets and mentions)
		edges = list(set(edges))
		return(edges)
	else:
		return(dictionary)

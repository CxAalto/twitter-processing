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
	Handles only files where each Tweet JSON in in their own one line.
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
		retweeter = tweet.get('user').get('id_str')
		if retweeter == None:
			retweeter = str(tweet.get('user').get('id'))
		if retweeter not in filters.get('senders_rt'):
			return None
		retweeted = tweet.get('retweeted_status').get('user').get('id_str')
		if retweeted == None:
			retweeted = str(tweet.get('retweeted_status').get('user').get('id'))
		if retweeted not in filters.get('receivers_rt'):
			return None
		if tweet['retweeted_status']['lang'] not in filters.get('languages'):
			return None
		retweet = tweet.get('retweeted_status')
		if retweet.get('truncated') == False and retweet.get('extended_tweet') != None:
			text = retweet.get('extended_tweet').get('full_text').lower()
		else:
			text = tweet['retweeted_status']['text'].lower()
		for keyword in filters.get('keywords'):
			if keyword.lower() in text:
				retweeter = tweet.get('user').get('id_str')
				if retweeter == None:
					retweeter = str(tweet.get('user').get('id'))
				retweeted = tweet.get('retweeted_status').get('user').get('id_str')
				if retweeted == None:
					retweeted = str(tweet.get('retweeted_status').get('user').get('id'))
				timestamp = tweet.get('timestamp_ms')
				if timestamp == None:
					timestamp = tweet.get('timestamp')
				edge = (retweeter,
					retweeted,
					timestamp)
				return(edge)
		return None
		tags = tweet.get('retweeted_status').get('hashtags')
		if tags == []:
			return None
		if tags == None and tweet.get('retweeted_status').get('entities') != None:
			tag_objects = tweet.get('retweeted_status').get('entities').get('hashtags')
			if tag_objects == None or tag_objects == []:
				return None
			else:
				tags = []
				for tag in tag_objects:
					tags.append(tag.get('text'))
		if tags == None and tweet.get('retweeted_status').get('entities') == None:
			return None
		for hashtag in filters.get('hashtags'):
			if hashtag in tags:
				retweeter = tweet.get('user').get('id_srt')
				if retweeter == None:
					retweeter = str(tweet.get('user').get('id'))
				retweeted = tweet.get('retweeted_status').get('user').get('id_str')
				if retweeted == None:
					retweeted = str(tweet.get('retweeted_status').get('user').get('id'))
				timestamp = tweet.get('timestamp_ms')
				if timestamp == None:
					timestamp = tweet.get('timestamp')
				edge = (retweeter,
					retweeted,
					timestamp)
				return(edge)
		return None
		retweeter = tweet.get('user').get('id_str')
		if retweeter == None:
			retweeter = str(tweet.get('user').get('id'))
		retweeted = tweet.get('retweeted_status').get('user').get('id_str')
		if retweeted == None:
			retweeted = str(tweet.get('retweeted_status').get('user').get('id'))
		timestamp = tweet.get('timestamp_ms')
		if timestamp == None:
			timestamp = tweet.get('timestamp')
		edge = (retweeter,
			retweeted,
			timestamp)
		return(edge)
	else:
		return None


def update_retweet_parser(kw, sndr, rcvr, union_rt, lng, hashtags):
	"""Remove filtering conditions in retweet parser; intended for
	internal use."""
	parse_retweet_source = getsource(parse_retweet)
	parse_retweet_source = parse_retweet_source.replace('def parse_retweet(', 'def parse_retweet_conditions(')
	if (sndr == None or sndr==[]) and (union_rt == None or union_rt == False):
		parse_retweet_source = parse_retweet_source.replace('\n\t\tretweeter = tweet.get(\'user\').get(\'id_str\')\n\t\tif retweeter == None:\n\t\t\tretweeter = str(tweet.get(\'user\').get(\'id\'))\n\t\tif retweeter not in filters.get(\'senders_rt\'):\n\t\t\treturn None', '')
	if (rcvr == None or rcvr == []) and (union_rt == None or union_rt == False):
		parse_retweet_source = parse_retweet_source.replace('\n\t\tretweeted = tweet.get(\'retweeted_status\').get(\'user\').get(\'id_str\')\n\t\tif retweeted == None:\n\t\t\tretweeted = str(tweet.get(\'retweeted_status\').get(\'user\').get(\'id\'))\n\t\tif retweeted not in filters.get(\'receivers_rt\'):\n\t\t\treturn None', '')
	# When union is of sets where senders or receivers include everybody, remove both filters
	if union_rt == True and (rcvr == None or rcvr == [] or sndr == None or sndr == []):
		parse_retweet_source = parse_retweet_source.replace('\n\t\tretweeter = tweet.get(\'user\').get(\'id_str\')\n\t\tif retweeter == None:\n\t\t\tretweeter = str(tweet.get(\'user\').get(\'id\'))\n\t\tif retweeter not in filters.get(\'senders_rt\'):\n\t\t\treturn None', '')
		parse_retweet_source = parse_retweet_source.replace('\n\t\tretweeted = tweet.get(\'retweeted_status\').get(\'user\').get(\'id_str\')\n\t\tif retweeted == None:\n\t\t\tretweeted = str(tweet.get(\'retweeted_status\').get(\'user\').get(\'id\'))\n\t\tif retweeted not in filters.get(\'receivers_rt\'):\n\t\t\treturn None', '')
	if union_rt == True and rcvr != None and rcvr != [] and sndr != None and sndr != []:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tretweeter = tweet.get(\'user\').get(\'id_str\')\n\t\tif retweeter == None:\n\t\t\tretweeter = str(tweet.get(\'user\').get(\'id\'))\n\t\tif retweeter not in filters.get(\'senders_rt\'):\n\t\t\treturn None\n\t\tretweeted = tweet.get(\'retweeted_status\').get(\'user\').get(\'id_str\')\n\t\tif retweeted == None:\n\t\t\tretweeted = str(tweet.get(\'retweeted_status\').get(\'user\').get(\'id\'))\n\t\tif retweeted not in filters.get(\'receivers_rt\'):\n\t\t\treturn None', '\n\t\tretweeter = tweet.get(\'user\').get(\'id_str\')\n\t\tif retweeter == None:\n\t\t\tretweeter = str(tweet.get(\'user\').get(\'id\'))\n\t\tretweeted = tweet.get(\'retweeted_status\').get(\'user\').get(\'id_str\')\n\t\tif retweeted == None:\n\t\t\tretweeted = str(tweet.get(\'retweeted_status\').get(\'user\').get(\'id\'))\n\t\tif retweeter not in filters.get(\'senders_rt\') and retweeted not in filters.get(\'receivers_rt\'):\n\t\t\treturn None')
	if lng == None or lng == []:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tif tweet[\'retweeted_status\'][\'lang\'] not in filters.get(\'languages\'):\n\t\t\treturn None', '')
	if kw == None or kw == []:
		parse_retweet_source = parse_retweet_source.replace('\n\t\tretweet = tweet.get(\'retweeted_status\')\n\t\tif retweet.get(\'truncated\') == False and retweet.get(\'extended_tweet\') != None:\n\t\t\ttext = retweet.get(\'extended_tweet\').get(\'full_text\').lower()\n\t\telse:\n\t\t\ttext = tweet[\'retweeted_status\'][\'text\'].lower()\n\t\tfor keyword in filters.get(\'keywords\'):\n\t\t\tif keyword.lower() in text:\n\t\t\t\tretweeter = tweet.get(\'user\').get(\'id_str\')\n\t\t\t\tif retweeter == None:\n\t\t\t\t\tretweeter = str(tweet.get(\'user\').get(\'id\'))\n\t\t\t\tretweeted = tweet.get(\'retweeted_status\').get(\'user\').get(\'id_str\')\n\t\t\t\tif retweeted == None:\n\t\t\t\t\tretweeted = str(tweet.get(\'retweeted_status\').get(\'user\').get(\'id\'))\n\t\t\t\ttimestamp = tweet.get(\'timestamp_ms\')\n\t\t\t\tif timestamp == None:\n\t\t\t\t\ttimestamp = tweet.get(\'timestamp\')\n\t\t\t\tedge = (retweeter,\n\t\t\t\t\tretweeted,\n\t\t\t\t\ttimestamp)\n\t\t\t\treturn(edge)\n\t\treturn None', '')
	if hashtags == None or hashtags == []:
		parse_retweet_source = parse_retweet_source.replace('\n\t\ttags = tweet.get(\'retweeted_status\').get(\'hashtags\')\n\t\tif tags == []:\n\t\t\treturn None\n\t\tif tags == None and tweet.get(\'retweeted_status\').get(\'entities\') != None:\n\t\t\ttag_objects = tweet.get(\'retweeted_status\').get(\'entities\').get(\'hashtags\')\n\t\t\tif tag_objects == None or tag_objects == []:\n\t\t\t\treturn None\n\t\t\telse:\n\t\t\t\ttags = []\n\t\t\t\tfor tag in tag_objects:\n\t\t\t\t\ttags.append(tag.get(\'text\'))\n\t\tif tags == None and tweet.get(\'retweeted_status\').get(\'entities\') == None:\n\t\t\treturn None\n\t\tfor hashtag in filters.get(\'hashtags\'):\n\t\t\tif hashtag in tags:\n\t\t\t\tretweeter = tweet.get(\'user\').get(\'id_srt\')\n\t\t\t\tif retweeter == None:\n\t\t\t\t\tretweeter = str(tweet.get(\'user\').get(\'id\'))\n\t\t\t\tretweeted = tweet.get(\'retweeted_status\').get(\'user\').get(\'id_str\')\n\t\t\t\tif retweeted == None:\n\t\t\t\t\tretweeted = str(tweet.get(\'retweeted_status\').get(\'user\').get(\'id\'))\n\t\t\t\ttimestamp = tweet.get(\'timestamp_ms\')\n\t\t\t\tif timestamp == None:\n\t\t\t\t\ttimestamp = tweet.get(\'timestamp\')\n\t\t\t\tedge = (retweeter,\n\t\t\t\t\tretweeted,\n\t\t\t\t\ttimestamp)\n\t\t\t\treturn(edge)\n\t\treturn None', '')
	return(parse_retweet_source)


def make_network(folder,
		 output="edges",
		 tweet_per_line=True,
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
	**filters :
	dates : list of two strings with start and end dates ('%Y%m%d'); or else
		all files in directory.
	retweets : logical of whether to include retweets in the network.
	mentions : logical of whether to include mentions in the network.
	keywords : list of all substrings to be matched; or else no filtering.
	hashtags : list of all hashtags to be matched; or else no filtering.
	senders_rt : list of retweeting accounts; or else all accounts included.
	receivers_rt : list of retweeted accounts; or else all accounts included.
	union_rt : logical of whether senders_rt and receivers_rt form a union or
		an intersection (i.e. are both required for an edge or only one)
	senders_at : list of mentioning accounts; or else all accounts included.
	receivers_at : list of all mentioned accounts; or else all accounts
		included.
	languages : list of languages to include; or else all languages included.
	Returns
	-------
	list of edges, or
	a dictionary where keys are tuples of linked accounts and tweet timestamp.
	"""
	edges = []
	dictionary = {}
	files = sorted([file for file in os.listdir(folder) if os.path.isfile(os.path.join(folder, file))])
	# Filter by date:
	dates = filters.get('dates')
	if dates != None and dates != []:
		dates = [datetime.datetime.strptime(date, '%Y%m%d') for date in dates]
		date_range = [(dates[0] + datetime.timedelta(n)).strftime('%Y%m%d') for n in range(int ((dates[1] - dates[0]).days + 1))]
		files = [file for file in files if file[-12:-4] in date_range]
	# Redefine retweet and mention parsers to satisfy specified filters
	if filters.get('retweets'):
		new_retweet_parser = update_retweet_parser(filters.get('keywords'),
								filters.get('senders_rt'),
								filters.get('receivers_rt'),
								filters.get('union_rt'),
								filters.get('languages'),
								filters.get('hashtags'))
		exec(new_retweet_parser, globals())
	if filters.get('mentions'):
		pass
	def filter_tweet_to_collection(tweet, **filters):
		parsed_rt = parse_retweet_conditions(tweet, **filters)
		if parsed_rt != None:
			if output == "edges":
				edges.append(parsed_rt)
			else:
				dictionary.update({parsed_rt:tweet})
	for file in files:
		with open(os.path.join(folder, file), 'r', encoding = 'utf-8') as infile:
			for line in infile:
				try:
					contents = json.loads(line)
					parsed_rt = None
					if filters.get('retweets'):
						if tweet_per_line:
							filter_tweet_to_collection(contents, **filters)
						else:
							for tweet_json in contents:
								filter_tweet_to_collection(tweet_json, **filters)
					if filters.get('mentions'):
						pass # For now does not parse mentions
				except json.decoder.JSONDecodeError:
					print(line)
	if output == "edges":
		# Removing duplicated edges
		# (currently does not differentiate between retweets and mentions)
		edges = list(set(edges))
		return(edges)
	else:
		return(dictionary)

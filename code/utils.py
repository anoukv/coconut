from nltk import pos_tag
from nltk.tag.simplify import simplify_wsj_tag

from nltk.stem.snowball import SnowballStemmer
Stemmer = SnowballStemmer("english")

def postag(word):
	try:
		return simplify_wsj_tag(pos_tag([word])[0][1])
	except:
		return "UNK"

def pos_is_revelant(pos):
	return pos in set(['N', 'NP', 'VG', 'VD', 'ADJ', 'ADV'])

def word_is_relevant(word):
	return pos_is_revelant(postag(word))

def read_vecs(limit=90000):
	f1 = open("../vectors/vocabul50", 'r')
	f2 = open("../vectors/vectors50", 'r')
	lines = zip(f1.readlines(), f2.readlines())[:limit]
	lines = filter(lambda x : word_is_relevant(x[0]), lines)
	f1.close()
	f2.close()
	lines = [ (x.replace("\n", ""), map(lambda n : float(n), filter(lambda p : len(p) > 2, y.replace("\n","").split(" ")))) for (x,y) in lines ]
	return lines
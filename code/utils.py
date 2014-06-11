from nltk import pos_tag
from nltk.tag.simplify import simplify_wsj_tag

from nltk.stem.snowball import SnowballStemmer
Stemmer = SnowballStemmer("english")

def postag(word):
	return simplify_wsj_tag(pos_tag([word])[0][1])

def pos_is_revelant(pos):
	return pos in set(['N', 'NP', 'VG', 'VD', 'ADJ', 'ADV'])

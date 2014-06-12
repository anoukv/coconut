from math import sqrt
from nltk import pos_tag
from nltk.tag.simplify import simplify_wsj_tag
from nltk.stem.snowball import SnowballStemmer
Stemmer = SnowballStemmer("english")

def postag(word):
	return simplify_wsj_tag(pos_tag([word])[0][1])

def pos_is_revelant(pos):
	return pos in set(['N', 'NP', 'VG', 'VD', 'ADJ', 'ADV'])

# returns normalized word vectors for every word from 'filename'
def load_vectors(filename):
	def normalizeString(vec):
		vec = [ float(x) for x in vec]
		total = sqrt( sum([v**2 for v in vec]) )
		new_vec = []
		for v in vec:
			new_vec.append(v/total)
		return tuple(new_vec)
	print "\tLoading projections..."
	f = open(filename,'r')
	f.readline()
	content = [ filter( lambda x : not x in ["\n",""], l.replace("\n", "").split(" ")) for l in f.readlines() ]
	content = [ (l[0], normalizeString(l[1:])) for l in content ]
	content = filter(lambda x : not x[1] == None, content)
	words = dict()
	for (word, vector) in content:
		words[word.lower()] = vector
	return words

# reads the SCWS task
def load_task(filename):
	task = dict()
	f = open(filename, 'r')
	lines = f.readlines()
	for question in lines:
		q = dict()
		question = question.split('\t')
		q['word1'] = question[1].lower()
		q['pos1'] = question[2]
		q['word2'] = question[3].lower()
		q['pos2'] = question[4]
		q['context1'] = question[5]
		q['context2'] = question[6]
		q['rating'] = float(question[7])
		task[int(question[0])] = q
	return task

# returns Spearman's Rank Correlation
def spearman(x, y):
	# add identifiers to to lists
	idX = [(i, x[i]) for i in xrange(len(x))]
	idY = [(i, y[i]) for i in xrange(len(y))]

	# sort the lists with identifier tuples based on the observed variable
	idX = sorted(idX, key = lambda x: x[1])
	idY = sorted(idY, key = lambda x: x[1])

	# throw away the values
	idX = map(lambda x: x[0], idX)
	idY = map(lambda x: x[0], idY)

	# get the ranking for the observed variables
	xx = [idX.index(i) + 1 for i in xrange(len(idX))]
	yy = [idY.index(i) + 1 for i in xrange(len(idY))]

	# compute the mean for the rankings (meanX == meanY)
	meanX = sum(xx) / float(len(xx))
	meanY = sum(yy) / float(len(yy))

	# iterate over all observed variable rankings and perform 
	# computations
	numerator = 0
	denominator1 = 0
	denominator2 = 0
	
	for i in xrange(len(xx)):
		numerator += (xx[i] - meanX) * (yy[i] - meanY)
		denominator1 += (xx[i] - meanX)**2
		denominator2 += (yy[i] - meanY)**2
	
	# result!
	denominator = sqrt(denominator1 * denominator2)
	rho = numerator / float(denominator)
	
	return rho

# vec1 and vec2 should already be normalized!!
def cosine_similarity(vec1, vec2):
	return sum([vec1[i] * vec2[i] for i in xrange(len(vec1))])

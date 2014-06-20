from nltk import pos_tag
from nltk.tag.simplify import simplify_wsj_tag
from nltk.stem.snowball import SnowballStemmer
Stemmer = SnowballStemmer("english")
from math import sqrt


class Word:
    def __init__(self, word, desc=None, meta=dict()):
    	self.word = word
    	self.desc = desc
    	self.meta = meta

    	self._lemma = None
        self._pos = None
        self._relevant = None

    def relevant(self):
      if self._relevant == None:
          self._relevant = pos_is_revelant(self.pos())
      return self._relevant

    def pos(self):
        if self._pos == None:
            self._pos = postag(self.word)
        return self._pos

    def lemma(self):
    	if self._lemma == None:
    		self._lemma = Stemmer.stem(self.word)
    	return self._lemma.encode('ascii','ignore') 

    def setDescription(self, x):
        self.desc = x



def postag(word):
	try:
		return simplify_wsj_tag(pos_tag([word])[0][1])
	except:
		return "UNK"

def pos_is_revelant(pos):
	return pos in set(['N', 'NP', 'VG', 'VD', 'ADJ', 'ADV'])

def word_is_relevant(word):
	return pos_is_revelant(postag(word))

# normalize a vector
def normalize(vec):
	total = sqrt( sum([v**2 for v in vec]) )
	new_vec = []
	for v in vec:
		new_vec.append(v/total)
	return tuple(new_vec)

# reads the SCWS task
def load_task(filename, allWords=False):
	words = set()
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
		words.add(question[1].lower())
		words.add(question[3].lower())
		if allWords:
			for w in (q['context1']+" "+q['context2']).lower().split(' '):
				words.add(w)
	words = [Word(x).lemma() for x in words]

	return task, words

# returns Spearman's Rank Correlation (takes care of ties)
def spearman(x, y):

	assert len(x) == len(y), "Problem with two lists in spearman (not the same size). Returning 0"

	# add identifiers to to lists
	idX = [(i, x[i]) for i in xrange(len(x))]
	idY = [(i, y[i]) for i in xrange(len(y))]

	# sort the lists with identifier tuples based on the observed variable
	idX = sorted(idX, key = lambda x: x[1])
	idY = sorted(idY, key = lambda x: x[1])
	# print [ x[0] for x in idX ]
	# print [ x[0] for x in idY ]

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
	
	return rho * 100

# returns Spearman's Rank Correlation (does not take care of ties)
def spearman2(x, y):
	
	assert len(x) == len(y), "Problem with two lists in spearman (not the same size). Returning 0"


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

	dSquaredList = [(xx[i] - yy[i])**2 for i in range(len(xx))]
	rho = 1 - (6 * sum(dSquaredList))/float(len(xx) * (len(xx)**2 - 1))
	
	return rho * 100

# returns normalized word vectors for every word from 'filename'
def load_vectors(filename, limit=False, filterRelevant=False):
	def normalizeString(vec):
		vec = [ float(x) for x in vec]
		total = sqrt( sum([v**2 for v in vec]) )
		new_vec = []
		for v in vec:
			new_vec.append(v/total)
		return tuple(new_vec)
	f = open(filename,'r')
	f.readline()
	content = [ filter( lambda x : not x in ["\n",""], l.replace("\n", "").split(" ")) for l in f.readlines() ]
	content = [ (l[0], normalizeString(l[1:])) for l in content ]
	content = filter(lambda x : not x[1] == None, content)
	if filterRelevant and not limit == False:
		newC = []
		while limit > 0:
			item = content.pop(0)
			if word_is_relevant(item[0]):
				newC.append(item)
				limit -= 1
		content = newC
	else:
		if filterRelevant:
			content = filter(lambda x : word_is_relevant(x[0]), content)
		if not limit == False:
			content = content[:limit]
	words = dict()
	for (word, vector) in content:
		words[word.lower()] = vector
	return words




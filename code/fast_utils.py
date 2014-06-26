"""
	These utils have no cPython dependencies and can be used in pypy
"""
from collections import defaultdict
from math import sqrt

def read_sets(filename="clusters.tmp"):
	clusters = []
	f = open(filename, 'r')
	for line in f.readlines():
		clusters.append(eval(line))
	f.close()
	return clusters
	
def get_coc(context):
	dic = defaultdict(int)
	for word in context:
		dic[word] += 1
	return normalize_coc(dic)

# for reading a textfile (corpus)
def read_file(filename):
	f = open(filename, 'r')
 	inpt = f.readline().replace("\n", "").split(" ")
 	f.close()
 	return inpt

def normalize_coc(coc):
	total = sqrt( sum([v**2 for v in coc.values()]) )
	return dict( [ (key, coc[key]/total) for key in coc ] )

def normalizeVec(vec):
	total = sqrt( sum([v**2 for v in vec]) )
	return tuple( [v/total for v in vec] )

# vec1 and vec2 should already be normalized!!
def cosine_similarity(vec1, vec2):
	return sum([vec1[i] * vec2[i] for i in xrange(len(vec1))])

# Has no filter for relevant words, make one using e.g. the utils equivalent.
def load_vectors(filename, limit=False):
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
	if not limit == False:
		content = content[:limit]
	words = dict()
	for (word, vector) in content:
		words[word.lower()] = vector
	return words

def getAverageWordRep(words, vectors):
	vecs = [vectors[word] for word in words if word in vectors]
	average = [sum(x) / float(len(x)) for x in zip(*vecs)]
	return normalizeVec(average)

def getAverageWordRep2(vecs):
	average = [sum(x) / float(len(x)) for x in zip(*vecs)]
	return normalizeVec(average)

def getAverageVector(vectors):
	average = [sum(x) / float(len(x)) for x in zip(*vectors)]
	return average

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
	

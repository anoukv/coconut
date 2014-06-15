"""
	These utils have no cPython dependencies and can be used in pypy
"""

def normalizeVec(vec):
	total = sqrt( sum([v**2 for v in vec]) )
	return tuple( [v/total for v in vec] )

# vec1 and vec2 should already be normalized!!
def cosine_similarity(vec1, vec2):
	return sum([vec1[i] * vec2[i] for i in xrange(len(vec1))])

def load_vectors(filename, limit=False, filterRelevant=True):
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
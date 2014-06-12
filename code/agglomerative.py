from math import sqrt
from time import time

class Node:
	def __init__(self, center, weight, identifier):
		self.center = center
		self.weight = weight
		self.identifier = identifier

	def similarity(self, otherNode):
		return sum( [ x * y for (x,y) in zip(self.center, otherNode.center) ] )

def combinedNode(n1, n2):
	c1, w1, c2, w2 = n1.center, n1.weight, n2.center, n2.weight
	t = w1 + w2
	return Node([ (x*w1 + y*w2)/t for (x,y) in zip(c1,c2) ], t, n1.identifier.union(n2.identifier))

def agglomerative_clustering(data, n=500, verbose=True):
	if verbose:
		print "\tCreating nodes..."

	nodes = []
	for (identifier, center) in data:
		nodes.append( Node(center, 1.0, set(identifier)) )

	data = None
	if verbose:
		print "\tClustering from", len(nodes), "nodes to", n

	merges = len(nodes) - n
	for n in xrange(merges):
		print "\t\tIteration", n
		start = time()
		bestS = -1
		bestP = (None, None)
		for i in xrange(len(nodes)-1):
			node = nodes[i]
			for j in xrange(i+1,len(nodes)):
				sim = node.similarity(nodes[j])
				if sim > bestS:
					bestP = (i, j)
		n2 = nodes.pop(j)
		n1 = nodes.pop(i)
		nodes.append(combinedNode(n1, n2))
		stop = time()
		print "\t\t\tTook", stop - start, "seconds"
	return nodes

# returns normalized word vectors for every word from 'filename'
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


if __name__ == '__main__':
	print "Loading vectors"
	data = load_vectors("../data/wordvectors/vectors50.relevant.wiki", 10000).items()
	print "Clustering"
	nodes = agglomerative_clustering(data, len(data)-2)











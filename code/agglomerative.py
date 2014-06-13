from math import sqrt
from time import time

class Node:
	"""
		Node class that contains a node center, weight, identifier and indexer
	"""
	def __init__(self, center, weight, identifier, nodeIndexer):
		self.center = center
		self.weight = weight
		self.identifier = identifier
		self.index = nodeIndexer

	def similarity(self, otherNode):
		return sum( [ x * y for (x,y) in zip(self.center, otherNode.center) ] )

def normalizeVec(vec):
	total = sqrt( sum([v**2 for v in vec]) )
	return tuple([v/total for v in vec])

def combinedNode(n1, n2, nodeIndexer):
	"""
		Combines two existing nodes and creates a new one with a given index
	"""
	c1, w1, c2, w2 = n1.center, n1.weight, n2.center, n2.weight
	t = w1 + w2
	return Node(normalizeVec([ (x*w1 + y*w2)/t for (x,y) in zip(c1,c2) ]), t, n1.identifier.union(n2.identifier), nodeIndexer)


# Private copy from utils version so that this file can be run using pypy
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



def agglomerative_clustering(data, n=500):
	"""
		Clusters the data agglomeratively.
		Data is stored in a list of nodes, which will be merged.
		Uses a cache to quickly recover node distances.
	"""
	print "\tCreating nodes..."

	nodeIndexer = 0
	nodes = []
	for (identifier, center) in data:
		nodes.append( Node(center, 1.0, set(identifier), nodeIndexer) )
		nodeIndexer += 1

	print "\tCreating cache..."
	start = time()

	# Create cache for fast access.
	# cache is a distionary of dictionaries which maps index -> dict( index -> similarity )
	cache = dict()
	for i in xrange(len(nodes)-1):
		node1 = nodes[i]
		cache_dic = dict()
		for j in xrange(i+1,len(nodes)):
			name2 = nodes[j].index
			cache_dic[name2] = node1.similarity(nodes[j])
		cache[node1.index] = cache_dic
	# Last one is empty
	cache[nodes[-1].index] = dict()

	stop = time()
	print "\t\tCache created in", int(stop - start + 0.5), "seconds"
	start = time()

	data = None
	print "\tClustering from", len(nodes), "nodes to", n

	# Loop to make a certain number of merges
	merges = len(nodes) - n
	for n in xrange(merges):
		# Communicate to developer:
		print "\t\tIteration", n

		# Find a best pair P with mest score S
		bestS = -2
		bestP = (None, None)

		# Use a double for loop to get all node index pairs and get their value from the cache.
		for i in xrange(len(nodes)-1):
			cache_dic = cache[nodes[i].index]
			for j in xrange(i+1,len(nodes)): # Restrict second loop to avaid symetries.
				sim = cache_dic[nodes[j].index]
				if sim > bestS:
					bestP = (i, j)
					bestS = sim

		# Merge the best node pair
		n2 = nodes.pop(bestP[1])
		n1 = nodes.pop(bestP[0])
		newNode = combinedNode(n1, n2, nodeIndexer)
		nodeIndexer += 1

		# Partially perform garbage collection on parts that are easy to delete.
		del cache[n1.index]
		del cache[n2.index]
		
		# Cache all the similarities between the new node and existing nodes before appending.
		name2 = newNode.index
		cache[name2] = dict() # This will be used in future iterations.
		for i in xrange(len(nodes)):
			sim = newNode.similarity(nodes[i])
			cache[nodes[i].index][name2] = sim
		nodes.append(newNode)

	stop = time()
	print "\t\tLooping took", stop - start, "seconds"

	return nodes

if __name__ == '__main__':
	print "Loading vectors"
	data = load_vectors("../data/wordvectors/vectors50.relevant.wiki", 6000).items()
	print "Clustering"
	nodes = agglomerative_clustering(data, len(data)-2)











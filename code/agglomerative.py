from fast_utils import normalizeVec, load_vectors

from math import sqrt
from time import time
import os, sys

class MaxMaintainer:
	def __init__(self, limit):
		self.limit = limit
		self.top = [(None, -999)]
		self.full = False

	def add(self, pair, sim):
		top = self.top
		if self.full:
			if self.min < sim:
				for i in xrange(len(top)):
					if top[i][1] < sim:
						top.insert(i, (pair, sim))
						top.pop()
						self.min = top[-1][1]
						break
				self.top = top
		else:
			for i in xrange(len(top)):
				if top[i][1] < sim:
					top.insert(i, (pair, sim))
					break
			full = len(top) == self.limit
			if full:
				self.min = top[-1][1]
				self.full = True
			self.top = top

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

def combinedNode(n1, n2, nodeIndexer):
	"""
		Combines two existing nodes and creates a new one with a given index
	"""
	c1, w1, c2, w2 = n1.center, n1.weight, n2.center, n2.weight
	t = w1 + w2
	return Node(normalizeVec([ (x*w1 + y*w2)/t for (x,y) in zip(c1,c2) ]), t, n1.identifier.union(n2.identifier), nodeIndexer)

def save_clusters_to_file(nodes, filename):
	f = open(filename, 'w')
	for node in nodes:
		f.write(str(node.identifier))
		f.write("\n")
	f.close()

def slow_agglomerative_procedure(nodes, final_size, cache, nodeIndexer):
	start = time()
	# Loop to make a certain number of merges
	merges = len(nodes) - final_size
	for n in xrange(merges, 0, -1):

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
		# Notice the pop order is of importance
		n2 = nodes.pop(bestP[1])
		n1 = nodes.pop(bestP[0])
		newNode = combinedNode(n1, n2, nodeIndexer)
		nodeIndexer += 1

		# Partially perform garbage collection on parts that are easy to delete.
		# Over time, nothing should stick around.
		del cache[n1.index]
		del cache[n2.index]
		
		nodes = [newNode] + nodes
		cache_dic = dict() # This will be filled now, and then added to the cache.
		for i in xrange(1, len(nodes)):
			sim = newNode.similarity(nodes[i])
			cache_dic[nodes[i].index] = sim
		cache[newNode.index] = cache_dic # Finally register the new cache dictionary.

	stop = time()
	print "\t\tFinal looping took", stop - start, "seconds"
	return nodes

def bootstrap_clustering(data):
	print "\tCreating nodes..."

	nodeIndexer = 0
	nodes = []
	for (identifier, center) in data:
		nodes.append( Node(center, 1.0, set([identifier]), nodeIndexer) )
		nodeIndexer += 1
	data = None # GC

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

	return (nodes, cache, nodeIndexer)

def agglomerative_clustering(data, final_size=500):
	"""
		Clusters the data agglomeratively.
		Data is stored in a list of nodes, which will be merged.
		Uses a cache to quickly recover node distances.
	"""
	start = time()
	(nodes, cache, nodeIndexer) = bootstrap_clustering(data)
	print "\tClustering from", len(nodes), "nodes to", final_size
	nodes = slow_agglomerative_procedure(nodes, final_size, cache, nodeIndexer)
	stop = time()
	print "\tProcess took", stop - start, "seconds"
	return nodes

def fag_clustering(data, fraction=0.01, final_size=500):
	"""
		Fast AGglomerative clustering.
	"""

	start = time()
	(nodes, cache, nodeIndexer) = bootstrap_clustering(data)

	while not len(nodes) == final_size:
		thisChunkSize = int((len(nodes) - final_size) * fraction)
		if thisChunkSize < 3 :
			print "\tNow finishing by", len(nodes) - final_size, "more single clusterings"
			nodes = slow_agglomerative_procedure(nodes, final_size, cache, nodeIndexer)
			stop = time()
			print "\tProcess took", stop - start, "seconds"
			return nodes
		else:
			if thisChunkSize > 10:
				print "\t\tWorking", thisChunkSize
			maxlist = MaxMaintainer(thisChunkSize)

			# Use a double for loop to get all node index pairs and get their value from the cache.
			for i in xrange(len(nodes)-1):
				cache_dic = cache[nodes[i].index]
				for j in xrange(i+1,len(nodes)): # Restrict second loop to avaid symetries.
					sim = cache_dic[nodes[j].index]
					maxlist.add((i,j), sim)

			limitset = maxlist.top

			indexesSet = set()
			pairs = []
			for (i, j) in [ x[0] for x in limitset ]:
				n1 = nodes[i].index
				n2 = nodes[j].index
				if n1 not in indexesSet and n2 not in indexesSet:
					indexesSet.add(n1)
					indexesSet.add(n2)
					pairs.append((i,j))

			nodePairs = [ (nodes[i], nodes[j]) for (i,j) in pairs ]
			if thisChunkSize > 10:
				print "\t\t\t", len(nodePairs), "nodes merged."

			# 
			for i in [ x[0] for x in pairs ] + [ x[1] for x in pairs ]:
				nodes[i] = None
			nodes = filter(lambda x : not x == None, nodes)
			

			for index in indexesSet:
				del cache[index]

			for (n1, n2) in nodePairs:
				newNode = combinedNode(n1, n2, nodeIndexer)
				nodeIndexer += 1
				nodes = [newNode] + nodes
				cache_dic = dict() # This will be filled now, and then added to the cache.
				for i in xrange(1, len(nodes)):
					sim = newNode.similarity(nodes[i])
					cache_dic[nodes[i].index] = sim
				cache[newNode.index] = cache_dic # Finally register the new cache dictionary.
	stop = time()
	print "\tProcess took", stop - start, "seconds"
	return nodes

def read_args():
	assert len(sys.argv) == 7
	vecs = sys.argv[1]
	coc_location = sys.argv[2]
	descriptors_name = sys.argv[3]
	limit = int(sys.argv[4])
	clusternumber = int(sys.argv[5])
	fast = sys.argv[6] == "True"
	return (vecs, coc_location, descriptors_name, limit, clusternumber, fast)

if __name__ == '__main__':
	# pypy agglomerative.py ../data/wordvectors/enwiki8.relevant.vectors ../../cocs/enwiki8_coc ../../cluster_descriptors/enwiki8.2000x500.clust-desc 2000 500
	(vecs, coc_location, descriptors_name, limit, clusternumber, fast) = read_args()
	print "Loading vectors"
	data = load_vectors(vecs, limit).items()
	print "Clustering"

	if fast:
		nodes = fag_clustering(data, 0.03, clusternumber)
	else:
		nodes = agglomerative_clustering(data, clusternumber)
	print "Saving clusters"
	save_clusters_to_file(nodes, "clusters.tmp")
	print "Converting clusters to coc representations"
	os.system("python clusters_to_cocs.py clusters.tmp " + coc_location + " " + descriptors_name)
	# os.remove("clusters.tmp")






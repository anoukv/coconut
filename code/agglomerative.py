from fast_utils import normalizeVec, load_vectors

from math import sqrt
from time import time
import os, sys

class MaxMaintainer:
	"""
		Fast way to maintain a top n of a list of items.
		Initiate with a limit and add elements. Only keeps the best _limit_  number of elements.
		Runs in O(n) as opposed to sort()[:limit] and uses _limit_ memory
	"""
	def __init__(self, limit):
		self.limit = limit
		self.top = [(None, -999)]
		self.full = False

	def add(self, pair, sim):
		"""
			Add a pair with similarity sim.
		"""
		top = self.top
		if self.full:
			# Maybe add to list
			if self.min < sim:
				# Needs to be added because is better than the current worse.
				for i in xrange(len(top)): # Find place to add 
					if top[i][1] < sim:	# Perform insertion, deletion and find new min
						top.insert(i, (pair, sim))
						top.pop()
						self.min = top[-1][1]
						break
				self.top = top
		else:
			# List is not yet full so just find a place to put it:
			for i in xrange(len(top)):
				if top[i][1] < sim:
					top.insert(i, (pair, sim))
					break
			# Just perform some basic administration
			full = len(top) == self.limit
			if full:
				self.min = top[-1][1]
				self.full = True
			self.top = top

class Node:
	"""
		Node class that contains a node center, weight, identifier (words) and indexer
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
	"""
		Just saves the nodes to a file as many sets.
	"""
	f = open(filename, 'w')
	for node in nodes:
		f.write(str(node.identifier))
		f.write("\n")
	f.close()

def slow_agglomerative_procedure(nodes, final_size, cache, nodeIndexer):
	"""
		Performs the 'regular' one-by-one agglomerative process.
		Uses a cach for quick comparison between nodes
	"""
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
	"""
		This bootstraps the different agglomerative clustering methods.
		Meaning that given some data it creates nodes and a cache for the nodes
		cache takes the form of a double dictionary: cache [ nodeID1 ] [ nodeID2 ] -> similarity(nodeID1, nodeID2)
		Double dic means better locality for looping, and can easily throw away large chunks when nodes merge.
	"""
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

def fag_clustering(data, fraction=0.01, final_size=500, minSize=10):
	"""
		Fast AGglomerative clustering.
		Clusters in batches of up to a given fraction of the number of joins that still need to be performed.
		Finishes the last iterations with regular clusterings.
		Uses the MaxMaintainer class to maintain a set of best matches.
		The nodeIndexer is used to give a unique nodeID to each node and find them fast in the cache, without depending on their location in the list of nodes.
	"""

	start = time()
	(nodes, cache, nodeIndexer) = bootstrap_clustering(data)

	while len(nodes) > final_size:
		thisChunkSize = int((len(nodes) - final_size) * fraction)
		if thisChunkSize < 3 : # Chick if we shouldn't finish with regular clustering
			print "\tNow finishing by", len(nodes) - final_size, "more single clusterings"
			nodes = slow_agglomerative_procedure(nodes, final_size, cache, nodeIndexer)
		else:
			# Will be finding a batch of merges
			if thisChunkSize > 15:
				print "\t\tWorking", thisChunkSize

			# maxlist to find thisChunkSize best node pairs
			maxlist = MaxMaintainer(thisChunkSize)

			# Use a double for loop to get all node index pairs and get their value from the cache.
			for i in xrange(len(nodes)-1):
				cache_dic = cache[nodes[i].index]
				for j in xrange(i+1,len(nodes)): # Restrict second loop to avaid symetries.
					sim = cache_dic[nodes[j].index]
					maxlist.add((i,j), sim)

			limitset = maxlist.top

			# Sometimes nodes will be very similar to multiple other nodes.
			# The following lines filter for this event and keeps the most urgen merges
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
			if thisChunkSize > 15:
				print "\t\t\t", len(nodePairs), "nodes merged."

			# Now we remove the nodes from the nodes collection (but keep nodePairs)
			for i in [ x[0] for x in pairs ] + [ x[1] for x in pairs ]:
				nodes[i] = None
			nodes = filter(lambda x : not x == None, nodes)
			
			# Perform some garbage collection on the cache:
			for index in indexesSet:
				del cache[index]

			# Now actually start merging nodes and updating the cache.
			for (n1, n2) in nodePairs:
				newNode = combinedNode(n1, n2, nodeIndexer)
				nodeIndexer += 1
				nodes = [newNode] + nodes
				cache_dic = dict() # This will be filled now, and then added to the cache.
				for i in xrange(1, len(nodes)):
					sim = newNode.similarity(nodes[i])
					cache_dic[nodes[i].index] = sim
				cache[newNode.index] = cache_dic # Finally register the new cache dictionary.

	nodes = filter(lambda x : len(x.identifier) >= minSize, nodes)
	print "\tFound", len(nodes), "clusters."
	stop = time()
	print "\tClustering took", stop - start, "seconds"
	return nodes

def read_args():
	assert len(sys.argv) == 5
	vecs = sys.argv[1]
	limit = int(sys.argv[2])
	clusternumber = int(sys.argv[3])
	minimum = int(sys.argv[4])
	return (vecs, limit, clusternumber, minimum)

if __name__ == '__main__':
	# pypy agglomerative.py ../data/wordvectors/enwiki8.relevant.vectors 2000 500 10
	(vecs, limit, clusternumber, minimum) = read_args()
	print "Loading vectors"
	data = load_vectors(vecs, limit).items()
	print "Clustering"

	nodes = fag_clustering(data, 0.03, clusternumber, minimum)


	print "Saving clusters"
	clusterName = "../data/agg_wordclusters/cluster_"
	clusterName += str(limit) + "x" + str(clusternumber) + "x" + str(minimum)
	save_clusters_to_file(nodes, clusterName)
	print "Done!"







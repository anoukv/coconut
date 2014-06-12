

class Node:
	def __init__(self, center, weight, identifier):
		self.center = center
		self.weight = weight
		self.identifier = identifier

	def similarity(self, otherNode):
		return sum( [ x * y for (x,y) in zip(self.center, otherNode.center) ] )

def combinedNode(n1, n2):
	c1, w1, c2, w2 = n1.center, n1.weight, n2.center, n2.weight
	return Node([ (x*w1 + y*w2)/t for (x,y) in zip(c1,c2) ], t, n1.identifier + n2.identifier)

def agglomerative_clustering(data, n=500, verbose=True):
	if verbose:
		print "\tCreating nodes..."

	nodes = []
	for (identifier, center) in data:
		nodes.append( Node(center, 1.0, set(identifier)) )

	data = None
	if verbose:
		print "\tClustering from", len(nodes), "nodes to", n

	while len(nodes) > n:
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
	return nodes














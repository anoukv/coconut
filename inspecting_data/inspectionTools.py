import sys
from math import sqrt
from collections import defaultdict
from matplotlib import pyplot as plt
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

def getHistogramOfSimilarities(vectors, word):
	wordRepresentation = vectors[word]
	dim = len(wordRepresentation)
	histogram = defaultdict(int)
	for wordvector in vectors:
		if wordvector != word:
			rep = vectors[wordvector]
			sim = round(sum([wordRepresentation[i] * rep[i] for i in xrange(dim)])*10)/10
			histogram[sim] += 1
	labels = [x / float(10) for x in range(-9, 10, 1)]
	counts = [histogram[label] for label in labels]

	x = range(len(labels))
	plt.bar(x, counts, align='center', width=0.5)
	plt.xticks(x, labels)
	ymax = max(counts) + 1
	plt.ylim(0, ymax)
	plt.show()

	return histogram

	

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		print "Usage: python inspectionTools.py <PATH TO VECTORS FILE>"
		sys.exit(0)
	filename = sys.argv[1]
	vectors = load_vectors(filename)
	print len(vectors), " words found in wordvector "
	getHistogramOfSimilarities(vectors, 'line')
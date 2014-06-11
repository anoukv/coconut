import sys, random
from math import sqrt
from collections import defaultdict
from matplotlib import pyplot as plt
from Word import Word

def getMean(someListOfNumbers):
	return sum(someListOfNumbers) / float(len(someListOfNumbers))

def getVariance(someListOfNumbers):
	mean = getMean(someListOfNumbers)
	summationResult = 0
	for elem in someListOfNumbers:
		summationResult += (elem - mean)**2
	return summationResult / float(len(someListOfNumbers))

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
		wordClass = Word(word)
		# print word, wordClass
		if wordClass.relevant():
			# print "Keeping: ", word, wordClass.pos()
			words[word.lower()] = vector
	return words

def getHistogramOfSimilarities(vectors, word):
	wordRepresentation = vectors[word]
	dim = len(wordRepresentation)
	histogram = defaultdict(set)
	for wordvector in vectors:
		if wordvector != word:
			rep = vectors[wordvector]
			sim = round(sum([wordRepresentation[i] * rep[i] for i in xrange(dim)])*10)/10
			histogram[sim].add(wordvector)
	labels = [x / float(10) for x in range(-9, 10, 1)]
	counts = [len(histogram[label]) for label in labels]

	x = range(len(labels))
	plt.bar(x, counts, align='center', width=0.5)
	plt.xticks(x, labels)
	ymax = max(counts) + 1
	plt.ylim(0, ymax)
	plt.show()

	for bin in histogram:
		words = list(histogram[bin])
		if len(words) > 0:
			similarities = []
			for i in range(100):
				word1 = random.choice(words)
				word2 = random.choice(words)
				if word1 != word2:
					wordvec1 = vectors[word1]
					wordvec2 = vectors[word2]
					sim = sum([wordvec1[i] * wordvec2[i] for i in xrange(dim)])
					print word1, word2, sim
					similarities.append(sim)
			if len(similarities) > 0:
				print bin, getMean(similarities), getVariance(similarities)
			print "\n --------------------------------------- \n"
	return histogram

	

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		print "Usage: python inspectionTools.py <PATH TO VECTORS FILE>"
		sys.exit(0)
	filename = sys.argv[1]
	vectors = load_vectors(filename)
	print len(vectors), " words found in wordvector "
	getHistogramOfSimilarities(vectors, 'line')

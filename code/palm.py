import sys, shelve
from collections import defaultdict
from copy import copy

# our own files
from fast_utils import read_file, load_vectors, getAverageWordRep, cosine_similarity, read_sets


def getHistogram(words, clusterCenters, vectors, indexCache):

	# initiate empty histogram
	histogram = [0 for i in range(len(clusterCenters))]
	
	# for every word
	for word in words:

		# check if word has a vector
		if word in vectors:
			# if it was already seen, we can ask for the right index from cache
			if word in indexCache:
				histogram[indexCache[word]] += 1
			# if not; 
			else:
				# get the word's vector
				vector = vectors[word]
				
				# compute the similarity with every cluster center
				sims = [cosine_similarity(vector, x) for x in clusterCenters]

				# the word will be assigned to the cluster that has the highest similarity
				# find its index
				index = sims.index(max(sims))

				# increase the histogram with 1 at the right index
				histogram[index] += 1

				# cache the result
				indexCache[word] = index

	# get the total count from the histogram
	total = float(sum(histogram))
	
	# normalize the histogram (every value between [0, 1])
	histogram = map(lambda x: x / total, histogram)

	return  histogram


def getSVM(word, corpus, rel, vectors, clusterCenters, expansionParam=5, skipsize=5):
	svm = 0
	data = defaultdict(list)
	
	# get contexts
	print "Collecting contexts"
	contexts = getContext(corpus, word, skipsize)

	print "Building subRel"
	relevantWords = rel[word]
	subRel = buildSubRel(rel, relevantWords.keys())

	# init indexCache that contains word => index of agg cluster
	indexCache = dict()
	
	# progress counter and total number of contexts
	counter = 0
	ending = len(contexts)
	
	# for every context
	for context in contexts:
		# for printing progress
		print counter, " / ", ending
		counter+=1

		# expand and clean the context
		expanded = expandAndCleanContext(context, word, subRel, expansionParam)
		
		# get label for expanded context
		label = getLabel(relevantWords, expanded)

		# get the histogram
		histogram = getHistogram(expanded, clusterCenters, vectors, indexCache)
		
		# add histogram with label to the data dictionary 
		data[label].append(histogram)
	
	# print all labels (just for fun, remove later)
	print data.keys()

	# return the data
	return data


# builds a subversion of the relatedness matrix rel, that contains the words in relWord
def buildSubRel(rel, relevantWords):
	
	# init dict
	subRel = dict()
	
	# for every relevant word
	for word in relevantWords:
		
		# add its vector to subRel
		subRel[word] = copy(rel[word])
	return subRel


# chooses a 'label' (may be interpreted as a substitute word) for the word that has 
# relatedness vector wordRel from the words in expanded context
def getLabel(wordRel, expandedContext):
	# init
	label = None
	highesetRel = None
	
	# we will only consider candidates that are in the word's relatedness vector
	expandedContext = filter(lambda x: x in wordRel, expandedContext)

	# iterate over all candidates to find the one with the highest relatedness score
	for candidate in expandedContext:
		relScore = wordRel[candidate]
		if relScore > highesetRel:
			highesetRel = relScore
			label = candidate
	return label


# expands and cleans the context (cleaning is basically taking out the word, it could be that the word appears twice withim window)
def expandAndCleanContext(context, word, rel, expansionParam):
	
	# remove word from context
	newContext = filter(lambda x: x != word, context)
	
	# for every word in the context
	for w in newContext:
		
		# if the word is in rel
		if w in rel:
			
			# sort the related words and keep 0-expansionParam, then throw away the scroes and take out 'word' 
			# add this to new context
			wRel = filter(lambda x: x != w, map(lambda x: x[0], sorted(rel[w].items(), key = lambda x: x[1], reverse = True)))[0:expansionParam]
			newContext =  filter(lambda x: x != word, wRel + newContext)
	
	return newContext


# get all contexts with windowsize skipsize*2 in which word occurs as the mid word
def getContext(inpt, wordOfInterest, skipsize):

	# initiate the contexts
	contexts = []	
	
	# size of the queue is 2 times the skipsize + 1 for the mid (so there are skipsize words on the left and on the right)
	queueSize = skipsize * 2 + 1

	# mid index is skipsize
	queueMid = skipsize
	
	# returns True if the lenght of x equals the queuesize, meaning x is filled
	queueIsReady = lambda x : len(x) == queueSize
	
	# pushes elemet to the queue
	# if necessary pops first element
	def push(element, queue):
		queue.append(element)
		if len(queue) > queueSize:
			queue.pop(0)
	
	# init empty queue
	queue = []

	# for every word in the corpus
	for word in inpt:
		# push the word onto the queue
		push(word, queue)

		# if the queue is ready
		if queueIsReady(queue):

			# get the middle word
			mid = queue[queueMid]

			# if the middle word equals the word of interest
			if mid == wordOfInterest:

				# add the queue to the contexts
				contexts.append(copy(queue))	
	
	return contexts

if __name__ == "__main__":
	
	print "Welcome to PALM!"
	
	if len(sys.argv) < 5:
		print "USAGE: python palm.py <TEXT FILE> <PATH TO COC> <PATH TO CLUSTERS> <PATH TO VECTORS>"
		sys.exit()

	# read all files
	textfile = sys.argv[1]
	relFile = sys.argv[2] + "_rel"
	clusterFile = sys.argv[3]
	vecFile = sys.argv[4]
	
	# open the rel
	rel = shelve.open(relFile)
	
	# open the vectors
	print "Loading vectors"
	vecs = load_vectors(vecFile)
	
	# read clusters and get their cluster centers by taking the average...
	print "Reading agglomerative cluster centers"
	agglomerativeClusterCenters = [getAverageWordRep(x, vecs) for x in read_sets(clusterFile)]

	# call getSVM
	getSVM('bat', read_file(textfile), rel, vecs, agglomerativeClusterCenters, expansionParam=5, skipsize=5)

	# close rel
	rel.close()

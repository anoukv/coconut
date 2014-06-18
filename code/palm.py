import sys, shelve
from collections import defaultdict
from fast_utils import read_file, load_vectors, getAverageWordRep, cosine_similarity
from copy import copy
from agglomerative import fag_clustering
from clusters_to_cocs import read_sets

def getSVM(word, corpus, rel, vectors, clusterCenters, expansionParam=5, skipsize=5):
	svm = 0
	data = defaultdict(set)
	
	# get contexts
	print "Collecting contexts"
	contexts = getContext(corpus, word, skipsize)

	print "Building subRel"
	wordRel = rel[word]
	subRel = buildSubRel(rel, wordRel)
	vocabulary = vectors.keys()
	for context in contexts:
		
		# expand every context
		print "Expanding and labeling"
		expanded = expandAndCleanContext(context, word, subRel, expansionParam)
		histogramOfAgglomerativeAssignments = [0 for i in range(len(clusterCenters))]
		# get label for expanded context
		label = getLabel(wordRel, expanded)
		data[label].add(tuple(expanded))
		print "Label: ", label
		print context
		for w in expanded:
			if w in vocabulary:
				wvec = vectors[w]
				sims = [cosine_similarity(wvec, x) for x in clusterCenters]
				index = sims.index(max(sims))
				histogramOfAgglomerativeAssignments[index] += 1
		totat = float(sum(histogramOfAgglomerativeAssignments))
		print map(lambda x: x / totat, histogramOfAgglomerativeAssignments)
	return data

def buildSubRel(rel, relWord):
	relVoc = relWord.keys()
	subRel = dict()
	for word in relVoc:
		subRel[word] = copy(rel[word])
	return subRel

def getLabel(wordRel, expandedContext):
	# init
	label = None
	highesetRel = None
	
	# we will only consider candidates that are in the word relatedness dictionary
	expandedContext = filter(lambda x: x in wordRel, expandedContext)

	# iterate over all candidates to find the highest
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
	# print word in newContext
	# get the vocabulary stored in rel
	relVoc = rel.keys()
	# print context, newContext
	# for every word in the context
	for w in newContext:
		# if the word is in rel
		if w in relVoc:
			# sort the related words and keep 0-expansionParam, then throw away the scroes and take out 'word' 
			# add this to new context
			wRel = filter(lambda x: x != w, map(lambda x: x[0], sorted(rel[w].items(), key = lambda x: x[1], reverse = True)))[0:expansionParam]
			#print w, wRel
			newContext =  filter(lambda x: x != word, wRel + newContext)
	return newContext

# get all contexts with windowsize skipsize*2 in which word occurs (as the mid word, maybe expand this?)
def getContext(inpt, wordOfInterest, skipsize):
	contexts = []	
	
	queueSize = skipsize * 2 + 1
	queueMid = skipsize
	
	queueIsReady = lambda x : len(x) == queueSize
	
	def push(element, queue):
		queue.append(element)
		if len(queue) > queueSize:
			queue.pop(0)
	
	queue = []
	for word in inpt:
		push(word, queue)
		if queueIsReady(queue):
			mid = queue[queueMid]
			if mid == wordOfInterest:
				#print queue
				contexts.append(copy(queue))	
	return contexts

if __name__ == "__main__":
	
	print "Welcome to PALM!"
	
	if len(sys.argv) < 5:
		print "USAGE: python palm.py <TEXT FILE> <PATH TO COC> <PATH TO CLUSTERS> <PATH TO VECTORS>"
		sys.exit()
	textfile = sys.argv[1]
	relFile = sys.argv[2] + "_rel"
	clusterFile = sys.argv[3]
	vecFile = sys.argv[4]
	
	rel = shelve.open(relFile)
	print "Loading vectors"
	vecs = load_vectors(vecFile)
	# fag_clustering(vecs.items(), final_size = 50)
	# print read_sets()
	print "Reading agglomerative cluster centers"
	agglomerativeClusterCenters = [getAverageWordRep(x, vecs) for x in read_sets(clusterFile)]
	getSVM('bat', read_file(textfile), rel, vecs, agglomerativeClusterCenters, expansionParam=2, skipsize=5)



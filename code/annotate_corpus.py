import sys, os
import shelve
from palm import expandAndCleanContext, getHistogram
from collections import defaultdict
from fast_utils import read_file, load_vectors, getAverageWordRep, cosine_similarity, read_sets
import pickle
from sklearn import svm
from copy import copy

# inpt - the actual corpus
# words of interest - list of words we want to relabel
# skipsize - window we want around the word
# vectors - word vectors
# pathToExpansionCache - path to file that has all expansion chaches
# expansionParam - parameter that determines how many words will be append to the context per word in the context
# rel - relatedness matrix (shelve object)
# clusterCenters - list of cluster centers
# expansionCacheInfo - identifiiers for expansionCache files
# svmFileInfo - identifiers for svm files
def getContext(inpt, wordsOfInterest, skipsize, vectors, pathToExpansionCache, expansionParam, rel, clusterCenters, expansionCacheInfo, svmFileInfo, pathToSVMFile):

	# initiate the contexts
	annotated = []	
	
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

	indexCaches = defaultdict(dict)

	total = len(inpt)

	partVoc = set(vectors.keys())

	labels = defaultdict(int)
	jointVocCache = dict()
	# for every word in the corpus
	for i, word in enumerate(inpt):
		# push the word onto the queue
		push(word, queue)

		# if the queue is ready
		if queueIsReady(queue):

			# get the middle word
			mid = queue[queueMid]
			# print mid
			# if the middle word equals the word of interest
			if mid in wordsOfInterest:

				# get the context
				context = copy(queue)

				# get jointVocabulary
				if mid not in jointVocCache:
					jointVocabulary = partVoc.intersection(set(rel[mid].keys()))
					jointVocCache[mid] = jointVocabulary
				else:
					jointVocabulary = jointVocCache[mid]
				
				# open expansionsCache
				expansionCache = shelve.open(pathToExpansionCache + mid + expansionCacheInfo)
				
				# get expanded context
				expandedContext = expandAndCleanContext(context, mid, rel, expansionParam, jointVocabulary, expansionCache)
				
				# close expansionCache
				expansionCache.close()
				
				# get the indexCache (the right one)
				indexCache = indexCaches[mid]

				# get the histogram
				histogram = getHistogram(expandedContext, clusterCenters, vectors, indexCache)

				# load the svm for mid
				svmForMid = pickle.load(open(pathToSVMFile +  mid + svmFileInfo, 'r'))

				# predict the label
				label = svmForMid.predict(histogram)[0]

				# print the info


				# add label to word
				mid = mid + "_" + label
				if i % 100 == 0:
					print i, "/", total, mid, label, context

				labels[mid]+=1
		
				# append to word to annotation
				# NOTE we are missing five words at the beginning and the end
				annotated.append(mid + " ")
			annotated.append(mid + " ")
	for key in labels:
		print key, labels[key]
	# print labels
	return annotated


if __name__ == "__main__":
	print "Welcome to PALM annotation tool!"
	
	if len(sys.argv) < 8:
		print "USAGE: python annotate_corpus.py <TEXT FILE> <PATH TO REL> <PATH TO CLUSTERS> <PATH TO VECTORS> <PATH TO SVM FILE> <PATH TO EXPANSIONCACHES> <PATH TO OUTPUT>"
		sys.exit()

	# read all files
	textfile = sys.argv[1]
	relFile = sys.argv[2]
	clusterFile = sys.argv[3]
	vecFile = sys.argv[4]
	pathToSVMFile = sys.argv[5]
	pathToExpansionCache = sys.argv[6]
	pathToOutput = sys.argv[7]
	
	# open the rel
	rel = shelve.open(relFile)
	
	# open the vectors
	print "Loading vectors"
	vecs = load_vectors(vecFile)
	
	# read clusters and get their cluster centers by taking the average...
	print "Reading agglomerative cluster centers"
	clusterCenters = [getAverageWordRep(x, vecs) for x in read_sets(clusterFile)]
	# IT MIGHT HAPPEN THAT SOME CLUSTER CENTERS ARE ()? HOW IS THIS POSSIBLE?
	
	# set some remaining parameters
	expansion = 5
	window = 5
	svmFileInfo = '_SVM_' + clusterFile.split('/')[-1] + "_expansionParam" + str(expansion) + "_window" + str(window)
	expansionCacheInfo = "_expansionParam_"  + str(expansion)

	wordsOfInterest = [x.split("_")[0] for x in os.listdir(pathToSVMFile)]
	print wordsOfInterest
	annotated = getContext(read_file(textfile), wordsOfInterest, window, vecs, pathToExpansionCache, expansion, rel, clusterCenters, expansionCacheInfo, svmFileInfo, pathToSVMFile)

	f = open(pathToOutput, 'w')
	f.write("".join(annotated))
	f.close()


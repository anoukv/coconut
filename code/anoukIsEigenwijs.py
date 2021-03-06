import sys, os
import shelve
from palm import expandAndCleanContext, getHistogram
from fast_utils import read_file, load_vectors, getAverageWordRep, read_sets
import pickle
from sklearn import svm
from copy import copy
from time import time
from palm import getContext as test

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
def getContext(inpt, wordsOfInterest, skipsize, vectors, pathToExpansionCache, expansionParam, rel, clusterCenters, expansionCacheInfo, svmFileInfo, pathToSVMFile, f):
	# pushes elemet to the queue
	# if necessary pops first element
	def push(element, queue):
		queue.append(element)
		queue.pop(0)
	# size of the queue is 2 times the skipsize + 1 for the mid (so there are skipsize words on the left and on the right)
	queueSize = skipsize * 2 + 1

	# mid index is skipsize
	queueMid = skipsize

	# init empty queue
	queue = [ inpt.pop(0) for _ in xrange(queueSize) ]

	expansionCache = shelve.open(pathToExpansionCache + wordsOfInterest + expansionCacheInfo)
	indexCache = dict()

	total = len(inpt)

	partVoc = set(vectors.keys())
	jointVocabulary = partVoc.intersection(set(rel[wordsOfInterest].keys()))

	# load the svm for mid
	svmName = pathToSVMFile +  wordsOfInterest + svmFileInfo

	# predict the label
	thisSVM = pickle.load(open(svmName, 'r'))

	start = time()
	# for every word in the corpus

	print "Starting.."
	for i in xrange(total):
		word = inpt.pop(0)

		# push the word onto the queue
		push(word, queue)

		# get the middle word
		mid = queue[queueMid]
		# print mid
		# if the middle word equals the word of interest
		if mid == wordsOfInterest:

			# get the context
			context = copy(queue)
			print context

			# get expanded context
			expandedContext = expandAndCleanContext(context, mid, rel, expansionParam, jointVocabulary, expansionCache)
			
			# get the histogram
			histogram = getHistogram(expandedContext, clusterCenters, vectors, indexCache)
			
			label = thisSVM.predict(histogram)[0]

			# add label to word
			if mid != None and label != None:
				mid = mid + "_" + label		
		
		f.write(mid + " ")

		if (i % 50000 == 0 or i == 10000) and i != 0:
			t = ( time() - start ) 
			eta = t / i * ( total - i )
			print "Iteration:", i
			print "\tEstimated time remaining:", eta / float(60) / float(60)

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
	inpt = read_file(textfile)

	start = time()
	for i, word in enumerate(wordsOfInterest):
		if word != ".DS":
			print "Working on word: ", word, i, "/", len(wordsOfInterest) - 2
			# f = open(pathToOutput, 'w')
			test(inpt, word, window)
			# getContext(inpt, word, window, vecs, pathToExpansionCache, expansion, rel, clusterCenters, expansionCacheInfo, svmFileInfo, pathToSVMFile, f)
			# f.close()

	stop = time()
	print "I spent", int(stop-start+0.5), "seconds."



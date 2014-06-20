import sys, os
from utils import load_task, Word
from fast_utils import cosine_similarity, load_vectors, spearman, getAverageWordRep, read_sets
import pickle
from sklearn import svm
import shelve
from palm import expandAndCleanContext, getHistogram

def decideOnLabel(word, context, vectors, clusterCenters, expansionParam, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, pathToSVMFile, svmFileInfo):
	
	# get the jointVocabulary
	if word not in jointVocCache:
		jointVocabulary = partVoc.intersection(set(rel[word].keys()))
		jointVocCache[word] = jointVocabulary
	else:
		jointVocabulary = jointVocCache[word]

	# open expansionsCache
	expansionCache = shelve.open(pathToExpansionCache + word + expansionCacheInfo)
	
	# get expanded context
	expandedContext = expandAndCleanContext(context, word, rel, expansionParam, jointVocabulary, expansionCache)
	# close expansionCache
	expansionCache.close()
	
	# get the indexCache (the right one)
	indexCache = dict()

	# get the histogram
	histogram = getHistogram(expandedContext, clusterCenters, vectors, indexCache)

	# load the svm for mid
	svmForWord = pickle.load(open(pathToSVMFile +  word + svmFileInfo, 'r'))

	# predict the label
	label = svmForWord.predict(histogram)[0]
	return label



if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 7:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO WORDVECTORS> <PATH TO SVMS> <PATH TO CLUSTERS> <PATH TO REL> <PATH TO EXPANSIONSCACHE>"
		sys.exit()
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]
	pathToSVMFile = sys.argv[3]
	clusterFile = sys.argv[4]
	relFile = sys.argv[5]
	pathToExpansionCache = sys.argv[6]

	expansion = 5
	window = 5
	svmFileInfo = '_SVM_' + clusterFile.split('/')[-1] + "_expansionParam" + str(expansion) + "_window" + str(window)
	expansionCacheInfo = "_expansionParam_"  + str(expansion)
	
	print "Loading rel, task, vector, words that have been disambiguated"
	rel = shelve.open(relFile)
	task, tralala = load_task(taskFilename)
	vectors = load_vectors(vectorsFilename)
	disambiguatedWords = [x.split("_")[0] for x in os.listdir(pathToSVMFile)]

	print "Reading agglomerative cluster centers"
	clusterCenters = [getAverageWordRep(x, vectors) for x in read_sets(clusterFile)]

	print "Starting..."
	# initiate empty ratings
	methodsRating = []
	humanRating = []
	# print tralala
	questions = task.values()

	jointVocCache = dict()
	partVoc = set(vectors.keys())

	print disambiguatedWords
	
	done = 0
	for i in xrange(len(questions)):
		# if i % 100 == 0:
		# 	print i

		question = questions[i]

		word1 = Word(question['word1']).lemma()
		word2 = Word(question['word2']).lemma()
		context1 = [Word(x).lemma() for x in question['context1'].lower().split(' ')]
		context2 = [Word(x).lemma() for x in question['context2'].lower().split(' ')]

		# set finders to false
		w1 = False
		w2 = False
		
		# if word1 has been disambiguated or is in vectors set finder to true
		
		if word1 in disambiguatedWords:
			# print i, "DISAMBIGUATE word 1!", word1
			# print question['context1']
			label = decideOnLabel(word1, context1, vectors, clusterCenters, expansion, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, pathToSVMFile, svmFileInfo)
			w1 = True
			vec1 = vectors[word1 + "_" + label]
		
		elif word1 in partVoc:
			w1 = True
			vec1 = vectors[word1]
			# normal course of action
		
		# if word2 has been disambiguated or is in vectors set finder to true

		if word2 in disambiguatedWords:
			# print i, "DISAMBIGUATE word 2!", word2
			# print question['context2']
			label = decideOnLabel(word2, context2, vectors, clusterCenters, expansion, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, pathToSVMFile, svmFileInfo)
			w1 = True
			vec2 = vectors[word2 + "_" + label]
		
		elif word2 in partVoc:
			w2 = True
			vec2 = vectors[word2]

		# only if both words have been found (somewhere), we continue
		if w1 and w2:
			methodsRating.append(cosine_similarity(vec1, vec2)) 
			humanRating.append(question['rating'])
			done += 1
		# else:
		# 	if not w1:
		# 		print "NOT FOUND", word1
		# 	if not w2: "NOT FOUND ", word2

	# print the spearman correlation
 	print spearman(methodsRating, humanRating)
 	print "Coverage: ", done / float(len(questions)) * 100, "%"

 	rel.close()


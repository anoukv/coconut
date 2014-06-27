import sys, os
from utils import load_task, Word
from fast_utils import cosine_similarity, load_vectors, spearman, getAverageWordRep, read_sets
import pickle
from sklearn import svm
import shelve
from palm import expandAndCleanContext, getHistogram

def decideOnLabel(word, context, vectors, clusterCenters, expansionParam, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, pathToSVMFile, svmFileInfo, disambiguatedWords):
	
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

	expandedContext = filter(lambda x: x  not in disambiguatedWords and x in jointVocabulary, expandedContext)
	
	# get the histogram
	histogram = getHistogram(expandedContext, clusterCenters, vectors, indexCache)

	# load the svm for mid
	svmForWord = pickle.load(open(pathToSVMFile +  word + svmFileInfo, 'r'))

	# predict the label
	label = svmForWord.predict(histogram)[0]
	return label



if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 8:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO WORDVECTORS> <PATH TO SVMS> <PATH TO CLUSTERS> <PATH TO REL> <PATH TO EXPANSIONSCACHE> <Normal vectors>"
		sys.exit()
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]
	pathToSVMFile = sys.argv[3]
	clusterFile = sys.argv[4]
	relFile = sys.argv[5]
	pathToExpansionCache = sys.argv[6]
	normalVecPath = sys.argv[7]

	expansion = 5
	window = 5
	svmFileInfo = '_SVM_' + clusterFile.split('/')[-1] + "_expansionParam" + str(expansion) + "_window" + str(window)
	expansionCacheInfo = "_expansionParam_"  + str(expansion)
	
	print "Loading rel, task, vector, words that have been disambiguated"
	rel = shelve.open(relFile)
	task, tralala = load_task(taskFilename)
	vectors = load_vectors(vectorsFilename)
	normalVectors = load_vectors(normalVecPath)
	disambiguatedWords = [x.split("_")[0] for x in os.listdir(pathToSVMFile)]

	print "Reading agglomerative cluster centers"
	clusterCenters = [getAverageWordRep(x, vectors) for x in read_sets(clusterFile)]

	print "Starting..."
	# initiate empty ratings
	methodsRating = []
	humanRating = []
	otherRating = []
	questions = task.values()

	jointVocCache = dict()
	partVoc = set(vectors.keys())

	print len(disambiguatedWords), "disambiguated words"
	
	done = 0
	for i in xrange(len(questions)):
		question = questions[i]

		word1 = Word(question['word1']).lemma()
		word2 = Word(question['word2']).lemma()
		context1 = [Word(x).lemma() for x in question['context1'].lower().split(' ')]
		context2 = [Word(x).lemma() for x in question['context2'].lower().split(' ')]

		# so we are not using disambiguated words in the context..?
		context1 = filter(lambda x: x in partVoc, context1)
		context2 = filter(lambda x: x in partVoc, context2)

		# set finders to false
		w1 = False
		w2 = False
		
		# if word1 has been disambiguated or is in vectors set finder to true
		if word1 in disambiguatedWords:
			label1 = decideOnLabel(word1, context1, vectors, clusterCenters, expansion, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, pathToSVMFile, svmFileInfo, disambiguatedWords)
			new = word1 + "_" + label1
			if new in vectors:
				vec1 = vectors[word1 + "_" + label1]
				w1 = True
		elif word1 in partVoc:
			label1 = "not ambiguous"
			vec1 = vectors[word1]
			w1 = True

			# normal course of action
		
		# if word2 has been disambiguated or is in vectors set finder to true

		if word2 in disambiguatedWords:
			label2 = decideOnLabel(word2, context2, vectors, clusterCenters, expansion, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, pathToSVMFile, svmFileInfo, disambiguatedWords)
			new = word2 + "_" + label2
			if new in vectors:
				vec2 = vectors[word2 + "_" + label2]
				w2 = True
		elif word2 in partVoc:
			label2 = "not ambiguous"
			vec2 = vectors[word2]
			w2 = True


		# only if both words have been found (somewhere), we continue
		if w1 and w2:
			
			
			score = cosine_similarity(vec1, vec2)
			base = cosine_similarity(normalVectors[word1], normalVectors[word2])

			# if abs(base - score) > 0.3:
				# print question['word1'], label1
				# print question['context1']
				# print question['word2'], label2
				# print question['context2']
				# print i, "\tHuman average: ", question['rating']
				# print i, "\tPALM score", score 
				# print i, "\tBaseline: ", base
				# print i, "\tDifferent between base and palm: ", abs(base - score)

			methodsRating.append(score) 
			humanRating.append(question['rating'])
			otherRating.append(base)
			# if i > 5 and abs(base - score) > 0.3:
			# 	print i, "\t", spearman(methodsRating, humanRating)
			# 	print i, "\t", spearman(otherRating, humanRating)
			done += 1
			# print
			# print

	# print the spearman correlation
 	print "Method: ", spearman(methodsRating, humanRating)
 	# print "Coverage: ", done / float(len(questions)) * 100, "%"
 	print "Baseline: ", spearman(otherRating, humanRating)
 	rel.close()


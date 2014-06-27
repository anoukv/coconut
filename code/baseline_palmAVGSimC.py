import sys, os
from utils import load_task, Word
from fast_utils import cosine_similarity, load_vectors, spearman, getAverageWordRep, read_sets
import pickle
from sklearn import svm
import shelve
from palm import expandAndCleanContext, getHistogram
from collections import defaultdict

def decideOnLabel(word, context, vectors, clusterCenters, expansionParam, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, disambiguatedWords, labels):
	
	def getHistogram2(words, clusterCenters):

		# initiate empty histogram
		histogram = [0 for i in range(len(clusterCenters))]
		
		# for every word
		for vector in words:
			
			# get the word's vector				
			# compute the similarity with every cluster center
			sims = [cosine_similarity(vector, x) for x in clusterCenters]

			for i in xrange(len(sims)):
				histogram[i] += sims[i]

		# get the total count from the histogram
		total = float(sum(histogram))
		
		# normalize the histogram (every value between [0, 1])
		if total > 0:
			histogram = map(lambda x: x / total, histogram)
		#print histogram

		return  histogram
	
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
	
	# get the histogram for the context
	histogram = getHistogram(expandedContext, clusterCenters, vectors, indexCache)

	# now get the histograms for the different word vectors
	wordvectors = [vectors[word + "_" + label] for label in labels]
	histograms = [getHistogram2([vec], clusterCenters) for vec in wordvectors]

	sims = [cosine_similarity(hist, histogram) for hist in histograms]
	simsCorrected = [sim + 1 for sim in sims]
	
	probabilities = [x / float(sum(simsCorrected)) for x in simsCorrected]
	
	return wordvectors, probabilities


def avgSimC(probs1, vecs1, probs2, vecs2):
	if len(probs1) != len(vecs1) or len(probs2) != len(vecs2):
		print "There is a serious problem!"
	
	summationResult = 0
	for i in xrange(len(probs1)):
		for j in xrange(len(probs2)):
			summationResult += (probs1[i] * probs2[j] * cosine_similarity(vecs1[i], vecs2[j]))
	summationResult = summationResult / float(len(probs1) * len(probs2))
	return summationResult


if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 6:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO WORDVECTORS> <PATH TO CLUSTERS> <PATH TO REL> <PATH TO EXPANSIONSCACHE>"
		sys.exit()
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]
	clusterFile = sys.argv[3]
	relFile = sys.argv[4]
	pathToExpansionCache = sys.argv[5]

	expansion = 5
	window = 5
	expansionCacheInfo = "_expansionParam_"  + str(expansion)
	
	print "Loading rel, task, vector, words that have been disambiguated"
	rel = shelve.open(relFile)
	task, _ = load_task(taskFilename)
	vectors = load_vectors(vectorsFilename)

	print "Reading agglomerative cluster centers"
	clusterCenters = [getAverageWordRep(x, vectors) for x in read_sets(clusterFile)]

	print "Starting..."
	# initiate empty ratings
	methodsRating = []
	humanRating = []
	questions = task.values()

	jointVocCache = dict()
	partVoc = set(vectors.keys())


	disambiguatedWords = defaultdict(set)
	for word in vectors:
		if "_" in word:
			splittedWords = word.split("_")
			disambiguatedWords[splittedWords[0]].add(splittedWords[1])

	print len(disambiguatedWords), "disambiguated words"

	
	done = 0
	for i in xrange(len(questions)):
		# print
		# print
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
			labels = disambiguatedWords[word1]
			vec1, probs1 = decideOnLabel(word1, context1, vectors, clusterCenters, expansion, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, disambiguatedWords, labels)
			w1 = True
		elif word1 in partVoc:
			vec1 = [vectors[word1]]
			probs1 = [1]
			w1 = True
		

		if word2 in disambiguatedWords:
			labels = disambiguatedWords[word2]
			vec2, probs2 = decideOnLabel(word2, context2, vectors, clusterCenters, expansion, rel, partVoc, jointVocCache, pathToExpansionCache, expansionCacheInfo, disambiguatedWords, labels)
			w2 = True
		elif word2 in partVoc:
			vec2 = [vectors[word2]]
			probs2 = [1]
			w2 = True



		# only if both words have been found (somewhere), we continue
		if w1 and w2:
			# print word1, word2
			# print probs1
			# print probs2
			sim = avgSimC(probs1, vec1, probs2, vec2)
			print sim
			methodsRating.append(sim) 
			humanRating.append(question['rating'])
			if len(methodsRating) % 100 == 0 and len(methodsRating) > 0:
				print "\t", i, spearman(methodsRating, humanRating)
			done += 1

	# print the spearman correlation
 	print spearman(methodsRating, humanRating)
 	print "Coverage: ", done / float(len(questions)) * 100, "%"

 	rel.close()


from kmeans import kmeans_process
from copy import copy
from collections import defaultdict

# deletes all the keys from dic that are not in keysToKeep
def deleteSomeKeys(keysToKeep, dic):
	intersection = keysToKeep.intersection(set(dic.keys()))
	new_dic = dict()
	for key in intersection:
		new_dic[key] = dic[key]
	return new_dic

# prepares the data for a word, that is necessary to create the two senses
def prepareExtraction(word, coc):

	# get co-occurences for the word
	wordCOC = copy(coc[word])
	coOccuringWords = set(wordCOC.keys())

	cococ = dict()
	for bla in coOccuringWords:
		vector = copy(coc[bla])
		vector = deleteSomeKeys(coOccuringWords, vector)
		cococ[bla] = vector

	return (wordCOC, cococ)

# extracts the two senses of a word
def extractSenses((word, preparation)):
	(wordCOC, cococ) = preparation

	# sort from high relatedness to low relatedness
	# cut off half, top half will be used, other half will be things that are relevant to all sensess
	tupleList = sorted(wordCOC.items(), key=lambda x: x[1], reverse = True)
	
	relevantCocWords = tupleList[:len(tupleList)/2]
	theRest = tupleList[len(tupleList)/2:]

	cocWords = [ elem[0] for elem in relevantCocWords ]
	relevantToAll = [elem[0] for elem in theRest]

	# for every co-occuring word with the word
	# we save the vector with co-occuring words (only containing words from cocWords)
	# this collection will be datapoints
	listOfDatapoints = [ cococ[elem] for elem in cocWords ]

	# Garbage collection
	cococ = None

	# cluster all co-occurence vectors
	clusters = kmeans_process(listOfDatapoints)
	
	# find out which term belongs to which cluster
	wordAssignemnts = defaultdict(list)
	for i, cocWord in enumerate(cocWords):
		bestClusterID = "NONE"
		bestDistance = 2
		for clusterID in clusters:
			dist = clusters[clusterID].distance(listOfDatapoints[i])
			if dist < bestDistance:
				bestDistance = dist
				bestClusterID = clusterID
		wordAssignemnts[bestClusterID].append(cocWord)
	
	# get the cluster distance
	clusterDistance = clusters[0].cluster_distance(clusters[1])
	
	# make a new representations for the different senses of the words
	# save also the cluster distance for future reference
	senses = dict()
	senses['clusterDistance'] = clusterDistance

	# for all clusters, we will now make a new sense of the word
	# the sense will contain the relevantToAll words and the words assigned to the specific cluster
	for key in wordAssignemnts:
		sense = copy(wordCOC)
		sense = deleteSomeKeys(set(wordAssignemnts[key]+relevantToAll), sense)
		senses[key] = sense

	# save the different sences of the word
	return (word, senses)

# ARGUMENTS: word, coc_rel and coc_voc (already opened with shelve)
# gives us a new dictionary with multiple senses of the words
# not all words will be in this dictionary, only the words for which 
# multiple senses were actually found
def makeNewCOCS(word, rel):
	# here we cluster! 
	preparation = prepareExtraction(word, rel)
	(word, senses) = extractSenses((word, preparation))
	return senses



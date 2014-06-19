from time import time
import sys, shelve
from utils import *
from fast_utils import cosine_similarity
from Word import Word


# expands and cleans the context (cleaning is basically taking out the word, it could be that the word appears twice withim window)
def expandAndCleanContext(context, word, rel, rel_keys, rel_cache, expansionParam):
	# remove word from context
	newContext = filter(lambda x: x != word, context)
	new = []	
	# print context, newContext
	# for every word in the context
	for w in newContext:
		# if the word is in rel
		if w in rel_keys:
			# sort the related words and keep 0-expansionParam, then throw away the scroes and take out 'word' 
			# add this to new context
			if not w in rel_cache:
				rel_cache[w] = rel[w]
			wRel = filter(lambda x: x not in [w, word], map(lambda x: x[0], sorted(rel_cache[w].items(), key = lambda x: x[1], reverse = True)[0:expansionParam]))
			#print w, wRel
			new += wRel
	return newContext + new

# maybe we can also select a word from the expanded context that is most similar vector wise
def getLabel(wordRel, expandedContext, vectors, word):
	# init
	label = word
	highesetRel = None
	
	# we will only consider candidates that are in the word relatedness dictionary
	expandedContext = filter(lambda x: x in wordRel, expandedContext)

	# iterate over all candidates to find the highest
	for candidate in expandedContext:
		relScore = wordRel[candidate]
		if relScore > highesetRel and candidate in vectors:
			highesetRel = relScore
			label = candidate
	return label

if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 4:
		print "USAGE: python baselline_labels .py <PATH TO TASK> <PATH TO WORDVECTORS> <PATH TO COC_>"
		sys.exit()
	start = time()
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]
	relFilename = sys.argv[3]
	print "Loading task"
	task, _ = load_task(taskFilename)
	print "Loading vectors"
	vectors = load_vectors(vectorsFilename)
	print "Loading coc_rel"
	rel = shelve.open(relFilename+"rel")
	rel_keys = set(rel.keys())
	rel_cache = dict()
	vocabulary = shelve.open(relFilename+"voc")
	# print vocabulary
	print "Loading vocabulary"
	print "OK let's go"
	methodsRating = []
	humanRating = []
	
	expansionParam = 2

	questions = task.values()

	stop = time()
	print "Loading took", stop - start, "seconds"
	start = time()
	for i in xrange(len(questions)):
		question = questions[i]
		
		word1 = Word(question['word1']).lemma().encode('ascii','ignore')
		word2 = Word(question['word2']).lemma().encode('ascii','ignore')
		context1 = [Word(x).lemma().encode('ascii','ignore') for x in question['context1'].lower().split(' ')]
		context2 = [Word(x).lemma().encode('ascii','ignore') for x in question['context2'].lower().split(' ')]
		
		if word1 in vectors and word2 in vectors: # and word1 == word2:
			print "\tIteration", i
			if word1 in vocabulary:
				newContext = expandAndCleanContext(context1, word1, rel, rel_keys, rel_cache, expansionParam)
				if not word1 in rel_cache:
					rel_cache[word1] = rel[word1]
				newWord = getLabel(rel_cache[word1], newContext, vectors, word1)
				print "\t\t\tW1: replacing", word1, "with", newWord

				# check if this word is actually available as a vector
				vec1 = vectors[newWord]
			else:
				vec1 = vectors[word1]

			if word2 in vocabulary:
				newContext = expandAndCleanContext(context2, word2, rel, rel_keys, rel_cache, expansionParam)
				if not word2 in rel_cache:
					rel_cache[word2] = rel[word2]
				newWord  = getLabel(rel_cache[word2], newContext, vectors, word2)
				print "\t\t\tW2: replacing", word2, "with", newWord

				# check if this word is actually available as a vector
				vec2 = vectors[newWord]
			else:
				vec2 = vectors[word2]
				
			methodsRating.append(cosine_similarity(vec1, vec2))
			humanRating.append(question['rating'])
			if len(methodsRating) > 2:
				print "\t\tSpearman: ",spearman(methodsRating, humanRating)
		else:
			# print "No rating here..."
			pass

	stop = time()
	print "Time:", stop - start

 	print spearman(methodsRating, humanRating)


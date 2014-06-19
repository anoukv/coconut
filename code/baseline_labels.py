import sys, shelve
from utils import *
from fast_utils import cosine_similarity
from Word import Word

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

# maybe we can also select a word from the expanded context that is most similar vector wise
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

def getLabel2(wordVector, expandedContext, vectors):
	bestSim = None
	bestWord = None

	for candidate in expandedContext:
		if candidate in vectors:
			sim = cosine_similarity(vectors[candidate], wordVector)
			if sim > bestSim:
				bestSim = sim
				bestWord = candidate
	return bestWord

if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 4:
		print "USAGE: python baselline_labels .py <PATH TO TASK> <PATH TO WORDVECTORS> <PATH TO COC_>"
		sys.exit()
	
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]
	relFilename = sys.argv[3]
	print "Loading task"
	task, _ = load_task(taskFilename)
	print "Loading vectors"
	vectors = load_vectors(vectorsFilename)
	print "Loading coc_rel"
	rel = shelve.open(relFilename+"rel")
	vocabulary = shelve.open(relFilename+"voc")
	# print vocabulary
	print "Loading vocabulary"
	print "OK let's go"
	methodsRating = []
	humanRating = []
	
	expansionParam = 5

	for key in sorted(task.keys()):
		print key
		question = task[key]
		
		word1 = Word(question['word1']).lemma().encode('ascii','ignore')
		word2 = Word(question['word2']).lemma().encode('ascii','ignore')
		context1 = [Word(x).lemma().encode('ascii','ignore') for x in question['context1'].lower().split(' ')]
		context2 = [Word(x).lemma().encode('ascii','ignore') for x in question['context2'].lower().split(' ')]
		
		if word1 in vectors and word2 in vectors and word1 == word2:
			if word1 in vocabulary:
				print "Expanding context"
				newContext = expandAndCleanContext(context1, word1, rel, expansionParam)
				#newWord = getLabel(rel[word1], newContext)
				newWord = getLabel2(vectors[word1], newContext, vectors)
				print "replacing ", word1, " with ", newWord

				# check if this word is actually available as a vector
				vec1 = vectors[newWord]
			else:
				vec1 = vectors[word1]

			if word2 in vocabulary:
				newContext = expandAndCleanContext(context2, word2, rel, expansionParam)
				#newWord = getLabel(rel[word2], newContext)
				newWord = getLabel2(vectors[word2], newContext, vectors)
				print "replacing ", word2, " with ", newWord

				# check if this word is actually available as a vector
				vec2 = vectors[newWord]
			else:
				vec2 = vectors[word2]
				
			methodsRating.append(cosine_similarity(vec1, vec2))
			humanRating.append(question['rating'])
		else:
			print "No rating here..."

		if len(methodsRating) > 5:
			print spearman(methodsRating, humanRating)
 
 	print spearman(methodsRating, humanRating)


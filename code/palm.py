import sys, shelve

def getSVM(word, expansionParam=5):
	svm = 0
	return svm

def getLabel(word, expandedContext, rel):
	
	# init
	label = None
	highesetRel = None
	
	# get word relatedness dictionary
	wordRel = rel[word]

	# we will only consider candidates that are in the word relatedness dictionary
	expandedContext = filter(lambda x: x in wordRel, expandedContext)

	# iterate over all candidates to find the highest
	for candidate in expandedContext:
		relScore = wordRel[expandedContext]
		if relScore > highesetRel:
			highesetRel = relScore
			label = candidate
	return label

# expands and cleans the context (cleaning is basically taking out the word, it could be that the word appears twice withim window)
def expandAndCleanContext(context, word, rel, expansionParam):
	# remove word from context
	newContext = filter(lambda x: x != word, context)
	
	# get the vocabulary stored in rel
	relVoc = rel.keys()
	
	# for every word in the context
	for w in context:
		# if the word is in rel
		if w in relVoc:
			# sort the related words and keep 0-expansionParam, then throw away the scroes and take out 'word' 
			# add this to new context
			wRel = filter(lambda x: x != word, map(lambda x: x[0], sorted(rel[w].items(), key = lambda x: x[1], reverse = True))[0:expansionParam])
			newContext= newContext + wRel + [w]
	return newContext

# get all contexts with windowsize skipsize*2 in which word occurs (as the mid word, maybe expand this?)
def getContext(inpt, word, skipsize=5):
	
	contexts = []	
	
	queueSize = skipsize * 2 + 1
	queueMid = skipsize + 1
	
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
			if mid == word:
				contexts.append(queue)
	
	return contexts

if __name__ == "__main__":
	
	print "Welcome to PALM!"
	
	if len(sys.argv) < 3:
		print "USAGE: python palm.py <TEXT FILE> <PATH TO COC>"
		sys.exit()
	textfile = sys.argv[1]
	relFile = sys.argv[2] + "_rel"
	rel = shelve.open(relFile)

	# inpt = read_file(textfile)
	# showExpandedSentences(inpt, rel, 5)
	# go over text
	# extract sentence with window
	# expand sentence with related words (make number of expansions a parameter)
	# create a vector over the different clusters
	# find a label for the vector (function chooseMostRelated)
	# collect labelled training data
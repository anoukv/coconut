import sys, shelve

def chooseMostRelated(word, wordsToChooseFrom, rel):
	highest = None
	bestword = None
	wordRelatednessVec = rel[word]
	wordsToChooseFrom = filter(lambda x: x in wordRelatednessVec, wordsToChooseFrom)
	# wordsToChooseFrom = wordsToChooseFrom.remove(word)
	for candidate in wordsToChooseFrom:
		relatedness= wordRelatednessVec[candidate]
		if relatedness > highest and candidate != word:
			highest = relatedness
			bestword = candidate
	return bestword

	return
def read_file(filename):
	f = open(filename, 'r')
 	inpt = f.readline().replace("\n", "").split(" ")
 	f.close()
 	return inpt

def showExpandedSentences(inpt, rel, skipsize):
	relevanceVoc = rel.keys()
	print relevanceVoc
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
			if mid == "apple":
				for word in queue:
					if word in relevanceVoc:
						print word
						print sorted(rel[word].items(), key = lambda x: x[1], reverse=True)[0:3]
				print len(queue), queue
				print
	return 0

if __name__ == "__main__":
	
	print "Welcome to PALM!"
	
	if len(sys.argv) < 3:
		print "USAGE: python palm.py <TEXT FILE> <PATH TO COC>"
		sys.exit()
	textfile = sys.argv[1]
	relFile = sys.argv[2] + "_rel"
	rel = shelve.open(relFile)
	print chooseMostRelated('apple',['mac', 'itools,', 'met', 'varying', 'degrees', 'success', 'apple', 'pomaceous', 'fruit', 'apple', 'tree,'], rel)
	# inpt = read_file(textfile)
	# showExpandedSentences(inpt, rel, 5)

	# go over text
	# extract sentence with window
	# expand sentence with related words (make number of expansions a parameter)
	# create a vector over the different clusters
	# find a label for the vector (function chooseMostRelated)
	# collect labelled training data
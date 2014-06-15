import sys
from collections import defaultdict
from time import time
import shelve
from math import sqrt
from Word import Word

# minimumOccurence should be adjusted when working with bigger files, this is for a small test only. Set to 5 again.
def get_document_vocabulary(inpt, minimumOccurence = 0):
	total = defaultdict(int)
	for word in inpt:
		total[word] += 1
	s = sum(total.values())
	voc = dict([ (key, total[key]) for key in total.keys() if total[key] > minimumOccurence ])
	voc["_UNKNOWN_"] = s - sum(voc.values())
	return voc

def normalize_coc(coc):
	total = sqrt( sum([v**2 for v in coc.values()]) )
	new_coc = dict()
	for key in coc.keys():
		new_coc[key] = coc[key] / total
	return new_coc

def relatedness(word, coc, vocabulary):
	new_coc = dict()
	for key in coc.keys():
		try:
			new_coc[key] = coc[key] / float((vocabulary[word] + vocabulary[key] - coc[key]))
		except:
			new_coc[key] = 1
	return new_coc

def getCocMatrix(inpt, skipsize):
	queueSize = skipsize * 2 + 1
	queueMid = skipsize + 1

	queueIsReady = lambda x : len(x) == queueSize
	def push(element, queue):
		queue.append(element)
		if len(queue) > queueSize:
			queue.pop(0)
	
	vocabulary = get_document_vocabulary(inpt)
	vocSize = len(vocabulary) + 1

	wordToVec = dict()
	for word in vocabulary:
		wordToVec[word] = defaultdict(int)

	queue = []
	for word in inpt:
		push(word, queue)
		if queueIsReady(queue):
			mid = queue[queueMid]
			if mid in vocabulary:
				for i in xrange(skipsize):
					if queue[i] in vocabulary:
						word1 = queue[i]
					else:
						word1 = "_UNKNOWN_"
					if queue[i+1+skipsize] in vocabulary:
						word2 = queue[i+1+skipsize]
					else:
						word2 = "_UNKNOWN_"
				
					wordToVec[mid][word1] += 1
					wordToVec[mid][word2] += 1

	normalized_wordToVec = dict()
	relations = dict()
	for word in wordToVec.keys():
		normalized_wordToVec[word] = normalize_coc(wordToVec[word])
		relations[word] = relatedness(word, wordToVec[word], vocabulary)
		relations[word] = normalize_coc(relations[word])

	return dict( {'voc': vocabulary, 'coc' : normalized_wordToVec, 'rel' : relations} )


def read_args():
	def read_file(filename):
		f = open(train, 'r')
	 	inpt = f.readline().replace("\n", "").split(" ")
	 	f.close()
	 	return inpt

	if len(sys.argv) < 3:
 		print "USAGE: python build_cocs.py training.txt outputname (skipsize = 5)"
 		sys.exit()

	train = sys.argv[1]
 	output_file = sys.argv[2]
 	skipsize = 5
 	if len(sys.argv) == 4:
 		skipsize = int(sys.argv[3])

 	return (read_file(train), output_file, skipsize)


if __name__ == "__main__":
	start = time()
	(inpt, output_file, skipsize) = read_args()
	# this is an adjustment / enhancement to coconut, we throw away all irrelevant words
	cache = dict()
	new_inpt = []
	while len(inpt) > 0:
		w = inpt.pop(0)
		if w in cache:
			if cache[w]:
				new_inpt.append(w)
		else:
			word_object = Word(w)
			rel = word_object.relevant()
			cache[w] = rel
			if rel:
				new_inpt.append(w)
	inpt = new_inpt
	coc = getCocMatrix(inpt, skipsize)
	for key in coc:
		myShelve = shelve.open(output_file + "_" + key)
		myShelve.update(coc[key])
		myShelve.close()
	stop = time()
 	print "I spent", int(stop-start+0.5), "seconds."


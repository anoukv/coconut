from fast_utils import load_vectors
from collections import defaultdict
from math import sqrt
import sys

if __name__ == "__main__":
	print "Stats"
	if len(sys.argv) < 2:
		print "USAGE: python baselline_word2vec.py <PATH TO WORDVECTORS>"
		sys.exit()
	
	vectorsFilename = sys.argv[1]
	vectors = load_vectors(vectorsFilename)

	splits = defaultdict(set)
	non_splits = set()

	for word in vectors:
		if "_" in word:
			splittedWords = word.split("_")
			splits[splittedWords[0]].add(splittedWords[1])
		else:
			non_splits.add(word)


	print len(splits)
	print len(non_splits)

	allsplits = []
	for key in splits:
		allsplits.append(len(splits[key]))
	mean =  sum(allsplits)/float(len(allsplits))
	new = [(x - mean)**2 for x in allsplits]
	stdv = sqrt(sum(new) / float(len(new)))
	print max(allsplits), mean, stdv
	print splits['mexico']
	print splits['brazil']
	print splits['israel']
	print splits['americ']







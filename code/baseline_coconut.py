import sys, shelve
from utils import *
from coconut_light import *

def getAverageWordRep(words):
	average = 0
	return average
	
if __name__ == "__main__":
	print "Baseline with wordvectors"
	
	if len(sys.argv) < 3:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO COC>"
		sys.exit()
	
	taskFilename = sys.argv[1]
	cocFilename = sys.argv[2]

	rel = shelve.open(cocFilename + '_rel')
	voc = shelve.open(cocFilename + '_voc')

	task, _ = load_task(taskFilename)

	methodsRating = []
	humanRating = []
	cache = dict()

	vocabulary = voc.keys()
	for key in sorted(task.keys()):
		
		question = task[key]
		anser = 0
		humanRating.append(question['rating'])
		
		word1 = question['word1']
		word2 = question['word2']
		
		# only proceed if both words are known
		if word1 in vocabulary and word2 in vocabulary:
			if word1 not in cache:
				cache[word1] = makeNewCOCS(word1, rel, voc)
			if word2 not in cache:
				cache[word2] = makeNewCOCS(word2, rel, voc)

		print key
 	print spearman(methodsRating, humanRating)


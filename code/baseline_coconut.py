import sys, shelve
from Word import Word
from utils import *
from fast_utils import *
from coconut_light import *
from fast_utils import getAverageWordRep

def getCorrectSense(context, sense1, sense2):
	setContext = set(context)
	one = len(setContext.intersection(sense1))
	two = len(setContext.intersection(sense2))
	if one > two:
		return sense1
	elif two > one: 
		return sense2
	elif len(sense1) > len(sense2):
		return sense1
	else:
		return sense2
	return []
		
if __name__ == "__main__":
	print "Baseline with wordvectors"
	
	if len(sys.argv) < 3:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO COC> <PATH TO VECTORS>"
		sys.exit()
	
	taskFilename = sys.argv[1]
	cocFilename = sys.argv[2]
	vectorsFilename = sys.argv[3]

	rel = shelve.open(cocFilename + 'rel')
	voc = shelve.open(cocFilename + 'voc')

	task, _ = load_task(taskFilename)

	vectors = load_vectors(vectorsFilename)

	methodsRating = []
	humanRating = []
	cache = dict()

	vocabulary = set(voc.keys())
	questions = task.values()

	for i in xrange(len(questions)):
		question = questions[i]

		word1 = Word(question['word1']).lemma().encode('ascii','ignore')
		word2 = Word(question['word2']).lemma().encode('ascii','ignore')
		
		# only proceed if both words are known
		if word1 in vocabulary and word2 in vocabulary:
			print i
			if word1 not in cache:
				word1Dic = makeNewCOCS(word1, rel, voc)
				cache[word1] = word1Dic
			else: 
				word1Dic = cache[word1]
			
			if word2 not in cache:
				word2Dic = makeNewCOCS(word2, rel, voc)
				cache[word1] = word2Dic
			else:
				word2Dic = cache[word2]

			context1 = [Word(x).lemma().encode('ascii','ignore') for x in question['context1'].lower().split(' ')]
			context2 = [Word(x).lemma().encode('ascii','ignore') for x in question['context2'].lower().split(' ')]
		
			senseWord1 = getCorrectSense(context1, word1Dic[0], word1Dic[1])
			senseWord2 = getCorrectSense(context2, word2Dic[0], word2Dic[1])
			
 			wordvec1 = getAverageWordRep(senseWord1, vectors)
 			wordvec2 = getAverageWordRep(senseWord2, vectors)
			
			humanRating.append(question['rating'])
			methodsRating.append(cosine_similarity(wordvec1, wordvec2))
			
 		if len(methodsRating) > 2:
 			print spearman(methodsRating, humanRating)


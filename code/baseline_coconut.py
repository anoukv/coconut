import sys, shelve
from time import time
from utils import *
from fast_utils import *
from coconut_light import makeNewCOCS
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
	
	if len(sys.argv) < 4:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO COC> <PATH TO VECTORS>"
		sys.exit()
	
	start = time()
	print "Loading..."

	taskFilename = sys.argv[1]
	cocFilename = sys.argv[2]
	vectorsFilename = sys.argv[3]
	questionStart = int(sys.argv[4])

	rel = shelve.open(cocFilename + 'rel')
	voc = shelve.open(cocFilename + 'voc')
	vocabulary = set(voc.keys())
	voc.close()

	task, _ = load_task(taskFilename)

	vectors = load_vectors(vectorsFilename)

	resultsSelve = shelve.open("results.shelve")

	methodsRating = []
	humanRating = []
	cache = dict()
	
	questions = [ y[1] for y in sorted(task.items(), key=lambda x : x[0]) ]

	print "\tLoaded in", int(time() - start + 0.5), "seconds."
	print "Clustering..."
	for i in xrange(questionStart, len(questions)):
		if str(i) not in resultsSelve:
			question = questions[i]

			word1 = Word(question['word1']).lemma()
			word2 = Word(question['word2']).lemma()
			
			# only proceed if both words are known
			if word1 in vocabulary and word2 in vocabulary:
				print "\tIteration:", i

				if word1 not in cache:
					cache[word1] = makeNewCOCS(word1, rel)
				if word2 not in cache:
					cache[word2] = makeNewCOCS(word2, rel)

				word1Dic = cache[word1]
				word2Dic = cache[word2]
				context1 = [ Word(x).lemma() for x in question['context1'].lower().split(' ') ]
				context2 = [ Word(x).lemma() for x in question['context2'].lower().split(' ') ]
			
				senseWord1 = getCorrectSense(context1, word1Dic[0], word1Dic[1])
				senseWord2 = getCorrectSense(context2, word2Dic[0], word2Dic[1])
				
	 			wordvec1 = getAverageWordRep(senseWord1, vectors)
	 			wordvec2 = getAverageWordRep(senseWord2, vectors)
				
				rh = question['rating']
				rc = cosine_similarity(wordvec1, wordvec2)
				methodsRating.append(rc)
				humanRating.append(rh)
				
		 		if len(methodsRating) > 2:
		 			print "\t\tScore:", spearman(methodsRating, humanRating)
		 	else:
		 		(rh,rc) = (999,999)
		 	resultsSelve[str(i)] = (rh,rc)

	stop = time()
	print "Done in", int(stop - start + 0.5), "seconds."
	print "Final spearman:", spearman(methodsRating, humanRating)





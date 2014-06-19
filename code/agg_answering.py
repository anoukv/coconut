from Word import Word
from utils import load_task, spearman
from fast_utils import get_coc

import shelve
import sys

def dic_similarity(large, large_keys, small):
	total = 0.0
	for key in small:
		if key in large_keys:
			total += large[key]
	return total

def relatedness(context1, context2, cocs, key_sets):
	# context1 = filter(lambda x : not x == "" and x.relevant(), [ Word(w) for w in context1.lower().split(" ") ])
	# context1 = [ w.lemma() for w in context1 ]
	# context2 = filter(lambda x : x.relevant(), [ Word(w) for w in context2.lower().split(" ") ])
	# context2 = [ w.lemma() for w in context2 ]


	context1 = get_coc(context1.split(" "))
	context2 = get_coc(context2.split(" "))

	total = 0.0
	for i in xrange(len(key_sets)):
		s1 = dic_similarity(cocs[i], key_sets[i], context1)
		s2 = dic_similarity(cocs[i], key_sets[i], context2)
		total += s1 * s2
	total /= len(key_sets)
	return total

if __name__ == '__main__':
	if not len(sys.argv) == 3:
		print "USAGE: python agg_answering.py <PATH TO TASK> <PATH TO cluster_descriptors>"
		sys.exit()

	print "Loading stuf..."
	taskFilename = sys.argv[1]
	filename = sys.argv[2] # "../../../cluster_descriptors/enwiki8.clust-desc.shelve"

	d = shelve.open(filename)
	key_sets = []
	newD = dict()
	vec_size = len(d.keys())

	for i in xrange(vec_size):
		key_sets.append(set(d[str(i)].keys()))
		newD[i] = d[str(i)]

	task, _ = load_task(taskFilename)
	questions = task.values()

	methodsRating = []
	humanRating = []

	print "Answering", len(task), "questions..."

	for i in xrange(len(questions)):
		if i % 100 == 0:
			print "\tIteration", i

		question = questions[i]
		context1 = question['context1'] + " " + question['word1'] + " " + question['word1']
		context2 = question['context2'] + " " + question['word2'] + " " + question['word2']

		methodsRating.append(relatedness(context1, context2, newD, key_sets))
		humanRating.append(question['rating'])

 	print 
 	print spearman(methodsRating, humanRating)




import sys
from Word import Word
from utils import *
from fast_utils import cosine_similarity, normalizeVec, normalize_coc

def read_sets(filename="clusters.tmp"):
	clusters = []
	f = open(filename, 'r')
	for line in f.readlines():
		clusters.append(eval(line))
	f.close()
	return [ normalize_coc(dict( [ (e, 1) for e in c] )) for c in clusters ]

def context_similarity(c1, c2, clusters):
	def get_vec_sim(clusters, context):
		def sim(c1, c2):
			s = 0
			for key in c2:
				if key in c1:
					s += c1[key] * c2[key]
			return s
		v = []
		for cluster in clusters:
			v.append(sim(cluster, context))
		return normalizeVec(v)
	return cosine_similarity(get_vec_sim(clusters, c1), get_vec_sim(clusters, c2))


if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 3:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO WORDVECTORS>"
		sys.exit()

	taskFilename = sys.argv[1]
	clustersFilename = sys.argv[2]

	task, _ = load_task(taskFilename)
	clusters = read_sets(clustersFilename)

	methodsRating = []
	humanRating = []

	questions = task.values()

	for i in xrange(len(questions)):
		question = questions[i]

		word1 = Word(question['word1']).lemma().encode('ascii','ignore')
		word2 = Word(question['word2']).lemma().encode('ascii','ignore')
		context1 = [Word(x).lemma().encode('ascii','ignore') for x in question['context1'].lower().split(' ')]
		context2 = [Word(x).lemma().encode('ascii','ignore') for x in question['context2'].lower().split(' ')]
		
		context1 = normalize_coc(dict( [ (e, 1) for e in context1] ))
		context2 = normalize_coc(dict( [ (e, 1) for e in context2] ))

		methodsRating.append(context_similarity(context1, context2, clusters))
		humanRating.append(question['rating'])
 
 	print spearman(methodsRating, humanRating)


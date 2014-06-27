import sys
from utils import Word, load_task
from fast_utils import cosine_similarity, normalizeVec, normalize_coc, spearman, load_vectors
from math import sqrt

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
		if sum(v) == 0:
			return v
		return normalizeVec(v)
	return cosine_similarity(get_vec_sim(clusters, c1), get_vec_sim(clusters, c2))

def vector_similarity(cs, w1, w2, vectors):
	if w1 == word2:
		return 1.0
	if w1 in vectors and w2 in vectors:
		return cosine_similarity(vectors[w1], vectors[w2])
	else:
		return cs

if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 4:
		print "USAGE: python me.py <PATH TO TASK> <PATH TO CLUSTERS> <PATH TO VECTORS>"
		sys.exit()

	print "Loading"
	taskFilename = sys.argv[1]
	clustersFilename = sys.argv[2]
	vectorsFilename = sys.argv[3]

	task, _ = load_task(taskFilename)
	clusters = read_sets(clustersFilename)
	vectors = load_vectors(vectorsFilename)

	methodsRating = []
	humanRating = []

	questions = task.values()

	print "Answering"
	for i in xrange(len(questions)):
		question = questions[i]

		word1 = Word(question['word1']).lemma()
		word2 = Word(question['word2']).lemma()
		context1 = [Word(x).lemma() for x in question['context1'].lower().split(' ')] #+ [word1 for _ in xrange(1000)]
		context2 = [Word(x).lemma() for x in question['context2'].lower().split(' ')] #+ [word2 for _ in xrange(1000)]
		
		context1 = normalize_coc(dict( [ (e, 1) for e in context1] ))
		context2 = normalize_coc(dict( [ (e, 1) for e in context2] ))

		c_s = context_similarity(context1, context2, clusters)
		sim = vector_similarity(0.33, word1, word2, vectors)
		score = sim**3 * c_s

		methodsRating.append( score )
		humanRating.append(question['rating'])

		if i % 500 == 0 and not i > 1800 and len(humanRating) > 2:
			print "\t", spearman(methodsRating, humanRating)
 
 	print "Final spearman:"
 	print spearman(methodsRating, humanRating)


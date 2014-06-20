import sys
from utils import Word, load_task
from fast_utils import cosine_similarity, normalizeVec, normalize_coc, spearman

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
		print "USAGE: python me.py <PATH TO TASK> <PATH TO CLUSTERS>"
		sys.exit()

	print "Loading"
	taskFilename = sys.argv[1]
	clustersFilename = sys.argv[2]

	task, _ = load_task(taskFilename)
	clusters = read_sets(clustersFilename)

	methodsRating = []
	humanRating = []

	questions = task.values()

	print "Answering"
	for i in xrange(len(questions)):
		question = questions[i]

		word1 = Word(question['word1']).lemma()
		word2 = Word(question['word2']).lemma()
		context1 = [Word(x).lemma() for x in question['context1'].lower().split(' ')] + [word1, word1, word1]
		context2 = [Word(x).lemma() for x in question['context2'].lower().split(' ')] + [word2, word2, word2]
		
		context1 = normalize_coc(dict( [ (e, 1) for e in context1] ))
		context2 = normalize_coc(dict( [ (e, 1) for e in context2] ))

		methodsRating.append(context_similarity(context1, context2, clusters))
		humanRating.append(question['rating'])

		if i % 300 == 0 and len(humanRating) > 2:
			print "\t", spearman(methodsRating, humanRating)
 
 	print "Final spearman:"
 	print spearman(methodsRating, humanRating)


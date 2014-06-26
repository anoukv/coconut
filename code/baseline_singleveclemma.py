import sys
from utils import load_task, Word
from fast_utils import cosine_similarity, load_vectors, spearman

if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 3:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO WORDVECTORS>"
		sys.exit()
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]

	task, _ = load_task(taskFilename)
	vectors = load_vectors(vectorsFilename)

	methodsRating = []
	humanRating = []

	questions = task.values()
	coverage = 0

	for i in xrange(len(questions)):
		question = questions[i]

		word1 = Word(question['word1']).lemma()
		word2 = Word(question['word2']).lemma()

		if word1 in vectors and word2 in vectors:
			vec1 = vectors[word1]
			vec2 = vectors[word2]
			methodsRating.append(cosine_similarity(vec1, vec2))
			humanRating.append(question['rating'])
			if len(methodsRating) % 100 == 0 and len(methodsRating) > 0:
				print i, spearman(methodsRating, humanRating)
			coverage += 1

 	print spearman(methodsRating, humanRating)
 	print "Coverage: ", coverage / float(len(questions)) * 100
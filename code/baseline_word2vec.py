import sys
from utils import *
from fast_utils import cosine_similarity

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

	for key in sorted(task.keys()):
		question = task[key]
		humanRating.append(question['rating'])
		word1 = question['word1']
		word2 = question['word2']

		if word1 in vectors and word2 in vectors:
			vec1 = vectors[word1]
			vec2 = vectors[word2]
			methodsRating.append(cosine_similarity(vec1, vec2))
		else:
			methodsRating.append(0)
 
 	print spearman(methodsRating, humanRating)


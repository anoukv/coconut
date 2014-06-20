import sys, os
from utils import load_task, Word
from fast_utils import cosine_similarity, load_vectors, spearman

if __name__ == "__main__":
	print "Baseline with wordvectors"
	if len(sys.argv) < 4:
		print "USAGE: python baselline_word2vec.py <PATH TO TASK> <PATH TO WORDVECTORS> <PATH TO SVMS>"
		sys.exit()
	taskFilename = sys.argv[1]
	vectorsFilename = sys.argv[2]
	pathToSVMFile = sys.argv[3]

	task, tralala = load_task(taskFilename)
	vectors = load_vectors(vectorsFilename)

	methodsRating = []
	humanRating = []
	print tralala
	questions = task.values()

	disambiguatedWords = [x.split("_")[0] for x in os.listdir(pathToSVMFile)]
	print disambiguatedWords

	for i in xrange(len(questions)):
		question = questions[i]

		humanRating.append(question['rating'])
		word1 = Word(question['word1']).lemma()
		word2 = Word(question['word2']).lemma()

		if word1 in vectors and word2 in vectors:
			vec1 = vectors[word1]
			vec2 = vectors[word2]
			methodsRating.append(cosine_similarity(vec1, vec2))
		else:
			methodsRating.append(0)
 
 	print spearman(methodsRating, humanRating)
from Word import Word

def filter_corpus_for_relevance(filein, fileout):
	print "Converting ", filein, " to ", fileout
	print "\tReading ", filein
	inpt = open(filein, 'r')
	content = filter(lambda x : not x == "", inpt.readlines()[0].replace("\n", "").split(" "))
	inpt.close()

	print "\tNow filtering and writing relevant words"
	print "\t", len(content), "words to go..."
	outpt = open(fileout, 'w')
	cache = dict()
	for i in xrange(len(content)):
		if i % 1000000 == 0:
			print "\t\tIteration", i
		word = content[i]
		if word not in cache:
			word_object = Word(word)
			if word_object.relevant():
				cache[word] = word_object.lemma()
			else:
				cache[word] = False
		token = cache[word]
		if not token == False:
			outpt.write(token + " ")
	outpt.close()
	print "Done!"

if __name__ == '__main__':
	filter_corpus_for_relevance("../../corpora/corpus.enwiki8", "../../corpora/corpus.enwiki8.relevant")


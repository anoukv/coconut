from Word import Word
import sys
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
	if len(sys.argv) < 3:
		print "USAGE: python builders.py <PATH TO CORPUS> <PATH TO NEW CORPUS>"
		sys.exit()

	original = sys.argv[1]
	new = sys.argv[2]
	filter_corpus_for_relevance(original, new)


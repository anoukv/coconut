print "Hello hard"
from nltk import word_tokenize

for i in xrange(1, 4):
	f = open('../data/original.hard/hard' + str(i), 'r')
	fout = open('../data/cleaned.hard/hard' + str(i), 'w')
	lines = f.readlines()
	for line in lines:
		line = line.lower()
		newLine = line.split(" ")
		while newLine[0] == '':
			newLine.pop(0)
		special = newLine[0].split(":")[1]
		newLine.pop(0)
		if len(special) > 0:
			if special[0] != "<":
				sentence = [special] + newLine
			else:
				newLine.pop(0)
				sentence = newLine
		result = "".join([x + " " for x in sentence])
		result = word_tokenize(result)
		fout.write("".join([x + " " for x in result]) + "\n")

	f.close()
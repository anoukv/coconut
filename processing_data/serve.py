from os import listdir
from nltk import word_tokenize

print "Hello serve!"

base = "../data/original.serve/"
outbase = "../data/cleaned.serve/"
all_files = listdir(base)

for name in all_files:
	f = open(base+name, 'r')
	out = open(outbase+name, 'w')
	for line in f.readlines():
		line = line.split(" ")
		line.pop(0)
		line = "".join( [ x + " " for x in line] )
		if len(line) > 0:
			line = "".join( [ x + " " for x in word_tokenize(line)] ).lower()
			out.write(line)
	f.close()
	out.close()


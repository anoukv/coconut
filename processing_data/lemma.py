from nltk.stem.snowball import SnowballStemmer
from os import listdir

import sys

if __name__ == "__main__":
	stemmer = SnowballStemmer("english")
	
	if(len(sys.argv) < 2):
		print "Usage: python lemma.py dir"

	filename = '../data/cleaned.' + sys.argv[1] + '/'
	
	for file in listdir(filename):
		fin = open(filename + file, 'r')
		temp = '../data/lemma.' + sys.argv[1] + '/' + file
		fout = open(temp, 'w')
		for line in fin.readlines():
			newLine = [stemmer.stem(word) for word in line.split(" ")]
			print newLine
			fout.write("".join([x + " " for x in newLine]))



from os import listdir
from nltk import word_tokenize
print "Hello line!"

base = "../data/original.serve/"
outbase = "../data/cleaned.serve/"
all_files = listdir(base)

for name in all_files:
	f = open(base+name, 'r')
	out = open(outbase+name, 'w')
	for line in f.readlines():
		line = list(line)
		while len(line)>0:
			char = line.pop(0)
			if char == "<":
				line.pop(0)
				line.pop(0)
				break
			if char == ":":
				break
		if ":" in "".join(line).split(" ")[0]:
			while not line.pop(0) == ":":
				pass
		line = "".join(line)
		for garbage in ["<s>", "</s>", "<p>", "</p>", "@"]:
			line = line.replace(garbage, "")
		while not line == line.replace("  ", ""):
			line = line.replace("  ", "")

		line = "".join( [ x + " " for x in line] )
		if len(line) > 0:
			line = "".join( [ x + " " for x in word_tokenize(line)] ).lower()
			out.write(line)
	f.close()
	out.close()
print "Hello hard"

for i in xrange(1, 4):
	f = open('../data/original.hard/hard' + str(i), 'r')
	fout = open('../data/cleaned.hard/hard' + str(i), 'w')
	lines = f.readlines()
	for line in lines:
		newLine = line.split(" ")
		while newLine[0] == '':
			newLine.pop(0)
		special = newLine[0].split(":")[1]
		newLine.pop(0)
		if len(special) > 0:
			if special[0] != "<":
				fout.write("".join([x + " " for x in ([special] + newLine)]))
			else:
				print special
				newLine.pop(0)
				fout.write("".join([x + " " for x in newLine]))
		else:
			fout.write("".join([x + " " for x in newLine]))

	f.close()
print "Hello hard"

for i in xrange(1, 4):
	f = open('../data/original.hard/hard' + str(i))
	lines = f.readlines()
	print len(lines)
	f.close()
import sys

def read_file(filename):
	f = open(filename, 'r')
 	inpt = f.readline().replace("\n", "").split(" ")
 	f.close()
 	return inpt

def getCocMatrix(inpt, skipsize):
	
	queueSize = skipsize * 2 + 1
	queueMid = skipsize + 1

	queueIsReady = lambda x : len(x) == queueSize
	def push(element, queue):
		queue.append(element)
		if len(queue) > queueSize:
			queue.pop(0)
	
	queue = []
	for word in inpt:
		push(word, queue)
		if queueIsReady(queue):
			mid = queue[queueMid]
			if mid == "apple":
				print len(queue), queue
	return 0

if __name__ == "__main__":
	
	print "Welcome to PALM!"
	
	if len(sys.argv) < 2:
		print "USAGE: python palm.py <TEXT FILE>"
		sys.exit()
	textfile = sys.argv[1]
	
	inpt = read_file(textfile)
	getCocMatrix(inpt, 5)

	# go over text, get relatedness things
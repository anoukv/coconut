from fast_utils import normalize_coc

from collections import defaultdict
import shelve

def read_sets(filename="clusters.tmp"):
	clusters = []
	f = open(filename, 'r')
	for line in f.readlines():
		clusters.append(eval(line))
	f.close()
	return clusters

def produce_coc(node_members, cocs):
	coc = defaultdict(int)
	for member in node_members:
		if member in cocs:
			dic = cocs[member]
			for (key, value) in dic.items(): 
				coc[key] += value
	return normalize_coc(coc)

def assign_cocs_to_nodes(clusters, cocs, cluster_coc_name):
	myShelve = shelve.open(cluster_coc_name)
	
	for i in xrange(len(clusters)):
		myShelve[str(i)] = produce_coc(clusters[i], cocs)

	myShelve.close()	

if __name__ == '__main__':
	import sys
	from time import time
	start = time()
	clusters_filename = sys.argv[1]
 	cocs_filename = sys.argv[2]
 	descriptors_filename = sys.argv[3]

 	clusters = read_sets(clusters_filename)
 	cocs = shelve.open(cocs_filename)

 	assign_cocs_to_nodes(clusters, cocs, descriptors_filename)
 	cocs.close()
 	stop = time()
 	print "Done in", int(stop-start + 0.5), "seconds"
 	

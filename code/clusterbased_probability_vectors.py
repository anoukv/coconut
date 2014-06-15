



if __name__ == '__main__':
	from agglomerative import agglomerative_clustering, load_vectors
	print "Loading vectors"
	data = load_vectors("../data/wordvectors/vectors320.all", 1000).items()
	print "Clustering"
	nodes = agglomerative_clustering(data, 100)


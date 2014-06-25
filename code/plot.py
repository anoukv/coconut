import matplotlib.pyplot as plt


if __name__ == '__main__':
	print "Loading.."
	clusters = []
	f = open("clusters_10000x500.tmp")
	for line in f.readlines():
		clusters.append(len(eval(line)))
	f.close()
	clusters = filter(lambda x : x > 9, clusters)
	print len(clusters)
	print "Plotting.."
	plt.hist(clusters, 25)

	# plt.plot(bins, y, 'r--')
	plt.xlabel('Cluster Size')
	plt.ylabel('Frequency')
	plt.title( 'Cluster size distribution')

	# Tweak spacing to prevent clipping of ylabel
	plt.subplots_adjust(left=0.15)
	plt.show()

	
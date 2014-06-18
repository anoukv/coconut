from fast_utils import load_vectors, cosine_similarity
import shelve

# chooses a 'label' (may be interpreted as a substitute word) for the word that has 
# relatedness vector wordRel from the words in expanded context
def getLabel(wordRel, expandedContext):
	# init
	label = None
	highesetRel = None
	
	# we will only consider candidates that are in the word's relatedness vector
	expandedContext = filter(lambda x: x in wordRel, expandedContext)

	# iterate over all candidates to find the one with the highest relatedness score
	for candidate in expandedContext:
		relScore = wordRel[candidate]
		if relScore > highesetRel:
			highesetRel = relScore
			label = candidate
	return label
labels = ['concept', 'discord', 'physiol', 'newton', 'steve', 'keyboard', 'disk', 'compani', 'itun', 'cut', 'grape', 'desktop', 'late', 'window', 'busi', 'board', 'introduc', 'digit', 'firewir', 'ceo', 'big', 'powerbook', 'mous', 'game', 'cyanid', 'bit', 'name', 'reveal', 'motorola', 'intel', 'gui', 'cider', 'clown', 'popular', 'x', 'pausania', 'candi', 'respond', 'nut', 'timelin', 'continu', 'see', 'video', 'logo', 'gross', 'alcohol', 'profit', 'new', 'sold', 'red', 'machin', 'ipod', 'job', 'corp', 'found', 'releas', 'news', 'advertis', 'lawsuit', 'card', 'g', 'sacr', 'technolog', 's', 'plus', 'retail', 'block', 'macintosh', 'softwar', 'sweet', 'modul', 'system', 'linux', 'macworld', 'market', 'use', 'type', 'pictur', 'wozniak', 'licens', 'hesperid', 'connector', 'interfac', 'basic', 'basin', 'was', 'threw', 'parc', 'brand', 'gravit', 'beatl', 'appel', 'iic', 'line', 'iii', 'ibm', 'syrup', 'properti', 'tree', 'matter', 'nine', 'danc', 'display', 'employe', 'hypercard', 'comput', 'share', 'pie', 'ii', 'replica', 'tabl', 'infring', 'phrase', 'quicktim', 'sell', 'develop', 'datura', 'rather', 'media', 'deni', 'inscrib', 'descend', 'eventu', 'smell', 'bundl', 'juic', 'pineappl', 'product', 'clone', 'pear', 'evil', 'mac', 'fruit', 'stereo', 'potato', 'home', 'su', 'patent', 'switch', 'adam', 'dos', 'audio', 'microsoft', 'wine']
#labels = ['inning', 'mexican', 'sequest', 'just', 'fox', 'guano', 'rodent', 'handcuff', 'sleep', 'endem', 'ear', 'ty', 'harmless', 'aaron', 'score', 'rabi', 'vulner', 'plate', 'anim', 'hit', 'megabat', 'ya', 'safe', 'roost', 'dark', 'game', 'leagu', 'batter', 'shadow', 'cage', 'earn', 'costum', 'masterson', 'entangl', 'sacrific', 'lament', 'superfamili', 'sanctuari', 'nose', 'night', 'mammal', 'batsmen', 'respond', 'vampir', 'noctilionida', 'speci', 'matur', 'percentag', 'burger', 'championship', 'greenhal', 'home', 'fli', 'ha', 'abl', 'cinemat', 'estim', 'fossil', 'get', 'thriae', 'hopikin', 'goth', 'team', 'pontoon', 'mississippi', 'usual', 'pup', 'molossida', 'trickster', 'comoro', 'career', 'joke', 'askariyya', 'livingston', 'boe', 'vespertilionida', 'logo', 'myoti', 'walk', 'sox', 'pp', 'caught', 'frolic', 'wicket', 'swarm', 'pollin', 'strike', 'prey', 'funnel', 'tenerif', 'season', 'spider', 'casey', 'conserv', 'nobodi', 'microchiroptera', 'eat', 'greenberg', 'sound', 'exposur', 'ben', 'hitter', 'hous', 'tree', 'rope', 'record', 'retir', 'shark', 'teammat', 'scanner', 'toss', 'cricket', 'player', 'basebal', 'alphabet', 'cave', 'bowl', 'batman', 'hibern', 'ruth', 'wildlif', 'ball', 'ye', 'autocod', 'insect', 'fruit', 'blood', 'averag', 'ghost', 'noun', 'batwoman', 'lineup', 'wing', 'subgroup']
vectors = load_vectors('../data/wordvectors/enwiki8.relevant.vectors')
rel = shelve.open('../../corponut/enwiki8_rel')
wordRel = rel['appl']
rel.close()

toBeShifted = []
for label in labels:
	if not label in vectors:
		toBeShifted.append(label)

labels = list(set(labels) - set(toBeShifted))

while len(labels) > 5:
	best1 = None
	best2 = None
	bestSim = None
	for label1 in labels:
		for label2 in labels:
			if label1 != label2:
				sim = cosine_similarity(vectors[label1], vectors[label2])
				if sim > bestSim:
					bestSim = sim
					best1 = label1
					best2 = label2
	if bestSim < 0.5:
		break
	keeper = getLabel(wordRel, [best1, best2])
	if keeper == best1:
		labels.remove(best2)
	else:
		labels.remove(best1)
	print bestSim, " Merging ", best1, " and " , best2, " into ", keeper

print labels
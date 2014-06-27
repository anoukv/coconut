from nltk import pos_tag
from nltk.tag.simplify import simplify_wsj_tag
from nltk.stem.snowball import SnowballStemmer
Stemmer = SnowballStemmer("english")
from math import sqrt


class Word:
    def __init__(self, word, desc=None, meta=dict()):
    	self.word = word
    	self.desc = desc
    	self.meta = meta

    	self._lemma = None
        self._pos = None
        self._relevant = None

    def relevant(self):
      if self._relevant == None:
          self._relevant = pos_is_revelant(self.pos())
      return self._relevant

    def pos(self):
        if self._pos == None:
            self._pos = postag(self.word)
        return self._pos

    def lemma(self):
    	if self._lemma == None:
    		self._lemma = Stemmer.stem(self.word)
    	return self._lemma.encode('ascii','ignore') 

    def setDescription(self, x):
        self.desc = x

def postag(word):
	try:
		return simplify_wsj_tag(pos_tag([word])[0][1])
	except:
		return "UNK"

def pos_is_revelant(pos):
	return pos in set(['N', 'NP', 'VG', 'VD', 'ADJ', 'ADV'])

def word_is_relevant(word):
	return pos_is_revelant(postag(word))

# normalize a vector
def normalize(vec):
	total = sqrt( sum([v**2 for v in vec]) )
	new_vec = []
	for v in vec:
		new_vec.append(v/total)
	return tuple(new_vec)

# reads the SCWS task
def load_task(filename, allWords=False):
	words = set()
	task = dict()
	f = open(filename, 'r')
	lines = f.readlines()
	for question in lines:
		q = dict()
		question = question.replace("\n","").split('\t')
		q['word1'] = question[1].lower()
		q['pos1'] = question[2]
		q['word2'] = question[3].lower()
		q['pos2'] = question[4]
		q['context1'] = question[5]
		q['context2'] = question[6]
		r = sum( [ float(question[i]) for i in xrange(8,18)]) / 10.0
		q['rating'] = r
		task[int(question[0])] = q
		words.add(question[1].lower())
		words.add(question[3].lower())
		if allWords:
			for w in (q['context1']+" "+q['context2']).lower().split(' '):
				words.add(w)
	f.close()
	words = [Word(x).lemma() for x in words]
	return task, words

if __name__ == '__main__':
	print load_task("../data/tasks/SCWS/ratings.txt")[:1]


from utils import Stemmer, postag, pos_is_revelant

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
    	return self._lemma 

    def setDescription(self, x):
        self.desc = x

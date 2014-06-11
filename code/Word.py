from utils import Stemmer, postag, pos_is_revelant

class Word:
    def __init__(self, word, desc=None, meta=dict()):
    	self.word = word
    	self.desc = desc
    	self.meta = meta

    	self._lemma = None
      self._pos = None
      self._relevant = None

    def lemma():
    	if self._lemma == None:
    		self._lemma = Stemmer.stem(word)
    	return self._lemma 

   	def pos():
   		if self._pos == None:
   			self._pos = postag(word)
   		return self._pos

   	def relevant():
   		if self._relevant == None:
   			self._relevant = pos_is_revelant(self.pos())
   		return self._relevant

    def setDescription(self, x):
        self.desc = x


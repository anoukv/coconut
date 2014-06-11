from utils import Stemmer, postag, pos_is_revelant

__all__ = ['Word']

class Word:
    def __init__(self, word, desc=None, meta=dict()):
    	self.word = word
    	self.desc = desc
    	self.meta = meta

    	self.lemma = None
        self.pos = None
        self.relevant = None

    def lemma():
    	if self.lemma == None:
    		self.lemma = Stemmer.stem(word)
    	return self.lemma 

   	def pos():
   		if self.pos == None:
   			self.pos = postag(word)
   		return self.pos

   	def relevant():
   		if self.relevant == None:
   			self.relevant = pos_is_revelant(self.pos())
   		return self.relevant

    def setDescription(self, x):
        self.desc = x


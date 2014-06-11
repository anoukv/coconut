from utils import Stemmer, postag, pos_is_revelant

__all__ = ['Word']

class Word:
    def __init__(self, word, desc=None, meta=dict()):
    	self.word = word
    	self.desc = desc
    	self.meta = meta

    	self.lemma = Stemmer.stem(word)
        self.pos = postag(word)
        self.relevant = pos_is_revelant(self.pos)

    def setDescription(self, x):
        self.desc = x


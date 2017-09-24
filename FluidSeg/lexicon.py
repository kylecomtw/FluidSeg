import os
from itertools import groupby
from typing import Tuple
import numpy as np

class LexiconFactory():
    def __init__(self):
        pass

    def get(self, lexfile):
        lex = Lexicon()
        wordlist = self.load_lexfile(lexfile)        
        lex.compile(wordlist)        
        return lex    
    
    def getWithList(self, wordlist):
        lex = Lexicon()
        lex.compile(wordlist)
        return lex
    
    def load_lexfile(self, fpath):
        if not os.path.exists(fpath):
            raise FileNotFoundError("File not found %s" % fpath)

        words = []
        fin = open(fpath, "r", encoding="UTF-8")
        for ln in fin.readlines():
            if ln.startswith("#"): continue
            words.append(ln.strip())
        fin.close()
        
        return words

class LemmaData:
    def __init__(self):
        self.len_hist = None
    
    def __repr__(self):
        return "<LemmaData: %s>" % str(self.len_hist)

class Lexicon:
    def __init__(self):        
        self.wordmap = {}           

    def compile(self, wordlist):
        word_map = {}
        # organize each word into its prefix category
        for word in wordlist:
            prefix = word[0]
            vec_x = word_map.get(prefix, [])
            vec_x.append(word)
            word_map[prefix] = vec_x

        for prefix, words in word_map.items():
            wlenMap = {}
            for w in words:
                wlen = len(w)
                wvec = wlenMap.get(wlen, [])
                wvec.append(w)
                wlenMap[wlen] = wvec

            len_keys = sorted(wlenMap.keys(), reverse=True)
            lenHist = [(L, wlenMap[L]) for L in len_keys]
            ldata = LemmaData()
            ldata.len_hist = lenHist
            word_map[prefix] = ldata

        self.wordmap = word_map

    def query_len_hist(self, prefix):
        if prefix not in self.wordmap:
            return []

        ldata = self.wordmap[prefix]
        lenhist = ldata.len_hist
        return lenhist

    def query_candidates(self, prefix, gran_lb, gran_ub):
        """ query_candidates find the words starting with `prefix`,
        that is between the percentile(0~1) [gran_lb, gran_ub],
        gran_lb is rounded to the nearest lower word length,
        gran_ub is rounded to the nearest higher word length
        """
    
        if prefix not in self.wordmap:
            return []

        ldata = self.wordmap[prefix]
        lenhist = ldata.len_hist
        wlen_vec = np.array([x[0] for x in lenhist])
        # np.percentile will sort the array ascendingly by default,
        # but wlen_vec is sorted descendingly. 
        # so we flip the gran_lb, gran_ub instead
        wlen_ub = np.percentile(wlen_vec, (1-gran_lb)*100, interpolation='higher')
        wlen_lb = np.percentile(wlen_vec, (1-gran_ub)*100, interpolation='lower')

        candid_words = []
        for L, L_words in lenhist:
            if L >= wlen_lb and L <= wlen_ub:
                candid_words += L_words            

        return candid_words


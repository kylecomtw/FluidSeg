import os
from itertools import groupby
from typings import Tuple

class LexiconFactory():
    def __init__(self):
        pass

    def get(self, lexfile):
        lex = Lexicon(lexfile)
        lex.compile()
        return lex

class LemmaData:
    def __init__(self):
        self.len_hist = []

class Lexicon:
    def __init__(self, lexfile):        
        self.wordlist = self.load_lexfile(lexfile)
        self.wordmap = self.compile()

    def load_lexfile(self, fpath):
        if not os.path.exists(fpath):
            raise FileNotFoundError("File not found %s" % fpath)
        
        words = []
        for ln in open(fpath, "r", encoding="UTF-8"):
            if ln.startswith("#"): continue
            words.append(ln.strip())
        
        return words        

    def compile(self):
        word_map = {}
        # organize each word into its prefix category
        for word in self.wordlist:
            prefix = word[0]
            vec_x = word_map.get(prefix, [])
            vec_x.append(word)
            word_map[prefix] = vec_x
        
        for prefix, words in word_map.items():
            wordlen = sorted([len(w) for w in words])            
            lenhist = [(x[0], list(x[1])) for x in groupby(wordlen)]
            ldata = LemmaData()
            ldata.len_hist = lenhist            
            word_map[prefix] = ldata

        return word_map
    
    def query_prefix(self, prefix, granularities: Tuple[float, float]):
        if prefix not in self.wordmap: 
            return []

        ldata = self.wordmap[prefix]
        lenhist = ldata.len_hist
        cumsum = 0
        nWord = sum([len(x[1]) for x in lenhist])
        gran_lb, gran_ub = granularities

        candid_words = []
        for L, L_words in lenhist:
            cumsum += len(L_words)
            if cumsum/nWord > gran_ub:
                break
            if cumsum/nWord > gran_lb:
                candid_words += L_words
        
        return candid_words

    
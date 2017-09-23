import pickle
import re
import pdb
import unicodedata
import os.path
from .segdata import Segments
from .tokenizer import Tokenizer
from .tokendata import TokenData
from .lexicon import Lexicon
import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
logger.addHandler(ch)

class FluidSeg:
    def __init__(self, lexicon: Lexicon) -> None:
        # load lexicon        
        self.lexicon = lexicon
        self.tokenizer = Tokenizer()
    
    def segment(self, tokens):
        tokens = self.tokenizer.tokenize(tokens)
        segData = Segments(tokens)
        gran_length = 10
        gran_step = 1
        for gran in range(0, gran_length, gran_step): 
            gran_arg = gran / gran_length 
            match_seg = self.matchTokens(tokens, gran_arg)
            segData.addLevel(match_seg) 

        return segData
    
    def matchTokens(self, tokens, granularity=0):        
        segList = []
        
        for i in range(0, len(tokens)):
            logger.info(" -- Go to position: %d -- ", i)            
            # iterate through different window size
            segFound = self.tryMatchFromLexicon(tokens, i,granularity)
            if segFound:
                segList.append(segFound)
            else:
                pass            
        return segList 

    def tryMatchFromLexicon(self, tokens, pos, granularity = 0):
        chprefix = tokens[pos]
        lemma_list = self.lexicon.query_prefix(chprefix, granularity)
        lemma_list = sorted(lemma_list, key=len, reverse=True)        
        
        seg = None
        for lemma in lemma_list:
            for cur in range(pos, pos + len(lemma)):
                candidStr = "".join(tokens[pos:pos+cur])
                if not lemma.startswith(candidStr):
                    break
                if candidStr == lemma:
                    lemma_found = lemma
                    chstart = tokens[pos].chstart
                    chend = tokens[pos+cur-1].chend
                    seg = TokenData(lemma_found, chstart, chend)
                    break
            if seg:
                break
        
        return seg
               
  

    

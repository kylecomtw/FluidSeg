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
    
    def segment(self, tokens, gran_steps=3):
        tokens = self.tokenizer.tokenize(tokens)
        segData = Segments(tokens)
        gran_length = gran_steps
        gran_step = 1
        for gran in range(0, gran_length+1, gran_step): 
            gran_x = gran / gran_length             
            logger.info("Trying granularity: [%.1f, %.1f]", gran_x, gran_x)            
            match_seg = self.matchTokens(tokens, gran_x, gran_x)
            logger.info(match_seg)
            segData.addLevel(match_seg) 

        return segData
    
    def matchTokens(self, tokens, gran_lb, gran_ub):        
        segList = []
        
        token_cur = 0
        while token_cur < len(tokens):       
            segFound, seg_end_idx = self.tryMatchFromLexicon(tokens, 
                                        token_cur, gran_lb, gran_ub)
            if segFound:
                segList.append(segFound)
                token_cur = seg_end_idx
            token_cur += 1
        return segList 

    def tryMatchFromLexicon(self, tokens, pos, gran_lb, gran_ub):
        chprefix = tokens[pos].text
        lemma_list = self.lexicon.query_candidates(chprefix, gran_lb, gran_ub)
        lemma_list = sorted(lemma_list, key=len, reverse=True)        

        seg = None
        token_end_idx = -1
        for lemma in lemma_list:            
            # tokens may not be consistent with character boundary
            # therefore the length of lemma is not the number of token.
            # We cannot join len(lemma) tokens directly.
            for end_cur in range(pos+1, pos+len(lemma)+1):
                candidStr = "".join([x.text for x in tokens[pos:end_cur]]) 
                if not lemma.startswith(candidStr):
                    break
                if candidStr == lemma:
                    lemma_found = lemma
                    chstart = tokens[pos].chstart
                    chend = tokens[end_cur-1].chend
                    seg = TokenData(lemma_found, chstart, chend)
                    token_end_idx = end_cur-1
                    break
            if seg:
                break
        
        return (seg, token_end_idx)
               
  

    

import pdb
import logging
from typing import List
from . import seq_algo as SeqAlgo
from .tokendata import TokenData

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
# formatter = logging.Formatter("%(name)s: %(message)s")
# ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

class Segments:
    def __init__(self, tokens: List[TokenData]) -> None:
        self.tokens = tokens
        self.gran_levels = {}
        self.data = ["B" * len(tokens)]
    
    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, x, y):
        self.data[x] = y
    
    def addLevel(self, labels):        
        self.data.append(labels)

    def getLevel(self, gran_level):
        return self.data[gran_level]
    
    def importSegData(self, otherSeg: List[TokenData]):
        # tokens_chstart: [chstart of each token]
        tokens_chstart = [x.chstart for x in self.tokens]
        tokens_chend = [x.chend for x in self.tokens]

        # chstart_map: a reverse map of tokens_chstart
        # a map from chstart to token index
        chstart_map = {chstart: token_i for token_i, chstart in enumerate(tokens_chstart)}
        chend_map = {chend: token_i for token_i, chend in enumerate(tokens_chend)}

        # other_chstart: [chstart of each other token]
        otherseg_chstart = [x.chstart for x in otherSeg]
        otherseg_chend = [x.chend for x in otherSeg]

        # aligned_chstart is the list of corresponding "index" of the 
        # tokens_chstart
        aligned_chstart_idx = SeqAlgo.align_sequence(tokens_chstart, otherseg_chstart)
        aligned_chend_idx = SeqAlgo.align_sequence(tokens_chend, otherseg_chend)

        aligned_chstart = []        
        for idx in aligned_chstart_idx:
            if idx < 0: continue
            chstart_x = tokens_chstart[idx]
            token_idx = chstart_map[chstart_x]
            aligned_chstart.append(token_idx)

        aligned_chend = []        
        for idx in aligned_chend_idx:
            if idx < 0: continue
            chend_x = tokens_chend[idx]
            token_idx = chend_map[chend_x]
            aligned_chend.append(token_idx)        

        logger.info("tokens_chstart: %s", tokens_chstart)
        logger.info("tokens_chend: %s", tokens_chend)
        logger.info("other_chstart: %s", otherseg_chstart)
        logger.info("other_chend: %s", otherseg_chend)
        logger.info("aligned_chstart_idx: %s", aligned_chstart_idx)
        logger.info("aligned_chend_idx: %s", aligned_chend_idx)
        logger.info("aligned_chstart: %s", aligned_chstart)
        logger.info("aligned_chend: %s", aligned_chend)

        nToken = len(self.tokens)
        labels = SeqAlgo.transform_chpos(nToken, aligned_chstart, aligned_chend)        
        return labels

    def presegAsSeed(self, preseg: List[TokenData]):
        preseg_labels = self.importSegData(preseg)
        self.data.append(preseg_labels)

    def show(self, granularity=-1):
        fmm = list()
        bmm = list()
        label = list()
        for chDict in self.data:
            if chDict['forward'] in ('B', 'O'):
                fmm.append("/")
            if chDict['backward'] in ('B', 'O'):
                bmm.append("/")
            if chDict['label'] in ('B', 'O'):
                label.append("/")

            bmm.append(chDict['char'])
            fmm.append(chDict['char'])
            label.append(chDict['char'])

        print("".join(label))
    

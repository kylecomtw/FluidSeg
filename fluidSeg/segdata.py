from typing import List
from .tokendata import TokenData

class Segments:
    def __init__(self, tokens):
        self.tokens = tokens
        self.data = ["B" * len(tokens)]
    
    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, x, y):
        self.data[x] = y

    def addLevels(self, labels):
        self.data.append(labels)

    def getLevels(self):
        return len(self.data)
    
    def presegAsSeed(self, preseg: List[TokenData]):
        # preseg cannot divide token delimit       
        tokens_chstart = [x.chstart for x in self.tokens]
        tokens_chend   = [x.chend for x in self.tokens]
        preseg_chstart = [x.chstart for x in preseg]
        preseg_chend   = [x.chend for x in preseg]
        aligned_chstart = self.align_seq(tokens_chstart, preseg_chstart)
        aligned_chend = self.align_seq(tokens_chend, preseg_chend)
        
        # transform aligned chpos into label
        


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
    

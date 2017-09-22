import pdb
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
        tokens_chend = [x.chend for x in self.tokens]
        preseg_chstart = [x.chstart for x in preseg]
        preseg_chend = [x.chend for x in preseg]
        aligned_chstart = self.align_sequence(tokens_chstart, preseg_chstart)
        aligned_chend = self.align_sequence(tokens_chend, preseg_chend)
        
        # transform aligned chpos into label
    
    def edit_distance(self, seq_ref, seq_x):
        m = len(seq_ref) + 1
        n = len(seq_x) + 1

        tbl = {}   # cost table
        bp = {}    # backpointer table

        # initialize table
        for i in range(m):
            tbl[i, 0] = i
            bp[i, 0] = None

        for j in range(n):
            tbl[0, j] = j
            bp[0, j] = None

        # dynamic programming
        for i in range(1, m):
            for j in range(1, n):
                cost = 0 if seq_ref[i-1] == seq_x[j-1] else 1
                idx_vec = [(i-1, j-1), (i, j-1), (i-1, j)]
                cost_vec = [tbl[idx_vec[0]]+cost, tbl[idx_vec[1]]+1, tbl[idx_vec[2]]+1]
                min_cost = min(cost_vec)                
                min_opt = cost_vec.index(min_cost)
                bp[i,j] = idx_vec[min_opt]
                tbl[i,j] = min_cost        
        return bp
    
    def align_sequence(self, seq_ref, seq_x):
        # bp_map: Map[(int, int), (int, int)]
        bp_map = self.edit_distance(seq_ref, seq_x)
        m = len(seq_ref)+1
        n = len(seq_x)+1
        bp = bp_map[m-1, n-1]
        
        seq_x_map = {}

        seq_x_map[n-1] = m-1
        while(bp):
            ref_idx = bp[0]
            x_idx = bp[1]   
            seq_x_map[x_idx] = min(ref_idx, seq_x_map.get(x_idx, m))
            bp = bp_map[bp]         

        # the minus one come frome the start element in edit matrix
        idx_of_ref = [seq_x_map[x]-1 for x in range(1, n)]
        dec_idx = []
        for idx_x, idx_ref in enumerate(idx_of_ref):
            if seq_x[idx_x] == seq_ref[idx_ref]:
                dec_idx.append(idx_ref)
            else:
                dec_idx.append(-1)
        return dec_idx

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
    

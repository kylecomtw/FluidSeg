import unittest
import pickle
import pdb
from itertools import chain
from unittest import TestCase
from FluidSeg import Segments
from FluidSeg.tokenizer import Tokenizer
from FluidSeg.tokendata import TokenData

class SegDataTest(TestCase):
    def testAlignSequence(self):
        seg = Segments(list(range(10)))
        aidx = seg.align_sequence([1, 4, 5, 6, 7], [1, 3, 5, 6, 7])        
        # self.assertListEqual(aidx, [0, -1, 2, 3, 4])
        aidx2 = seg.align_sequence([1, 2, 3], [1, 2, 3, 4])
        # self.assertListEqual(aidx2, [0, 1, 2, -1])
        aidx3 = seg.align_sequence([1, 2, 3, 5, 6], [1, 2, 6])
        # self.assertListEqual(aidx3, [0, 1, 4])
        aidx4 = seg.align_sequence([1, 2, 3, 5, 6], [1, 2, 4, 6])         
        # self.assertListEqual(aidx4, [0, 1, -1, 4])
        aidx5 = seg.align_sequence([1, 2, 3, 5, 6], [1, 6, 7, 8])         
        print(aidx5)
        self.assertListEqual(aidx4, [0, 4, -1, -1])

    @unittest.skip("")    
    def testPresegAsSeed(self):
        tokens = Tokenizer().tokenize("今天來說的話，沒有其實也沒關係  ^^;*~.`")
        seg = Segments(tokens)
        ocseg = pickle.load(open("test_seg.pyObj", "rb"))        
        preseg = chain.from_iterable(ocseg.tokens)
        preseg = [TokenData(x[0], x[3], x[4])for x in preseg]        
        seg.presegAsSeed(preseg)
        print(seg.data)
        print("Tokens:", str(tokens))
        print("Preseg:", preseg)

if __name__ == "__main__":
    unittest.main()
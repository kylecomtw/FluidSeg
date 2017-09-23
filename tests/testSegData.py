import unittest
import pickle
import pdb
import logging
from itertools import chain
from unittest import TestCase
from FluidSeg import Segments
from FluidSeg.tokenizer import Tokenizer
from FluidSeg.tokendata import TokenData

class SegDataTest(TestCase):
    
    def testPresegAsSeed(self):
        logging.getLogger("FluidSeg.segdata").setLevel("WARNING")
        tokens = Tokenizer().tokenize("今天來說的話，沒有其實也沒關係  ^^;*~.`")
        seg = Segments(tokens)
        ocseg = pickle.load(open("test_seg.pyObj", "rb"))        
        preseg = chain.from_iterable(ocseg.tokens)
        preseg = [TokenData(x[0], x[3], x[4])for x in preseg]        
        seg.presegAsSeed(preseg)        
        # print(seg.data)
        # print("Tokens:", str(tokens))
        # print("Preseg:", preseg)
        self.assertEqual(seg.data[1], "BEBEBEBBEBEBBOEB")

if __name__ == "__main__":
    unittest.main()
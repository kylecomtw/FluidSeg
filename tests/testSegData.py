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

    # @unittest.skip("")
    def testPreseg(self):
        logging.getLogger("FluidSeg.segdata").setLevel("WARNING")
        tokens = Tokenizer().tokenize("今天來說的話，沒有其實也沒關係  ^^;*~.`")
        seg = Segments(tokens)
        ocseg = pickle.load(open("test_seg.pyObj", "rb"))
        preseg = chain.from_iterable(ocseg.tokens)
        preseg = [TokenData(x[0], x[3], x[4])for x in preseg]
        seg.setPresegment(preseg)
        aligned_seg = seg.merge_segments(seg.tokens, seg.preseg)
        print("Tokens:", str(tokens))
        print("Preseg:", preseg)
        print("Preseg-aligned: ", aligned_seg)
        # print("Labels: ", labels)
        # self.assertEqual(seg.data[1], "BEBEBEBBEBEBBOEB")

    # @unittest.skip("")
    def testPartialPreseg(self):
        logging.getLogger("FluidSeg.segdata").setLevel("WARNING")
        tokens = Tokenizer().tokenize("今天來說的話，沒有其實也沒關係  ^^;*~.`")
        seg = Segments(tokens)
        preseg = [TokenData("其實也沒關係", 9, 15)]
        aligned_preseg = seg.merge_segments(tokens, preseg)

        print("Tokens:", str(tokens))
        print("Preseg:", preseg)
        print("Preseg-aligned: ", aligned_preseg)
        # print("Labels: ", labels)
        # self.assertEqual(seg.data[1], "BEBEBEBBEBEBBOEB")

    def testUnmatchedStartEnd(self):
        tokens = Tokenizer().tokenize("我不知道")
        seg = Segments(tokens)
        preseg = [TokenData("我", 0, 1), TokenData("知不知道", 1, 4), TokenData("你", 4, 5)]
        chunks = [TokenData("道", 3, 4), TokenData("你", 4, 5)]
        aligned_chunks = seg.merge_segments(preseg, chunks)
        print("aligned_chunks", aligned_chunks)


if __name__ == "__main__":
    unittest.main()
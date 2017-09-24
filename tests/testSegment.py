import pickle
from itertools import chain
from unittest import TestCase
import unittest
from FluidSeg import FluidSeg
from FluidSeg import LexiconFactory
from FluidSeg import TokenData

class SegTest(TestCase):
    
    def testSegment(self):
        lexicon = LexiconFactory().get("test_lexfile.txt")
        fseg = FluidSeg(lexicon)
        segData = fseg.segment("今天來說的話，我想說，不知道大家要不要再研究看看。")
        with open("test_segment.pyObj", "rb") as fin:
            od = pickle.load(fin)
            preseg = list(chain.from_iterable(od.tokens)) 
            preseg = [TokenData(x[0], x[3], x[4]) for x in preseg] 
        segData.setPresegment(preseg)        
        # print(segData)

        # print("TokenRef: ", segData.toSegmentedText(segData.tokens, 1))
        print(segData.preseg)
        print("PresegRef: ", segData.toSegmentedText(segData.preseg, 1))
    
    def testGranularSegment(self):
        lexicon = LexiconFactory().get("test_lexfile.txt")
        fseg = FluidSeg(lexicon)
        tokens = fseg.tokenizer.tokenize("今天來說的話，我想說，不知道大家要不要再研究看看。")        
        match_seg = fseg.matchTokens(tokens, 1.0, 1.0)
        wlen_seg = [len(x.text) for x in match_seg]
        self.assertListEqual(wlen_seg, [4,2,3,3,3,3])        
    
    def testBroaderSegment(self):        
        lexicon = LexiconFactory().get("test_lexfile.txt")
        fseg = FluidSeg(lexicon)
        tokens = fseg.tokenizer.tokenize("今天來說的話，我想說，不知道大家要不要再研究看看。")              
        match_seg = fseg.matchTokens(tokens, 0, 0)
        wlen_seg = [len(x.text) for x in match_seg]                
        self.assertListEqual(wlen_seg, [6, 3, 13])    


if __name__ == "__main__":
    unittest.main()
import unittest
from FluidSeg.lexicon import LexiconFactory

TEST_LEXFILE = "test_lexfile.txt"
class LexiconTest(unittest.TestCase):
    def testLexiconLoad(self):
        lex = LexiconFactory().get(TEST_LEXFILE)
        print(lex.wordmap)
        self.assertTrue(True)

    def testLexiconSupp(self):
        lex = LexiconFactory().get(TEST_LEXFILE)
        lex.addSupplementary(["我也不知道", "應該大概n是", "應該吧", "應該"])
        self.assertEqual(len(lex.wordmap["我"].len_hist), 2)
        self.assertEqual(len(lex.wordmap["應"].len_hist), 3)        
        lex.addSupplementary(["我想說"])
        print("\n")        
        self.assertEqual(len(lex.wordmap["我"].len_hist), 1)
        self.assertFalse("應" in lex.wordmap)
        

    def testLexiconQuery(self):
        lex = LexiconFactory().get(TEST_LEXFILE)        
        lhist = lex.query_len_hist("不")
        # print(lhist)
        for item in lhist:
            self.assertTrue(isinstance(item[0], int))
            self.assertTrue(all([isinstance(x, str) for x in item[1]]))
    
    def testGranularity(self):
        lex = LexiconFactory().get(TEST_LEXFILE)        
        candids = lex.query_candidates("不", 0.5, 1)                                        
        self.assertEqual(len(candids[0]), 8)
        self.assertEqual(len(candids[1]), 3)
        self.assertEqual(len(candids), 2)
        print(lex.query_candidates("不", 0.5, 1.0))

if __name__ == "__main__":
    unittest.main()
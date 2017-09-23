import unittest
import pickle
import pdb
import logging
from itertools import chain
from unittest import TestCase
import FluidSeg.seq_algo as SeqAlgo

class SegDataTest(TestCase):
    def testAlignSequence(self):
        aidx = SeqAlgo.align_sequence([1, 4, 5, 6, 7], [1, 3, 5, 6, 7])        
        self.assertListEqual(aidx, [0, -1, 2, 3, 4])
        aidx2 = SeqAlgo.align_sequence([1, 2, 3], [1, 2, 3, 4])
        self.assertListEqual(aidx2, [0, 1, 2, -1])
        aidx3 = SeqAlgo.align_sequence([1, 2, 3, 5, 6], [1, 2, 6])
        self.assertListEqual(aidx3, [0, 1, 4])
        aidx4 = SeqAlgo.align_sequence([1, 2, 3, 5, 6], [1, 2, 4, 6])         
        self.assertListEqual(aidx4, [0, 1, -1, 4])
        aidx5 = SeqAlgo.align_sequence([1, 2, 3, 5, 6], [1, 6, 7, 8])                 
        self.assertListEqual(aidx5, [0, 4, -1, -1])
    
if __name__ == "__main__":
    unittest.main()
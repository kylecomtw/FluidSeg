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

    def testGenerateLabels(self):
        tok_seq = {'start': [0, 2, 4, 6, 7, 9, 11, 12, 15], 
                   'end': [1, 3, 5, 6, 8, 10, 11, 14, 15]}
        labels = SeqAlgo.generate_labels(16, tok_seq["start"], tok_seq["end"])
        self.assertEqual(labels, "BEBEBEBBEBEBBIEB")   

    def testPartialLabels(self):     
        tok_seq = {'start': [4, 11], 
                   'end': [7, 15]}
        labels = SeqAlgo.generate_labels(16, tok_seq["start"], tok_seq["end"])        
        self.assertEqual(labels, "XXXXBIIEXXXBIIIE") 

    def testMergeLabels(self):
        labels_a = "BEBBEEBEBIIEB"
        labels_b = "BEBEEEBEBIIEB"
        mlabels = SeqAlgo.merge_labels(labels_a, labels_b)
        print(mlabels)

if __name__ == "__main__":
    unittest.main()
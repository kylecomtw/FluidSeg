import unittest
from unittest import TestCase
from FluidSeg import Segments

class SegDataTest(TestCase):
    def testAlignSequence(self):
        seg = Segments(list(range(10)))
        aidx = seg.align_sequence([1, 4, 5, 6, 7], [1, 3, 5, 6, 7])        
        self.assertListEqual(aidx, [0, -1, 2, 3, 4])
        aidx2 = seg.align_sequence([1, 2, 3], [1, 2, 3, 4])
        self.assertListEqual(aidx2, [0, 1, 2, -1])
        aidx3 = seg.align_sequence([1, 2, 3, 5, 6], [1, 2, 6])
        self.assertListEqual(aidx3, [0, 1, 4])
        aidx4 = seg.align_sequence([1, 2, 3, 5, 6], [1, 2, 4, 6])         
        self.assertListEqual(aidx4, [0, 1, -1, 4])
    
if __name__ == "__main__":
    unittest.main()
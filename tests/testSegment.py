from unittest import TestCase
import unittest
from FluidSeg import FluidSeg
from FluidSeg import LexiconFactory

def SegTest(TestCase):
    lexicon = LexiconFactory.get()
    fseg = FluidSeg(lexicon)
    fseg.segment("今天來說的話，我想說，不知道大家要不要再研究看看。")

if __name__ == "__main__":
    unittest.main()
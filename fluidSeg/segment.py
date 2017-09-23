import pickle
import re
import pdb
import unicodedata
import os.path
from .segdata import Segments
from .tokenizer import Tokenizer
from .tokendata import TokenData
import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
logger.addHandler(ch)

class FluidSeg:
    
    def __init__(self, lexicon):
        # load lexicon
        basepath = os.path.dirname(os.path.abspath(__file__))
        self.lexicon = lexicon        
        self.suppLexicon = {}        
        self.tokenizer = Tokenizer()

    def setSupplementLexicon(self, auxDict):
        self.suppLexicon = auxDict

    def parse(self, textStr):
        tokens = self.tokenizer.tokenize(textStr)
        segData = Segments(tokens)        
        fwd_mat = self.maxMatching('forward', tokens)
        bck_mat = self.maxMatching('backward', tokens)
        seg_labels = self.resolve(fwd_mat, bck_mat)                    

        return segData
    
    def resolve(self, fwd_match, bck_match):
        pass

    def isOutBound(self, pos, winSize, direction):
        MAX_STRLEN = len(self.targetStr)
        if direction == 'forward':
            return winSize > MAX_STRLEN - pos
        elif direction == 'backward':
            return winSize > pos + 1
        else: 
            raise Exception('Not valid direction')
            

    def getRangeIter(self, maxIndex, direction):
        if direction == 'forward':
            stringIter = range(0, maxIndex)
        elif direction == 'backward':
            stringIter = range(maxIndex - 1, -1, -1)
        else:
            raise Exception('Not valid direction')

        return stringIter

    def getChunk(self, pos, winSize, direction):
        
        MAX_STRLEN = len(self.targetStr)
        if direction == 'forward':
            lb = max(0, pos)
            ub = min(pos + winSize, MAX_STRLEN)
        elif direction == 'backward':
            lb = max(0, pos - (winSize - 1))
            ub = min(pos + 1, MAX_STRLEN)
        else:
            raise Exception('Not valid direction')

        chunk = self.targetStr[lb: ub]
        return chunk
    
    def getLabel(self, winSize, direction):
        if direction == 'forward':
            return ('B', 'E')
        elif direction == 'backward':
            # if window is one, a one-char word is labeled as B
            if winSize == 1:
                return ('B', 'B')
            else:
                return ('E', 'B')
        else:
            raise Exception('Not valid direction')

    def tryWindowSize(self, pos, maxWin, direction):

        for w in range(maxWin, 0, -1):
            logger.info("Try window size: {0}".format(w))
            # if remaining string is not encough, go to next
            if self.isOutBound(pos, w, direction): continue
            
            # get the string
            chunk = self.getChunk(pos, w, direction)
            logger.info("Testing chunk: {0}".format(chunk))            
            if len(chunk) == 1 and\
                unicodedata.category(chunk) in self.EXCLUDE_CATEGORY:
                logger.info("Found in excluded category: {0}".format(chunk), 2)
                return {'label': 'O', 'labelStack': []}
                
            if chunk in self.wdict:
                
                # if the chunk is a known word, the lower window can be
                # skipped, information is stored in _labelStack_
                logger.info("known word: {0}".format(chunk), 2)
                label = self.getLabel(w, direction) 
                labelStack = [label[1]] * min(w - 1, 1)+ ['I'] * max((w - 2), 0)
                logger.info("labelStack pushed: {0}".format(labelStack), 2)
                return {'label': label[0], 'labelStack': labelStack}

            else:
                if len(chunk) == 1:
                    logger.info("No matching word in dictionary: {0}" \
                            .format(chunk), 2)
                    return {'label': 'O', 'labelStack': []}

        
        # if all check failed, return an empty dict
        return {'label': '', 'labelStack': []}

    def maxMatching(self, tokens, direction, maxWin = 4):

        targetStr = self.targetStr
        segList = self.segList

        if len(targetStr) != len(segList):
            raise Exception("ERROR: String and segList length mismatch!")
        
        labelStack = []
        # Loop through the target string

        for i in self.getRangeIter(len(targetStr), direction):
            logger.info(" -- Go to position: {0} -- ".format(i), 2)
            if len(labelStack) > 0:
                label = labelStack.pop()
                logger.info("Assign label '{0}'".format(label), 2)
                segList[i][direction] = label
                continue

            # iterate through different window size
            labelDict = self.tryWindowSize(i, maxWin, direction)
            segList[i][direction] = labelDict['label']
            labelStack = labelDict['labelStack']
        return segList

    def GetSegment(self):
        label = list()
        for chDict in self.segList:            
            if chDict['label'] in ('B', 'O'):
                label.append("/")
            label.append(chDict['char'])

        return ''.join(label)

    def GetAmbigFlag(self):
        return self.isAmbig

    def detectAmbig(self):
        logger.info("Ambiguity check...")
        self.isAmbig = False
        for chDict in self.segList:
            if not chDict['forward'] == chDict['backward']:
                self.isAmbig = True
                break

        if not self.isAmbig:
            for chDict in self.segList:
                chDict['label'] = chDict['forward']
            logger.info("pass")
        else:
            logger.info("FOUND")
            self.resolveAmbig()

        return

    def getWordList(self, version):
        logger.info('Parse word lists')
        wordList = []
        word = [] 
        prevLabel = ''
        for chDict in self.segList:
            label = chDict[version]            
            logger.info(' -- label: {0} -- '.format(label))

            if prevLabel + label == 'BB' or \
                prevLabel + label == 'BO':
                logger.info('BB: flush and new')
                wordList.append(''.join(word))
                word = []

            if label in ('B', 'E', 'I'):
                logger.info('B|E|I: push', 2)
                word.append(chDict['char'])
            
            if label in ('E'):
                logger.info('E|O: flush and new')
                wordList.append(''.join(word))
                word = []

            prevLabel = label
        logger.info(wordList, 2)
        return wordList
    
    def var(self, vec):
        n = len(vec)
        if n==1: return None

        x2sum = sum([x**2 for x in vec])
        xbar = sum(vec) / n
        SS = x2sum - n * (xbar ** 2)
        return SS/(n-1)


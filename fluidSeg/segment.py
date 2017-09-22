import pickle
import re
import pdb
import unicodedata
import os.path
from pyCSeg.cacheHandler import SegCache
class SimpleSeg:

    def __init__(self):
        basepath = os.path.dirname(os.path.abspath(__file__))
        with open(basepath  + '/as_wordFreq.pickle', 'rb') as fin:
            self.wdict = pickle.load(fin)

        self.segList = None
        self.targetStr = None
        self.segCache = SegCache()
        self.useCache = True
        
        self.EXCLUDE_CATEGORY = \
            ('Po', 'Ps', 'Pe', 'Pd', 'Pc', 'Ll', 'Lu', 'Nd', 'Sm')
    
    def SetUseCache(self, flag):
        self.useCache = flag

    def SetAuxDict(self, auxDict):
        self.wdict.update(auxDict)

    def Parse(self, targetStr, verbose):
        if self.useCache:
            seg = self.segCache.readCache(targetStr)
            self.isAmbig = None
        else:
            seg = None

        if seg is None:
            self.verbose = verbose
            self.targetStr = targetStr
            self.isAmbig = True
            self.segList = self.initializeSegList(self.targetStr)
            self.segList = self.maxMatching('forward')
            self.segList = self.maxMatching('backward')
            self._print(self.segList, 2)
            self.detectAmbig()
            self.ReportSeg()
            seg = self.GetSegment()            

        return seg

    def initializeSegList(self, targetStr):
        strList = list()
        for ch in targetStr:
            chDict = {
                'char': ch,
                'label': '',
                'forward': '',
                'backward': ''
            }

            strList.append(chDict)
        return strList
    
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
            self._print("Try window size: {0}".format(w), 2)
            # if remaining string is not encough, go to next
            if self.isOutBound(pos, w, direction): continue
            
            # get the string
            chunk = self.getChunk(pos, w, direction)
            self._print("Testing chunk: {0}".format(chunk), 2)            
            if len(chunk) == 1 and\
                unicodedata.category(chunk) in self.EXCLUDE_CATEGORY:
                self._print("Found in excluded category: {0}".format(chunk), 2)
                return {'label': 'O', 'labelStack': []}
                
            if chunk in self.wdict:
                
                # if the chunk is a known word, the lower window can be
                # skipped, information is stored in _labelStack_
                self._print("known word: {0}".format(chunk), 2)
                label = self.getLabel(w, direction) 
                labelStack = [label[1]] * min(w - 1, 1)+ ['I'] * max((w - 2), 0)
                self._print("labelStack pushed: {0}".format(labelStack), 2)
                return {'label': label[0], 'labelStack': labelStack}

            else:
                if len(chunk) == 1:
                    self._print("No matching word in dictionary: {0}" \
                            .format(chunk), 2)
                    return {'label': 'O', 'labelStack': []}

        
        # if all check failed, return an empty dict
        return {'label': '', 'labelStack': []}

    def maxMatching(self, direction, maxWin = 4):

        targetStr = self.targetStr
        segList = self.segList

        if len(targetStr) != len(segList):
            raise Exception("ERROR: String and segList length mismatch!")
        
        labelStack = []
        # Loop through the target string

        for i in self.getRangeIter(len(targetStr), direction):
            self._print(" -- Go to position: {0} -- ".format(i), 2)
            if len(labelStack) > 0:
                label = labelStack.pop()
                self._print("Assign label '{0}'".format(label), 2)
                segList[i][direction] = label
                continue

            # iterate through different window size
            labelDict = self.tryWindowSize(i, maxWin, direction)
            segList[i][direction] = labelDict['label']
            labelStack = labelDict['labelStack']
        return segList

    def ReportSeg(self):
        fmm = list()
        bmm = list()
        label = list()
        for chDict in self.segList:
            if chDict['forward'] in ('B', 'O'):
                fmm.append("/")
            if chDict['backward'] in ('B', 'O'):
                bmm.append("/")
            if chDict['label'] in ('B', 'O'):
                label.append("/")

            bmm.append(chDict['char'])
            fmm.append(chDict['char'])
            label.append(chDict['char'])

        self._print("FMM: {0}".format(''.join(fmm)), 0)
        self._print("BMM: {0}".format(''.join(bmm)), 0)
        self._print("Final: {0}".format(''.join(label)), 0)
    
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
        self._print("Ambiguity check...", 0)
        self.isAmbig = False
        for chDict in self.segList:
            if not chDict['forward'] == chDict['backward']:
                self.isAmbig = True
                break

        if not self.isAmbig:
            for chDict in self.segList:
                chDict['label'] = chDict['forward']
            self._print("pass", 0)
        else:
            self._print("FOUND", 0)
            self.resolveAmbig()

        return

    def getWordList(self, version):
        self._print('Parse word lists', 2)
        wordList = []
        word = [] 
        prevLabel = ''
        for chDict in self.segList:
            label = chDict[version]            
            self._print(' -- label: {0} -- '.format(label), 2)

            if prevLabel + label == 'BB' or \
                prevLabel + label == 'BO':
                self._print('BB: flush and new', 2)
                wordList.append(''.join(word))
                word = []

            if label in ('B', 'E', 'I'):
                self._print('B|E|I: push', 2)
                word.append(chDict['char'])
            
            if label in ('E'):
                self._print('E|O: flush and new', 2)
                wordList.append(''.join(word))
                word = []

            prevLabel = label
        self._print(wordList, 2)
        return wordList
    
    def var(self, vec):
        n = len(vec)
        if n==1: return None

        x2sum = sum([x**2 for x in vec])
        xbar = sum(vec) / n
        SS = x2sum - n * (xbar ** 2)
        return SS/(n-1)

    def resolveAmbig(self):
        cherry = self.deambiguateHandler()
        
        if cherry is None:
            self._print("Disambiguity failed.", 0)
        else:
            for chDict in self.segList:
                chDict['label'] = chDict[cherry]
        return

    def deambiguateHandler(self):
        evenWL = self.evenWordLenDeambig()
        if not evenWL is None:
            self._print("Ambiguities resolved with even word length.", 0)
            self._print("method {0} is picked.".format(evenWL), 2)
            return evenWL

        maxDOF = self.maxSingleDOFDeambig()
        if not maxDOF is None:
            self._print("Ambiguities resolved with single word DOF.", 0)
            self._print("method {0} is picked.".format(maxDOF), 2)
            return maxDOF 
        return None

        maxFreq = self.maxFreqDeambig()
        if not maxFreq is None:
            self._print("Fallback to maximum frequency sum.", 0)
            self._print("method {0} is picked.".format(maxFreq), 2)
            return maxFreq 

        return None
    
    def evenWordLenDeambig(self):
        fmmList = self.getWordList('forward')
        bmmList = self.getWordList('backward')
        fmmWL = [len(x) for x in fmmList]
        bmmWL = [len(x) for x in bmmList]
        fmmVar = self.var(fmmWL)
        bmmVar = self.var(bmmWL)
        self._print((fmmWL, bmmWL), 2)
        self._print("FMM WordLen Variance: {0}".format(fmmVar), 2)
        self._print("BMM WordLen Variance: {0}".format(bmmVar), 2)
        if fmmVar is None or bmmVar is None:
            return None
        elif fmmVar < bmmVar:
            return "forward"
        elif fmmVar > bmmVar:
            return "backward"
        else:
            return None

    def maxSingleDOFDeambig(self):
        fmmList = self.getWordList('forward')
        bmmList = self.getWordList('backward')
        
        fmmSingle = [x for x in filter(lambda x: len(x) == 1, fmmList)]
        bmmSingle = [x for x in filter(lambda x: len(x) == 1, bmmList)]
        fmmSum = sum([self.wdict[x] for x in fmmSingle])
        bmmSum = sum([self.wdict[x] for x in bmmSingle])

        self._print((fmmSum, bmmSum), 2)
        self._print("FMM WordFreq Sum: {0}".format(fmmSum), 2)
        self._print("BMM WordFreq Sum: {0}".format(bmmSum), 2)
        
        if fmmSum > bmmSum:
            return "forward"
        elif fmmSum < bmmSum:
            return "backward"
        else:
            return None

    def maxFreqDeambig(self):
        fmmList = self.getWordList('forward')
        bmmList = self.getWordList('backward')

        fmmFreq = [self.wdict[x] for x in fmmList]
        bmmFreq = [self.wdict[x] for x in bmmList]
        
        fmmSum = sum(fmmFreq)
        bmmSum = sum(bmmFreq)
        
        self._print((fmmSum, bmmSum), 2)
        self._print("FMM WordFreq Sum: {0}".format(fmmSum), 2)
        self._print("BMM WordFreq Sum: {0}".format(bmmSum), 2)
        if fmmSum > bmmSum:
            return "forward"
        elif fmmSum < bmmSum:
            return "backward"
        else:
            return None

    def _print(self, msg, msgLevel):
        if msgLevel <= self.verbose:
            print(msg)

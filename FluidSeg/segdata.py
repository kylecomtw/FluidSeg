import pdb
import logging
from typing import List, Dict
from io import StringIO
from . import seq_algo as SeqAlgo
from .tokendata import TokenData

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
# formatter = logging.Formatter("%(name)s: %(message)s")
# ch.setFormatter(formatter)
logger.addHandler(ch)
# logger.setLevel(logging.INFO)

class Segments:
    def __init__(self, tokens: List[TokenData]) -> None:
        self.tokens = tokens
        self.preseg = []   # type: List[TokenData]
        self.data = {}     # type: Dict[int, List[TokenData]]

    def __repr__(self):
        strbuf = ["<Segments>"]
        if self.tokens:
            strbuf.append("Tokens: \n  " + str(self.tokens))
        if self.preseg:
            strbuf.append("Preseg: \n  " + str(self.preseg))
        if self.data:
            strbuf.append("Data: ")
            for k in sorted(self.data.keys(), reverse=True):
                strbuf.append("  [%.2f]: %s" % (k, str(self.data[k])))
        return "\n".join(strbuf)

    def addLevel(self, granularity, chunks):
        if granularity in self.data:
            logger.warning("granularity %.2f already exists", granularity)
        self.data[granularity] = chunks

    def getLevel(self, granularity):
        if granularity not in self.data:
            return self.data[granularity]
        else:
            logger.warning("granularity %.2f not found", granularity)
            return []

    def setPresegment(self, preseg: List[TokenData]):
        aligned_preseg = self.merge_segments(self.tokens, preseg)
        self.preseg = aligned_preseg

    def find_cloest_granularity(self, gran):
        if gran not in self.data:
            closest_g = -1
            min_diff = 2
            for g in self.data.keys():
                diff = abs(g-gran)
                if diff < min_diff:
                    min_diff = diff
                    closest_g = g
            if closest_g > 0:
                return closest_g
            else:
                logger.error("Cannot find valid granularity, use the min gran.")
                return min(self.data.keys())
        else:
            return gran

    def toSegmentedText(self, ref_seg=None, granularity=-1):    
        if not ref_seg:
            ref_seg = self.tokens
        if granularity >= 0:
            gran = self.find_cloest_granularity(granularity)
            gran_seg = self.data[gran]
            tokseg = self.merge_segments(ref_seg, gran_seg)
        else:
            # there is no data in self.data
            tokseg = self.merge_segments(ref_seg, ref_seg)
        
        return "\u3000".join(x.text for x in tokseg)

    def merge_segments(self, refSeg: List[TokenData], otherSeg: List[TokenData]):
        # tokens_chstart: [chstart of each token]
        tokens_chstart = [x.chstart for x in refSeg]
        tokens_chend = [x.chend for x in refSeg]

        # chstart_map: a reverse map of tokens_chstart
        # a map from chstart to token index
        chstart_map = {chstart: token_i for token_i, chstart in enumerate(tokens_chstart)}
        chend_map = {chend: token_i for token_i, chend in enumerate(tokens_chend)}

        # other_chstart: [chstart of each other token]
        otherseg_chstart = [x.chstart for x in otherSeg]
        otherseg_chend = [x.chend for x in otherSeg]

        # aligned_chstart_idx is the list of corresponding "index" of the
        # tokens_chstart
        aligned_chstart_idx = SeqAlgo.align_sequence(tokens_chstart, otherseg_chstart)
        aligned_chend_idx = SeqAlgo.align_sequence(tokens_chend, otherseg_chend)

        aligned_chstart = [tokens_chstart[i] for i in aligned_chstart_idx if i >= 0]
        aligned_chend = [tokens_chend[i] for i in aligned_chend_idx if i >= 0]

        merged_seg = []        
        token_i = 0
        while token_i < len(refSeg):
            tok_chstart = refSeg[token_i].chstart
            tok_idx_end = token_i
            if tok_chstart in aligned_chstart:
                try:
                    aidx = aligned_chstart.index(tok_chstart)
                    chend_x = aligned_chend[aidx]
                    tok_idx_end = chend_map[chend_x]
                except:
                    pdb.set_trace()
            tok_list = refSeg[token_i:tok_idx_end+1]
            tok_text = "".join([x.text for x in tok_list])
            try:
                tok_start = tok_list[0].chstart
                tok_end = tok_list[-1].chend
            except:
                pdb.set_trace()
            tok_x = TokenData(tok_text, tok_start, tok_end)
            merged_seg.append(tok_x)
            token_i = tok_idx_end + 1

        logger.info("tokens_chstart: %s", tokens_chstart)
        logger.info("tokens_chend: %s", tokens_chend)
        logger.info("other_chstart: %s", otherseg_chstart)
        logger.info("other_chend: %s", otherseg_chend)
        logger.info("aligned_chstart_idx: %s", aligned_chstart_idx)
        logger.info("aligned_chend_idx: %s", aligned_chend_idx)
        logger.info("aligned_chstart: %s", aligned_chstart)
        logger.info("aligned_chend: %s", aligned_chend)

        return merged_seg


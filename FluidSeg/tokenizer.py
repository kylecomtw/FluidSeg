import re
from .tokendata import TokenData

class Tokenizer:
    TOKEN_PAT = r"[\u3400-\u9fff\uf900-\ufaff]|[^\s\u3400-\u9fff\uf900-\ufaff]+"
    def __init__(self):
        self.token_pat = re.compile(Tokenizer.TOKEN_PAT)
        
    def tokenize(self, text):
        token_mat_iter = self.token_pat.finditer(text)
        tokens = []
        for it in token_mat_iter:
            tokens.append(TokenData(it.group(), it.start(), it.end()))
        return tokens

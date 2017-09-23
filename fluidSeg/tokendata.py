class TokenData:
    def __init__(self, txt, start, end):
        self.text = txt
        self.chstart = start
        self.chend = end

    def __repr__(self):
        return "<{}-{},{}>".format(self.text, self.chstart, self.chend)
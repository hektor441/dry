from sys import argv
from dry_reduction import *

### UTILITIES ###

def typeof(x):
    if type(x) == list: return "Group"
    elif type(x) == str:
        if x[0].isupper() or x[0] == "?": return "Variable"
        else: return "Keyword"
    raise TypeError

def separate(s):
    s = s.replace("\n", "")
    for c in [".", "=", "#", "(", ")"]:
        s = s.replace(c, " "+c+" ")
    s = s.split(" ")
    
    while "" in s:
        s.remove("")
    return s

class Code:
    def __init__(self, code):
        self.code = code
        
        if len(code) == 0:
            print("The code is empty")
            raise Exception
        
        self.eof = "% EOF %"
        self.indx = 0
        self.tokn = self.code[0]

    def succ(self):
        if self.indx + 1 < len(self.code):
            self.indx += 1
            self.tokn = self.code[self.indx]
        else:
            self.tokn = self.eof

    def expc(self, x):
        if self.tokn == x:
            return self.succ()
        self.error(x + " expected, " + self.tokn + " found")
    
    def error(self, msg):
        print(msg)
        exit()

### PARSING ###

def parse_expr(p):
    ret = []
    while not p.tokn in [".", "=", ")", p.eof]:
        if p.tokn == "(":
            # enclosed expression (group)
            p.succ()
            ret.append(parse_expr(p))
            p.expc(")")
        else:
            # anything that can be a Variable or Keyword
            ret.append(p.tokn)
            p.succ()

    return ret
    
def parse(p):
    while p.tokn != p.eof:
        expr = parse_expr(p)
        if p.tokn == "=":
            # definition
            p.succ()
            reduction = parse_expr(p)
            add_reduction(expr, reduction)
            #print("Added reduction ",expr, "->", reduction)
        else:
            ret = continuously_reduce(expr)
            #print(ret)
        p.expc(".")

    
    while len(OUT_STREAM) + len(ERR_STREAM) > 0:
        if len(ERR_STREAM) > 0:
            print(ERR_STREAM[0])
            ERR_STREAM.pop(0)
        if len(OUT_STREAM) > 0:
            print(OUT_STREAM[0])
            OUT_STREAM.pop(0)


INLINE = len(argv) == 1

if INLINE:
    print("Not yet implemented")
else:
    file = "\n".join(open(argv[1]).readlines())
    file = separate(file)
    if len(file) > 1:
        code = Code(file)
        parse(code)
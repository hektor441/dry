
PVARS = {}

def add_var(k, v):
    global PVARS
    PVARS[k] = v

def match(x, m):
    # x -> input
    # m -> word to match x with
    # x and m are always lists [x0 x1 x.i] [m0 m1 m.k]
    # where each x.i and m.i can be either Keyword or Variable
    
    lx = len(x)
    
    # when x and m have different length they cannot match
    if lx != len(m):
        return False
    
    for i in range(0, lx):
        xi = x[i]
        mi = m[i]
        if type(mi) == "Keyword":
            # a keyword can only match another, identical, keyword
            if mi != ki:
                return False
        elif type(mi) == "Variable":
            # a variable can match either a keyword or another variable
            # x[i] now is trying to give an actual value to m[i]
            
            if mi in pvars:
                # if any value has already been given to m[i], x[i] should match it 
                if xi != pvars[mi]:
                    return False
            else:
                # otherwise store x[i] as value of m[i] in PVARS
                add_var(mi, xi)
        elif type(mi) == "Group":
            # a group has to be matched with another group
            if type(xi) != "Group":
                return False
            
            # two groups must be matched as if they were top-level words
            # the variables grabbed previously will be checked as PVARS is global
            # same for the variables grabbed from now on
            if not match(xi, mi):
                return False
    return True


tests = [
    [['test', 'a'], ['test', 'A'], True]
]

def pretty(x):
    if len(x) > 2:
        return "(" + " ".join(map(pretty, x)) + ")"
    return x

for test in tests:
    x, m, r = test
    print(pretty(x),"~",pretty(m), r, match(x, m))
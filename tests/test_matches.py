def typeof(x):
    if type(x) == list: return "Group"
    elif type(x) == str:
        if x.islower(): return "Keyword"
        else: return "Variable"
    raise TypeError

PVARS = {}

def add_var(k, v):
    if type(k) == list:
        k = tuple(k)
    PVARS[k] = v
    
def get_var(k):
    if type(k) == list:
        return PVARS[tuple(k)]
    return PVARS[k]

def del_var():
    global PVARS
    PVARS = {}

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
        if typeof(mi) == "Keyword":
            # a keyword can only match another, identical, keyword
            if mi != xi:
                return False
        elif typeof(mi) == "Variable":
            # a variable can match either a keyword or another variable
            # x[i] now is trying to give an actual value to m[i]
            
            if mi in PVARS or tuple(mi) in PVARS:
                # if any value has already been given to m[i], x[i] should match it 
                if xi != get_var(mi):
                    return False
            else:
                # otherwise store x[i] as value of m[i] in PVARS
                add_var(mi, xi)
        elif typeof(mi) == "Group":
            # a group has to be matched with another group
            if typeof(xi) != "Group":
                return False
            # two groups must be matched as if they were top-level words
            # the variables grabbed previously will be checked as PVARS is global
            # same for the variables grabbed from now on
            if not match(xi, mi):
                return False
    return True


def pretty(x):
    if len(x) > 1 and type(x) == list:
        return "(" + " ".join(map(pretty, x)) + ")"
    return x

def test_set_1():
    to_match = [
    ['test', 'A'],
    ['test', 'A', 'B'],
    ['test', 'A', 'B', 'C'],
    ['test', 'A', 'a'],
    ['test', ['A', 'B'], 'A'],
    ['test', 'A', ['A', 'B']],
    ['test', 'A', ['B', 'A', 'B'], 'A'],
    ['test', ['A', 'B']]
    ]

    to_test = [
    ['test', 'a'], ['test', 'A'], ['test', 'A', 'B'],
    ['test', 'T', 'a'], ['test', 'a', 'b', 'c'], ['test', ['test', 'a'], ['test', ['A', 'B']], 'c'],
    ['test', 'a', ['a', 'b']], ['test', 'a', ['b', 'a']], ['test', 'a', ['t', 'a', 't'], 'a'], ['test', ['a', 'b'], 'a'],
    ['test', ['a', 'b'], 't'], ['test', 'a', ['a', 't', 'a'], 'a'], ['test', 'a', 'a'], ['test', ['a', 'b']]
    ]

    tests = [[a, b] for a in to_match for b in to_test]

    
    for test in tests:
        m, x = test
        print(pretty(m),"~",pretty(x), "\t", match(x, m))
        del_var()


def test_set_2():
    to_match = [
    [['test', 'A'], 'B'],
    [['test', 'A'], 'A'],
    ['A', 'test', 'B'],
    ['test', ['cube', 'A', 'B', 'C']]
    ]
    
    to_test = [
    [['test', 'a'], 'b'],
    [['test', 'a'], 'a'],
    ['test', 'a', 'A'],
    ['a', 'test', 'A'],
    ['test', ['cube', '1', '2', '3']]
    ]
    
    tests = [[a, b] for a in to_match for b in to_test]

    
    for test in tests:
        m, x = test
        print(pretty(m),"~",pretty(x), "\t", match(x, m))
        del_var()

test_set_2()
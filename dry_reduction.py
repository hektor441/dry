# --- Utility Functions ---

def typeof(x):
    if type(x) == list: return "Group"
    elif type(x) == str:
        if x[0].isupper() or x[0] in ["?", "!", "*"]: return "Variable"
        else: return "Keyword"
    raise TypeError

def flatten(x):
    while len(x) == 1 and type(x) == list:
        x = x[0]
    return x
    
# --- Variable Grabbing ---
# all the necessary precautions when dealing with a dictionary and lists as keys

PVARS = {}                               
def to_tuple(x):
    if type(x) == list:
        for i in range(0, len(x)):
            x[i] = to_tuple(x[i])
        return tuple(x)
    return x

def to_list(x):
    if type(x) == tuple:
        x = list(x)
        for i in range(0, len(x)):
            x[i] = to_list(x)
    return x

def add_var(k, v):
    if type(k) == list:
        k = to_tuple(k)
    PVARS[k] = v
    
def get_var(k):
    if type(k) == list:
        return PVARS[to_tuple(k)]
    return PVARS[k]

def in_var(k):
    if type(k) == list:
        return to_tuple(k) in PVARS
    return k in PVARS

def del_var():
    global PVARS
    PVARS = {}


# --- Matching ---

def match(x, m):
    # x -> input
    # m -> word to match x with
    # x and m are always lists [x0 x1 x.i] [m0 m1 m.k]
    # where each x.i and m.i can be either Keyword or Variable
    
    if type(x) == str:
        x = [x]
    
    lx = len(x)
    
    # when x is shorter than m they cannot match
    if lx < len(m):
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
            
            if in_var(mi[:]):
                # if any value has already been given to m[i], x[i] should match it 
                if xi != get_var(mi[:]):
                    return False
            elif mi[0] == "*":
                # *VAR as a final argument captures the rest of x and finish matching
                if i + 1 != len(m): return False
                add_var(mi[:], x[i:])
                return True
            else:
                # otherwise store x[i] as value of m[i] in PVARS
                if mi[0] == "?" and typeof(xi) != "Variable":
                    # ?VAR matches only with variables
                    return False
                elif mi[0] == "!" and typeof(xi) != "Keyword":
                    # !VAR matches only with keywords
                    return False
                add_var(mi[:], xi)
        elif typeof(mi) == "Group":
            # a group has to be matched with another group
            if typeof(xi) != "Group":
                return False
            # two groups must be matched as if they were top-level words
            # the variables grabbed previously will be checked as PVARS is global
            # same for the variables grabbed from now on
            if not match(xi, mi):
                return False
        elif mi == "*":
            # capture group
            # prefix * ~ prefix A B C ... N
            if len(x[i:]) == 0:
                return False
            
    return True


# --- Reduction ---

matches    = []
reductions = []

def add_reduction(m, r):
    matches.append(m)
    reductions.append(r)

def place_vars(x):
    for i in range(0, len(x)):
        if in_var(x[i][:]):
            if x[i][0] == "*":
                group = get_var(x[i][:])
                x.pop(i)
                x = x[:i] + group + x[i+1:]
            else:
                x[i] = get_var(x[i][:])
        elif type(x[i]) in [list, tuple]:
            x[i] = place_vars(x[i][:])
    return x

def reduce(x):
    # x -> input to reduce
    # x is always a list
    
    red = None
    if type(x) == list:
        if len(x) == 1:
            # perform the trivial reduction [word] -> word
            x = flatten(x)
        else:
            # reduce each word in the phrase
            for i in range(0, len(x)):
                if type(x[i]) == list:
                    x[i] = continuously_reduce(x[i])
                else:
                    rx = (reduce([x[i]]))
                    if type(rx) == list:
                        rx = flatten(rx)
                    x[i] = rx
                    
                # perform the trivial reduction on the reduced word
                if type(x[i]) == list:
                    if len(x[i]) == 1:
                        x[i] = flatten(x[i])

    # search for a match in the dictionary
    for i in range(0, len(matches)):
        del_var() # reset dictionary
        if match(x, matches[i]):
            # important, _COPY_ the reduction from the dictionary!
            
            red = flatten(reductions[i][:])

            if x[0] in special or x in special:
                # special reduction identified
                # special reductions are always of the form <<prefix arguments>>
                if x[0] in special:
                    red = reduce_special(x[0], x[1:])
                else:
                    red = reduce_special(x, x)
                    
            elif type(red) != list:
                red = place_vars([red])
            else:
                red = place_vars(red)
            
            del_var()
            return red
    return x

def continuously_reduce(x):
    # reduce x until a stable form is reached
    y = reduce(x[:])
    while x != y:
        x = y[:]
        y = reduce(x[:])
    return y

# --- Special Reductions ---
special = ["out", "str", "strs", "error", "beep", "import"]

for pfx in ["beep", "dot"]:
    # nullary special prefixes
    add_reduction([pfx], [pfx])

for pfx in ["out", "str", "strs", "error"]:
    # unary special prefixes
    add_reduction([pfx, "X"], ["X"])

for pfx in ["str", "strs"]:
    # binary special prefixes
    add_reduction([pfx, "X", "Y"], ["Y"])

def pretty(x):
    if type(x) == list:
        return "(" + " ".join(pretty(i) for i in x) + ")"
    return x

OUT_STREAM = []
ERR_STREAM = []

def reduce_special(pfx, args):
    ret = ""
    if pfx == "out":
        # output the arguments
        OUT_STREAM.append(pretty(flatten(args)))
        ret = args[0]        
    elif pfx == "error":

        ERR_STREAM.append("Error ({0}): " + pretty(flatten(args)))
    elif pfx == "str":
        # joins two arguments 
        ret = pretty(args[0]) + pretty(args[1])
    elif pfx == "strs":
        # joins two arguments 
        ret = pretty(args[0]) + " " + pretty(args[1])
    elif pfx == "beep":
        OUT_STREAM.append("\a")
    else:
        print(pfx, "not yet implemented!")
    return ret
    
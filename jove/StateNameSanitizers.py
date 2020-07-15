
# coding: utf-8

# In[5]:

from jove.SysConsts import STATENAME_NFAMAX
from jove.SysConsts import NXTSTATENUM

def ResetStNum(N=0):
    """Reset the state numbering counter.
    """
    global NXTSTATENUM
    NXTSTATENUM = N
    return NXTSTATENUM
    
def NxtStateStr(prefix="St"):
    global NXTSTATENUM
    NXTSTATENUM += 1
    return prefix + str(NXTSTATENUM)

def shomo(S,f):
    """In : S (string)
            f (function from char to char)
       Out: String homomorphism of S wrt f.
       Example: 
       S = "abcd"
       f = lambda x: chr( (ord(x)+1) % 256 )
       shomo("abcd",f) -> 'bcde'  
    """
    return "".join(map(f,S))

def dotsan_map(ch):
    """In : ch (char)
       Out: ch (char)
       A homomorphism to sanitize the characters
       contained in (state) names, for dot printing.
    """
    if ch in {  "{",   " ",   "'",   "}" }: 
            return ""
    elif ch == ",":
            return "_"
    elif ch == "(":
            return "\("
    elif ch == ")":
            return "\)"
    else:
            return ch

def dot_san_str(st):
    """In : st (string) usually
       Out: sanitized string
       If input not a string, make it a string
       Then apply dotsan_map to all chars in the string
       Sanitize for dot printing
    """
    if not(type(st) == str):
        st = str(st) # Coerce into string type first
    if st=="set()":
        return "EMPTY_SET"
    else:
        return shomo(st, dotsan_map)

def isNotBH(q):
    """In : q (state : string)
       Out: Boolean
       Given a state q, check if non-black-hole, 
       i.e. not 'BH'.
    """
    return (q != 'BH')


# In[ ]:

print('''You may use any of these help commands:
help(ResetStNum)
help(NxtStateStr)
''')


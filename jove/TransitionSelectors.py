
# coding: utf-8

# In[1]:



def fst(pair):
    """ First of a pair."""
    return pair[0]

def snd(pair):
    """ Second of a pair."""
    return pair[1]

def fn_dom(fn):
    """In : fn (function : dict)
       Out: domain of function (list of keys of dict)
    """
    return [k for k in fn.keys()]

def fn_range(fn):
    """In : fn (function : dict)
       Out: range of function (list of values of dict)
    """    
    return [v for v in fn.values()]

def fn_trans(fn):
    """In : fn (function : dict)  
       Out: list of mppings (list of items in dict)
    """    
    return list(fn.items())

def trSrc(transition):
    """Given a transition represented as ((Q,symb),Q'), 
       return Q.
    """
    return transition[0][0]

def trSymb(transition):
    """Given a transition represented as ((Q,symb),Q'), 
       return symb.
    """
    return transition[0][1]

def trTrg(transition):
    """Given a transition represented as ((Q,symb),Q'), 
       return Q'.
    """
    return transition[1]

# -- for PDA, a transition looks like this
#   [ ('s1','(','z') , { ('s1','((') } 
# 
# trSrc returns 's1', the state name
# trSymb returns the input symbol '(' 
# trStkSymb (new) returns 'z'
# trTrg returns ('s1','((')

def trStkSymb(transition):
    """Given a transition ((Q,symb,stksymb), Q'),
       return stksymb.
    """
    return transition[0][2]

def pdaNstate(trTrg):
    """Given (newq, new_stk_str), 
       return newq.
    """
    return trTrg[0]

def pdaNstkStr(trTrg):
    """Given (newq, new_stk_str), 
       return new_stk_str.
    """
    return trTrg[1]

def tmNstate(trTrg):
    """Given (newq, new_tape_sym, dir), 
       return newq.
    """
    return trTrg[0]

def tmNtpSym(trTrg):
    """Given (newq, new_tape_sym, dir), 
       return new_tape_sym.
    """
    return trTrg[1]

def tmNdir(trTrg):
    """Given (newq, new_tape_sym, dir), 
       return dir.
    """
    return trTrg[2]


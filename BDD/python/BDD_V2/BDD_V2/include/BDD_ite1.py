#Tyler Sorensen
#University of Utah
#March 18, 2012
#BDD_ite.py

##############################################################################
#Implementation of the efficient 'ite' method of building a BDD discussed
#in Bryan et al's paper "Efficient Implementation of a BDD Package".
#
#I believe this approach deserves it's own module because it's slightly
#less straight forward than Anderson's algorithms, and should be studied
#after an understanding of the simpler algorithms
##############################################################################

import PyBool_builder          as pbb
import PyBool_public_interface as pb
import copy


#This one memoizes.
class MemoizeMutable:
    """
    Memoize(fn) - an instance which acts like fn but memoizes its arguments
    Will work on functions with mutable arguments (slower than Memoize)
    """
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        import cPickle
        str = cPickle.dumps(args)
        if not self.memo.has_key(str):
            self.memo[str] = self.fn(*args)
        return self.memo[str]


##############################################################################
#Public Method
##############################################################################

def ite_build(bdd):
    """
    Public Function that initializes the main expression for the 
    recursive ite function and takes care of the corner cases (all
    True and all False)
    """
    expr = copy.deepcopy(bdd["expr"])
    expr = pb.simplify(expr)
    F,G,H = _parse_ite(expr)

    ite = MemoizeMutable(_ite)
    x = ite(bdd, F, G, H)

    #Corner Case
    if bdd["u"] == 1:
        bdd["u"] = x

##############################################################################
#Private Methods
##############################################################################

def _ite(bdd,F,G,H):
    """
    Main recursive method. Follows Bryants paper with a few
    added heuristics which are noted.
    """
    ####################
    #Possible Base Cases
    ####################
    #If G and H and constants:
    #
    #Base case if F is a variable or constant
    #Else Parse F into FGH form.
    if _is_const(G,True) and _is_const(H,False):
        if F["type"] == "var":
            return _ite_mk(bdd, F["name"][0] ,1,0)
        elif F["type"] == "const":
            return 1 if F["value"] else 0
        else:
            F,G,H = _parse_ite(F)

    elif _is_const(H,True) and _is_const(G,False):
        if F["type"] == "var":
            return _ite_mk(bdd, F["name"][0] ,0,1)
        elif F["type"] == "const":
            return 0 if F["value"] else 1
        else:
            F,G,H = _parse_ite(F)
            
    ####################
    #if H and G are equal and constant
    #Just return what H and G are (my heuristic)
    elif _is_const(G, False) and _is_const(H, False):
        return 0

    elif _is_const(G,True) and _is_const(H,True):
        return 1

    ####################
    #If F is a const, then we only have to consider
    #Either G or H. Base case if they're variable otherwise
    #parse them into F, G, H
    elif _is_const(F,True):
        if G["type"] == "var":
            return _ite_mk(bdd,G["name"][0],1,0)
        else:
            F,G,H = _parse_ite(G)

    elif _is_const(F,False):
        if H["type"] == "var":
            return _ite_mk(bdd, H["name"][0],1,0)
        else:
            F,G,H = _parse_ite(H)
    ####################

    #Find the top variable.
    v = top_variable(bdd, F,G,H)

    #create new expressions with variable propagated
    Fv, Gv, Hv = copy.deepcopy(F), copy.deepcopy(G), copy.deepcopy(H)
    Fv = pb.propagate(Fv, (v, True))
    Gv = pb.propagate(Gv, (v, True))
    Hv = pb.propagate(Hv, (v, True))

    Fnv = pb.propagate(F, (v, False))
    Gnv = pb.propagate(G, (v, False))
    Hnv = pb.propagate(H, (v, False))

    #Recursively find T (then) and E (else) nodes
    T = _ite(bdd, Fv, Gv, Hv)
    E = _ite(bdd, Fnv, Gnv, Hnv)

    #If they're the same, then we don't need to make a new
    #node
    if T == E:
        return T
    
    #make a new node and return it
    R = _ite_mk(bdd,v,T,E)
    return R

def _parse_ite(expr):
    """
    This method takes in any expression EXPR and parses it into
    a F, G, H expressions such that expr is the same as ite(F,G,H).
    This is possible because every boolean function can be represented
    in ite form. See Bryant's paper for formulas.
    """
    if expr["type"] == "const":
        v = expr["value"]
        return pbb.mk_const_expr(v),pbb.mk_const_expr(v),pbb.mk_const_expr(v)

    if expr["type"] == "var":
        return expr, pbb.mk_const_expr(True), pbb.mk_const_expr(False)

    if expr["type"] == "neg":
        return expr["expr"], pbb.mk_const_expr(False), pbb.mk_const_expr(True)

    if expr["type"] == "and":
        return expr["expr1"], expr["expr2"], pbb.mk_const_expr(False)

    if expr["type"] == "or":
        return expr["expr1"], pbb.mk_const_expr(True), expr["expr2"]

    if expr["type"] == "impl":
        return expr["expr1"], expr["expr2"], pbb.mk_const_expr(True)

    if expr["type"] == "xor":
        return expr["expr1"], pbb.mk_neg_expr(expr["expr2"]), expr["expr2"]

    if expr["type"] == "eqv":
        return expr["expr1"], expr["expr2"], pbb.mk_neg_expr(expr["expr2"])

def _ite_mk(bdd, v, t, e):
    """
    Special mk method for the ite operator.
    (Could possibly be improved by passing in a minimum
    variable index so the entire var_order list doesn't have to be
    traversed each time.
    """
    #Get the index
    i = bdd["var_order"].index(v) + 1

    #Have we seen it before?
    if (i,t,e) in bdd["h_table"]:
        return bdd["h_table"][(i,t,e)]

    #Make new Node
    u = bdd["u"] + 1

    bdd["h_table"][(i,t,e)] = u
    bdd["t_table"][u]       = (i,t,e)
    bdd["u"]                = u
    
    return u


def top_variable(bdd, F,G,H):
    """
    Given 3 expressions (F, G, H) and a bdd dictionary, returns the top
    variable in the three expressions.
    (Could possibly be faster by passing a minimum argument so that
    the whole var_order list doesn't have to be traversed)
    """
    #Make a big list with all the variables in it.
    exp_vars = pb.get_vars(F)
    exp_vars.extend(pb.get_vars(G))
    exp_vars.extend(pb.get_vars(H))

    #Turn it into a set.
    exp_vars = set(exp_vars)
    
    #Traverse through all the variables in 
    #var_order and return the one that appears
    #first.
    for x in bdd["var_order"]:
        if x in exp_vars:
            return x
        
    #else return None.
    return None


def _is_const(expr, value):
    """
    Helper Method, given an expression, returns True
    if the expression is a constant and is equal to
    the value passed in with VALUE
    """
    if expr["type"] == "const":
        return value == expr["value"]
    return False

#Tyler Sorensen
#February 17, 2011
#University of Utah

#PyBool_algorithms.py

#This is where all the actual algorithms are

from   peak.rules          import abstract, when
from   prioritized_methods import prioritized_when
from   types               import *
from   PyBool_builder      import *
import copy
import pdb


#According to several websites I read, using the
#peak.rules and prioritized_methods was the correct
#way to do functional style patern matching in python.
#A lot of these methods use it.


############################################################
#print_expr
############################################################

#Prints a human readable string representing the formula

#() are added for precendence. The following precedence rules
#are from Calculus of Computation:

#The precedence of the logical connectives are (from highest
#to lowest:
# ~, &, |, XOR, ->, <-> 
#where -> and <-> associate
#from to the right so
#P -> Q -> R
#is the same as:
#P -> (Q -> R)

#The main abstract function
@abstract()
def print_expr(expr):
    pass

#Rules for printing depending on type of expression
@prioritized_when(print_expr, "expr[\"type\"] == \"const\"")
def print_const_expr(expr):
    return str(expr["value"])

@prioritized_when(print_expr, "expr[\"type\"] == \"var\"")
def print_var_expr(expr):
    return expr["name"][0]

@prioritized_when(print_expr, "expr[\"type\"] == \"neg\"")
def print_neg_expr(expr):
    if expr["expr"]["type"] in ["var", "const"]:
        return "~%s" % print_expr(expr["expr"])
    else:
        return "~(%s)" % print_expr(expr["expr"])

@prioritized_when(print_expr, "expr[\"type\"] == \"and\"")
def print_and_expr(expr):
    
    if expr["expr1"]["type"] in ["const", "neg", "and", "var","XOR"] \
            and \
            expr["expr2"]["type"] in ["const", "neg", "and", "var", "XOR"]:
        return "%s & %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr1"]["type"] in ["const", "neg", "and", "var", "XOR"]:
        return "%s & (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr2"]["type"] in ["const", "neg", "and", "var", "XOR"]:
        return "(%s) & %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
    else:
        return "(%s) & (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
    
@prioritized_when(print_expr, "expr[\"type\"] == \"or\"")
def print_or_expr(expr):
    if expr["expr1"]["type"] in ["or", "const", "neg", "and", "var","XOR"] \
            and \
            expr["expr2"]["type"] in ["or", "const", "neg", "and", "var", "XOR"]:
        return "%s | %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
    elif expr["expr1"]["type"] in ["or", "const", "neg", "and", "var", "XOR"]:
        return "%s | (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr2"]["type"] in ["or", "const", "neg", "and", "var", "XOR"]:
        return "(%s) | %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
    else:
        return "(%s) | (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    
#NOT NEEDED precendence is built into the structure
#@prioritized_when(print_expr, "expr[\"type\"] == \"paren\"")
#def print_paren_expr(expr):
#    return "(%s)" % print_expr(expr["expr"])

@prioritized_when(print_expr, "expr[\"type\"] == \"impl\"")
def print_or_expr(expr):
    if expr["expr1"]["type"] in ["eqv"] \
            and \
            expr["expr2"]["type"] in ["eqv"]:
        return "(%s) -> (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr2"]["type"] in ["eqv"]:
        return "%s -> (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr1"]["type"] in ["eqv"]:
        return "(%s) -> %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
    else:
        return "%s -> %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
@prioritized_when(print_expr, "expr[\"type\"] == \"xor\"")
def print_or_expr(expr):
    if expr["expr1"]["type"] in ["eqv", "impl"] \
            and \
            expr["expr2"]["type"] in ["eqv", "impl"]:
        return "(%s) XOR (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr2"]["type"] in ["eqv", "impl"]:
        return "%s XOR (%s)" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))

    elif expr["expr1"]["type"] in ["eqv", "impl"]:
        return "(%s) XOR %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))
    
    else:
        return "%s XOR %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))


@prioritized_when(print_expr, "expr[\"type\"] == \"eqv\"")
def print_or_expr(expr):
    return "%s <=> %s" % (print_expr(expr["expr1"]), print_expr(expr["expr2"]))


############################################################
#apply_sol
############################################################

#This method applies a supplied solution to the expression.
#simply does a recursive solve. Returns true for a valid solution
#false otherwise.

#Abstract method
@abstract()
def apply_sol_expr(expr, sol):
    pass

#Different methods called depending on the type of expression.
@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"const\"")
def apply_sol_expr_const(expr,sol):
    return expr["value"]

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"var\"") #and type(sol) is DictType")
def apply_sol_expr_var0(expr,sol):
    return sol[expr["name"][0]]

#NOT NEEDED (supports a solution in the form of a list)
#@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"var\" and type(sol) is ListType")
#def apply_sol_expr_var1(expr,sol):
#    return sol[expr["name"][1]]

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"neg\"")
def apply_sol_expr_neg(expr,sol):
    return not apply_sol_expr(expr["expr"],sol)

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"and\"")
def apply_sol_expr_and(expr,sol):
    return apply_sol_expr(expr["expr1"],sol) and apply_sol_expr(expr["expr2"],sol)

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"or\"")
def apply_sol_expr_or(expr,sol):
    return apply_sol_expr(expr["expr1"],sol) or apply_sol_expr(expr["expr2"],sol)

#NOT NEEDED precedence is built into the structure
#@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"paren\"")
#def apply_sol_expr_paren(expr,sol):
#    return apply_sol_expr(["expr"],sol)

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"impl\"")
def apply_sol_expr_impl(expr,sol):
    if apply_sol_expr(expr["expr1"],sol):
        return apply_sol_expr(expr["expr2"],sol)
    else:
        return True

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"eqv\"")
def apply_sol_expr_eqv(expr,sol):
    return apply_sol_expr(expr["expr1"],sol) == apply_sol_expr(expr["expr2"],sol)

@prioritized_when(apply_sol_expr, "expr[\"type\"] == \"xor\"")
def apply_sol_expr_xor(expr,sol):
    return apply_sol_expr(expr["expr1"],sol) != apply_sol_expr(expr["expr2"],sol)


############################################################
#propagate
############################################################

#propagates a variable assignment through the solution and reduces
#the formula along the way (good for early detection of SAT and keeping
#the size of the expression down)

@abstract()
def propagate(expr, tup):
    pass

@prioritized_when(propagate, "expr[\"type\"] == \"const\"")
def propagate_const(expr,tup):
    return expr

@prioritized_when(propagate, "expr[\"type\"] == \"var\"")# and type(tup[0]) is StringType")
def propagate_var1(expr,tup):
    if tup[0] == expr["name"][0]:
        return mk_const_expr(tup[1])
    return expr

#NOT NEEDED (used to support variable look-up by integer, didn't work out.
#@prioritized_when(propagate, "expr[\"type\"] == \"var\" and type(tup[0]) is IntType")
#def propagate_var2(expr,tup):
#    if tup[0] == expr["name"][1]:
#        return mk_const_expr(tup[1])
#    return expr

@prioritized_when(propagate, "expr[\"type\"] == \"neg\"")
def propagate_neg(expr,tup):
    x = propagate(expr["expr"], tup)
    if x["type"] != "const":
        expr["expr"] = x
        return expr
    else:
        return mk_const_expr(not x["value"])

@prioritized_when(propagate, "expr[\"type\"] == \"and\"")
def propagate_and(expr,tup):
    x = propagate(expr["expr1"],tup) 
    y = propagate(expr["expr2"],tup)
    if x["type"] != "const" and y["type"] != "const":
        expr["expr1"] = x
        expr["expr2"] = y
        return expr
    
    elif y["type"] == "const":
        return mk_const_expr(False) if not y["value"] else x

    elif x["type"] == "const":
        return mk_const_expr(False) if not x["value"] else y

    else:
        return mk_const_expr(x["value"] and y["value"])
    
@prioritized_when(propagate, "expr[\"type\"] == \"or\"")
def propagate_or(expr,tup):
    x = propagate(expr["expr1"],tup) 
    y = propagate(expr["expr2"],tup)
    if x["type"] != "const" and y["type"] != "const":
        expr["expr1"] = x
        expr["expr2"] = y
        return expr
    
    elif x["type"] == "const":
        return mk_const_expr(True) if x["value"] else y

    elif y["type"] == "const":
        return mk_const_expr(True) if y["value"] else x

    else:
        return mk_const_expr(x["value"] or y["value"])


@prioritized_when(propagate, "expr[\"type\"] == \"paren\"")
def propagate_paren(expr,tup):
    x = propagate(expr["expr"],tup)
    if x["type"] != "const":
        expr["expr"] = x
        return expr
    else:
        return x

@prioritized_when(propagate, "expr[\"type\"] == \"impl\"")
def propagate_impl(expr,tup):
    x = propagate(expr["expr1"],tup) 
    y = propagate(expr["expr2"],tup)
    if x["type"] != "const" and y["type"] != "const":
        expr["expr1"] = x
        expr["expr2"] = y
        return expr
    
    elif x["type"] == "const":
        return mk_const_expr(True) if not x["value"] else y

    elif y["type"] == "const":
        return mk_const_expr(True) if y["value"] else mk_neg_expr(x)

    else:
        return mk_const_expr(True if not x["value"] else y["value"])


@prioritized_when(propagate, "expr[\"type\"] == \"eqv\"")
def propagate_eqv(expr,tup):
    x = propagate(expr["expr1"],tup) 
    y = propagate(expr["expr2"],tup)
    if x["type"] != "const" and y["type"] != "const":
        expr["expr1"] = x
        expr["expr2"] = y
        return expr
    
    elif x["type"] == "const" and y["type"] != "const":
        return mk_neg_expr(y) if not x["value"] else y
    
    elif y["type"] == "const" and x["type"] != "const":
        return mk_neg_expr(x) if not y["value"] else x
    
    else:
        return mk_const_expr(x["value"] == y["value"])


@prioritized_when(propagate, "expr[\"type\"] == \"xor\"")
def propagate_xor(expr,tup):
    x = propagate(expr["expr1"],tup) 
    y = propagate(expr["expr2"],tup)
    if x["type"] != "const" and y["type"] != "const":
        expr["expr1"] = x
        expr["expr2"] = y
        return expr
    
    elif x["type"] == "const":
        return mk_neg_expr(y) if x["value"] else y
    
    elif y["type"] == "const":
        return mk_neg_expr(x) if y["value"] else x
    
    else:
        return mk_const_expr(x["value"] != y["value"])

############################################################
#std_expr 
############################################################

#This function replaces all non-standard operators from the expression
#With standard operators
#Non standard operators are : ->, XOR, <->
#standard operators are : ~, | &

@abstract()
def std_expr(expr):
    pass

@prioritized_when(std_expr, "expr[\"type\"] == \"const\" or expr[\"type\"] == \"var\"")
def std_expr_atomic(expr):
    return expr

@prioritized_when(std_expr, "expr[\"type\"] == \"neg\"")
def std_expr_neg(expr):
    return mk_neg_expr(std_expr(expr["expr"]))

@prioritized_when(std_expr, "expr[\"type\"] == \"and\"")
def std_expr_and(expr):
    return mk_and_expr(std_expr(expr["expr1"]), std_expr(expr["expr2"]))

@prioritized_when(std_expr, "expr[\"type\"] == \"or\"")
def std_expr_or(expr):
    return mk_or_expr(std_expr(expr["expr1"]), std_expr(expr["expr2"]))

@prioritized_when(std_expr, "expr[\"type\"] == \"impl\"")
def std_expr_impl(expr):
    return mk_or_expr(mk_neg_expr(std_expr(expr["expr1"])), std_expr(expr["expr2"]))

@prioritized_when(std_expr, "expr[\"type\"] == \"eqv\"")
def std_expr_eqv(expr):
    x = mk_impl_expr(expr["expr1"], expr["expr2"])
    y = mk_impl_expr(expr["expr2"], expr["expr1"])
    return std_expr(mk_and_expr(x,y))
    
@prioritized_when(std_expr, "expr[\"type\"] == \"xor\"")
def std_expr_xor(expr):
    x = mk_and_expr(expr["expr1"], mk_neg_expr(expr["expr2"]))
    y = mk_and_expr(expr["expr2"], mk_neg_expr(expr["expr1"]))
    return std_expr(mk_or_expr(x,y))

############################################################
#nne
############################################################

#returns expr converted into negation normal form (negation sign
#only appears in front of variables

@abstract()
def nne(expr):
    pass

@prioritized_when(nne, "expr[\"type\"] == \"const\"")
def nne_const(expr):
    return expr["value"]

@prioritized_when(nne, "expr[\"type\"] == \"var\"")
def nne_var(expr):
    return expr

@prioritized_when(nne, "expr[\"type\"] == \"neg\"")
def nne_neg(expr):
    
    if expr["expr"]["type"] == "const":
        return mk_const_expr(not expr["expr"]["value"])
    
    if expr["expr"]["type"] == "var":
        return expr

    if expr["expr"]["type"] == "neg":
        return nne(expr["expr"]["expr"])
    
    if expr["expr"]["type"] == "and":
        return mk_or_expr(nne(mk_neg_expr(expr["expr"]["expr1"])), nne(mk_neg_expr(expr["expr"]["expr2"])))

    if expr["expr"]["type"] == "or":
        return mk_and_expr(nne(mk_neg_expr(expr["expr"]["expr1"])), nne(mk_neg_expr(expr["expr"]["expr2"])))

    if expr["expr"]["type"] == "paren":
        return mk_paren_expr(nne(mk_neg_expr(expr["expr"]["expr"])))

                             
@prioritized_when(nne, "expr[\"type\"] == \"and\"")
def nne_and(expr):
    return mk_and_expr(nne(expr["expr1"]), nne(expr["expr2"]))

@prioritized_when(nne, "expr[\"type\"] == \"or\"")
def nne_or(expr):
    return mk_or_expr(nne(expr["expr1"]), nne(expr["expr2"]))

############################################################
#exp_cnf
############################################################

#This alogrithm converts expr into an expodentially sized cnf
#formula (requires formula be in negation normal form)

@abstract()
def exp_cnf(expr):
    pass

@prioritized_when(exp_cnf, "expr[\"type\"] in [\"const\", \"var\", \"neg\"]")
def exp_cnf_same(expr):
    return expr

@prioritized_when(exp_cnf, "expr[\"type\"] == \"and\"")
def exp_cnf_and(expr):
    return mk_and_expr(exp_cnf(expr["expr1"]), exp_cnf(expr["expr2"]))

@prioritized_when(exp_cnf, "expr[\"type\"] == \"or\"")
def exp_cnf_or(expr):

#    while expr["expr1"]["type"] == "paren":
#        expr["expr1"] = expr["expr1"]["expr"]
        
#    while expr["expr2"]["type"] == "paren":
#        expr["expr2"] = expr["expr2"]["expr"]


    if expr["expr1"]["type"] == "and":
        F1 = exp_cnf(expr["expr1"]["expr1"])
        F2 = exp_cnf(expr["expr1"]["expr2"])
        F3 = exp_cnf(expr["expr2"])
        
        F4 = exp_cnf(mk_or_expr(F1,F3))
        F5 = exp_cnf(mk_or_expr(F2,F3))
        
        return mk_and_expr(F4, F5)
    
    if expr["expr2"]["type"] == "and":
        F1 = exp_cnf(expr["expr1"])
        F2 = exp_cnf(expr["expr2"]["expr1"])
        F3 = exp_cnf(expr["expr2"]["expr2"])
        
        F4 = exp_cnf(mk_or_expr(F1,F2))
        F5 = exp_cnf(mk_or_expr(F1,F3))
        
        return mk_and_expr(F4, F5)
    
    else:
        return mk_or_expr(exp_cnf(expr["expr1"]), exp_cnf(expr["expr2"]))

############################################################
#en
############################################################

#The "en" algorithm from Calculus of Computation
#used in making poly-nomial sized cnf

@abstract()
def en(expr, repHash):
    pass

@prioritized_when(en, "expr[\"type\"] == \"const\" or expr[\"type\"] == \"var\"")
def en_atomic(expr, repHash):
    return True

@prioritized_when(en, "expr[\"type\"] == \"neg\"")
def en_neg(expr, repHash):
    P = rep(expr, repHash)
    Pn = rep(expr["expr"], repHash)
    return mk_and_expr(mk_or_expr(mk_neg_expr(P), mk_neg_expr(Pn)), mk_or_expr(P, Pn))

@prioritized_when(en, "expr[\"type\"] == \"and\"")
def en_and(expr, repHash):
    P   = rep(expr, repHash)
    Pn  = rep(expr["expr1"], repHash)
    Pn2 = rep(expr["expr2"], repHash)
    
    first  = mk_or_expr(mk_neg_expr(P), Pn)
    second = mk_or_expr(mk_neg_expr(P), Pn2)
    third  = mk_or_expr(P, mk_neg_expr(Pn))
    third  = mk_or_expr(third, mk_neg_expr(Pn2))
    
    fourth = mk_and_expr(first, second)
    return mk_and_expr(fourth, third)

    
@prioritized_when(en, "expr[\"type\"] == \"or\"")
def en_or(expr, repHash):
    P   = rep(expr, repHash)
    Pn  = rep(expr["expr1"], repHash)
    Pn2 = rep(expr["expr2"], repHash)
    
    first  = mk_or_expr(mk_neg_expr(Pn), P)
    second = mk_or_expr(mk_neg_expr(Pn2), P)
    third  = mk_or_expr(Pn, mk_neg_expr(P))
    third  = mk_or_expr(third, Pn2)
    
    fourth = mk_and_expr(first, second)
    return mk_and_expr(fourth, third)


@prioritized_when(en, "expr[\"type\"] == \"paren\"")
def en_paren(expr, repHash):
    return True

@prioritized_when(en, "expr[\"type\"] == \"impl\"")
def en_impl(expr, repHash):
    P   = rep(expr, repHash)
    Pn  = rep(expr["expr1"], repHash)
    Pn2 = rep(expr["expr2"], repHash)
    
    first = mk_or_expr(Pn, P)
    second = mk_or_expr(mk_neg_expr(Pn2), P)
    third = mk_or_expr(mk_neg_expr(Pn), mk_neg_expr(P))
    third = mk_or_expr(third, Pn2)
    
    fourth = mk_and_expr(first, second)
    return mk_and_expr(fourth, third)

@prioritized_when(en, "expr[\"type\"] == \"eqv\"")
def en_eqv(expr, repHash):
    P   = rep(expr, repHash)
    Pn  = rep(expr["expr1"], repHash)
    Pn2 = rep(expr["expr2"], repHash)
    
    first = mk_or_expr(Pn, P)
    first = mk_or_expr(first, Pn2)
    
    second = mk_or_expr(mk_neg_expr(Pn), mk_neg_expr(P))
    second = mk_or_expr(second, Pn2)

    third = mk_or_expr(mk_neg_expr(Pn2), mk_neg_expr(P))
    third = mk_or_expr(third, Pn)

    fourth = mk_or_expr(mk_neg_expr(Pn2), mk_neg_expr(Pn))
    fourth = mk_or_expr(fourth, P)
    
    fifth = mk_and_expr(first, second)
    fifth = mk_and_expr(fifth, third)

    return mk_and_expr(fifth, fourth)

############################################################
#polynomial cnf methods
############################################################

#The rep method from Calculus of Computation
#Takes in a rep hash table (dictionary) so that
#it can keep track of the reps it's already created
def rep(expr, repHash):

    if expr["type"] in ["const", "var"]:
        return expr
    hashN = make_hash(expr)

    if hashN in repHash:
        return repHash[hashN]

    var_name = mk_var_name(expr, repHash)
    newVar = mk_var_expr(var_name)
    repHash[hashN] = newVar
    return newVar

#Returns a list of sub formulas of expr, needed
#so that a rep can be created for each one.
def get_subForms(expr):

    if expr["type"] in ["var", "const"]:
        return [expr]

    if expr["type"] == "neg":
        L = get_subForms(expr["expr"])
        L.append(expr)
        return L
    
    else:
        L1 = get_subForms(expr["expr1"])
        L2 = get_subForms(expr["expr2"])
        L1.extend(L2)
        L1.append(expr)
        
        return L1

#Creates a unique variable name for the rep function
def mk_var_name(expr, repHash):
    m = get_var_map(expr)
    var_list = [x[0] for x in m]
    
    r_name, i = "Z1", 1
    taken_names = [x["name"][0] for x in repHash.values()]
    
    while r_name in var_list or r_name in taken_names:
        i = i + 1
        r_name = "Z%i" % i

    return r_name

#The polynomial cnf method from Calculus of Computation
#(uses rep and en methods)
def poly_cnf(expr, repHash):
    
    sub_forms = get_subForms(expr)

    P = rep(expr, repHash)
    
    for ex in sub_forms:
        Pn = en(ex, repHash)
        if not type(Pn) is BooleanType:
            P = mk_and_expr(P, Pn)

    return P

############################################################
#Recursive to List representation methods
############################################################

#Returns a list of tuples (variable_name, integer)
#where the variable is mapped to the integer in the expression
#(usually used to get a list of variables)
def get_var_map(expr):

    if expr["type"] == "var":
        return [expr["name"]]

    if expr["type"] == "const":
        return []
    
    if expr["type"] in ["neg", "paren"]:
        return get_var_map(expr["expr"])

    else:
        L1 = get_var_map(expr["expr1"])
        L2 = get_var_map(expr["expr2"])
        L1.extend(L2)
        return list(set(L1))

#Takes a variable map (can be optained from the above method)
#and creates a new one where variables are mapped to unique integers
def create_new_map(m):    
    r_list = []
    for i in range(len(m)):
        r_list.append((m[i][0],i+1))

    return r_list

#Applies a new (variable_name, integer) mapping to expression expr
def apply_map(expr, m):
    
    if expr["type"] == "var":
        for i in m:
            if i[0] == expr["name"][0]:
                expr["name"] = i
        return
    
    if expr["type"] in ["neg", "paren"]:
        apply_map(expr["expr"],m)

    else:
        apply_map(expr["expr1"],m)
        apply_map(expr["expr2"],m)

#Main function that turns recursive representation into
#list form (requires expr be in cnf and an updated mapping,
#which is provided in above methods)
def cnf_list(expr):
    
    if expr["type"] == "var":
        return [expr["name"][1]]

    if expr["type"] == "neg":
        return [-(expr["expr"]["name"][1])]

    if expr["type"] == "or":
        L = cnf_list(expr["expr1"])
        L1 = cnf_list(expr["expr2"])
        L1.extend(L)
        return L1

    if expr["type"] == "and":
        L = cnf_list(expr["expr1"])
        L1 = cnf_list(expr["expr2"])
        if type(L[0]) is ListType and type(L1[0]) is ListType:
            L.extend(L1)
            return L
        if type(L[0]) is ListType:
            L.append(L1)
            return L

        if type(L1[0]) is ListType:
            L1.append(L)
            return L1

        return [L,L1]

############################################################
#List representation CNF methods
############################################################

#Propagates the assignment of variable to truth_value through
#clauses
def cnf_propagate(clauses, variable, truth_value):
    i = 0
    while i < len(clauses):
        for y in clauses[i]:
            if cnf_get_var(y) == variable:
                if cnf_get_sign(y) == truth_value:
                    clauses.remove(clauses[i])
                    i = i-1
                    break
                else:
                    clauses[i].remove(y)
        i = i + 1

    return clauses

#Applies the solution sol to clauses
#returns True if sat, False otherwise
def cnf_apply_sol(clauses, sol):
    i = 0
    while i < len(clauses):
        for lit in clause:
            val = sol[cnf_get_var(lit)]
            if cnf_get_sign(y) == val:
                clauses.remove(clause)
                i = i -1
                break
            else:
                clauses[i].remove(y)
        i = i + 1

    if len(clauses) == 0:
        return True
    return False

#Returns a list of literals that appear in unit clauses
#in clauses
def cnf_get_unit_clauses(clauses):
    return [x[0] for x in clauses if len(x) == 1]

#Returns a list of literals that appear as pure variables
#in clauses
def cnf_get_pure_literals(clauses):
    returnList = []
    allVar = set([y for x in clauses for y in x])
    
    for v1 in allVar:
        count = 0
        for v2 in allVar:
            if cnf_get_var(v1) == cnf_get_var(v2):
                count = count+1
                
        if count == 1:
            returnList.append(v1)
        
    return returnList

#Returns a recursive form of clauses
def cnf_to_rec(clauses):
    clause_list       = []
    variable_hash     = {}
    neg_variable_hash = {}

    for clause in clauses:
        literal_list = []
        for literal in clause:

            if not str(cnf_get_var(literal)) in variable_hash:
                literal_expr = mk_var_expr(str(cnf_get_var(literal)))
                variable_hash[str(cnf_get_var(literal))] = literal_expr
            else:
                literal_expr = variable_hash[str(cnf_get_var(literal))]

            if not cnf_get_sign(literal):
                if not str(literal) in literal_hash:
                    var_expr = mk_neg_expr(str(literal))
                    literal_hash[str(literal)] = var_expr
                else:
                    var_expr = literal_hash[str(literal)]
            
            else:
                var_expr = literal_expr
            literal_list.append(var_expr)


        if len(literal_list) == 1:
            clause_list.append(literal_list[0])
            
        if len(literal_list) != 0:
            
            or_expr = mk_or_expr(literal_list[0], literal_list[1])
            for i in range(2,len(literal_list)):
                or_expr = mk_or_expr(or_expr, literal_list[i])
            
            clause_list.append(or_expr)

    if len(clause_list) == 1:
        return clause_list[0]
    
    if len(clause_list) == 0:
        return None

    main_expr = mk_and_expr(clause_list[0], clause_list[1])
    for i in range(2,len(clause_list)):
        main_expr = mk_and_expr(main_expr, clause_list[i])

    return main_expr

#cnf literal helper methods
def cnf_get_var(literal):
    return abs(literal)

def cnf_get_sign(literal):
    return literal > 0

#From http://stackoverflow.com/questions/5884066/hashing-a-python-dictionary
#For hashing dictionaries
def make_hash(o): 
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """
    if isinstance(o, set) or isinstance(o, tuple) or isinstance(o, list):
        
        return tuple([make_hash(e) for e in o])    
    
    elif not isinstance(o, dict):
        
        return hash(o)
    
    new_o = copy.deepcopy(o)
    for k, v in new_o.items():
        new_o[k] = make_hash(v)
        
    return hash(tuple(frozenset(new_o.items())))

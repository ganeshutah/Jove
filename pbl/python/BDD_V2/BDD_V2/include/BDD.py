#Tyler Sorensen
#University of Utah
#March 1, 2012
#BDD.py

##############################################################################
#An updated BDD package with the following improvements:
#
# -- A robust boolean formula library for file parsing and propagation (PyBool)
#
# -- A more pythonic implementation focusing less on objects and more on
#          simple, native data structures and algorithms.
#
# -- Cleaner, well defined public interface
#
# -- No more printing statistics, the user can do that themselves!
# 
# -- Written in Python2.x. Previous version in Python3.x caused some 
#          Headaches.
##############################################################################

import copy
import sys

import PyBool_public_interface as pb
import dot_bdd as dbdd
import BDD_ite as ite

###################################################################
#Public Interface
###################################################################

def bdd_init(example):
    """
    Initializes a BDD data structure (dictionary) with the 
    Boolean Formula stored in file name FNAME
    """
    #parse file using PyBool
    expr      = pb.parse_std(example)
    var_order = expr["var_order"]
    expr      = expr["main_expr"]

    #make sure all variables are accounted for
    assert(len(var_order) >= pb.number_vars(expr))

    #values are tuples in the form (i, low, high)
    t_table = {0 : ((len(var_order)+1), None, None),
               1 : ((len(var_order)+1), None, None)}

    return {"u"              : 1             ,
            "n"              : len(var_order),
            "h_table"        : {}            ,
            "t_table"        : t_table       ,

            #boolean formula info
            "var_order"      : var_order     ,
            "expr"           : expr          }

def build(bdd):
    """
    Public function to build. Starts off the recursive function and
    deals with a simple corner case
    """
    #Copy the main expression and build
    expr = copy.deepcopy(bdd["expr"])
    x = _build(bdd, expr, 1)

    #Corner Case
    if bdd["u"] == 1:
        bdd["u"] = x

def any_sat(bdd):
    """
    Public function to any_sat. Simply returns an arbitrary satisfying assignement
    returns [] if none.
    """
    #Corner case where all SAT
    if bdd["u"] == 1:
        return ["%s" % var for var in bdd["var_order"]]
    
    l =  _any_sat(bdd, bdd["u"],[])

    if len(l) == 0:
        return l
    
    #Arbitrarily assigning true to "don't care" variables
    vars_in_l = [_get_var(x) for x in l]
    i = 0
    while i < len(bdd["var_order"]):
        if bdd["var_order"][i] not in vars_in_l:
            new_l = copy.deepcopy(l)
            l.insert(i, "%s" %  bdd["var_order"][i])
        i += 1

    return l

def sat_count(bdd):
    """
    Public function sat_count, returns the number of satisfying assignments
    """
    u = bdd["u"]
    return int(_count(bdd, u) * (2**(bdd["t_table"][u][0]-1)))

def all_sat(bdd):
    """
    Public function all_sat. Returns all satisfiying assignments
    in a list of lists form
    """
    #find all satisfying assignments from the BDD
    assig =  _all_sat(bdd, bdd["u"])

    #Fill in "don't care" variables. Kind of sloppy, but
    #it's kind of a pain.
    for l in assig:
        vars_in_l = [_get_var(x) for x in l]
        i = 0
        while i < len(bdd["var_order"]):
            if bdd["var_order"][i] not in vars_in_l:
                new_l = copy.deepcopy(l)
                l.insert(i, "%s" %  bdd["var_order"][i])
                new_l.insert(i, "~%s" %  bdd["var_order"][i])
                assig.append(new_l)
            i += 1
    
    return assig

def dot_bdd(bdd, fname):
    """
    prints a dot file FNAME representing the binary decision
    diagram BDD
    """
    dbdd.print_bdd(bdd, fname)
    
def stat_string(bdd):
    """
    Return a string with some stats about the BDD
    """
#    pdb.set_trace()
    return "Number of Variables : %i\n" % len(bdd["var_order"]) +\
           "Number of Nodes     : %i\n" % (bdd["u"]+1)          +\
           "Variable Ordering\n"                                +\
           "------------------------------------\n"             +\
           str(bdd["var_order"])

def ite_build(bdd):
    ite.ite_build(bdd)

###################################################################
#Main recursive private functions
###################################################################

def _mk(bdd, i, l, h):
    """
    mk function, will check to see if a node is already created for
    a variable, high, low triple. If not, makes one.
    """
    #if high and low are the same
    if l == h:
        return l

    #if a node already exists
    if (i,l,h) in bdd["h_table"]:
        return bdd["h_table"][(i,l,h)]

    #else make a new node
    u = bdd["u"] + 1

    #update BDD
    bdd["h_table"][(i,l,h)] = u
    bdd["t_table"][u]       = (i,l,h)
    bdd["u"]                = u
    
    return u

def _build(bdd, expr, i):
    """
    Recursive build function. Exponential algorithm.
    Easy to implement. Terrible performance
    """
    #Base Case
    if i > bdd["n"]:
        pb.simplify(expr)
        return 1 if expr["value"] else 0

    #The variable to consider
    var = bdd["var_order"][i-1]

    #propagate false
    expr1 = copy.deepcopy(expr)
    expr1 = pb.propagate(expr1, (var, False))

    #propagate true
    expr  = pb.propagate(expr, (var, True))

    #get high and low edges
    low   = _build(bdd, expr1, i+1)
    high  = _build(bdd, expr,  i+1)

    return _mk(bdd, i, low, high)

def _any_sat(bdd, u, l):
    """
    Recursive part of any_sat
    """
    #Base Cases
    if u in [0,1]:
        return l
    
    var = _get_var_name(bdd, u)

    #Arbitrarily consider lower branch
    if bdd["t_table"][u][1] == 0:
        l.append("%s" % var)
        new_u = bdd["t_table"][u][2]

    else:
        l.append("~%s" % var)
        new_u = bdd["t_table"][u][1]

    return _any_sat(bdd, new_u, l)

def _count(bdd, u):
    """
    Recursive count function for sat_count
    """
    #base cases
    if u in [1,0]:
        return u

    #Some intermediate variables to make computation a little
    #cleaner
    t_table  = bdd["t_table"]
    t_low, t_high = t_table[u][1], t_table[u][2]

    pow_f = lambda x , y: 2**(x - y - 1)

    return (pow_f(t_table[t_low][0], t_table[u][0])   * _count(bdd, t_low))  +\
           (pow_f(t_table[t_high][0], t_table[u][0])  * _count(bdd, t_high))

def _all_sat(bdd, u):
    """
    The recursive part of all_sat
    """
    #Base Cases
    if u == 0:
        return []

    if u == 1:
        return [[]]

    var = _get_var_name(bdd, u)

    low_list  = _all_sat(bdd, bdd["t_table"][u][1])
    high_list = _all_sat(bdd, bdd["t_table"][u][2])

    #Append appropriate assignments to lists
    [x.insert(0,"~%s" % var) for x in low_list]
    [x.insert(0,"%s" % var) for x in high_list]

    #return the combination of both lists.
    low_list.extend(high_list)
    return low_list

def _reset_bdd(bdd):
    t_table = {0 : ((len(bdd["var_order"])+1), None, None),
               1 : ((len(bdd["var_order"])+1), None, None)}

    bdd["u"] = 1
    bdd["n"] = len(bdd["var_order"])
    bdd["h_table"] = {}
    bdd["t_table"] = t_table

def _walk_variable_up(num_nodes, current_position, bdd, out, verbose):
    best_order = bdd["var_order"]
    #walk var to top
    while(current_position > 0):
        _reset_bdd(bdd)
        tmp = bdd["var_order"][current_position-1]
        bdd["var_order"][current_position-1] = bdd["var_order"][current_position]
        bdd["var_order"][current_position] = tmp
        current_position -= 1
        ite.ite_build(bdd)
        if num_nodes > bdd["u"]+1:
            num_nodes = bdd["u"]+1
            best_order = list(bdd["var_order"])
            if verbose:
                print( "Walk Up New Number of Nodes: %d" % num_nodes )
                print( "Walk Up New Var Order: %s" % str(bdd["var_order"]) )
    out["num_nodes"] = num_nodes
    out["best_order"] = best_order
    
import threading

def reorder_ite_build(bdd, vars_to_consider=[], verbose=False):
    """
    Parameters:
        bdd - the bdd to build and minimize
        vars_to_consider - the list of varibles to reorder
        verbose - whether info should be printed during build time
    """
    ite.ite_build(bdd)
    num_nodes = bdd["u"]+1
    num_vars = len(bdd["var_order"])
    if verbose:
        print( "Original Number of Nodes: %d" % num_nodes )
        print( "Number of Variables: %d" % num_vars )
    checked_vars = {}
    if not vars_to_consider:
        vars_to_consider = bdd["var_order"]
    for v in vars_to_consider:
        checked_vars[v] = False
    while False in checked_vars.values():
        var_to_be_checked = None
        for key in checked_vars:
            if not checked_vars[key]:
                var_to_be_checked = key
                break

        best_order = list(bdd["var_order"])
        original_order = best_order
        current_position = bdd["var_order"].index(var_to_be_checked)
        if verbose:
            print( "Current Variable: %s" % var_to_be_checked )
        original_position = current_position
        
        #start thread to walk to top
        walk_up_bdd = copy.deepcopy(bdd)
        walk_up_out = {"num_nodes":None, "best_order":None}
        walk_up_thread = threading.Thread(
            target=_walk_variable_up,
            args=(copy.copy(num_nodes),
                  copy.copy(current_position),
                  walk_up_bdd,
                  walk_up_out,
                  verbose)
        )
        walk_up_thread.start()
        
        #walk var to bottom
        for j in range(original_position,num_vars):
            _reset_bdd(bdd) #reset our bdd to try again
            tmp = bdd["var_order"][j]
            bdd["var_order"][j] = bdd["var_order"][current_position]
            bdd["var_order"][current_position] = tmp
            current_position = j
            ite.ite_build(bdd)
            if num_nodes > bdd["u"]+1:
                num_nodes = bdd["u"]+1
                best_order = list(bdd["var_order"])
                if verbose:
                    print( "Walk Down New Number of Nodes: %d" % num_nodes )
                    print( "Walk Down New Var Order: %s" % str(bdd["var_order"]) )
            
        walk_up_thread.join()
        
        if num_nodes > walk_up_out["num_nodes"]:
            num_nodes = walk_up_out["num_nodes"]
            best_order = walk_up_out["best_order"]
        
        #mark var as checked
        checked_vars[var_to_be_checked] = True
        bdd["var_order"] = best_order
        
    _reset_bdd(bdd)
    bdd["var_order"] = best_order
    ite.ite_build(bdd)
    if verbose:
        print( "Final Number of Nodes: %d" % num_nodes )
        print( "Final Var Order %s" % str(bdd["var_order"]) )


###################################################################
#Helper Functions
###################################################################

def _get_var(s):
    """
    Given a variable in a variable assigment, return the variable
    (sometimes they have the negation sign ~ in front of them
    """
    return s if s[0] != '~' else s[1:len(s)]

def _get_var_name(bdd, u):
    """
    Given a variable index u in the BDD, return the variable
    Name
    """
    var_index = bdd["t_table"][u][0]-1
    return bdd["var_order"][var_index]

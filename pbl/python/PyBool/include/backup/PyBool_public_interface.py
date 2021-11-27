#Tyler Sorensen
#February 15, 2012
#University of Utah

#PyBool_public_interface.py

#The public interface for PyBool. Methods and representation
#styles are described more completely in README.txt

import PyBool_algorithms_expirimental as PBA
import PyBool_builder as PBB

#note: This is the public interface, so while
#some of the calls look redundant, it is in this
#form so that extra code can be added in the
#future without worrying about messing with 
#the algorithms

#####################################################
#RECURSIVE REPRESENTATION INTERFACE
#####################################################


def propagate(expr, tup):
    """
    Propagae the assignment TUP (string variable name, boolean value)
    through expression EXPR
    """
    expr = PBA.propagate(expr, tup)
    if type(expr) == bool:
        return PBB.mk_const_expr(expr)
    return expr


def apply_sol_expr(expr, sol):
    """
    apply the solution SOL (DictType {string variable name : boolean value}
    to the expression EXPR
    """
    return PBA.apply_sol_expr(expr, sol)

def print_expr(expr):
    """
    prints a readable string representing the expression EXPR
    """
    return PBA.print_expr(expr)

def nne(expr):
    """
    converts the expression EXPR into negation normal form
    """
    #first get rid of all non standard
    #operators
    expr = PBA.std_expr(expr)

    #Then propagate the negation
    return PBA.nne(expr)

def exp_cnf(expr):
    """
    converts the expression EXPR into an expodentially
    large cnf expression (still recursive, use cnf_list to
    convert to list representation)
    """
    #Convert to nne
    expr = nne(expr)
    
    #distribute
    return PBA.exp_cnf(expr)

def poly_cnf(expr):
    """
    converts the expression EXPR into a polynomial sized
    cnf formula (adds variables and returned expression
    is still recursive, use cnf_list to
    convert to list representation)
    """
    repHash = {}
    return PBA.poly_cnf(expr, repHash)

def cnf_list(expr):
    """
    returns a list representation of the recursive expression EXPR
    in the form of a dict where the clauses field is the actual list
    and Map is the mapping of variable names to numbers (in the form
    of a list of tuples)
    """

    #Get a var map, create a new one (in case the old one
    #is wrong) and apply the new map.
    m = PBA.get_var_map(expr)
    m = PBA.create_new_map(m)
    PBA.apply_map(expr, m)

    return {"Clauses" : PBA.cnf_list(expr) ,
            "map"     : m              }

def number_vars(expr):
    """
    returns the number of variables in expr
    """    
    m = PBA.get_var_map(expr)
    return len(m)

def get_vars(expr):
    return [x[0] for x in PBA.get_var_map(expr)]

def simplify(expr):
    expr = propagate(expr, (None, True))
    if type(expr) == bool:
        return PBB.mk_const_expr(expr)
    return expr


#####################################################
#CNF LIST REPRESENTATION INTERFACE
#####################################################

def cnf_propagate(clauses, variable, truth_value):
    """
    propagates the assingment of VARIABLE to TRUTH_VALUE in
    CLAUSES
    """
    return PBA.cnf_propagate(clauses, variable, truth_value)

def cnf_apply_sol(clauses, sol):
    """
    applys the solution SOL to CLAUSES (should return a 
    boolean value) SOL is a list of booleans where the variable
    name corresponds to the index of the list
    """
    return PBA.cnf_apply_sol(clauses, sol)

def cnf_get_unit_clauses(clauses):
    """
    returns a list of literals appearing in unit clauses
    in CLAUSES
    """
    return PBA.cnf_get_unit_clauses(clauses)

def cnf_get_pure_literals(clauses):
    """
    returns a list of pure literals (variables appearing exclusively
    negated or non negated) in CLAUSES
    """
    return PBA.cnf_get_pure_literals(clauses)

def cnf_get_var(literal):
    """
    given a literal LITERAL, return the variable it represents
    """
    return abs(literal)

def cnf_get_sign(literal):
    """
    given a literal LITERAL, return the false if it is negated
    true otherwise
    """
    return literal > 0

def cnf_to_rec(clauses):
    """
    given a list form of an expression CLAUSES, return an equivalent
    recursive form
    """
    return PBA.cnf_to_rec(clauses)

def cnf_vars(clauses):
    """
    return a list of variables in the list represented expression CLAUSES
    """
    return list(set([abs(lit) for clause in clauses for lit in clause]))

def cnf_sat(clauses):
    """
    returns true if clauses is satisfied
    """
    return len(clauses) == 0
    
def cnf_unsat(clauses):
    """
    returns true if clauses is un-satisfied
    """
    return True in [len(x) == 0 for x in clauses]

#####################################################
#FILE IO INTERFACE
#####################################################


class Parse_Error(Exception):
    """
    The exception that gets raised if there is a parsing error
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def parse_dimacs(fname):
    """
    parses a dimacs file FNAME and returns a list represented
    formula
    """

    from PyBool_dimacs_parse import parse_file as parse_dimacs_file
    clauses = parse_dimacs_file(fname)
    
    return {"num_vars"    : len(cnf_vars(clauses)),
            "num_clauses" : len(clauses)          ,
            "clauses"     : clauses               }

def write_dimacs(clauses, fname):
    """
    given a list represented expression CLAUSES, writes
    a dimacs formatted file FNAME
    """

    #opening comments
    f = open(fname, 'w')
    s = "c File Produced by PyBool\n"
    f.write(s)
    
    #stat line
    s = "p cnf %i %i\n" % (len(cnf_vars(clauses)), len(clauses))
    f.write(s)

    #write the clauses
    for clause in clauses:
        s = ""
        for literal in clause:
            s = "%s %i" % (s, literal)
        
        #end the line
        s = "%s 0\n" % s
        s = s[1:len(s)]
        f.write(s)

    #close the file
    f.close()

def parse_std(fname):
    """
    parses a standard input file and returns
    a dictionary in the form of
    "var_order": the optional ordering of the variables
    "main_expr": the main expression parsed
    """
    from PyBool_std_parse import parse_file as parse_std_file
    return parse_std_file(fname)

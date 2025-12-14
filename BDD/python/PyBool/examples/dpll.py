#! /usr/bin/env python2.6

#Name: Tyler Sorensen 
#Date: January 5, 2012
#File Name: dpll.py
#
#Description: The dpll algorithm for PySat
#Goal. Keep it under 200 Lines! Currently at 112 (including comments!)


import copy
import sys
sys.path.append("../include/")
import PyBool_public_interface as Bool
import pdb

#simple dpll algorithm.
def PySat_dpll(clauses):

#    pdb.set_trace()
    if len(clauses) == 0:
        return True
    
    if True in [len(x) == 0 for x in clauses]:
        return False

#    pdb.set_trace()

    
    unit_C = Bool.cnf_get_unit_clauses(clauses)
    for unit in unit_C:
        clauses = Bool.cnf_propagate(clauses, Bool.cnf_get_var(unit), Bool.cnf_get_sign(unit))

#    pdb.set_trace()

    pureLits = Bool.cnf_get_pure_literals(clauses)
    
#    pdb.set_trace()

    for pl in pureLits:
        clauses = Bool.cnf_propagate(clauses, Bool.cnf_get_var(pl), Bool.cnf_get_sign(pl))

        
#    pdb.set_trace()

    if len(clauses) == 0:
        return True
    
    if True in [len(x) == 0 for x in clauses]:
        return False
    
#    pdb.set_trace()

    newVar = chooseVar(clauses)

    trueClause = Bool.cnf_propagate(copy.deepcopy(clauses), Bool.cnf_get_var(newVar),True)

    if PySat_dpll(trueClause):
        return True

    falseClause = Bool.cnf_propagate(copy.deepcopy(clauses), Bool.cnf_get_var(newVar),False)


    if PySat_dpll(falseClause):
        return True

    return False;
        
#Choose the next variable to assign. Just choose a variable in the smallest clause
def chooseVar(clauses):
    minC = clauses[0]
    for x in clauses:
        if len(x) < len(minC):
            minC = x

    return minC[0]

if __name__ == "__main__":
    clauses = Bool.parse_dimacs("example_dimacs_files/75VarSat.cnf")
    print (PySat_dpll(clauses["clauses"]))

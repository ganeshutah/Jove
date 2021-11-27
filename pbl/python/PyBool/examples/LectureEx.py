#! /usr/bin/env python2.7

import copy
import sys
sys.path.append("../include/")
import PyBool_public_interface as Bool
import PyBool_builder as BoolB
import pdb

#Good example to demo PyBool. Step through with pdb, and print
#variables at each stage. For the recursive representations (expr and expr2)
#use Bool.print_expr(expr) for pretty printing. Uses very simple DIMACS
#file example_dimacs_files/lecture.cnf
if __name__ == "__main__":

    #Read and parse a dimacs file
    clauses = Bool.parse_dimacs("example_dimacs_files/lecture.cnf")
    clauses = clauses["clauses"]

    #convert dimacs form to recursive form
    expr = Bool.cnf_to_rec(clauses)

    #make a new formula that is the negation of previous
    expr = BoolB.mk_neg_expr(expr)

    expr2 = copy.deepcopy(expr)

    #Put in negation normal form
    expr = Bool.nne(expr)

    #now make a possibly exp. sized cnf
    expr = Bool.exp_cnf(expr)
    
    #with this expression we make a worst case
    #polynomial sized cnf
    expr2 = Bool.poly_cnf(expr2)

    #Now put the recursive formula back to list form
    clauses = Bool.cnf_list(expr2)

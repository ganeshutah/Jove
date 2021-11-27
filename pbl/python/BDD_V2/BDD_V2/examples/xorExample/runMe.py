#!/usr/bin/python2.7

#Tyler Sorensen
#Sept 18, 2011

#This example shows how BDD's can be used to test
#the equivalence of formulas.

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD
import pdb

if __name__ == "__main__":
    
    #creating and initializing the BDD
    x = BDD.bdd_init("xor.txt")

    #building the tree
    BDD.ite_build(x)

    print "Are the formulas the same?"
    if BDD.sat_count(x) == 32:
        print "yes"
    else:
        print "No, Here is a counter example:"
        print ""
        print BDD.any_sat(x)

    #BDD.dot_bdd(x, "myDot.dot")

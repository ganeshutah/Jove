#!/usr/bin/python2.7

#Tyler Sorensen
#Sept 18, 2011

#Simple example first example. Shows off public for the BDD.

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD
import pdb

if __name__ == "__main__":
    
    #creating and initializing the BDD
    x = BDD.bdd_init("formula.txt")

    #building the tree
    BDD.ite_build(x)

    #find and display all sat assignments
    print("All Sat assignments: ")
    print("----------------------------")

    b = BDD.all_sat(x)

    for q in b:
        print(q)

    print ""

    print BDD.stat_string(x)

    print ""
    print "One satisfying assignment is: "
    print BDD.any_sat(x)
    BDD.dot_bdd(x, "myDot.dot")


#!/usr/bin/python2.7

#Tyler Sorensen
#Sept 18, 2011

#This example shows a simple bit-blasting decision procedure.
#See formula.txt for more info

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD
import pdb

if __name__ == "__main__":
    
    #creating and initializing the BDD
    bdd = BDD.bdd_init("formaula2.txt")


    #building the tree
    BDD.ite_build(x)
    BDD.dot_bdd(x,"dotfile4.dot")

    #find and display all sat assignments
    print("All Sat assignments: ")
    print("----------------------------")#

    b = BDD.all_sat(x)

    for q in b:
        print(q)

    print "There are: " + str(BDD.sat_count(x)) + " satisfying assignments"
    print ""
    print ""

    print BDD.stat_string(x)

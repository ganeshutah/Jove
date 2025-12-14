#!/usr/bin/python2.7

#Tyler Sorensen
#Sept 18, 2011

#This example shows the second more complicated Lewis Carroll puzzle.
#See wiseYoungPigs.txt for the formula.

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD

if __name__ == "__main__":
    
    #creating and initializing the BDD
    x = BDD.bdd_init("wiseYoungPigs.txt")

    #building the tree
    BDD.ite_build(x)


    print "Can wise young pigs go up in balloons?"

    if BDD.sat_count(x) == 0:
        print "No"
    else:
        print "Yes, and here's how:"
        
        print ""
        print BDD.any_sat(x)
        BDD.dot_bdd(x,"my_dot.dot")

    #BDD.dot_bdd(x, "myDot.dot")

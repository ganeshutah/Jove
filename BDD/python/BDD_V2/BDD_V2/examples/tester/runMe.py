#!  /usr/bin/env python2.7

#Tyler Sorensen
#Oct 10, 2011

#Simple BDD script to prove that Babies cannot manage crocodiles
#See Solution.txt for a complete walkthrough.

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD
import os

if __name__ == "__main__":
    
    #creating and initializing the BDD
    x = BDD.bdd_init("build8.txt")
    y = BDD.bdd_init("build8.txt")
    
    #building the tree
    BDD.build(x)
    BDD.ite_build(y)

    BDD.dot_bdd(x, "dotfile1.dot")
    BDD.dot_bdd(y, "dotfile2.dot")

    if BDD.sat_count(x) != BDD.sat_count(y):        
        print "error!"

    if BDD.all_sat(x) != BDD.all_sat(y):        
        print "error!"
    
    

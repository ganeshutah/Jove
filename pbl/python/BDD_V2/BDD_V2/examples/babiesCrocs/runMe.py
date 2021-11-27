#!  /usr/bin/env python2.7

#Tyler Sorensen
#Oct 10, 2011

#Simple BDD script to prove that Babies cannot manage crocodiles
#See Solution.txt for a complete walkthrough.

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD

if __name__ == "__main__":
    
    #creating and initializing the BDD
    x = BDD.bdd_init("BabiesAndCrocs.txt")

    
    #building the tree
    BDD.ite_build(x)

    #Can babies manage crocs? If they can't then we should have
    #No satisfying assignments
    BDD.dot_bdd(x,"dotfile.dot")
    print("Can Babies Manage Crocs?")
    if BDD.sat_count(x) == 0:
        print("No")
    else:
        print("Yes")

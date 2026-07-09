#!/usr/bin/python2.7

#Tyler Sorensen
#Sept 18, 2011

#This example shows how BDD's can be used to show how many
#4 colorings of a given map are available.

#The relationships are that:
#Navada   <-> Utah
#Navada   <-> Arizona
#Utah     <-> Arizona
#Colorado <-> Arizona
#Colorado <-> Utah

import sys
sys.path.append("../../include/")
sys.path.append("../../../../PyBool/include/")
import BDD

if __name__ == "__main__":

    #creating and initializing the BDD
    x = BDD.bdd_init("constraints.txt")
    
    BDD.build(x)
    print "There are " + str(BDD.sat_count(x)) + " four colorings of the map"

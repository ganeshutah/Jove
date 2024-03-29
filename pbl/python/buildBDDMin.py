import os
import sys
from common import *

uniqid       = sys.argv[1]
dot_OUT      =  "> python/images/" + uniqid + ".png"

sys.path.append(BDD_PATH)
sys.path.append(PyBool_PATH)
import BDD
import PyBool_public_interface as pb

ERR_str = ""
STAT_str = ""

def exit_err():
    f = open("python/programoutput/error" + uniqid + ".txt", "w")
    f.write(ERR_str)
    f.close()
    exit(0)
    

if __name__ == "__main__":
   
    try:
        bdd = BDD.bdd_init("python/programoutput/" + uniqid + ".txt")
        
    except pb.Parse_Error as e:
        ERR_str = "There was an error parsing your file, please check your syntax\n" \
                  + e.value + "\n"
        exit_err()
        
    if len(bdd["var_order"]) > BDD_VAR_LENGTH:
        ERR_str = "Your formula contains too many variables for the web interface. Please try again with less than 14 variables or download the BDD package and run it on your own machine."
        exit_err()
                        
    if len(pb.print_expr(bdd["expr"])) > 500:
        ERR_str = "Your formula is too long for the web interface. Please try again with a smaller formula or download the BDD package and run it on your own machine."
        exit_err()

    BDD.reorder_ite_build(bdd)

    stats = BDD.stat_string(bdd)
    sat_count = BDD.sat_count(bdd)
    variable_order = bdd["var_order"]
    sat_assigns = BDD.all_sat(bdd)
    sat_assigns_string = ""
    for x in sat_assigns:        
        sat_assigns_string += str(map(lambda y : 0 if '~' in y else 1, x)) + '\n'
    
    dot_file = "python/programoutput/" + uniqid + ".dot"
    BDD.dot_bdd(bdd, dot_file)
    #print reduce(lambda x, y : x + " " + y, [dot_PATH, dot_ARGS, dot_file, dot_OUT])
    err = os.system(reduce(lambda x, y : x + " " + y, [dot_PATH, dot_ARGS, dot_file, dot_OUT]))
    #print rm + " " + dot_file
    os.system(rm + " " + dot_file)

    if err != 0:
        ERR_str = "There was an error running dot on the server"
        exit_err()
    
    STAT_str = "Number of satisfying assignments: " + str(sat_count) + "\n"\
                + stats + "\n\nAll satisfying assignts:\n" + "------------------------------\n"\
                + sat_assigns_string
    
    f = open("python/programoutput/info" + uniqid + ".txt", "w")
    f.write(STAT_str)
    f.close()

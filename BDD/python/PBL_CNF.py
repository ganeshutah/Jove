import os
import sys
from common import *

uniqid       = sys.argv[1]

sys.path.append(PyBool_PATH)
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
        expr = pb.parse_std("python/programoutput/" + uniqid + ".txt")["main_expr"]    
        
    except pb.Parse_Error as e:
        ERR_str = "There was an error parsing your file, please check your syntax\n" \
                  + e.value + "\n"
        exit_err()
        
    if pb.number_vars(expr) > PBL_VAR_LENGTH:
        ERR_str = "Your formula contains too many variables for the web interface. Please try again with less than 14 variables or download the PBL package and run it on your own machine."
        exit_err()
                        
    if len(pb.print_expr(expr)) > 500:
        ERR_str = "Your formula is too long for the web interface. Please try again with a smaller formula or download the PBL package and run it on your own machine."
        exit_err()

    
    expr = pb.exp_cnf(expr)
    STAT_str = pb.print_expr(expr) + "\n"
    
    f = open("python/programoutput/info" + uniqid + ".txt", "w")
    f.write(STAT_str)
    f.close()

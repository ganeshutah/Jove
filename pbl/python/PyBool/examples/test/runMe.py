#! /usr/bin/env python2.7

import sys
sys.path.append("../../include/")
import PyBool_public_interface as Bool


if __name__ == "__main__":
    expr = Bool.parse_std("input.txt")
    expr = expr["main_expr"]
    
    expr = Bool.simplify(expr)
    
    expr = Bool.nne(expr)

    print Bool.print_expr(expr)

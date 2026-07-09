#Tyler Sorensen
#February 15, 2012
#University of Utah

#PyBool_builder.py

#The interface to build recursive style boolean expressions
#See README.txt for more information

def mk_const_expr(val):
    """
    returns a constant expression of value VAL
    VAL should be of type boolean
    """
    return {"type" : "const",
            "value": val    }

def mk_var_expr(name):
    """
    returns a variable expression of name NAME
    where NAME is a string
    """
    return {"type" : "var"    ,
            "name" : (name, 0)}

def mk_neg_expr(expr):
    """
    returns a negated expression where EXPR
    is the expression to be negated
    """
    return {"type" : "neg",
            "expr" : expr }

def mk_and_expr(expr1, expr2):
    """
    returns an and expression 
    of the form (EXPR1 /\ EXPR2)
    where EXPR1 and EXPR2 are expressions
    """
    return {"type"  : "and" ,
            "expr1" : expr1 ,
            "expr2" : expr2 }

def mk_or_expr(expr1, expr2):
    """
    returns an or expression 
    of the form (EXPR1 \/ EXPR2)
    where EXPR1 and EXPR2 are expressions
    """    
    return {"type"  : "or"  ,
            "expr1" : expr1 ,
            "expr2" : expr2 }

#NOT NEEDED
def mk_paren_expr(expr):
    return {"type" : "paren",
            "expr" : expr   }

def mk_impl_expr(expr1, expr2):
    """
    returns an or expression 
    of the form (EXPR1 -> EXPR2)
    where EXPR1 and EXPR2 are expressions
    NOTE: Order of expr1 and expr2 matters here
    """    
    return {"type"  : "impl",
            "expr1" : expr1 ,
            "expr2" : expr2 }

def mk_eqv_expr(expr1, expr2):
    """
    returns an or expression 
    of the form (EXPR1 <=> EXPR2)
    where EXPR1 and EXPR2 are expressions
    """    
    return {"type"  : "eqv" ,
            "expr1" : expr1 ,
            "expr2" : expr2 }

def mk_xor_expr(expr1, expr2):
    """
    returns an or expression 
    of the form (EXPR1 XOR EXPR2)
    where EXPR1 and EXPR2 are expressions
    """    
    return {"type"  : "xor" ,
            "expr1" : expr1 ,
            "expr2" : expr2 }

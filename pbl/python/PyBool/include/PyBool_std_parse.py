#Tyler Sorensen
#February 17, 2012
#University of Utah

#Parser for general equations

import os
import ply.lex  as lex
import ply.yacc as yacc
import pdb
import itertools
from PyBool_builder import *
from PyBool_public_interface import Parse_Error
from PyBool_public_interface import rename_var
from PyBool_public_interface import rename_var_list
from PyBool_public_interface import print_expr

#############################################
#Lex
#############################################

#Keywords
reserved = {
   'XOR'       : 'XOROP'   ,
   'Var_Order' : 'VARORDER',
   'Main_Exp'  : 'MAINEXP',
   'exists'     : 'EXISTS',
   'exists_excl' : 'EXISTS_EXCL'
}

tokens = ["CONST"     ,
          "VARIABLE"  ,
          "LBRAC"    ,
          "RBRAC"    ,
          "LPAREN"    ,
          "RPAREN"    ,
          "OROP"      ,
          "ANDOP"     ,
          "IMPLIESOP" ,
          "EQOP"      ,
          "NOTOP"     ,
          "ASSIGNOP"  ,
          "COLON"     ,
          "DOT"       ,
          ] + list(reserved.values()) #adding listed of reserved val

#Defining simple tokens
t_CONST      = "0|1"
t_LPAREN     = "\("
t_RPAREN     = "\)"
t_LBRAC     = "\["
t_RBRAC     = "\]"
t_OROP       = "\|?\|"
t_ANDOP      = "&?&"
t_XOROP      = "XOR"
t_EQOP       = "<=>|<->"
t_IMPLIESOP  = "=>|->"
t_NOTOP      = "~|!"
t_VARIABLE   = "[a-zA-Z2-9][a-zA-Z0-9_]*"
t_ASSIGNOP   = "="
t_COLON      = ":"
t_DOT        = "\."

t_ignore         = ' ;\t\n\r,'
t_ignore_COMMENT = r'\#.*'

#Checking for reserved words
def t_ID(t):
    r'[a-zA-Z2-9][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'VARIABLE')    # Check for reserved words
    return t    

#Defining errors (not too robust)
def t_error(t):
    raise Parse_Error("Unable to tokenize: '" + str(t.value) + "'  Line Number: " + str(line_num))
    #t.lexer.skip(1)

#Build the lexer
lexer = lex.lex()

#############################################
#Yacc
#############################################

#Global variables needed for parsing
main_expr  = {}
var_order  = []
sub_expr   = {}
line_num   = 0

#Defining precedence
precedence = (
    ('right', 'EQOP'     ),
    ('right', 'IMPLIESOP'),
    ('left' , 'XOROP'    ),
    ('left' , 'OROP'     ),
    ('left' , 'ANDOP'    ),
    ('left' , 'NOTOP'    ),
    ('left' , 'LBRAC', 'RBRAC'),
    ('left' , 'LPAREN', 'RPAREN')
)

def remove_dups(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

#Start state
def p_start(p):
    '''start : VARORDER COLON variableList
             | VARIABLE ASSIGNOP expression
             | MAINEXP COLON expression
             | empty'''

    global main_expr 
    global sub_expr
    global var_order

    #ignore comments
    if p[1] == "COMMENT":
        return

    #if it was a sub_expression assignment, record it
    elif p[2] == "=":            
        sub_expr[p[1]] = p[3]

    #if it was the main expression record it.
    elif p[1] == "Main_Exp":
        main_expr = p[3]

    #if it was the main expression record it.
    elif p[1] == "Var_Order":
        #get rid of duplicates        
        var_order = remove_dups(var_order + p[3])


#Rules for all the expressions (mostly using PyBool_builder)
def p_expression_paren(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_not(p):
    '''expression : NOTOP expression'''
    p[0] = mk_neg_expr(p[2])

def p_expression_and(p):
    '''expression : expression ANDOP expression'''
    p[0] = mk_and_expr(p[1], p[3])
    
def p_expression_or(p):
    '''expression : expression OROP expression'''
    p[0] = mk_or_expr(p[1], p[3])

def p_expression_xor(p):
    '''expression : expression XOROP expression'''
    p[0] = mk_xor_expr(p[1], p[3])

def p_expression_impl(p):
    '''expression : expression IMPLIESOP expression'''
    p[0] = mk_impl_expr(p[1], p[3])

def p_expression_eqv(p):
    '''expression : expression EQOP expression'''
    p[0] = mk_eqv_expr(p[1], p[3])

def p_expression_exists(p):    
    '''expression : EXISTS VARIABLE DOT LPAREN expression RPAREN'''
    q = [rename_var(p[5], (p[2],var)) for var in var_order]
    p[0] = reduce(lambda x,y: mk_or_expr(x,y), q)

def p_expression_exists_excl(p):    
    '''expression : EXISTS_EXCL variableList DOT LPAREN expression RPAREN'''
    q = [rename_var_list(p[5],zip(p[2],perm)) for perm in itertools.permutations(var_order, len(p[2]))]
    p[0] = reduce(lambda x,y: mk_or_expr(x,y), q)

def p_expression_rename(p):
    '''expression : VARIABLE LBRAC variableList COLON ASSIGNOP variableList RBRAC'''
    dom = sub_expr.keys()
    if p[1] in dom:
        expr = sub_expr[p[1]]
        p[0] = rename_var_list(expr,zip(p[3],p[6]))
    else:
        raise Parse_Error("Expression: " + p[1] + " is not declared. Line Number: " + str(line_num))



#Variable is the only hard one
def p_expression_var(p):
    '''expression : VARIABLE'''

    #See if we've seen the variable before, if so,
    #just return it.
    dom = sub_expr.keys()
    if p[1] in dom:
        p[0] = sub_expr[p[1]]

    #else make a new var expr
    else:
        var_expr = mk_var_expr(p[1])
        sub_expr[p[1]] = var_expr
        p[0] = var_expr


def p_expression_const(p):
    '''expression : CONST'''
    if p[1] == "0":
        p[0] = mk_const_expr(False)
    else:
        p[0] = mk_const_expr(True)

#Used for comments
def p_empty(p):
    'empty :'
    p[0] = "COMMENT"

#Used for the optional variable list (it is illegal to 
#declare a variable twice in the variable ordering)
def p_variableList(p):
    '''variableList : VARIABLE variableList
                    | VARIABLE'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]
        
# Error rule for syntax errors
def p_error(p):
    raise Parse_Error("Unable to parse line number " + str(line_num))

# Build the parser
parser = yacc.yacc()

#############################################
#external methods
#############################################

#Parsing the main file and returning information.
def parse_file(example):
    """
    Parses the file FNAME according to the above grammer
    Returns a dictionary containing the optional variable
    order and main expression
    """
    global var_order
    global main_expr
    global sub_expr
    global line_num

    var_order = []
    main_expr = {}
    sub_expr  = {}

    print("cwd = ", os.getcwd())
    #fName = read( "fName: ")
#   fName = "examples/example1"
#   print("fName is ", fName)
#    f = open(fName, 'r')
#    s = f.readline()
    s = example
    
    while s != []:
        line_num += 1
        parser.parse(s[0])
        s = s[1:] # f.readline()        


    #Return a dictionary of information
    #to include both the var_order and main_expr
    return {"var_order" : var_order,
            "main_expr" : main_expr}

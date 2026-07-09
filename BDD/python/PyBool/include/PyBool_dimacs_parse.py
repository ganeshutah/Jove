#A Ply parser for the dimacs file format.
#importing lex and yacc
import ply.lex  as lex
import ply.yacc as yacc

import sys
import copy
import pdb

#Tokens for the ply
tokens = ["VARIABLE",
          "TERMCHAR",
          "P_LINE"  ,
          "CNF"     ]


#Tokens defined with regular expressions
t_VARIABLE        = "-?[1-9][0-9]*"  #Variable
t_TERMCHAR        = "0"              #Clause terminating variable
t_P_LINE          = "p"              #P line to tell us how many vars we have
t_CNF             = "cnf"            #Part of the P line
t_ignore_COMMENT  = "^c.*$"          #Comment
t_ignore          = " \t"            #ignore spaces and tabs.

#Defining errors (required).
def t_error(t):
    t.lexer.skip(1)

#Build the lexer
lexer = lex.lex()

#Global variables for building the clauses
clauses = []
clause  = []

#The start production
#According to the .cnf specifications, a line can be a comment
#or a list of variables ended with 0(terminate clause variable)
#or just a list of variables.
def p_start(p):
    '''start : P_LINE CNF VARIABLE VARIABLE
             | variableList TERMCHAR
             | variableList
             | empty'''

    global clauses
    global clause
    
    if p[1] == "COMMENT": #Then it was a comment and ignore
        return

    elif len(p) == 5:     #Dealing with the P line (ignored)
        return 

    elif len(p) == 2:     #Then it was the variable list w/out terminating variable
        return
    else:                 #Save and restart the clause if it was terminated.
        clauses.append(copy.deepcopy(clause))
        clause = []

#Store the variables as they are seen in a clause.
def p_variableList(p):
    '''variableList : variableList VARIABLE  
                    | VARIABLE'''

    global clause
    if len(p) == 3:
        clause.append(int(p[2]))
    else:
        clause.append(int(p[1]))

#Empty comment rule
def p_empty(p):
    '''empty :'''
    p[0] = "COMMENT"

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

#build the parser
parser = yacc.yacc()

#Use yacc to populate the clauses list.
#(Call this file)
def parse_file(fname):
    global clauses

    f = open(fname, 'r')
    s = f.readline()
    while s != "":
        parser.parse(s)
        s = f.readline()
        
    f.close()
    return clauses

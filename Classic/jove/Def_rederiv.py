
# coding: utf-8

# In[ ]:


from lex import lex
from yacc import yacc
from jove.StateNameSanitizers import ResetStNum, NxtStateStr
from jove.SystemImports       import *


# In[ ]:


tokens = ('EPS','STR','LPAREN','RPAREN','PLUS','STAR', 'NOT', 'AND')

# Tokens
t_PLUS    = r'\+'
t_STAR    = r'\*'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_EPS     = r'\'\'|\"\"'  # Not allowing @ for empty string anymore! # t_EPS = r'\@'
t_STR     = r'[a-zA-Z0-9]'
t_NOT     = r'\!'
t_AND     = r'\&'

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer if necessary
# lex()

# Parsing rules

precedence = (
   ('left','PLUS'),
   ('left', 'AND'),
   ('left','STAR'),
   ('right','NOT')
  )

def p_expression_plus(t):
    '''expression : expression PLUS catexp'''
    #
    t[0] = attrDyadicInfix("+", t[1], t[3])    
    
def p_expression_plus1(t):
    '''expression : catexp'''
    #
    t[0] = t[1] # attrZeroadic(t[1])

def p_expression_cat(t):
    '''catexp :  catexp andexp'''
    #
    t[0] = attrDyadicInfix(".", t[1], t[2])
    
def p_expression_cat1(t):
    '''catexp :  andexp'''
    #
    t[0] = t[1] # attrZeroadic(t[1])
    
def p_expression_ordy(t):
    '''andexp : andexp AND ordyexp'''
    #
    t[0] = attrDyadicInfix("&", t[1], t[3])
    
def p_expression_ordy1(t):
    '''andexp : ordyexp'''
    #
    t[0] = t[1] # attrZeroadic(t[1])

def p_expression_ordy_star(t):
    '''ordyexp : ordyexp STAR'''
    #
    ast = ('*', t[1]['ast'])

    nlin = t[1]['dig']['nl']
    elin = t[1]['dig']['el']
    
    rootin = nlin[0]

    root = NxtStateStr("R*_") # NxtStateStr("$_")
    right = NxtStateStr("*_")

    t[0] = {'ast' : ast,
            'dig' : {'nl' : [root] + nlin + [right], # this order important for proper layout!
                     'el' : elin + [ (root, rootin),
                                     (root, right) ]
                    }}

def p_expression_ordy_not(t):
    '''ordyexp : NOT ordyexp'''
    #
    ast  = ('!', t[2]['ast'])
    
    nlin = t[2]['dig']['nl']
    elin = t[2]['dig']['el']
    
    rootin = nlin[0]

    root = NxtStateStr("!R_") # NxtStateStr("$_")
    left = NxtStateStr("!_")

    t[0] = {'ast' : ast,
            'dig' : {'nl' : [ root, left ] + nlin, # this order important for proper layout!
                     'el' : elin + [ (root, left),
                                     (root, rootin) ]
                    }}

    
def p_expression_ordy_paren(t):
    '''ordyexp : LPAREN expression RPAREN'''
    #
    ast  = t[2]['ast']
    
    nlin = t[2]['dig']['nl']
    elin = t[2]['dig']['el']
    
    rootin = nlin[0]
    
    root = NxtStateStr("(R)_") # NxtStateStr("$_")
    left = NxtStateStr("(_")
    right= NxtStateStr(")_")
    
    t[0] = {'ast' : ast,
            'dig' : {'nl' : [root, left] + nlin + [right], #order important f. proper layout!
                     'el' : elin + [ (root, left),
                                     (root, rootin),
                                     (root, right) ]
                    }}

def p_expression_ordy_eps(t):
    '''ordyexp : EPS'''
    #
    strn = '@'
    ast  = ('@', strn)           
    t[0] = { 'ast' : ast,
             'dig' : {'nl' : [ strn + NxtStateStr("_") ],
                      'el' : []
                     }}

# Maintain nl as node list including root node introduced at
# each level. That will be at the head of nl
# el has edges that stitch from new root to existing root + ( ) etc
# a root is an anchor $_.. or a leaf            
    
def p_expression_ordy_str(t):
    '''ordyexp : STR'''
    #
    strn = t[1]
    ast  = ('str', strn)
    t[0] = {'ast' : ast,
            'dig' : {'nl' : [ strn + NxtStateStr("_") ],
                     'el' : [] 
                    }}

def p_error(t):
    print("Syntax error at '%s'" % t.value)

#--

'''
def attrZeroadic(attr):   
    return attr
    ast = attr['ast']
    nlin = attr['dig']['nl']
    elin = attr['dig']['el']
    rootin = nlin[0]
    root = NxtStateStr("$_")
    return {'ast' : ast,
            'dig' : {'nl' : [ root ] + nlin,
                     'el' : elin + [ (root, rootin) ]
                     }}
'''
    
def attrDyadicInfix(op, attr1, attr3):
    ast  = (op, (attr1['ast'], attr3['ast']))
    
    nlin1 = attr1['dig']['nl']
    nlin3 = attr3['dig']['nl']
    nlin  = nlin1 + nlin3
    
    elin1 = attr1['dig']['el']
    elin3 = attr3['dig']['el']
    elin  = elin1 + elin3
    
    rootin1 = nlin1[0]
    rootin3 = nlin3[0]    
    
    root   = NxtStateStr("R1"+op+"R2"+"_") # NxtStateStr("$_")
    left   = rootin1
    middle = NxtStateStr(op+"_")
    right  = rootin3
    
    return {'ast' : ast,
            'dig' : {'nl' : [ root, left, middle, right ] + nlin,
                     'el' : elin + [ (root, left),
                                     (root, middle),
                                     (root, right) ]
                     }}
#===

def re2ast(s):
    """This function turns a regular expression (passed in as a string s)
       into an abstract syntax tree, and returns the tree (encoded in Python)
    """
    mylexer  = lex()
    myparser = yacc()
    pt = myparser.parse(s, lexer = mylexer)
    return (pt['ast'], pt['dig']['nl'], pt['dig']['el'])


# In[ ]:


def drawPT(nl, el, comment="PT"):
    """Given a node list nl and edge-list el,
       draw the Parse Tree. The node names are uniq'ed,
       and so strip the _.. part before drawing.
    """
    dopt = Digraph(comment)
    dopt.graph_attr['rankdir'] = 'TB'
    for n in nl:
        prNam = n.split('_')[0]
        dopt.node(n, prNam, shape="oval", peripheries="1")
    for e in el:
        dopt.edge(e[0], e[1])
    return dopt


# In[ ]:


print('''You may use any of these help commands:
help(re2ast)
help(drawPT)
''')


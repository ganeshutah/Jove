
# coding: utf-8

# # Regular Expressions, conversion to NFA
# 
# In this module, we will cover regular expressions by showing how they can be converted to NFA. The scanner and parser for RE to convert them to NFA are the main part of this module.
# 

# In[1]:

from jove.Def_NFA import mk_nfa
from jove.lex     import lex
from jove.yacc    import yacc
from jove.StateNameSanitizers import ResetStNum, NxtStateStr


# # Parsing regular expressions : ReParse
# 

# In[2]:

# -----------------------------------------------------------------------------
# reparseNEW.py
#
# Parses regular expressions (without the empty RE case)
# Produces NFA as output.
#
# The NEW signifies that I'm generating NFAs starting from
# sets of states.
#
# Adapted from calc.py that is available from 
# www.dabeaz.com/ply/example.html
# -----------------------------------------------------------------------------


#-----------------------------------------------------------------
#-- Begin lexer construction
#-----------------------------------------------------------------

#-- The tokens that constitute an RE are these
tokens = (
    'EPS','STR','LPAREN','RPAREN','PLUS','STAR'
    )

#-- The token definitions in terms of raw strings are being expressed now
t_PLUS    = r'\+'
t_STAR    = r'\*'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_EPS     = r'\'\'|\"\"'  # Not allowing @ for empty string anymore!
t_STR     = r'[a-zA-Z0-9]'  
# Making the above r'[a-zA-Z0-9]+' to accept strings as 
# "tokens", i.e. indivisible units that can be subject to
# RE operations

#-- Ignored characters by the lexer
t_ignore = " \t"

#-- Upon new lines, increase the lexer's line count variable
def t_newline(t):
    r'\n+'
    print("getting newline")
    t.lexer.lineno += t.value.count("\n")

#-- Lexer's error announcer for illegal characters
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
#-- We don't build lexer here; we build before calling yacc()
#-- and then feed the lexer into reparser.parse (see below)


#--------------------------------------------------------------------
#--- Here is the parser set-up in terms of binary operator attributes
#--------------------------------------------------------------------



#-- Token precedences and associativity are declared in one place
#-- By declaring PLUS before STAR, we are implying that it's of lower 
#-- precedence. Also declared is that they are both left-associative.

precedence = (
    ('left','PLUS'),
    ('left','STAR'),
    )

#---------------------------------------------------------------------
#--- Here are the parsing rules for REs; each returns an NFA as "code"
#---------------------------------------------------------------------

#-- * The E -> E + C production

def p_expression_plus(t):
    '''expression : expression PLUS catexp'''
    print("Got a plus token")
    t[0] = mk_plus_nfa(t[1], t[3]) # Union of the two NFAs is returned
    
def mk_plus_nfa(N1, N2):
    """Given two NFAs, return their union.
    """
    print("Given the parse of two NFA, making one PLUS-connected NFA")
    delta_accum = dict({})
    delta_accum.update(N1["Delta"])
    delta_accum.update(N2["Delta"]) # Simply accumulate the transitions
    # The alphabet is inferred bottom-up; thus we must union the Sigmas 
    # of the NFAs!
    return mk_nfa(Q     = N1["Q"] | N2["Q"], 
                  Sigma = N1["Sigma"] | N2["Sigma"], 
                  Delta = delta_accum, 
                  Q0    = N1["Q0"] | N2["Q0"], 
                  F     = N1["F"] | N2["F"])    

#-- * The E -> C production
    
def p_expression_plus_id(t):
    '''expression : catexp'''
    # Simply inherit the attribute from t[1] and pass on    
    t[0] = t[1] 

#-- * The C -> C O production

def p_expression_cat(t):
    '''catexp :  catexp ordyexp'''
    t[0] = mk_cat_nfa(t[1], t[2])

def mk_cat_nfa(N1, N2):
    delta_accum = dict({}) 
    delta_accum.update(N1["Delta"])
    delta_accum.update(N2["Delta"])
    # Now, introduce moves from every one of N1's final states
    # to the set of N2's initial states.
    for f in N1["F"]:
        # However, N1's final states may already have epsilon moves to
        # other N1-states!
        # Expand the target of such jumps to include N2's Q0 also!
        if (f, "") in N1["Delta"]: 
            delta_accum.update({ (f,""):(N2["Q0"] | N1["Delta"][(f, "")])
                               })
        else:
            delta_accum.update({ (f, ""): N2["Q0"] })
    # In syntax-directed translation, it is impossible
    # that N2 and N1 have common states. Check anyhow
    # in case there are bugs elsewhere that cause it.
    assert((N2["F"] & N1["F"]) == set({})) 
    return mk_nfa(Q     = N1["Q"] | N2["Q"], 
                  Sigma = N1["Sigma"] | N2["Sigma"], 
                  Delta = delta_accum, 
                  Q0    = N1["Q0"],
                  F     = N2["F"])

#-- * The C -> O production

def p_expression_cat_id(t):
    '''catexp :  ordyexp'''
    # Simply inherit the attribute from t[1] and pass on
    t[0] = t[1]

#-- * The O -> O STAR production

def p_expression_ordy_star(t):
    'ordyexp : ordyexp STAR'
    t[0] = mk_star_nfa(t[1])

def mk_star_nfa(N):
    # Follow construction from Kozen's book:
    # 1) Introduce new (single) start+final state IF
    # 2) Let Q0 = set({ IF })
    # 2) Move on epsilon from IF to the set N[Q0]
    # 3) Make N[F] non-final
    # 4) Spin back from every state in N[F] to Q0
    #
    delta_accum = dict({})
    IF = NxtStateStr()
    Q0 = set({ IF }) # new set of start + final states
    # Jump from IF to N's start state set
    delta_accum.update({ (IF,""): N["Q0"] })
    delta_accum.update(N["Delta"])
    #
    for f in N["F"]:
        # N's final states may already have epsilon moves to
        # other N-states!
        # Expand the target of such jumps to include Q0 also.
        if (f, "") in N["Delta"]:
            delta_accum.update({ (f, ""): (Q0 | N["Delta"][(f, "")]) })
        else:
            delta_accum.update({ (f, ""): Q0 })
    #
    return mk_nfa(Q     = N["Q"] | Q0, 
                  Sigma = N["Sigma"], 
                  Delta = delta_accum, 
                  Q0    = Q0, 
                  F     = Q0)

#-- * The O -> ( E ) production

def p_expression_ordy_paren(t):
    'ordyexp : LPAREN expression RPAREN'
    # Simply inherit the attribute from t[2] and pass on
    t[0] = t[2]

#-- * The O -> EPS production
    
def p_expression_ordy_eps(t):
    'ordyexp : EPS'
    t[0] = mk_eps_nfa()

def mk_eps_nfa():
    """An nfa with exactly one start+final state
    """
    Q0 = set({ NxtStateStr() })
    F  = Q0
    return mk_nfa(Q     = Q0, 
                  Sigma = set({}), 
                  Delta = dict({}), 
                  Q0    = Q0, 
                  F     = Q0)                      

#-- * The O -> STR production, i.e. a single re letter

def p_expression_ordy_str(t):
    'ordyexp : STR'
    t[0] = mk_symbol_nfa(t[1])

def mk_symbol_nfa(a):
    """The NFA for a single re letter
    """
    # Make a fresh initial state
    q0 = NxtStateStr()
    Q0 = set({ q0 })
    # Make a fresh final state
    f = NxtStateStr()
    F = set({ f })
    return mk_nfa(Q     = Q0 | F, 
                  Sigma = set({a}), 
                  Delta = { (q0,a): F },
                  Q0    = Q0, 
                  F     = F)

def p_error(t):
    print("Syntax error at '%s'" % t.value)

#-- NOW BUILD THE PARSER if needed --    
# parser = yacc()

# End of reparseNEW.py
# -----------------------------------------------------------------------------


# ## RE to NFA code

# In[3]:

def re2nfa(s, stno = 0):
    """Given a string s representing an RE and an optional
       state number stno (default 0), generate an NFA that
       is language equivalent to the RE
    """
    # Reset the state number generator to 0
    ResetStNum() 
    # NxtStateStr() gets called whenever needed. 
    # Defined in StateNameSanitizers.py

    relexer = lex()

    #-- NOW BUILD THE PARSER -- 
    reparser = yacc()
    #-- FEED IT THE LEXER --
    myparsednfa = reparser.parse(s, lexer=relexer)
    #-- for debugging : return dotObj_nfa(myparsednfa, nfaname)
    return myparsednfa


# In[4]:

print('''You may use any of these help commands:
help(re2nfa)
''')


# In[ ]:





# coding: utf-8

# # A markdown for machines
# 
# One of the purposes of a Models of Computation course is to teach students some basic machine types. It is common practice to input these machines interactively using a graphical tool such as JFLAP, and to view their simulation results also in the same graphical environment.
# 
# Graphical interactions are powerful and intuitive. They provide powerful visual cues that tell a student how the machines "work" in the sense of chugging along, should they be built.
# 
# However, a __graphics-only__ presentation for a machine typically studied in such a course is woefully deficient in two ways:
# 
# 1. It does not really allow a user to write programs for these complex machines. Programs that are purely presented as pictures 
#  
#  a. quickly get cluttered
#  
#  b. quickly become a sphagetti of edges, circles, and edge labels that bump into other graphical elements
#  
# 2. It does not allow us to write comments. Without comments:
# 
#  a. Others (and even the original authors) will find it difficult to understand their construction
#  
#  b. Critical structures such as loops cannot be adequately documented, unless one has a textual representation
#  
# In a nutshell, leaving complex machine constructions as pictures alone can lead to constructions that go wrong more often than they would emerge right. Even everyday things such as sending a machine description to someone becomes a chore. Automated grading is that much more clumsy: one needs the graphical environment around.
# 
# We prefer a textual input method for these machines, from which graphical drawings can be easily produced. More specifically, we devise a __markdown__ language for DFA, NFA, PDA and TM. Our language is called the "automd" language standing for "automata markdown".
# 
# A markdown approach has both advantages, namely:
# 
# * One gets the program in textual form with comments
# 
# * One can _also_ generate a drawing very easily, thus preserving most of the advantages (if not all) of a picture-only input method
# 
# * In future, we can convert our markdowns to inputs to programs such as JFLAP
# 
# In our tool suite, we don't have a full graphical simulation output at this point. However, we do provide sufficiently rich textual outputs that adequately capture simulations. (These facilities are easy to extend based on user-feedback.)
# 
# ## Markdown processing
# 
# We define a single function md2mc() with arguments to be elaborated soon, but basically being the markdown input. This function produces an internal representation for the described machine (as a Python dictionary). This representation can be rendered as a drawing as well as simulated. 
# 
# We now describe how these are accomplished. Examples may be found in Jupyter notes Drive_md2mc. We now informally describe our markdown grammar and also provide its formal BNF grammar. (Incidentally, the markdown compiler forms a fantastic example that is worth studying. It has a regular grammar, but we use context-free productions to easily handle its constructs.)
# 
# # Markdown grammar
# 

# # Markdown code structure

# In[1]:

from lex import lex
from yacc import yacc 

#=================================================================
# Maintain our own LINENO for error reporting 
# This is incremented by \n, and reset to -1 after successful parsing 
# "Successful parsing" also includes the case of matching an error token
#  (see the production rule p_you_are_hosed below)

LINENO   = -1  
reserved = {
   'NFA' : 'NFA', 
   'DFA' : 'DFA', 
   'PDA' : 'PDA', 
   'TM'  : 'TM' 
}
   
def t_ID(t):
    r'[a-zA-Z0-9#$%&()*+/=?@\[\\\]^_{}~]+'
    # Printable ASCII sans space,  quotations ` ' " and . : , ; - > < | !
    # See https://docs.python.org/3/howto/regex.html for Python Regex
    # See https://en.wikipedia.org/wiki/ASCII for printable ASCII
    t.type = reserved.get(t.value,'ID') # default is 'ID'
    return t

tokens = ['EPS', 'BLANK', 'COLON', 'COMMA', 'SEMICOLON', 'ARROW', 
          'OR', 'ID'] + list(reserved.values())

t_EPS    = r'\'\'|\"\"'  # No longer allowing @ as epsilon
t_BLANK  = r'.'   
t_COLON  = r'\:'
t_COMMA  = r'\,'
t_SEMICOLON = r'\;'
t_ARROW  = r'\-\>'
t_OR     = r'\|'

# Ignored characters
t_ignore = " \t"

def t_NEWLINE(t):
    r'\n+'
    global LINENO
    if LINENO==-1:
        LINENO = 2
    else:
        LINENO += 1
    t.lexer.lineno += t.value.count("\n")

# Strip user comments in input file, as described in
# http://www.eng.utah.edu/~cs3100/lectures/l14/ply-3.4/doc/ply.html
def t_COMMENT(t):
    r'\!\!.*'
    print("Got a Jove markdown comment")
    pass
    # No return value. Token discarded
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Build the lexer before calling yacc() below
# Feed the lexer into the parser (see below)
 


# ## Define data structures to hold semantic attributes

# In[2]:

#=================================================================
# Function default_line_attr() generates an empty attribute-structure
# that is filled while parsing.
#
# The 'NEED ORDER' below marks those entities that collect items
# from one line of markdown input HAVING TO preserve positional order.
#
# Example: in S : a,b ; c | d,e ; f -> G
#  we go  S : a,b;c -> G   and   S : d,e;f -> G .
# That is, "a goes with b and c", and not that "a goes with e and f".
#
# Since some entities demand order preservation, turn ALL of them into 
# lists, so that our coding becomes more uniform.

def default_line_attr():
    """Used in virtually all p_.. rules in the parser.
       ---
       Default empty attribute that can be populated as we parse.
       Here is how we fill the fields.
       
       For DFA, NFA, PDA, and TM:
       - The 'from' state goes into "FromState".
       - The 'to' states go into "ToStates".
       - The input Sigma or Eps go into "SigmaEps".
       
       For PDA and TM:
       - The input Gamma or Eps go into "GammaIn".
       - The output Gamma goes into "GammaOut".
       
       For PDA, note that GammaOut can have strings > 1 in len.
    """
    return {"FromState" : [], # Always singleton, per line of markdown
            "ToStates"  : [], # Singleton (per line of markdown) for DFA
            "GammaIn"   : [], # NEED ORDER; Single Gamma symbol or Eps
            "GammaOut"  : [], # NEED ORDER; Gamma STRING for PDA
            "HeadDirn"  : [], # NEED ORDER; Head direction STRING for TM
            "Q0"        : [], # This field ends up singleton (barring NFA)
            "F"         : [], # No restrictions
            "SigmaEps"  : []  # NEED ORDER; Eps not for DFA
           }

from functools import reduce
#=================================================================
# length_ok_input_items()
# * Sigma and Gamma_in must be of length <= 1
# * Gamma_out for PDA is allowed to be longer (multi-symbol push)
# * All other Gamma_out also of length <= 1
#
def length_ok_input_items(items):
    """Helper for union_line_attr_list_fld()
       ---
       Takes a list of items (grabbed from the attribute structure) and 
       ensures that the user input-items per markdown line are of length 
       1. This check is needed for Sigma, G_in, and G_out for TMs.  
       However, G_out for PDAs can be of any length, so this checks 
       skips PDA.
    """
    for item in items:
        if len(item) != 1 and item != "":
            print("Erroneous item -> ", item, " <- during parsing : ")
            return False
    return True
    
def union_line_attr_list_fld(line_attr_list, field, mc_type):
    """Helper for get_machine_components()
       ---
       Given a line_attr list and the name of a field, and a
       machine type, check for errors, and then obtain the 
       union of those fields if all line_attr list members are OK.
    """
    #-- Error checks.
    assert(mc_type in {'DFA','NFA','PDA','TM'}
          ),"Error: Illegal machine type given: " + mc_type
    for line_attr in line_attr_list:
        G_in  = line_attr["GammaIn"]
        G_out = line_attr["GammaOut"]
        Sigma = line_attr["SigmaEps"]
        #
        #-- Epsilon-related checks. For TM, we customize error message...
        #
        if mc_type=='DFA':
            assert(set({"''",'""'})
                   & set(Sigma) == set({})
                  ),"Error: DFA with an epsilon input illegal."
        if mc_type=='TM':
            assert(set({"''",'""'}) 
                   & set(G_in) == set({})
                ),"Error: TM with epsilon input illegal. You meant '.'?"
            assert(set({"''",'""'}) 
                   & set(G_out) == set({})
                ),"Error: TM with epsilon output illegal. You meant '.'?"            
        #
        #-- Sigma, G_in and G_out related length checks
        #-- for all items present, their lengths must be 1

        assert(length_ok_input_items
               (Sigma)
              ),"Error: Sigma contains a string longer than 1"
            
        assert(length_ok_input_items
               (G_in)
              ),"Error: G_in contains a string longer than 1"
        
        if mc_type != 'PDA':
            assert(length_ok_input_items
                   (G_out)
                  ),"Error: G_out contains a string longer than 1"
                
        #--end for

        
    #-- All checks pass. The reduce below might be fused with the for 
    #   above...
    return reduce(lambda x,y: x+y, # list concat
                  map(lambda line_attr: line_attr[field], line_attr_list),
                  [])

#=================================================================

from itertools import product

def extend_rsltdict(D, key, val, Extend=False):
    """Helper for form_delta()
       ---
       Given a result dictionary D, extend it, depending on
       the setting of Boolean Extend. For some dictionaries,
       duplicates mean "extend"; for others, that means error.
       This is a crucial helper used by "form_delta".
    """
    if Extend:
        if key in D:
            D[key] = D[key] | set({ val })
        else:
            D[key] = set({ val })
    else:
        assert(key not in D
              ),("Error: Duplicate map at key " + str(key) + 
                 "; duplicates: " + str(D[key]) + " and " + str(val)
                )
        D[key] = val # don't make a set
    return D
    
    
def form_delta(line_attr_list, mc_type):
    """Helper for get_machine_components()
       ---
       Given the machine type, cull the needed info from line_attr_list
       and form the delta appropriate to the machine type.
       
       There are obviously many corner cases here! We discuss each 
       separately, taking pithy made-up examples from 
       DFA, NFA, PDA, and TM.  
       
       DFA/NFA: Given I : a | a -> P  \n  I : a -> Q, 
                we form 
                (I,a) -> {P,Q}
                
                At the end, err for DFA saying we can't jump to 
                multiple targets. I.e., DFA can't jump to two states on 
                one input. (extend_rsltdict with Extend=False).
                
       PDA: Given I : a,b ; c | a,b ; d -> P,Q \n I : a,b ; r -> R,
            we form 
            (I, a, b) : { (c,P), (c,Q), (d,P), (d,Q), (r,R) } by
            keeping a dict entry for (I, a, b), and extending that.
                
       TM:  Given I : a; b,c | a; b,d -> P,Q \n I : a; b,r -> R,
            we form 
            (I, a) : { (b,c,P), (b,c,Q), (b,d,P), (b,d,Q), (b,r,R) } 
            by keeping a dict entry for (I, a, b), and extending that.
    """
    rslt_dict = dict({ })
    #--
    for attr in line_attr_list:
        from_states = attr["FromState"]
        assert(len(from_states)==1
              ),"Error: More than one 'from-state' per markdown line."
        from_state  = from_states[0]
        #
        sigeps_list = attr["SigmaEps"]
        G_in        = attr["GammaIn"]
        G_out       = attr["GammaOut"]
        to_states   = attr["ToStates"]
        head_dirn   = attr["HeadDirn"]
        #
        if mc_type=='PDA':
            assert(len(G_in)==len(G_out)
                ),"Error: PDA G_in/G_out lists are unequal in length."
            assert(len(sigeps_list)==len(G_out)
                ),"Error: PDA SigmaEps/G_out lists are unequal in length."                
            #
            ziplab         = list(zip(sigeps_list, G_in, G_out))
        elif mc_type=='TM':
            assert(len(G_in)==len(G_out)
                ),"Error: TM G_in/G_out lists are unequal in length."
            assert(len(head_dirn)==len(G_out)
                ),"Error: TM HeadDirn/G_out lists are unequal in length."
            #
            ziplab         = list(zip(G_in, G_out, head_dirn))
        else:
            assert(mc_type in {'NFA','DFA'}
                  ),"Error: Unknown machine type: " + mc_type
            ziplab         = sigeps_list
        
        # List of zipped labels paired with next states.
        # From this, we have to form the transition-table key/value pairs.
        # We call zipped labels paired with next states "zl_nxtst"
        # and a list of them as l_zl_nxtst
                 
        l_zl_nxtst = product(ziplab, to_states)
                 
        # Now, we elaborate on l_zl_nxtst for various machine types:
        #
        # D/NFA: [ (in1,P), (in1,Q), (in2,Q) ]
        # PDA  : [ ((in1, si1, sp1),P), ((in1,si1,sp2),P), 
        #           ((in1,si2,sp3),Q) .. ]
        # TM   : [ ((ti1, to1,dir1),P), ((ti1,to2,dir2),P), 
        #           ((ti2,to3,dir3),Q) .. ]
        #
        for zl_nxtst in l_zl_nxtst:
            if mc_type=='DFA':
                # Prevent nondeterminism
                (inpsym, nxtst) = zl_nxtst
                rslt_dict = extend_rsltdict(rslt_dict,
                                            (from_state, inpsym),
                                            nxtst,
                                            Extend=False)
            elif mc_type=='NFA':
                # Allow nondeterminism                
                (inpsym, nxtst) = zl_nxtst
                rslt_dict = extend_rsltdict(rslt_dict,
                                            (from_state, inpsym),
                                            nxtst,
                                            Extend=True)
            elif mc_type=='PDA':
                # Allow nondeterminism
                ((inpsym, stkpop, stkpush), nxtst) = zl_nxtst
                rslt_dict = extend_rsltdict(rslt_dict,
                                            (from_state, inpsym, stkpop),
                                            (nxtst, stkpush),
                                            Extend=True)
            else:
                assert(mc_type=='TM'
                    ),"Error: Illegal machine type supplied: " + mc_type
                ((tapein, tapeout, dirn), nxtst) = zl_nxtst
                rslt_dict = extend_rsltdict(rslt_dict,
                                            (from_state, tapein),
                                            (nxtst, tapeout, dirn),
                                            Extend=True)
    #--
    return rslt_dict


#=================================================================

def get_machine_components(line_attr_list, mc_type):
    """Used in four top-level parser rules, namely
       p_dfa_md(), p_nfa_md(), p_pda_md() and p_tm_md()
       ---
       Given a list of line_attr dict items and mc_type
       (which is one of 'DFA','NFA','PDA','TM'),
       extract these components:
       1) Q by unioning FromState and ToStates
       2) Gamma by unioning GammaIn symbols and GammaOut strings
       3) Q0 by unioning all Q0
       4) F by unioning all F
       5) Sigma by unioning all the SigmaEps sets, removing Eps
       6) Eps by taking Eps from the set in 5

       The formation of Delta is postponed till now. This is because
       till now, we do not really know what machine-type we are dealing
       with. So we will have to approach that within 
       union_line_attr_list_fld.
    """
    # Given that we turned default_line_attr to all lists, we need to "unique"
    # some of the lists formed here. We use list(set(L)) as we don't care
    # about the order of many of these lists.
    #
    From_s = union_line_attr_list_fld(line_attr_list, 
                                      "FromState", mc_type)
    To_s   = union_line_attr_list_fld(line_attr_list, 
                                      "ToStates", mc_type)
    #    
    G_in    = union_line_attr_list_fld(line_attr_list, 
                                       "GammaIn", mc_type)
    G_out   = union_line_attr_list_fld(line_attr_list, 
                                       "GammaOut", mc_type)
    #
    Dirn    = union_line_attr_list_fld(line_attr_list, 
                                       "HeadDirn", mc_type)                                  
    #    
    Q0     = union_line_attr_list_fld(line_attr_list, 
                                      "Q0", mc_type)
    #    
    F      = union_line_attr_list_fld(line_attr_list, 
                                      "F", mc_type)
    #    
    Sigma  = union_line_attr_list_fld(line_attr_list, 
                                      "SigmaEps", mc_type)

    Delta = form_delta(line_attr_list, mc_type)

    return (set(From_s), set(To_s),
            set(G_in),   set(G_out),
            set(Q0),     set(F),
            set(Sigma),  set(Dirn),
            Delta)
#=================================================================
# Some simple extractors 

def is_init_st(id):
    """Used in p_one_line()
       ---
       Checks if id begins with i or I.
    """
    return id[0] in {'i','I'}


def is_fin_st(id):
    """Used in p_one_line()
       ---
       Checks if id begins with f or F or if or IF.
    """
    return ( (id[0] in {'f','F'})
             or ((len(id) > 1) and (id[0:2] == 'if' or id[0:2] == 'IF')) 
           )


# ## Define the parsing rules now
# 
# The first production is the "top-level symbol"

# In[3]:

#=================================================================
# Rules for DFA, NFA, PDA, TM + error!
# From the PLY manual: http://www.dabeaz.com/ply/ply.html#ply_nn28
# Normally, the first rule found in a yacc specification defines the
# starting grammar rule (top level rule). To change this,
# simply supply a start specifier in your file.Rtt

def p_you_are_hosed(t):
    '''md : error'''
    print("Your are hosed due to a syntax error!")
    global LINENO
    LINENO = -1 # restore sanity wrt future reporting of errors
    t[0] = ('ERROR', 'ERROR')
    
def p_dfa_md(t):
    '''md : DFA lines'''
    print("Parsed DFA keyword")
    mc = get_machine_components(t[2], 'DFA')
    (From_s, To_s,
     G_in,   G_out,
     Q0,     F,
     Sigma,  Dirn, Delta) = mc
    assert(len(Q0) == 1
    ),"Error: DFA with " +str(len(Q0))+ " starting states is illegal."
    global LINENO
    LINENO = -1 # restore for next error processing
    t[0] = ('DFA', mc)
    
def p_nfa_md(t):
    '''md : NFA lines'''
    global LINENO
    LINENO = -1 # restore for next error processing
    t[0] = ('NFA', get_machine_components(t[2], 'NFA'))

def p_pda_md(t):
    '''md : PDA lines'''
    mc = get_machine_components(t[2], 'PDA')
    (From_s, To_s,
     G_in,   G_out,
     Q0,     F,
     Sigma,  Dirn, Delta) = mc
    assert(len(Q0) == 1),"PDA with more than one starting state illegal."    
    global LINENO
    LINENO = -1 # restore for next error processing
    t[0] = ('PDA', mc)
    
def p_tm_md(t):
    '''md : TM lines'''
    mc = get_machine_components(t[2], 'TM')
    (From_s, To_s,
     G_in,   G_out,
     Q0,     F,
     Sigma,  Dirn, Delta) = mc
    assert(len(Q0) == 1
          ),"TM with more than one starting state illegal."
    global LINENO
    LINENO = -1 # restore for next error processing
    t[0] = ('TM', mc)

#=================================================================
# lines for all machine types
    
def p_lines1(t):
    '''lines : one_line'''
    t[0] = [ t[1] ] # One line's attribute is a dict
    
def p_lines2(t):
    '''lines : one_line lines'''
    one_line_attr = [ t[1] ]
    lines_attr    = t[2]
    t[0] = one_line_attr + lines_attr # List of line attrs

def p_one_line(t):
    '''one_line : state COLON labels ARROW states'''
    print("Parsed one line of Jove MD code, involving tokens COLON and ARROWS and other things in an MD line")
    lineattr  = default_line_attr()
    lineattr["FromState"] = t[1]
    lineattr["ToStates"]  = t[5]
    states_in_line        = t[1] + t[5]
    #
    lineattr["Q0"]        = list(filter(is_init_st, states_in_line))
    lineattr["F"]         = list(filter(is_fin_st, states_in_line))
    #
    lineattr["SigmaEps"]  = t[3]["SigmaEps"]
    #
    lineattr["GammaIn"]   = t[3]["GammaIn"]
    lineattr["GammaOut"]  = t[3]["GammaOut"]
    lineattr["HeadDirn"]  = t[3]["HeadDirn"]    
    #
    t[0] = lineattr

def p_state(t):
    '''state : ID'''
    t[0] = [ t[1] ]

def p_states1(t):
    '''states : state'''
    t[0] = t[1] 
    
def p_states2(t):
    '''states : state COMMA states'''
    t[0] = t[1] + t[3]

def p_labels1(t):
    '''labels : one_label'''
    t[0] = t[1]
    
def p_labels2(t):
    '''labels : one_label OR labels'''
    # Combine SigmaEps, GammaIn, GammaOut, HeadDirn labels 
    # component-wise
    L1 = t[1]
    Ls = t[3]
    lineattr = default_line_attr()
    lineattr.update({ "SigmaEps": L1["SigmaEps"] + Ls["SigmaEps"] })                                   
    lineattr.update({ "GammaIn" : L1["GammaIn"]  + Ls["GammaIn"]  })
    lineattr.update({ "GammaOut": L1["GammaOut"] + Ls["GammaOut"] })
    lineattr.update({ "HeadDirn": L1["HeadDirn"] + Ls["HeadDirn"] })
    t[0] = lineattr

# One label is a big deal. It deals with labels for DFA, NFA, PDA, or TM
# A label for DFA and NFA are just ID_or_EPS
# A label for a PDA is ID_or_EPS , One_gamma ; Many_Gammas
# A label for a TM is  ID_or_B ; ID_or_B , ID  where the last ID is L,R,S
def p_one_label1(t):
    '''one_label : ID_or_EPS_or_B'''
    t[0] = t[1]
    
def p_ID_or_EPS_or_B(t):
    '''ID_or_EPS_or_B : ID
                      | EPS
                      | BLANK'''
    id = t[1]
    #--sanitize forms of epsilon after parsing
    if id=='""':
        id = ""
    elif id=="''":
        id = ''
    #--
    print("Got one label of a DFA, which is an ID, that being", id)
    lineattr = default_line_attr()
    lineattr.update({ "SigmaEps" : [ id ] })
    t[0] = lineattr

def p_one_label2(t):
    '''one_label : ID_or_EPS_or_B COMMA ID_or_EPS_or_B SEMICOLON ID_or_EPS_or_B'''
    # t[1] is input symbol for PDA, that would already have 
    # climbed into SigmaEps.
    #
    # t[3] is stack-pop symbol for PDA
    # t[5] is stack-push string for PDA
    #
    # We can take t[1] and update it to carry
    # GammaIn coming in via t[3], and
    # GammaOut coming in via t[5].
    #
    lineattr = t[1]
    lineattr.update({ "GammaIn" : t[3]["SigmaEps"]  })
    lineattr.update({ "GammaOut": t[5]["SigmaEps"] })
    t[0] = lineattr

def dirn_is_ok(dirn):
    """Ensure that the TM head direction is OK.
    """
    return dirn in set({'L','R','S'})

def p_one_label3(t):
    '''one_label : ID_or_EPS_or_B SEMICOLON ID_or_EPS_or_B COMMA ID_or_EPS_or_B'''        
    # t[1] is input symbol for TM, that would already have 
    # climbed into SigmaEps.
    #
    # It also belongs to GammaIn, so fix that up too.
    #
    # t[3] is tape-write symbol for TM
    # t[5] is direction for TM
    #
    # We can take t[1] and update it to carry
    # GammaOut coming in via t[3].
    # We can check for t[5] being L,R,S.
    #
    lineattr = t[1] # Contains the SigmaEps attribute coming in
    lineattr.update({ "GammaIn" : lineattr["SigmaEps"] }) #shift to G_in
    lineattr.update({ "GammaOut": t[3]["SigmaEps"] })     #shift to G_out
    #                                   
    dirn_list = t[5]["SigmaEps"]
    assert(len(dirn_list)==1), "Direction specifier set has length > 1"
    assert(dirn_is_ok(dirn_list[0])),"Illegal head-direction in TM!"
    #                                                                      
    lineattr.update({ "HeadDirn" : dirn_list })
    t[0] = lineattr
    
#=================================================================
    
def p_error(t):
    print("Syntax error at '%s'" % t.value, " on line ", LINENO)
    
#=================================================================
# End of all parsing rules


# # md2mc():  Function exported out of this module

# In[4]:

from functools import reduce
def md2mc(src="None", fname="None"):
    """md2mc converts a markdown source to a machine (mc).
    
       One can feed the markdown in three ways, shown via 
       pseudo-examples:
       
       1) md2mc()
       
          It means you will provide a file-name
          (you will be prompted for one). Then the markdown is read from
          that file. 
          
       2) md2mc(src="<any string S other than 'File'>")
       
          S is now taken as the markdown string and parsed. This is 
          bound to be a multi-line file. 
          
          There is a Jupyter bug that if the parser (or any process) 
          consuming a multi-line input throws an exception, you will get 
          a strange error message: 
          ERROR:root:An unexpected error occurred while tokenizing input
          Ignore it please, and instead spend your time fixing the 
          markdown input. See for details:
          https://github.com/ipython/ipython/issues/6864
          
          
       3) md2mc(src="File", fname="<your file name path>")
       
          Obviously, you should not be feeding a markdown with contents 
          "File". It is not legit markdown syntax. So if src="File", 
          then fname is taken to be the path-name to a file that is 
          opened and read.
        
       In all cases, the returned result is a machine structure (dict).
    """
    if (src=="None"):
        mdstr = open(input('File name ='), 'r').read()
    elif (src=="File"):
        mdstr = open(fname).read()
    else:
        mdstr = src
    myparser = yacc()
    mdlexer = lex()   # Build lexer custom-made for markdown
    rslt = myparser.parse(mdstr, lexer=mdlexer) # feed into parse fn
    #--
    # Now, based on machine type, return correct machine object.
    #--
    (machine_type,
     (From_s, To_s,
      G_in,   G_out,
      Q0,     F,
      Sigma,  Dirn, Delta)) = rslt
    #--
    #-- for now, make struct right here; later call right maker
    #--
    if machine_type != 'NFA':
        assert(len(Q0)==1)
        q0 = list(Q0)[0]
    if machine_type=='DFA':
        return {"Q"    : From_s | To_s,
                "Sigma": Sigma,
                "Delta": Delta,
                "q0"   : q0,
                "F"    : F}
    
    elif machine_type=='NFA':
        return {"Q"    : From_s | To_s,
                "Sigma": Sigma - {'',""},
                "Delta": Delta,
                "Q0"   : Q0,
                "F"    : F}
    
    elif machine_type=='PDA':
        G_out_set = reduce(lambda x,y: x|y, map(set, G_out), set({}))
        return {"Q"    : From_s | To_s,
                "Sigma": Sigma - {'',""},
                "Gamma": (G_in | G_out_set | {'#'} | Sigma) - {'',""},
                "Delta": Delta,
                "q0"   : q0,
                "z0"   : '#',   # Hash-mark is the new "z0" for a PDA!
                "F"    : set(F)}
    else: 
        assert(machine_type=='TM')
        return {"Q"    : From_s | To_s,
                "Sigma": Sigma - {'',"",'@','.'},
                "Gamma": (G_in | G_out | {'.'} | Sigma) - {'',"",'@'},
                "Delta": Delta,
                "q0"   : q0,
                "B"    : '.',
                "F"    : F}        
        
    return rslt
    
#=================================================================


# In[5]:

print('''You may use any of these help commands:
help(md2mc)
.. and if you want to dig more, then ..
help(default_line_attr)
help(length_ok_input_items)
help(union_line_attr_list_fld)
help(extend_rsltdict)
help(form_delta)
help(get_machine_components)
''')


# This finishes our description of the md2mc module.

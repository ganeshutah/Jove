
# coding: utf-8

# # These are definitions wrt 'dot'
# 
# ```
# Functions of interest for outside are below:
# 
# D : DFA
# N : NFA
# 
# def dot_dfa(D, STATENAME_MAXSIZE):
# def dotObj_dfa(D, dfaName='do_', STATENAME_MAXSIZE):
# def dot_dfa_w_bh(D, STATENAME_MAXSIZE):
# def dotObj_dfa_w_bh(D, dfaName='do_', STATENAME_MAXSIZE):
# def dot_nfa(N):
# def dotObj_nfa(N, nfaName = 'NO_'):
# 
# ```

# In[ ]:


from jove.SysConsts           import *
from jove.StateNameSanitizers import *
from jove.SystemImports       import *
from jove.TransitionSelectors import *
from jove.ShrinkStates        import shrink_dfastates
from jove.ShrinkStates        import shrink_nfastates

#=== Consistency Checkers : do that before generating dot! ===

#-- for DFA


def is_consistent_dfa(D):
    """In : DFA D
       Out: Boolean (Are D's traits consistent?)
    """
    return (is_partially_consistent_dfa(D) and
    set(fn_dom(D["Delta"])) == set(product(D["Q"], D["Sigma"])))  

def is_partially_consistent_dfa(D):
    """In : DFA D
       Out: Boolean (are D's traits are partially consistent?)
    """
    fn_dom_Delta   = set(fn_dom(D["Delta"]))
    fn_range_Delta = set(fn_range(D["Delta"])) 
   
    Q     = D["Q"]
    Sigma = D["Sigma"]
    Delta = D["Delta"]
    q0    = D["q0"]
    F     = D["F"]
    # - Obsolete as of 6/12/17: Assume existing BH means BH
    # For a DFA with a truly partial Delta function, it must not 
    # already have a state 'BH'. This is because we will be 
    # introducing a new state called 'BH' and we don't want it
    # to clash with a similarly named state that already exists.
    #
    # - if fn_dom_Delta < set(product(Q,Sigma)):
    # -    assert(not('BH' in Q))
    return (Q != {}              and
            Sigma != {}          and
            fn_dom_Delta   <= set(product(Q,Sigma)) and
            fn_range_Delta != {} and
            fn_range_Delta <= Q  and
            q0 in Q              and
            F <= Q)  

#-- for NFA

def is_consistent_nfa(N):
    """In : NFA N
       Out: Boolean (Given NFA's traits consistent?)
    """
    fn_dom_Delta   = set(fn_dom(N["Delta"]))   # Set of states
    fn_range_Delta = list(fn_range(N["Delta"]))# List of sets of states
    Q     = N["Q"]
    Sigma = N["Sigma"]
    Delta = N["Delta"]
    Q0    = N["Q0"]
    F     = N["F"]
    Sigma_w_Eps = (Sigma | set({""})) # Extended Alphabet

    # Are all NFA transition targets (sets of states) in Q?
    # True added to reduce in case fn_range_Delta is empty
    fn_range_Check = reduce(lambda x,y: x and y, 
                            [x <= Q for x in fn_range_Delta], True)
    
    return (Q != {}          and
            Sigma != {}      and
            "" not in Sigma  and
            fn_dom_Delta <= set(product(Q, Sigma_w_Eps)) and
            fn_range_Check   and
            Q0 <= Q          and
            F <= Q)
    # Notice that Q0 is a subset of Q
    # This is as per the new defn of NFA starting from
    # a set of starting states, namely Q0.

#-- for GNFA

def is_consistent_gnfa(G):
    """In : GNFA G
       Out: Boolean (Given GNFA's traits consistent?)
    """
    # Set of states
    fn_dom_Delta   = set(map(trSrc, fn_trans(G["Delta"])))
    fn_range_Delta = list(fn_range(G["Delta"]))# List of sets of states
    Q     = G["Q"]
    Delta = G["Delta"]
    Q0    = G["Q0"]
    F     = G["F"]

    # Are all GNFA transition targets (sets of states) in Q?
    # True added to reduce in case fn_range_Delta is empty
    fn_range_Check = reduce(lambda x,y: x and y, 
                            [x <= Q for x in fn_range_Delta], True)
    
    return (Q != {}           and
            fn_dom_Delta <= Q and
            fn_range_Check    and
            Q0 <= Q           and
            F <= Q)

#-- for PDA

def chk_consistent_pda(P):
    """Given a PDA P, check whether it is consistent.
    """
    Q     = P["Q"]
    Sigma = P["Sigma"]
    Gamma = P["Gamma"]
    Delta = P["Delta"]
    q0    = P["q0"]
    z0    = P["z0"]
    F     = P["F"]
    assert(Q != set({})),   "PDA being made with an empty Q."
    assert(Sigma != set({})), "PDA being made with an empty Sigma."
    
    if (z0 != ""):
        assert(z0 in Gamma),"PDA's z0 symbol isn't present in its Gamma."
        assert(Sigma < Gamma),"PDA's Sigma not properly contained in Gamma."
    else:
        assert(Sigma <= Gamma),"PDA's Sigma not contained in Gamma."
    assert(z0 not in Sigma),"PDA's Sigma mustn't contain its z0 symbol."
    assert("" not in Gamma),"PDA's Gamma contains Epsilon; it mustn't"
    assert(q0 in Q),        "PDA's q0 is not within its Q."
    assert(F <= Q),         "PDA's F is not contained within its Q."
    Delta_trans = fn_trans(Delta)
    for trans in Delta_trans:
        src = trSrc(trans)
        assert(src in Q), "Delta has illegal 'from' state."
        symb = trSymb(trans)
        assert(
            (symb in Gamma) or (symb == "")
        ), "Delta has illegal input symbol."
        stksymb = trStkSymb(trans)
        assert(
            (stksymb in Gamma) or (stksymb == "")
        ), "Delta has illegal stack symbol."
        for trg in trTrg(trans):
            assert(
                pdaNstate(trg) in Q
            ), "PDA jumps to illegal state in its Delta."
            nstkstr = pdaNstkStr(trg)
            assert(
                type(nstkstr) == str
            ), "PDA's 'new stack string' isn't a string."
            set_of_pushes = set(nstkstr)
            assert(
                set_of_pushes <= Gamma
            ), "PDA pushes illegal symbol into its stack." 

#-- for TM

def chk_consistent_tm(T):
    "Given a TM T, check whether it is consistent."
    Q     = T["Q"]
    Sigma = T["Sigma"]
    Gamma = T["Gamma"]
    Delta = T["Delta"]
    q0    = T["q0"]
    B     = T["B"]
    F     = T["F"]
    assert(Q != set({})),   "TM being made with an empty Q."
    assert(Sigma != set({})), "TM being made with an empty Sigma."
    assert(Sigma < Gamma),  "TM's Sigma isn't contained in its Gamma."
    assert(B in Gamma),     "TM's blank symbol isn't present in its Gamma."
    assert(B not in Sigma), "TM's Sigma mustn't contain its blank symbol."
    assert("" not in Sigma),"TM's Sigma contains Epsilon; it mustn't"
    assert(q0 in Q),        "TM's q0 is not within its Q."
    assert(F <= Q),         "TM's F is not contained within its Q."
    Delta_trans = fn_trans(Delta)
    for trans in Delta_trans:
        src = trSrc(trans)
        assert(src in Q), "Delta has illegal 'from' state."
        symb = trSymb(trans)
        assert(symb in Gamma), "Delta has illegal tape symbol."
        for trg in trTrg(trans):
            assert(
                tmNstate(trg) in Q
            ), "TM jumps to illegal state in its Delta."
            assert(
                tmNtpSym(trg) in Gamma
            ), "TM writes illegal tape symbol in its Delta."
            assert(
                tmNdir(trg) in {"L","R","S"}
            ), "TM has illegal direction in its Delta." 
            
#=== DFA-related dot bashers ===

def dot_dfa(D, STATENAME_MAXSIZE=20):
    """In : D (DFA : partially consistent)
            STATENAME_MAXSIZE : number
       Out: dot representation (string)
       Generate a dot string representing the automaton. 
       Suppress "black-hole states". 
    """
    assert(is_partially_consistent_dfa(D))
    D           = shrink_dfastates(D, STATENAME_MAXSIZE)
    hdr         = prDotHeader()
    nodeDefs    = prNodeDefs(D, isNotBH) # Show isNotBH states
    orientation = prOrientation()
    # Show edge if src AND trg are isNotBH
    edges       = prEdges(D, isNotBH)
    closing     = prClosing()
    return hdr + nodeDefs + orientation + edges + closing

def dotObj_dfa(D, FuseEdges = False, dfaName='do_', STATENAME_MAXSIZE=20):
    """In : D1 (DFA : partially consistent)
            dfaName (string)
            STATENAME_MAXSIZE : number
       Out: A dot object. 
       Generate a dot object representing the automaton. 
       Suppress "black-hole states".       
    """
    assert(is_partially_consistent_dfa(D))
    D           = shrink_dfastates(D, STATENAME_MAXSIZE)
    if dfaName == 'do_':
        dfaName = dfaName + NxtStateStr()
    dotObj1     = Digraph(comment=dfaName)  
    dotObj1.graph_attr['rankdir'] = 'LR'
    # Show isNotBH states
    dotObj2     = addNodeDefs(D, dotObj1, isNotBH) 
    # Show edge if src AND trg are isNotBH   
    dotObj3     = addEdges(D, dotObj2, FuseEdges, isNotBH)          
    return dotObj3

def dot_dfa_w_bh(D, STATENAME_MAXSIZE=20):
    """In : D (DFA : partially consistent)
            STATENAME_MAXSIZE : number
       Out: dot representation (string)
       Generate a dot string representing the automaton. 
       Do not suppress "black-hole states". 
    """ 
    assert(is_partially_consistent_dfa(D))
    D           = shrink_dfastates(D, STATENAME_MAXSIZE)
    hdr         = prDotHeader()
    nodeDefs    = prNodeDefs(D, lambda x: True) # Show all nodes
    orientation = prOrientation()
    edges       = prEdges(D, lambda x: True)    # Show all edges  
    closing     = prClosing() 
    return hdr + nodeDefs + orientation + edges + closing

def dotObj_dfa_w_bh(D, FuseEdges = False, dfaName='do_', STATENAME_MAXSIZE=20):
    """In : D (DFA : partially consistent, states shrunk)
            dfaName (string)
            STATENAME_MAXSIZE : number
       Out: A dot object. 
       Generate a dot object representing the automaton. 
       Do not suppress "black-hole states".       
    """
    assert(is_partially_consistent_dfa(D))
    D       = shrink_dfastates(D, STATENAME_MAXSIZE)
    if dfaName == 'do_':
        dfaName = dfaName + NxtStateStr()
    dotObj1 = Digraph(comment=dfaName)   
    dotObj1.graph_attr['rankdir'] = 'LR'
    dotObj2 = addNodeDefs(D, dotObj1, lambda x: True)# Show all nodes  
    dotObj3 = addEdges(D, dotObj2, FuseEdges, lambda x: True)   # Show all edges
    return dotObj3

def prDotHeader():
    """In : None
       Out: dot string for dot-file header.
    """
    return (
           'digraph G {\n'    + 
           '/* Defaults */\n' + 
           'fontsize = 12;\n' + 
           'graph [rankdir=LR]\n' )

def prFinalNodeName(q):
    """In : q (state : string)
       Out: dot string (string)
       Return dot string for generating final state (double circle)
    """
    return dot_san_str(q) + '[shape=circle, peripheries=2];'

def prNodeDefs(D, pred): 
    """In : D (DFA : partially consistent)
            pred (predicate to keep non-final nodes.)
       Out: dot string with states passing pred represented.
    """
    nodescmt       = '/* Node definitions */\n'
    emptystate     = '"" [shape=plaintext];\n'
    nonfinalstates = "".join([prNonFinalNodeName(q) 
                             for q in (D["Q"] - D["F"]) if pred(q)] )
    # Final state won't be black-hole!
    finalstates    = "".join([prFinalNodeName(q) 
                             for q in D["F"]])  
    return nodescmt + emptystate + nonfinalstates + finalstates

def prOrientation():
    """In : None
       Out: Generate dot string for orientation.
    """
    return '\n/* Orientation */\n' + 'orientation = portrait;\n' 

def prNonFinalNodeName(q):
    """In : q (state : string)
       Out: dot string representing state q as single circle.
    """
    return dot_san_str(q) + '[shape=circle, peripheries=1];\n'

def prEdges(D, pred):
    """In : DFA D (partially consistent)
            pred (predicate, filter to keep states)
       Out: dot str containing DFA edges q->q' if pred(q) and pred(q').
    """
    cmt       = '/* The graph itself */ \n'              
    initedge  = '""  -> ' + dot_san_str(D["q0"]) + ";\n"
    listedges = [ dot_san_str(trSrc(trans)) + ' -> ' +  
                  dot_san_str(trTrg(trans)) + '[label="' + 
                  dot_san_str(trSymb(trans)) +  '"]; \n' 
                  for trans in fn_trans(D["Delta"]) 
                  if pred(trSrc(trans) and pred(trTrg(trans))) ]
    strlistedges = "".join(listedges)
    return cmt + initedge + strlistedges

def prClosing():
    """In : None
       Out: Dot-file closing (string)."""
    return (
           "\n}\n/*www.graphviz.org/Documentation/dotguide.pdf*/\n"+\
           "     /*graphviz.readthedocs.io/en/latest/manual.html*/\n" 
    )
        
def addNodeDefs(D, dotObj, pred): 
    """In : D : (DFA : partially consistent)
            dotObj : (dot object being populated)
            pred : predicate filter to keep non-final nodes.
       Out: dot object with nodes added.
    """ 
    emptyNode      = dotObj.node("EMPTY", "", shape="plaintext") 
    
    # Filter non-final nodes as per filter
    for q in (D["Q"] - D["F"]):
        if pred(q):
            dotObj.node(dot_san_str(q), dot_san_str(q), 
                        shape = "circle", peripheries = "1")
    
    # Don't subject nodes in F to predicate filter
    for q in D["F"]:
        dotObj.node(dot_san_str(q), dot_san_str(q), 
                    shape = "circle", peripheries = "2")
        
    return dotObj

def addEdges(D, dotObj, FuseEdges, pred):
    """In : DFA D (partially consistent)
            dotObj (dot object being populated)
            pred (predicate, filter to keep states)
       Out: dot object. Keep DFA edges q->q' if pred(q) & pred(q')
    """
    dotObj.edge("EMPTY", dot_san_str(D["q0"]))
    dotAl = []
   
    for trans in fn_trans(D["Delta"]):
        if pred(trSrc(trans)) and pred(trTrg(trans)):
             '''
             dotObj.edge(dot_san_str(trSrc(trans)), 
                         dot_san_str(trTrg(trans)), 
                         label = dot_san_str(trSymb(trans)) )
             '''
             dotAl += [ ((dot_san_str(trSrc(trans)),
                          dot_san_str(trTrg(trans))),
                         dot_san_str(trSymb(trans))) ]
    if FuseEdges:
        dotAl = fuseDotAl(dotAl)
        
    for ((s1,s2), lab) in dotAl:
        dotObj.edge(s1,s2, label = "{} ".format(lab))
        
    return dotObj

#=== NFA-related dot bashers ===

def dot_nfa(N, visible_eps=False):
    """In : N (NFA : consistent)
       Out: dot representation (string)
       Generate a dot string representing the NFA. 
    """
    assert(is_consistent_nfa(N))
    N           = shrink_nfastates(N)
    hdr         = prDotHeader()       # Same header would do
    nodeDefs    = prNFANodeDefs(N)
    orientation = prOrientation()
    edges       = prNFAEdges(N, visible_eps)
    closing     = prClosing()
    return hdr + nodeDefs + orientation + edges + closing


def prNFANodeDefs(N): 
    """In : N (NFA : consistent)
       Out: dot string of node definitions.
    """
    nodescmt       = '/* Node definitions */\n'
    emptystate     = '"" [shape=plaintext];\n'
    nonfinalstates = "".join([prNonFinalNodeName(q) 
                              for q in (N["Q"] - N["F"]) ])
    finalstates    = "".join([prFinalNodeName(q) 
                              for q in N["F"]])
    return nodescmt + emptystate + nonfinalstates + finalstates

def prDotHeader():
    """In : None
       Out: dot string for dot-file header.
    """
    return     ('digraph G {\n'    +
                '/* Defaults */\n' + 
                'fontsize = 12;\n' +
                'graph [rankdir=LR]\n'
               )

def ShowEps(s, visible_eps):
    """Show Epsilons as '@' in printouts if visible_eps
       is set. Else suppress Epsilons (edges will carry no
       labels then.)
    """
    if (s==""):
        if visible_eps:
            return '@'
        else:
            return "''"  # Was @ once upon a time!
    else:
        return s

def prNFAEdges(N, visible_eps):
    """In : N (NFA that is consistent)
       Out: Dot string of NFA edges. 
    """
    cmt      = '/* The graph itself */'
    
    initedge = "" # build up from here
    for q0 in N["Q0"]:
        initedge = (initedge        + 
                    '""  -> '       + 
                    dot_san_str(q0) + 
                    ";\n" 
                   )
    
    listedges = ""
    for trans in fn_trans(N["Delta"]):
        for nxt_state in trTrg(trans):
            listedges += (dot_san_str(trSrc(trans)) +
                          ' -> '                    + 
                          dot_san_str(nxt_state)    +
                          '[label="'                +                         
                dot_san_str(ShowEps(trSymb(trans),visible_eps))+  
                          '"];'
                         )
    return cmt + initedge + listedges

def prFinalNodeName(q):
    """In : state q
       Out: dot string for a double-circle.
    """
    return dot_san_str(q) + '[shape=circle, peripheries=2];'

def prOrientation():
    """In : None
       Out: Generate dot string for orientation.
    """
    return '\n/* Orientation */\n' + 'orientation = portrait;\n'          

def prClosing():
    """In : None
       Out: Dot-file closing (string)."""
    return  ("\n}\n/*www.graphviz.org/Documentation/dotguide.pdf*/\n"+ 
             "     /*graphviz.readthedocs.io/en/latest/manual.html*/\n" 
            )

def prNonFinalNodeName(q):
    """In : q (state : string)
       Out: dot string representing state q as single circle.
    """
    return dot_san_str(q) + '[shape=circle, peripheries=1];\n'

def dotObj_nfa(N, FuseEdges = False, visible_eps=False, nfaName = 'NO_'):
    """In : N (NFA : consistent)
            nfaName (string)
       Out: A dot object. 
       Generate a dot object representing the automaton.       
    """
    assert(is_consistent_nfa(N))
    N           = shrink_nfastates(N)    
    if nfaName == 'NO_':
        nfaName = nfaName + NxtStateStr()
    dotObj1     = Digraph(comment=nfaName)   
    dotObj1.graph_attr['rankdir'] = 'LR'
    dotObj2     = addNFANodeDefs(N, dotObj1)
    dotObj3     = addNFAEdges(N, dotObj2, FuseEdges, visible_eps)          
    return dotObj3

def addNFANodeDefs(N, dotObj): 
    """In : N : (NFA : consistent)
            dotObj : (dot object being populated)
       Out: dot object with nodes added.
    """ 
    emptyNode = dotObj.node("EMPTY", "", shape="plaintext") 
    for q in (N["Q"] - N["F"]):
        dotObj.node(dot_san_str(q),                     
                    dot_san_str(q), shape = "circle", 
                    peripheries = "1")  
    for q in N["F"]:
        dotObj.node(dot_san_str(q),                     
                    dot_san_str(q), shape = "circle", 
                    peripheries = "2")
    return dotObj

def addNFAEdges(N, dotObj, FuseEdges, visible_eps=False):
    """In : NFA N (consistent)
            dotObj (dot object being populated)
       Out: dot object with NFA edges added.  
    """
    # Since NFAs can have multiple start states, put an "arrow"
    # coming from "the air" and impinging on every member of Q0
    for q0 in N["Q0"]:
        dotObj.edge("EMPTY", dot_san_str(q0))
    dotAl = []
    
    for trans in fn_trans(N["Delta"]):
        for nxt_state in trTrg(trans):
            dotAl += [ ((dot_san_str(trSrc(trans)),
                         dot_san_str(nxt_state)),
                        ShowEps(trSymb(trans), visible_eps)) ]                        
            
    if FuseEdges:
        dotAl = fuseDotAl(dotAl)
        
    for ((s1,s2), lab) in dotAl:
        dotObj.edge(s1,s2, label = "{} ".format(lab))
            
    return dotObj 

#-- DOT bashers for GNFA

def dotObj_gnfa(G, FuseEdges = False, visible_eps=False, gnfaName = 'GO_'):
    """In : G (GNFA : consistent)
            gnfaName (string)
       Out: A dot object. 
       Generate a dot object representing the automaton.       
    """
    assert(is_consistent_gnfa(G)) # main diff wrt nfa
    G           = shrink_nfastates(G)    
    if gnfaName == 'GO_':
        gnfaName = gnfaName + NxtStateStr()
    dotObj1     = Digraph(comment=gnfaName)   
    dotObj1.graph_attr['rankdir'] = 'LR'
    dotObj2     = addNFANodeDefs(G, dotObj1)
    dotObj3     = addNFAEdges(G, dotObj2, FuseEdges, visible_eps)          
    return dotObj3

#-- DOT bashers for PDA

def dotObj_pda(P, FuseEdges = False, visible_eps=False, pdaName = 'PO_'):
    """In : P (PDA : consistent)
            pdaName (string)
       Out: A dot object. 
       Generate a dot object representing the PDA P.
    """
    chk_consistent_pda(P)
    if pdaName == 'PO_':
        pdaName = pdaName + NxtStateStr()
    dotObj1     = Digraph(comment=pdaName)   
    dotObj1.graph_attr['rankdir'] = 'LR'
    dotObj2     = addPDANodeDefs(P, dotObj1)
    dotObj3     = addPDAEdges(P, dotObj2, FuseEdges, visible_eps)          
    return dotObj3

def pdaEdgLab(tr_isymb, tr_ssymb, nstkstr, visible_eps):
    return (ShowEps(tr_isymb, visible_eps)
            + ", " 
            + ShowEps(tr_ssymb, visible_eps)
            + " ; " 
            + ShowEps(nstkstr, visible_eps))

def fuseDotAl(dotAl):
    """Given input [ (2, "3"), (4, "5"), (2,"6") ],
       d will be  a dict  { 2: {"3","6"}, 4: {"5"} }
       and return value   { 2: {"3 \n 6"}, 4: {"5"} }
    """
    d = dict([(x, {y for (z,y) in dotAl if z==x}) for (x,w) in dotAl])  # sets of y for the same x
    return [(a, reduce(lambda x,y: x + " \n " + y, b)) for (a,b) in d.items()]  # concat the ys now

def addPDAEdges(P, dotObj, FuseEdges, visible_eps):
    """In : PDA P (consistent)
            dotObj (dot object being populated)
       Out: dot object with PDA edges added.  
    """
    dotObj.edge("EMPTY", dot_san_str(P["q0"]))
    dotAl = []
    
    for trans in fn_trans(P["Delta"]):
        tr_isymb = trSymb(trans)
        tr_ssymb = trStkSymb(trans)
        for trg in trTrg(trans):
            nstate  = pdaNstate(trg)
            nstkstr = pdaNstkStr(trg)
            dotAl += [ ((dot_san_str(trSrc(trans)),
                         dot_san_str(nstate)),
                        pdaEdgLab(tr_isymb, 
                                  tr_ssymb, 
                                  nstkstr,
                                  visible_eps)) ]
                     
    if FuseEdges:
        dotAl = fuseDotAl(dotAl)
        
    for ((s1,s2), lab) in dotAl:
        dotObj.edge(s1,s2, label = lab)
    
    return dotObj 


def addPDANodeDefs(P, dotObj): 
    """In : P : (PDA : consistent)
            dotObj : (dot object being populated)
       Out: dot object with nodes added.
    """ 
    emptyNode = dotObj.node("EMPTY", "", shape="plaintext") 
    for q in (P["Q"] - P["F"]):
        dotObj.node(dot_san_str(q),                     
                    dot_san_str(q), shape = "circle", 
                    peripheries = "1")  
    for q in P["F"]:
        dotObj.node(dot_san_str(q),                     
                    dot_san_str(q), shape = "circle", 
                    peripheries = "2")
    return dotObj

#-- DOT bashers for TM

def dotObj_tm(T, FuseEdges = False, tmName='TO_'):
    """In : T (TM : consistent)
            tmName (string)
       Out: A dot object. 
       Generate a dot object representing the TM T.
    """
    chk_consistent_tm(T)
    if tmName == 'TO_':
        tmName = tmName + NxtStateStr()
    dotObj1     = Digraph(comment=tmName)   
    dotObj1.graph_attr['rankdir'] = 'LR'
    dotObj2     = addTMNodeDefs(T, dotObj1)
    dotObj3     = addTMEdges(T, dotObj2, FuseEdges)          
    return dotObj3

def tmEdgLab(tr_isymb, ntpsym, direction):
    return (tr_isymb
            + " ; " 
            + ntpsym
            + "," 
            + direction)

def addTMEdges(T, dotObj, FuseEdges):
    """In : TM T (consistent)
            dotObj (dot object being populated)
       Out: dot object with TM edges added.  
    """
    dotObj.edge("EMPTY", dot_san_str(T["q0"]))
    dotAl = []
        
    for trans in fn_trans(T["Delta"]):
        tr_isymb = trSymb(trans)
        for trg in trTrg(trans):
            nstate    = tmNstate(trg)
            ntpsym    = tmNtpSym(trg)
            direction = tmNdir(trg)
            '''
            dotObj.edge(dot_san_str(trSrc(trans)),
                        dot_san_str(nstate),
                        label = tmEdgLab(tr_isymb, ntpsym, direction)               
                       )
            '''
            dotAl += [ ((dot_san_str(trSrc(trans)),
                         dot_san_str(nstate)),
                        tmEdgLab(tr_isymb, ntpsym, direction)) ]

    if FuseEdges:
        dotAl = fuseDotAl(dotAl)
        
    for ((s1,s2), lab) in dotAl:
        dotObj.edge(s1,s2, label = lab)
            
    return dotObj 

def addTMNodeDefs(T, dotObj): 
    """In : T : (TM : consistent)
            dotObj : (dot object being populated)
       Out: dot object with nodes added.
    """ 
    emptyNode = dotObj.node("EMPTY", "", shape="plaintext") 
    for q in (T["Q"] - T["F"]):
        dotObj.node(dot_san_str(q),                     
                    dot_san_str(q), shape = "circle", 
                    peripheries = "1")  
    for q in T["F"]:
        dotObj.node(dot_san_str(q),                     
                    dot_san_str(q), shape = "circle", 
                    peripheries = "2")
    return dotObj





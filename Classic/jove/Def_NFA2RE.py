
# coding: utf-8

# # Overview
# 
# This module focuses on converting NFA to RE. This is achieved by eliminating states one by one, and building an abstract syntax tree for the RE generated at each stage. Finally, the abstract syntax tree is rendered into an RE string.
# 
# # Top-level functions in this module
# 
# ```
# This module contains the following functions that may be used in other modules to exercise concepts, compose functions, etc.
# 
# N  : NFA
# D  : DFA
# G  : GNFA
# 
# def mk_gnfa(N):
# def mk_gnfa_from_D(D):
# def dfa2nfa(D):
# def del_gnfa_states(Gin):
# ```

# In[1]:

from jove.SystemImports import *
from jove.DotBashers  import *


# ## Algorithm
# 
# The algorithm is spelled out along these major steps:
# 
# * If given a DFA, convert it to an NFA, else proceed with given NFA
# 
# * Pick a state to eliminate 
# 
#     - doing this interactively, state by state, would make for a good interactive animation
# 
# * Find replacement paths for the state
# 
# * Do this till all states except GNFA's initial and final are gone
#  

# In[2]:

def opr(E):
    return E[0]

def arg1(E):
    return E[1][0]

def arg2(E):
    return E[1][1]

def arg(E):
    return E[1]


# In[3]:

def RE2Str(RE):
    """Helper for del_gnfa_states
       ---
       Given an RE as a tree, return the string equivalent of the RE.
    """
    if type(RE) == str:
        if (RE == ""):
            return '""'  # was return '@', but now no more '@'
        else:
            return RE
    elif type(RE) == tuple:
        if opr(RE) == "*":
            return( "("+ RE2Str(arg(RE)) + ")*")
        elif opr(RE) == "+":
            return ( "("+ RE2Str(arg1(RE)) + " + " +
                          RE2Str(arg2(RE)) +")" )
        elif opr(RE) == ".":
            return ( "("+ RE2Str(arg1(RE)) + " "  +
                          RE2Str(arg2(RE)) +
                     ")" )
        else:
            print("Illegal RE detected in RETree2Str")


# In[4]:

def mk_gnfa(Nin):
    """Input : Nin, an NFA.
       Output: G, a GNFA, with at-most one transition from any
               state p to a state q.??true any more?? Note that we have created
               an NFA (G+NFA), and so one state can have a transition
               to A SET OF STATES !!
       Method: Add a new set of states {Real_I} and another, {Real_F}.
               Move from state Real_I to the NFA's initial set of states
               upon epsilon, and from each state in NFA's F to Real_F.
               Return this GNFA.
               We will keep GNFA's alphabet implicit (whatever edge
               labels exist will be deemed to be in the alphabet.)
    """
    assert(
        is_consistent_nfa(Nin)
    ), "NFA given to mk_gnfa is not consistent."
    assert(
        Nin["F"] != set({})
    ), "Can't make GNFA from NFA with empty F (its language is empty)"
    N       = copy.deepcopy(Nin)
    GNFA_Q0 = {"Real_I"} # Name Real_I reserved for GNFA's starting state
    GNFA_F  = {"Real_F"} # Name Real_F reserved for GNFA's final state
    GNFA_Q  = N["Q"] | GNFA_Q0 | GNFA_F
    # Start with NFA's moves in Delta accumulator
    GNFA_Delta = N["Delta"]
    # Add a jump from Real_I to the original initial state
    GNFA_Delta.update({ ("Real_I","") : N["Q0"] })   
    # Add all "original final" to "Real_F" moves
    # ALSO, preserve the orig. final's Epsilon moves, IF ANY!
    GNFA_Delta = extend_Delta(GNFA_Delta, [((f,""), GNFA_F) for f in N["F"]])  
    
    # Return the GNFA
    return { "Q"     : GNFA_Q,
             "Sigma" : N["Sigma"],
             "Delta" : GNFA_Delta,
             "Q0"    : GNFA_Q0,
             "F"     : GNFA_F }

def extend_Delta(Delta, new_edges):
    """Given a dict Delta,  and new_edges which is a list [ ((a,b), C) ...], 
       in case (a,b) is in Delta, add to Delta (a,b) : (C | Delta[(a,b)])
       else add to Delta (a,b) : C. Return the final Delta.
    """
    DeltaOut = copy.deepcopy(Delta)
    for ((a,b),C) in new_edges:
        if (a,b) in Delta:
            DeltaOut.update ( { (a,b) : C | Delta[(a,b)] })
        else:
            DeltaOut.update ( { (a,b) : C })
    return DeltaOut
        
def mk_gnfa_from_D(D):
    """Given a DFA D, turn that into a GNFA by first making the D
       into an equivalent N, and then passing onto mk_gnfa.
    """
    assert(
    is_partially_consistent_dfa(D)
    ), "DFA given to mk_gnfa_from_D is not part. consist."
    return mk_gnfa(dfa2nfa(D))

def dfa2nfa(D):
    """Given a DFA D, make a language-equivalent NFA.
    """
    assert(
    is_partially_consistent_dfa(D)
    ), "DFA given to dfa2nfa is not part. consist."
    return { "Q"     : D["Q"],
             "Sigma" : D["Sigma"],
             "Delta" : dict((a,{b}) for (a,b) in D["Delta"].items()),
             "Q0"    : { D["q0"] },
             "F"     : D["F"] }   

def del_gnfa_states(Gin, DelList=[]):
    """Given a GNFA Gin with no unreachable states, 
       delete all states but f
       or Real_I and Real_F.
       If DelList is given, follow the state deletion
       order mentioned therein; else choose order internally.
       
       Return a triple (Gfinal, dotObj_List, final_re_str), where
         Gfinal       : the final GNFA
         dotObj_List  : a list of Dot objects recording the process of
                        deleting states and forming intermediate REs
         final_re_str : the final RE as a string (ready to be fed to  
                        re2nfa for converting back to an NFA)
    """
    G = copy.deepcopy(Gin) # To preserve the given GNFA
    
    if DelList==[]:        # User hasn't provided a preferred order
        StatesLeft = list(G["Q"]) # Form list from G["Q"]
    else:                  # User has provided a preferred order
        StatesLeft = DelList + ["Real_I", "Real_F"] # Add these
        
    dotObj_List = [ dotObj_gnfa(G) ] # List of intermediate GNFAs  
    while len(StatesLeft) > 2: # Exists one more than Real_I,Real_F
        (qdel, StatesLeft) = choose_state_to_del(G, StatesLeft)
        print("**** Eliminating state " + qdel + " ****")
         
        New_Edges = dict() #-- Brand new edges; ALL new paths supported 
                           #-- by qdel 
        for p in StatesLeft:
            for q in StatesLeft:
                new_p_q_label = del_one_gnfa_state(G, p, qdel, q)
                if new_p_q_label != "NOPATH": # There is a p-qdel->q path
                    old_p_q_labels = Edges_Exist_Via(G, p, q) # Exist p-qdel->q edges?
                    if old_p_q_labels != "NOEDGE":            # There are.
                        combined_label = form_alt_RE( [new_p_q_label] + old_p_q_labels )                   
                        New_Edges = extend_Delta(New_Edges, [((p, combined_label), set({q}))])
                    else:
                        # Only new_p_q_label needs to be added
                        New_Edges = extend_Delta(New_Edges, [((p, new_p_q_label), set({q}))])               
                #else no new path involving qdel exists for THIS p,q pair
            #-end for
        #-end for
        G["Q"] = set(StatesLeft)   # Fix G by adjusting its Q 
        
        # Extinguish qdel from Delta by (1) and (2) below
        Surviving_Edges = []  # These edges don't get nuked
        for ((q,symb), States) in G["Delta"].items():
            if (q != qdel): # (1) Removing all mappings out of qdel
                Surviving_Edges += [ ((q,symb), States - { qdel }) ] # (2) Remove from images 
                 
        # Now bring in the brand new edges
        # When bringing in the new edges, it may clobber an already existing mapping
        # If there is any, we should merge with new ones!
        G["Delta"] = extend_Delta(New_Edges, Surviving_Edges)
            
        # Stringify the REs in the G to display at the end
        dotObj_List += [ dotObj_gnfa( gnfa_w_REStr(G) ) ]
    #Finish while loop and then return
    
    #-- What is in G's Delta as edge-labels now is what G's Sigma is
    G["Sigma"] = { edgelab for ((p,edgelab), q) in G["Delta"].items() }
    
    #-- Merge edge labels of all paths from Real_I to Real_F into one
    final_re     = form_alt_RE(Edges_Exist_Via(G, "Real_I", "Real_F"))
    final_re_str = RE2Str(final_re)
  
    #-- Make a relevant GNFA retaining only Real_I, Real_F and one connection
    Gfinal = {"Q"     : {"Real_I", "Real_F"},
              "Sigma" : {final_re},
              "Delta" : { ("Real_I", final_re) : {"Real_F"} },
              "Q0"    : { "Real_I" },
              "F"     : { "Real_F" }
             }
    
    #-- Return the triple Gfinal, dotObj_List, final_re_str 
    return (Gfinal, dotObj_List, final_re_str)

def gnfa_w_REStr(G):
    """Helper for del_gnfa_states
       ---
       Given a GNFA G, return a GNFA with the RE Trees labeling its
       edges replaced by RE strings.
    """
    Gstr = copy.deepcopy(G)
    NewDelta = []
    for ((q, RE), States) in G["Delta"].items():
        NewDelta += [ ( (q, RE2Str(RE)), States ) ]
    Gstr["Delta"] = dict( NewDelta )
    return Gstr

            
def del_one_gnfa_state(G, p, qdel, q):   
    """Helper for del_gnfa_states
       ---
       Delete state qdel if path p--qdel-->q exists.
       Return "NOPATH" if no such path.
       Else return new direct edge label p--new_label-->q.
       new_label will be a single RE.
    """
    #print("G,p,qdel,q", G,p,qdel,q)
    p_qdel_edges = Edges_Exist_Via(G, p, qdel)
    qdel_q_edges = Edges_Exist_Via(G, qdel, q) 

    if (p_qdel_edges == "NOEDGE" or qdel_q_edges == "NOEDGE"):
        return "NOPATH"
    else:
        p_qdel_RE = form_alt_RE(p_qdel_edges)
        qdel_q_RE = form_alt_RE(qdel_q_edges)
        
        qdel_qdel_edges = Edges_Exist_Via(G, qdel, qdel)
        if qdel_qdel_edges == "NOEDGE":
            return form_concat_RE(p_qdel_RE, qdel_q_RE)  
        else:
            qdel_qdel_RE = form_alt_RE(qdel_qdel_edges)
            return form_concat_RE(p_qdel_RE,
                                  form_concat_RE(
                                    form_kleene_RE(qdel_qdel_RE),
                                    qdel_q_RE))
        
def Edges_Exist_Via(G, p, q):
    """Helper for del_gnfa_states
       ---
       If G has a direct edge p--edgelab-->q, return edgelab.
       Else return "NOEDGE". We maintain the invariant of
       at-most one edge such as edgelab for any p,q in the GNFA.
    """
    edges = [ edge 
              for ((x, edge), States) in G["Delta"].items() 
              if x==p and q in States ]
    if len(edges) == 0:
        return "NOEDGE"
    else:
        return edges
   
# Make this interactive later.. menu-selectible
def choose_state_to_del(G, StatesLeft):
    """Helper for del_gnfa_states
       ---
       Given a GNFA G and a list StatesLeft,
       choose first eligible state to delete, and return it
       plus the set of non-deleted entries. 
       Called only if there is an eligible state to be deleted.
    """
    for q in StatesLeft: 
        if (q not in G["Q0"] | G["F"]):
            # There is one eligible state to delete
            return ( q, [x for x in StatesLeft if x != q] )


def form_alt_RE(RElist):
    """Helper for del_gnfa_states and del_one_gnfa_state
       ---
       Given a non-empty RElist, merge them all using a binary
       tree formed with root '+' and interior nodes x,y.
    """
    fst = RElist[0]
    rst = RElist[1:]
    if len(RElist) > 1:
        if fst in rst:
            return form_alt_RE(rst) # remove duplicates
        else:
            return ('+', (fst, form_alt_RE(rst)))
    else:
        return fst
    
def form_concat_RE(re1, re2):
    """Helper for del_one_gnfa_state
       ---
       Given two non-eps REs, form their concatenation.
    """
    if re1=="":
        return re2
    elif re2=="":
        return re1
    else:
        return ('.', (re1, re2))

def form_kleene_RE(re):
    """Helper for del_one_gnfa_state
       ---
       Given a non-eps RE, form its star.
    """
    if re=="":
        return re
    else:
        return ('*', re)   


# In[5]:

print('''You may use any of these help commands:
help(RE2Str)
help(mk_gnfa)
help(mk_gnfa_from_D)
help(dfa2nfa)
help(del_gnfa_states)
help(gnfa_w_REStr)
help(del_one_gnfa_state)
help(Edges_Exist_Via)
help(choose_state_to_del)
help(form_alt_RE)
help(form_concat_RE)
help(form_kleene_RE)
''')


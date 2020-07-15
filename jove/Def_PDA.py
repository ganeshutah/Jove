
# coding: utf-8

# In[ ]:


from jove.SystemImports       import *
from jove.TransitionSelectors import *
from jove.DotBashers          import chk_consistent_pda


# # Pushdown Automata (PDA)
# 
# ## Basic Definitions
# 
# Pushdown Automata are structures
# 
#   $(Q, Sigma, Gamma, Delta, q0, z0, F)$
#   
# where
# 
#  * $Q$       : Finite non-empty set of states
# 
#  * $Sigma$   : Finite non-empty input alphabet
# 
#  * $Gamma$   : Finite non-empty stack alphabet (usually subsumes Sigma)
# 
#  * $Delta$   : A transition function 
# 
# and $Delta$'s signature is
#        
# $(Q \times (Sigma \cup \{\varepsilon\}) \times (Gamma\cup\{\varepsilon\}) \rightarrow (Q \times Gamma^*)$
# 
# ## Example
# 
# We model Delta as a mapping of this form
#              
#  (q, a, b) -> { (q1,G1s), (q2,G2s), ... }
#              
#           where
#              a   gets read
#              b   gets popped, if non-empty
#              Gis gets pushed
#              qi  becomes the next state
#              
# * q0      : Starting state
# 
# * z0      : Initial stack's lone contents
# 
#             - prevents an "accept by
#               empty stack" PDA from accepting as soon as it is 
#               switched on
# 
# * F       : Finite, possibly empty set of final states
# 
# We will define acceptance by final state _or_ empty stack, as will be detailed in this sequel. 
# 
# ## Instantaneous Description
# 
# An instantaneous description (ID) of a PDA is a triple (p, aI, bS). 
# 
# Now, ID (p, aI, bS) evolves to an ID (q, I, GS) 
# 
# written
# 
#    (p, aI, bS) $\vdash$ (q, I, GS)
#    
#    
# if  Delta(p,a,b) contains (q,G)
# 
# A PDA accepts by final state if its ID is of the form (p, "", S)
# where p in F. 
# 
# That is, the input is fully consumed
# and control resides within F. Note that S is arbitrary.
# 
# A PDA accepts by empty stack if its ID is of the form (p, "", "")
# at any point (for any p).
# 
# ## Design Details of a PDA
# 
# To __prevent__ a PDA P whose acceptance is defined via an empty stack
# from accepting "as soon as it is turned on", we put in an
# initial stack letter denoted by P["z0"].
# 
#  * As of now, P["z0"] is the hash mark, #
#  
#      - It does not matter what this character it is
#      
#      - With markdowns, the initial stack contents is always #
# 
#  * Note that this is only to help-out the user. The user may decide to start with 
#  an empty stack, which is fine.
#  
#  * Our preferred initial stack symbol is "z" (lower-case z). 
#  
# 
# # Our coding decisions wrt acceptance
# 
# In our coding,
# 
# * For PDA, we will require there to be an initial stack symbol
# 
# * We will permit acceptance either by final state or empty stack (this will be a 
#   parameter given to the run_pda function)
#   
# * We will require that a PDA always pop something from the stack (but allow zero or more things to be pushed). This way ("zero or more"), emptying the stack becomes possible.
# 
# * When we encounter an ID for which acceptance has been noted, that ID will still be expanded if there are moves leading out of it.
# 

# # Routines to run PDA 
# 
# We now devise a routine to run a PDA according to either the "accept by final state" criterion or "accept by empty stack" criterion. We call these "ACCEPT_F" and "ACCEPT_S" with the default being ACCEPT_F.  The main difference is that the "final" configurations are collected differently.

# In[ ]:


def explore_pda(inp, P, acceptance = 'ACCEPT_F', STKMAX=6, chatty=False):
    """A handy routine to print the result of run_pda plus making 
       future extensions to explore run-results.
    """
    # print("*** Exploring wrt STKMAX= ", STKMAX, "; increase it if needed ***")
    chk_consistent_pda(P)
    (term, final, visited) = run_pda(inp, P, acceptance, STKMAX=STKMAX,
                                     chatty=chatty)
    if (final == []):
        print("String " + inp + " rejected by your PDA :-(")
        print("Visited states are:")
        print(visited)
    else:
        print("String " + inp + " accepted by your PDA in " + 
               str(len(final)) + " ways :-) ")
        print("Here are the ways: ")
        for fin_path in final:
            (fin, path) = fin_path
            print("Final state ", fin)
            print("Reached as follows:")
            for p in path:
                print("-> ", p)
            print("-> ", fin, ".")


# In[ ]:


def run_pda(str, P, acceptance = 'ACCEPT_F', STKMAX=6, chatty=False):
    """Helper for explore_pda
       ---
       Input:  An initial string str.
               A PDA P
               The acceptance criterion (default is "by final state"
               encoded as ACCEPT_F. The alternative is ACCEPT_S
               that stands for "acceptance by empty stack").
               
       Output: (s_term_id, l_final_id_path, s_visited_id)
               Thus, an external routine can probe and determine
               * terminal IDs
               * acceptance configurations
               * visited IDs
    """
    if chatty:
        print("*** Exploring wrt STKMAX = ", STKMAX, "; increase it if needed ***")
    chk_consistent_pda(P)
    init_id         = (P["q0"], str, P["z0"]) # Initial ID
    init_l_id_path  = [(init_id, [])]   # [(Initial ID, empty path)]
    s_visited_id    = set({}) # Nothing visited yet
    
    (l_surv, 
     s_term, 
     l_final) = classify_l_id_path(init_l_id_path, s_visited_id, P, acceptance,
                                   STKMAX=STKMAX)
    
    rslt            = h_run_pda(l_id_path       = l_surv,
                                s_term_id       = s_term,     
                                l_final_id_path = l_final,  
                                s_visited_id    = s_visited_id,  
                                pda             = P,   
                                acceptance      = acceptance, # Acceptance criterion
                                STKMAX = STKMAX
                               )
    (s_terminal_id, l_final_id_path, s_visited_id) = rslt
    if chatty:
        print("s_terminal_id = ", s_terminal_id) 
        print("l_final_id_path = ", l_final_id_path)
        print("s_visited_id = ", s_visited_id)
    return rslt


# In[ ]:


def classify_l_id_path(l_id_path, s_visited_id, P, acceptance, STKMAX):
    """Helper for run_pda
       ---
       Given a list l_id_path of id_path pairs, a list s_visited_id
       of visited IDs, a PDA P, and the acceptance criterion, classify
       the contents of id_path into survivors, terminals, and finals.
    """
    #print("---")
    #print("classify_l_id_path >> ")
    #print("l_id_path = ", l_id_path)
    #print("s_visited_id = ", s_visited_id)
    
    surv_pool  = list(map(survivor_id(s_visited_id, P, STKMAX=STKMAX), l_id_path))
    term_pool  = list(map(term_id(s_visited_id, P, STKMAX=STKMAX), l_id_path))
    final_pool = list(map(final_id(P, acceptance), l_id_path))
   
    l_surv = list(map(lambda x: x[1],
                      filter(lambda x: x[0]=="surv",
                             surv_pool)))
    s_term = set(map(lambda x: x[1][0], #-- [1] gets id_path; [0] gets id
                      filter(lambda x: x[0]=="term",
                             term_pool)))
    l_final = list(map(lambda x: x[1],
                       filter(lambda x: x[0]=="final",
                              final_pool)))
    #print("classify_l_id_path << ")    
    #print("l_surv = ", l_surv)
    #print("s_term = ", s_term)
    #print("l_final = ", l_final)
    #print("---")
    
    return (l_surv, s_term, l_final)


# In[ ]:


def h_run_pda(l_id_path, s_term_id, l_final_id_path, s_visited_id, 
              pda, acceptance, STKMAX):
    """Helper for run_pda
       ---
       Input:  A list of id_path, all of which are surviving i.e. not
               "term" or terminal. This invariant is maintained.
               A set of terminal id_path (terminal in that there is
                 no point pushing on them; stuck or loopy).
               A list of final id_path: whenever we meet the 
               acceptance condition, we record that configuration;
               A list of visited id. This will help determine if
                 terminal or not. Detects looping as well.
               A PDA.
       Output: (s_term_id, l_final_id_path, s_visited_id)
               Thus, an external routine can probe and determine
               * terminal IDs
               * acceptance configurations
               * visited IDs
    """
    while (l_id_path != []):
        id_path0    = l_id_path[0]
        (id0,path0) = id_path0     # separate out the id and path
               
        # First, record the current id0 in s_visited_id 
        s_visited_id = {id0} | s_visited_id 
        
        # Then obtain  (ID, path) pairs generated by 
        # taking all possible one-step moves out of id0. 
        # We also record the extension of path0 in each such
        # reached new ID.
        nl_id_path0 = step_pda(id0, path0, pda)

        if nl_id_path0 == []:
            # Nothing gen by firing id0; recurse on rest
            l_id_path = l_id_path[1:]
        else:
            # Classify the progenies of id0 in nl_id_path0
            (l_surv, 
             s_term, 
             l_final) = classify_l_id_path(nl_id_path0, s_visited_id, pda, acceptance, STKMAX)

            l_id_path       = l_id_path[1:]   + l_surv
            s_term_id       = s_term_id | s_term
            l_final_id_path = l_final_id_path + l_final

    return (s_term_id, l_final_id_path, s_visited_id)


# In[ ]:


def interpret_w_eps(q_inp_stk, pda):
       """Helper for step_pda
          ---
          Produce the most liberal interpretation of q_inp_stk for pda
          i.e.  in (q, inp_str, stk_str), we can ignore inp_str or stk_str.
          E.g. if inp_str is "ab", we can consider it to be "" or "a".
          The rest of the string will then be "ab" or "b" respectively.
          This is done if a move in Delta can process that option.
       """
       (q, inp_str, stk_str) = q_inp_stk  
       
       inp_interps = cvt_str_to_sym(inp_str)  # Diverse interpretations of input
       stk_interps = cvt_str_to_sym(stk_str)  # and stack strings.
       
       # A list of the form [ ((if, ir), (sf, sr)), ... ] pairs where
       # ifst is the first of the input and sfst is the first of the stack
       # irst is the rest  of the input and srst is the rest  of the stack
       i_s_interps = list(product(inp_interps, stk_interps))  
       
       pda_delta = pda["Delta"]
       key_list  = list(pda_delta.keys())
       
       # Form a dictionary i_s_interp_dict of { i_s_interp : delta-codom-pt-set }
       i_s_interp_dict = dict({})
       
       for i_s_interp in i_s_interps:
           # Each i_s_interp is ((ifst, irst), (sfst, srst))
           (inp_interp, stk_interp) = i_s_interp
           (ifst, irst) = inp_interp
           (sfst, srst) = stk_interp
           
           # Now form all possible transitions under each interpretation
           key_sought = (q, ifst, sfst)
           if key_sought in key_list:
               # Transition as per that, recording the irst, srst also
               i_s_interp_dict.update({i_s_interp : pda_delta[key_sought]})
               
       return i_s_interp_dict


# In[ ]:


def step_pda(q_inp_stk, path, pda):
    """Inputs: An ID q_inp_stk = (q, inp_str, stk_str)
               A path reaching this ID. path is a list
                 of Delta's domain triples via which the firings occurred.
               A pda (Q, Sigma, Gamma, Delta, q0, z0, F)
               
       Output: Let inp_sym and stk_sym be the symbols in the input/stack.
               In case (q,inp_sym, stk_sym) is not in the domain of pda's
               TRel, return [], i.e. empty list.

               Else return the list [ (q_inp_stk_i, path_i), ... ]
               
               where ID q_inp_stk_i can be reached via path_i,
               and path_i is obtained by extending path
               with the domain triple that fired.
               
               For instance, if path_list is [p1,p2,p3] and the
               transition at domain point (q,c,s) fired from (q,inp,stk),
               and the codomain has its third entry as (q3,inp3,stk3), 
               then q_inp_stk_i will be (q3,inp3,stk3)
               and  path_i      will be [p1,p2,p3, (q,c,s)].
    """
    i_s_interp_dict = interpret_w_eps(q_inp_stk, pda)
    
    nxt_id_path_l = []
    
    extpath = path + [ q_inp_stk ]
    
    for i_s_interp_item in i_s_interp_dict.items():
        (((ifst, irst), # extract input fst,rst
          (sfst, srst)), # and stack fst,rst 
         codom_set      # and codom_set
        ) = i_s_interp_item
        for codom_pt in codom_set:
            (nxt_st, str_psh) = codom_pt
            nxt_id_path_l += [((nxt_st, irst, str_psh+srst),
                               extpath)]
    return nxt_id_path_l


# In[ ]:


def survivor_id(s_visited_id, pda, STKMAX):
    """Helper for classify_l_id_path
       ---
       Classify s_visited_id using is_surv_id to tag 
       its entries 'surv' or 'not_surv'.
    """
    return (lambda id_path:
                (("surv", id_path)
                    if is_surv_id(id_path, s_visited_id, pda, STKMAX=STKMAX)
                    else ("not_surv", id_path)))

def term_id(s_visited_id, pda, STKMAX):
    """Helper for classify_l_id_path
       ---
       Classify s_visited_id using is_term_id to tag 
       its entries 'term' or 'not_term'.
    """
    return (lambda id_path:
                (("term", id_path)
                    if is_term_id(id_path, s_visited_id, pda, STKMAX=STKMAX)
                    else ("not_term", id_path)))

def final_id(pda, acceptance):
    """Helper for classify_l_id_path
       ---
       Classify s_visited_id using is_final_id to tag 
       its entries 'final' or 'not_final'.
    """
    return (lambda id_path:
                (("final", id_path)
                    if is_final_id(id_path, pda, acceptance)
                    else ("not_final", id_path)))


# In[ ]:


def cvt_str_to_sym(str):
    """Helper for interpret_w_eps
       ---
       Given a string, interpret it in all possible ways and return a set of pairs
       of (first, rest). E.g. "ab" interpreted as ("", "ab") as well as ("a", "b").
       However, "" interpreted only as ("", "").
    """
    if str == "":
        return [("", "")]
    else:
        return [("", str), (str[0], str[1:])]


# In[ ]:


def is_surv_id(id_path, s_visited_id, pda, STKMAX):
    """Helper for survivor_id
       ---
       If there is any move out of the id of id_path,
       and the id is not subsumed by s_visited_id,
       then it is "surv"; else not.
    """
    #print("--is_surv_id--")
    (id, path) = id_path
    S = subsumed(id, s_visited_id, STKMAX=STKMAX)
    #print("not S = ", (not S))
    return (not S)
       
from functools import reduce

def subsumed(id, s_visited_id, STKMAX):
    """Helper for is_term_id and is_surv_id
       ---
       If            id is (q,in_str,stk_str)
       and exists a member (q1,in_str1,stk_str1) in s_visited_id
       then subsumed is True if q==q1, in_str==in_str1
                                and stk_str1 starts with stk_str.
       This "starts with" test models stk_str being on top of the stack.
    """
    #print("  ~~~")
    #print("  subsumed >>>")
    #print("id",id)
    #print("s_visited_id",s_visited_id)
    (q,  inp_str,  stk_str)  = id
    for (q1, inp_str1, stk_str1) in s_visited_id:
        if ((q==q1) and
            (inp_str == inp_str1) and
            (stk_str.startswith(stk_str1)
             or
             (len(stk_str) - len(stk_str1)) >= STKMAX)):
            return True
    return False

def is_term_id(id_path, s_visited_id, pda, STKMAX):
    """Helper for term_id
       ---
       If the id of id_path is subsumed by s_visited_id,
       then it is "term"; else not.
    """
    #print("--is_term_id--")
    (id, path) = id_path
    #print("id = ", id)
    #print("s_visited_id = ", s_visited_id)
    S = subsumed(id, s_visited_id, STKMAX=STKMAX)
    #print("subsumed(..) = ", S)
    return S


def is_final_id(id_path, pda, acceptance):
    """Helper for final_id
       ---
       If the id of id_path meets the acceptance criterion 
       that is passed in, then it is "final"; else not.
    """ 
    (id, path) = id_path
    (q, inp_str, stk_str) = id
    if (acceptance == "ACCEPT_F"):
        return (inp_str=="" and q in pda["F"])
    else:
        assert(acceptance == "ACCEPT_S")
        return (inp_str=="" and stk_str=="")


# Now for the functions in this file

# In[ ]:


print('''You may use any of these help commands:
help(explore_pda)
help(run_pda)
help(classify_l_id_path)
help(h_run_pda)
help(interpret_w_eps)
help(step_pda)
help(suvivor_id)
help(term_id)
help(final_id)
help(cvt_str_to_sym)
help(is_surv_id)
help(subsumed)
help(is_term_id)
help(is_final_id)
''')


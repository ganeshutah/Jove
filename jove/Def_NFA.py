
# coding: utf-8

# In[ ]:


from jove.DotBashers import is_consistent_nfa
from jove.TransitionSelectors import *
from jove.SysConsts import *
from jove.SystemImports import *
from jove.ShrinkStates import *
from jove.Def_DFA import mk_dfa  # used in nfa2dfa


# # Definitions of NFA routines

#  __We will follow Kozen and endow an NFA with multiple start states __
# 
# This will allow the NFA to be more naturally handled. For instance, the reverse of a DFA is an NFA. When we reverse a DFA, all its final states become initial states of the NFA (that models the reversed language). There are 2 ways to handle this:
# 
# 1. Introduce a fake new initial state and jump from it via $\varepsilon$ onto (what were the final state of the DFA).
# 
# 2. Don't introduce the fake new initial state, but rather allow the NFA to start from all of F being really its start state.
# 
# We prefer the latter.
# 
# __So now, following Kozen, we have__
# 
# 
# An NFA is a quintuple $(Q,\Sigma,\delta,Q_0,F)$, where:
# 
# * $Q$ is a _finite nonempty_ set of states.
# 
# * $\Sigma$ is a _finite nonempty_ alphabet containing _symbols_.
# 
# * $\delta$ is a (partial)
# 	transition function, containing a set of _transitions_. The transitions take
#     a pair from $Q\times \Sigma$ and return a __subset__ of states in $Q$. All this is succinctly
#     captured by writing
#     $\delta: Q\times \Sigma \rightarrow 2^Q$. 
#     Here we use $2^Q$ to denote the powerset of $Q$.
#     
#   
# * $Q_0\subseteq Q$, is __a set of initial states__.  Notice that we change from q0 (or $q_0$) which is what you find books such as Sipser and Linz using.
# 
# 
# * $F\subseteq Q$ is a _finite_ (and _possibly empty_) set of
# 	final (or _accepting_) states. These are shown as double-circled nodes in the graph of a DFA. 
#  
# > There is no other change. I.e. $\delta$ remains the same as before.
# > It is that when an NFA starts, it can find itself in a set of start states.
# > Most NFAs start from a __singleton__ Q0, which is then, effectively, an NFA
#  that matches most books say.
# 
# Some terminology:
# 
# > We call $Q$,$\Sigma$, $\delta$, $Q_0$, and $F$ the **_traits_** of the NFA.
# 
# > We will call an NFA **_structurally consistent_** or simply **"consistent"** if its traits pass the aforesaid checks.
# 
# 
# Here is how the checks will be broken down:
# 
# * The supplied $\delta$ function will be checked to see if it has allowed domain and range points. 
#  - The domain points must be a subset of $Q\times \Sigma$
#  - The range points must be a subset of $2^Q$
#   We do no insist that the supplied $\delta$ be total.
#     
# * $Q_0\subseteq Q$, is _the_ initial state.
# 
# * $F\subseteq Q$ is a _finite_ (and _possibly empty_) set of
# 	final (or _accepting_) states.  
#     
# We will often use the state set({}) to be the equivalent of a black-hole state for an NFA.

# # Making NFA

# In[ ]:


def mk_nfa(Q, Sigma, Delta, Q0, F):
    """Check for structural consistency of the given NFA traits.
       If the check passes, make and return an NFA.
    """
    newNFA = {"Q":Q, "Sigma":Sigma, "Delta":Delta, "Q0":Q0, "F":F}
    assert(
        is_consistent_nfa(newNFA)
    ), "NFA given to mk_nfa is not consistent. Plz check its components."
    return(newNFA)


# In[ ]:



def totalize_nfa(N):
    """In : NFA N
       Out: Totalized NFA
       Given a partially specified NFA, make it total by 
       transitioning to state set({}) wherever the incoming 
       Delta has gaps. This is done for an NFA only for things 
       like printing.
    """
    assert(
        is_consistent_nfa(N)
    ), "NFA given to totalize_nfa is not consistent."
    Sigma_w_Eps = (N["Sigma"] | {""}) # Extended Alphabet
    add_delta = { (q,c) : set({}) 
                   for q in N["Q"] 
                   for c in Sigma_w_Eps 
                   if (q,c) not in N["Delta"] }
    #
    add_delta.update(N["Delta"])
    #
    return {"Q"    : N["Q"],
            "Sigma": N["Sigma"],
            "Delta": add_delta,
            "Q0"   : N["Q0"],
            "F"    : N["F"]}


# In[ ]:


def apply_h_dfa(D, h):
    """Given a DFA D and a homomorphism h on Sigma* (as a lambda from chars to
       chars) where Sigma is D's alphabet, return an NFA with the homomorphism
       applied to D (essentially to D's Sigma and Delta).
    """
    deltaL = list(
        map(lambda x: ((x[0][0], h(x[0][1])), x[1]), D["Delta"].items()))
    # If we have two targets for same key, make a set of the targets
    NFADelta = dict([(x, {y for (z,y) in deltaL if z==x}) for (x,w) in deltaL])     
    return mk_nfa(
    D["Q"], 
    set(map(h,D["Sigma"])),
    NFADelta,
    {D["q0"]},
    D["F"])    


# # Stepping and Running NFA
# 
# Now that we've defined NFA and allied actions such as consistency checking and printing, let's write functions to step and run them.
# 
# * How the state transition function $\delta$ "works"
#   - captured in step_nfa

# In[ ]:


def step_nfa(N, q, c):
    """In : N (consistent NFA)
            q (state in N)
            c (symbol in N's sigma or "")
       Out: The set of states reached via N's Delta.
       EClosure is NOT performed.
       If the move is not defined, return {}.
    """    
    assert(
        c in (N["Sigma"] | {""})
    ), "c given to step_nfa not in Sigma."
    assert(
        q in  N["Q"]
    ), "q given to step_nfa not in Q."
    
    
    # We have to run it wrt the total version of the NFA. 
    # Since that is expensive to do each time, special-case this check.                                                               
    if (q,c) in N["Delta"].keys():
        return  N["Delta"][(q,c)]
    else:
        # If a move is undefined, it is a transition to the empty set
        return  set({})  


# ## Now we define the $\hat{\delta}$ function that runs an NFA on a string
# 
# * This is captured in run_nfa
#   
#      * This is more elaborate than with a DFA because we need to account for Epsilon moves
#      * So we will define routines to compute the E-closure of a state
#      
#        - The set of states reachable by traversing Epsilon edges
#   
# * Our algorithm is this:
# 
#      * Eclose the given set of states S
#          - If given string s is "", we are done (retn Eclosed set of states)
#          - Else take step via s[0]; Eclose it to get S'; run s[1:] on S'

# In[ ]:


def run_nfa(N, S, s, chatty=False):
    """In : N (consistent NFA)
            S (SET of states S belonging to N's states)
            s (string over N's alphabet)
       Out: SET of states reached after processing s.
       Run the NFA starting with a SET of states S on string,
       with EClosure wherever necessary. Return set of states reached.
    """       
    # First EClose the given set of states S.
    S = Eclosure(N, S)
    if s=="":
        # run_nfa returns S if nothing to process
        return S
    else:
        # else one step via s[0]; return Eclosure of the resulting states
        return run_nfa(N, ec_step_nfa(N, S, s[0], chatty), s[1:], chatty)


# In[ ]:


def ec_step_nfa(N, S, c, chatty=False):
    """Helper for run_nfa
       ---
       In : N (consistent NFA)
            S (EClosed set of states)
            c (character in N's alphabet; does not equal "")
            chatty (Boolean): Verbose-mode optional parameter
       Return Eclosure of all states one "c" step away from S.   
    """
    post_c_state_sets = list(map(lambda st: step_nfa(N, st, c), S))
                                                                              
    # Take union of state sets contained in post_c_states
    # basis case set({}) added to make reduction succeed                                
    post_c_states = reduce(lambda x,y: set(x) | set(y), 
                           post_c_state_sets, 
                           set({}))
        
    # Eclose from post-c-states                                                                          
    Eclosed_post_c_states = Eclosure(N, post_c_states)
    
    # Return final set of states after second Eclosure  
    if chatty:
        print("States reached = ", Eclosed_post_c_states)
    return Eclosed_post_c_states

def Eclosure(N, S):
    """In : N (consistent NFA)
            S (set of states of NFA to be Eclosed)
       Out: Eclosure of S (set of states).
    """
    return Echelp(N, S, set({}))

def Echelp(Nfa, Allsofar, Previous):
    """Helper for Eclosure
       ---
       In : Nfa (consistent NFA)
            Allsofar (set of states reached so far)
            Previous (set of states reached previously)                                     
       len(N["Delta"].items()) is the longest chain in the NFA;
       We will end up iterating that much. 
    """
    # Fixpoint reached; return Allsofar
    if (Allsofar == Previous):
        return Allsofar
    else:
        # When we apply step_nfa, we get state sets; 
        # form a list of those.
        post_eps_state_sets = list(map(lambda q: 
                                       step_nfa(Nfa, q, ""), 
                                       Allsofar))
        
        # Now OR-reduce 'em; basis case of set({}) 
        # added to make reduction succeed                           
        post_eps_states = reduce(lambda x, y: set(x) | set(y), 
                                 post_eps_state_sets,
                                 set({}))
            
        # Recurse till fixpoint reached
        return Echelp(Nfa      = Nfa, 
                      Allsofar = set(post_eps_states) | 
                                 set(Allsofar), 
                      Previous = Allsofar)


# Now we define NFA acceptance. We provide a silent version and a chatty (verbose) version called accepts_nfav that tells you HOW the acceptance was concluded.

# In[ ]:


def accepts_nfa(N, s, chatty=False):
    """NFA acceptance.
       Input : N : given NFA
               s : given string
               chatty : Boolean (prints accepting path,
                        which is the state-sets encountered).
    """
    Q0 = N["Q0"]
    if (run_nfa(N, Q0, s, chatty) & N["F"]) != set({}):
        if chatty:
            print("NFA accepts '" + s + 
                  "' by reaching " + 
                  str(run_nfa(N, Q0, s, False)))
        return True
    else:
        if chatty:
            print("NFA rejects '" + s + "'")
        return False


# # NFA to DFA conversion
# 
# This is one of the most important of NFA-related operations. It will have a lot in common with running NFA where the computation of EClosure was involved in every step.
# 
# 

# In[ ]:


def nfa2dfa(N, STATENAME_MAXSIZE=20): #--default state size kept
    """In : N (consistent NFA), and optional STATENAME_MAXSIZE
            for the generated DFA states
       Out: A consistent DFA that is language-equivalent to N.
    """
    assert(
        is_consistent_nfa(N)
    ), "nfa2dfa was given an inconsistent NFA."
    # EClose the starting state of the NFA
    EC = Eclosure(N, N["Q0"])
    return n2d(Frontier=[EC], Visited=[EC], Delta=dict({}), Nfa=N,
                STATENAME_MAXSIZE=STATENAME_MAXSIZE)


# In[ ]:


def n2d(Frontier, Visited, Delta, Nfa, STATENAME_MAXSIZE=20):
    """Helper for nfa2dfa.
       ---
       In : Frontier (list of state sets; initially Eclosed Q0)
            Visited  (list of visited state sets; initially Eclosed Q0)
            Delta    (the DFA transition function being formed)
            Nfa      (the NFA being converted)
            STATENAME_MAXSIZE : number
       Helper to nfa2dfa. Given a (BFS) frontier, a Visited
       set of states, the Delta being formed, and NFA Nfa, see
       if all new moves are in Visited: 
         do last gasp of Delta update; make and return a DFA;
       else: extend Frontier, Visited, Delta; recurse.
    """
    All_c_Moves = [ ((Q,c),ec_step_nfa(Nfa,Q,c)) 
                   for Q in Frontier 
                   for c in Nfa["Sigma"] ]
    New_c_Moves = list(filter(lambda QcQ: trTrg(QcQ) not in Visited, 
                              All_c_Moves))  
    if New_c_Moves == []:
        # Add last-gasp c-moves that curl back!
        last_gasp_c_moves = dict([ ((mkSSnam(Qfrom),c),mkSSnam(Qto)) 
                                  for ((Qfrom, c), Qto) in All_c_Moves ])
        Delta.update(last_gasp_c_moves)
                  
        # DFA states are visited states
        DFA_Q = { mkSSnam(Q) for Q in Visited }
                  
        # Retain alphabet
        DFA_Sigma = Nfa["Sigma"]
                  
        # Delta is ready to go
        DFA_Delta = Delta
                  
        # DFA starts at Eclosure of Nfa's Q0 set of states
        DFA_q0 = mkSSnam(Eclosure(Nfa, Nfa["Q0"]))
                  
        # DFA's final states are those in visited that contain an NFA 
        # F-state but don't retain any empty sets, in case the NFA given 
        # has no F-states!
        # This is another corner-case (i.e. don't shove-in black hole 
        # states!)
        DFA_F = set(map(lambda Q: mkSSnam(Q), 
                        filter(lambda Q: (Nfa["F"]&Q) != set({}), 
                               Visited)))
                  
        # Make the DFA; send it to the DFA-shrink to bask ugly long 
        # state names...
        return shrink_dfastates(mk_dfa(DFA_Q, 
                                       DFA_Sigma, 
                                       DFA_Delta, 
                                       DFA_q0, 
                                       DFA_F),
                               STATENAME_MAXSIZE=STATENAME_MAXSIZE)
    else:
        newFrontier = list(map(lambda QcQ: trTrg(QcQ), New_c_Moves)) 
        newVisited = Visited + newFrontier
                  
        # Even though the NFA has not closed back on itself, we MUST 
        # accommodate for the "curl-backs" along the way !!  Thus, run it
        # over All_c_Moves which may include "partial revisits along the 
        # way". We MUST pick up those curl-backs!
        NewMovesDelta = dict([ ((mkSSnam(Qfrom),c),mkSSnam(Qto)) 
                              for ((Qfrom, c), Qto) in All_c_Moves ]) 
        Delta.update(NewMovesDelta)
        return n2d(newFrontier, newVisited, Delta, Nfa,
                  STATENAME_MAXSIZE=STATENAME_MAXSIZE)
                                  
#---NFA to DFA


# # Brzozowski's DFA Minimization
# 
# Picking up from our earlier discussions, to minimize a DFA using Brzozowski's algorithm, here are the steps:
# 
# * Make sure that the given DFA has no unreachable states
# * Reverse the DFA
# * Determinize it
# * Reverse that DFA
# * Determinize it
# 
# Thus we need to write a routine to reverse a DFA. We already have a way to ensure that a DFA does not have unreachable states (in another Jupyter notebook; we won't bother to include it here, and trust the user to always provide such DFA only).
# 
# We can observe that if a DFA has black-hole states, then those states won't matter in the reversed machine (reversed NFA). Thus, we can work with __partial__ dfa (i.e., DFA that are partially consistent).

# ## DFA reversal

# In[ ]:


def inSets(D,trg,ch):
    """Helper for rev_dfa
       ---
       In : D   = partially consistent dfa,
            trg = a target state in D["q"]
            ch  = a member of D["Sigma"]
       Out: a set of states. { q s.t. Delta[q,ch] == trg }
    """
    return { q for q in D["Q"] if D["Delta"][(q,ch)] == trg }

def rev_dfa(D):
    """In : D = a partially consistent DFA without any unreachable states.
       Out: A consistent NFA whose language is D's language reversed.
    """
    # 1. Given that NFAs start from a SET of states, we already have that
    #   info. No need to add any transitions from "a new initial state" 
    #   etc
    
    # 2. Now add the inSets of each state as the NFA next set of states
    NDict = { (q,ch) : inSets(D,q,ch) 
              for q in D["Q"] 
              for ch in D["Sigma"] }
    
    # Notice that we retain D["Q"] and start from Q0 = D["F"]
    # going backwards along NDict toward F_dfa = { D["q0"] }
    return mk_nfa(D["Q"], D["Sigma"], NDict, D["F"], {D["q0"]})


# In[ ]:


def min_dfa_brz(D):
    """Minimize a DFA as per Brzozowski's algorithm.
    """
    return nfa2dfa(rev_dfa(nfa2dfa(rev_dfa(D))))


# In[ ]:


print('''You may use any of these help commands:
help(mk_nfa)
help(totalize_nfa)
help(step_nfa)
help(run_nfa)
help(ec_step_nfa)
help(Eclosure)
help(Echelp)
help(accepts_nfa)
help(nfa2dfa)
help(n2d)
help(inSets)
help(rev_dfa)
help(min_dfa_brz)
''')


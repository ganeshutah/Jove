
# coding: utf-8

# In[1]:

from jove.DotBashers import is_partially_consistent_dfa
from jove.DotBashers import is_consistent_dfa
from jove.TransitionSelectors import *
from jove.SysConsts import *
from jove.SystemImports import *


# # DFA
# 
# ## Basic Structure

#  
# A DFA is a quintuple $(Q,\Sigma,\delta,q_0,F)$, where:
# 
# * $Q$ is a _finite nonempty_ set of states.
# 
# * $\Sigma$ is a _finite nonempty_ alphabet containing _symbols_.
# 
# * $\delta$ is a **total** 
# 	transition function, containing a set of _transitions_. The transitions take
#     a pair from $Q\times \Sigma$ and return a state in $Q$. All this is succinctly
#     captured by writing
#     $\delta: Q\times \Sigma \rightarrow Q$. 
#     
#     - Note that in mathematics, one considers all functions to tbe **total** i.e., is defined everywhere in the domain. In programming (and computability theory), often functions are not total in this sense. We will be using the CS notion of partial functions and total functions early on, so that you don't have too many surprises later on (but we will remind you the math usage which always requires total functions)
#     
#   
# * $q_0\in Q$, is _the_ initial state.
# 
# * $F\subseteq Q$ is a _finite_ (and _possibly empty_) set of
# 	final (or _accepting_) states. These are shown as double-circled nodes in the graph of a DFA. 
#  
# Some terminology:
# 
# > We call $Q$,$\Sigma$, $\delta$, $q_0$, and $F$ the **_traits_** of the DFA.
# 
# > We will call a DFA **_structurally consistent_** or simply **"consistent"** if its traits pass the aforesaid checks.
# 
# > We will call a DFA **_partially consistent_** if it meets most of the structural consistency conditions, but may be supplied a _partial_ $\delta$ function (which function totalize_dfa will be eager to make totally consistent). 
# 
# Specifically, partial consistency will include the following checks:
# 
# * $Q$ is a _finite nonempty_ set of states.
# 
# * $\Sigma$ is a _finite nonempty_ alphabet containing _symbols_.
# 
# * The supplied $\delta$ function will be checked to see if it has allowed domain and range points. 
#  - The domain points must be a subset of $Q\times \Sigma$
#  - The range points must be a subset of $Q$
#   We do no insist that the supplied $\delta$ be total.
#     
# * $q_0\in Q$, is _the_ initial state.
# 
# * $F\subseteq Q$ is a _finite_ (and _possibly empty_) set of
# 	final (or _accepting_) states.  
#     
# Also to maintain sanity with respect to our Python encoding, we assume that the user does not have a state called "BH" in their DFA, unless its Delta is already total. (BH will be used to denote black-hole states that we introduce.)

# ## Functions for making DFA

# In[2]:

def mkp_dfa(Q, Sigma, Delta, q0, F):
    """In : Traits of a DFA
       Out: A DFA
       Check for partial consistency of the given DFA traits.
       If the check passes, make and return a DFA with a partial 
       Delta.
    """
    newDFA = {"Q":Q, "Sigma":Sigma, "Delta":Delta, "q0":q0, "F":F}
    assert(
        is_partially_consistent_dfa(newDFA)
    ), "DFA given to mkp_dfa is not partially consistent. Plz check its components."
    return(newDFA)

def mk_dfa(Q, Sigma, Delta, q0, F):
    """In : Traits of a DFA
       Out: A DFA
       Check for structural consistency of the given DFA traits.
       If the check passes, make and return a DFA with a total 
       Delta.
    """
    newDFA = {"Q":Q, "Sigma":Sigma, "Delta":Delta, "q0":q0, "F":F}
    assert(
        is_consistent_dfa(newDFA)
    ), "DFA given to mk_dfa is not consistent. Plz check its components."
    return(newDFA)

def totalize_dfa(D):
    """In : Partially consistent DFA
       Out: A consistent DFA 
       Given a partially specified DFA, make it total by 
       transitioning to state BH wherever the incoming Delta 
       has gaps. The returned DFA is structurally consistent.
    """
    assert(
        is_partially_consistent_dfa(D)
    ), "DFA given to totalize_dfa is not partially consistent."
    if set(fn_dom(D["Delta"])) == set(product(D["Q"], D["Sigma"])):
        # It is already total!
        return D 
    else:        
        # We must introduce a BH state of not already present
        # and proceed from there
        incoming_Delta = D["Delta"].copy()
    
        # Gaps in incoming_Delta's transition function are sent
        # to the BH (black-hole) state
        gaps_in_Tr = { (q,c) : "BH" for q in D["Q"] for c in D["Sigma"] 
                       if (q,c) not in D["Delta"] }
    
        # We are gonna add a new black-hole-state.
        # It must curl back to itself for every symbol in Sigma
        bh_self_absorbent_moves = { ("BH", c): "BH" for c in D["Sigma"] }

        # Fill the gaps in incoming_Delta
        incoming_Delta.update( gaps_in_Tr )
    
        # Add in the moves where the black-hole state curls 
        # back to itself
        incoming_Delta.update( bh_self_absorbent_moves )
        
        # All updates required are accomplished
        finished_Delta = incoming_Delta
    
        # See that we update D["Q"] with the "BH" (black-hole) 
        # state; also return the fixed-up incoming_Delta
        return {"Q"    : D["Q"] | { "BH" }, 
                "Sigma": D["Sigma"],    
                "Delta": finished_Delta,
                "q0"   : D["q0"],          
                "F"    : D["F"] }
    
def addtosigma_dfa(Din, addition):
    """Given a DFA Din and a proposed addition to its Sigma,
       if there is an overlap with the existing Sigma ,
       complain and reject (possible user typo); else
       add to Din's Sigma and return the new D. Useful when
       we define a DFA via markdown and later want to 
       add extra inputs (Sigma) that aren't decoded.
    """
    for symb in addition:
        assert(type(symb)==str and len(symb)==1
              ),("Adding non-string or longer than 1 string " +
                  symb + " in addtosigma_dfa.")
    assert(Din["Sigma"] & addition == set()
          ),("Din[Sigma] already has these symbols: "+
             str(Din["Sigma"] & addition))
    D = Din.copy()
    D["Sigma"] = Din["Sigma"] | addition
    return D


# ## Stepping and Running DFA
# 
# Now that we've managed to define DFA, we come to the core aspects of DFA, namely
# 
# * How the state transition function $\delta$ "works"
#   - captured in step_dfa
# 
# * How to run a DFA on a string, thus obtaining the $\hat{\delta}$ function
#   - captured in run_dfa
#   
# * The check of whether a DFA accepts_dfa a string
#   - captured by the predicate accepts_dfa

# In[3]:

def step_dfa(D, q, c):
    """In : D (consistent DFA)
            q (state in D)
            c (symbol in D's sigma)
       Out: next state of q via c (state in D) 
    """
    assert(c in D["Sigma"]), "step_dfa given c not in Sigma."
    assert(q in D["Q"]), "step_dfa given q not in Q."
    return D["Delta"][(q,c)]

def run_dfa(D, s):
    """In : D (consistent DFA)
            s (string over D's sigma, including "")
       Out: next state of D["q0"] via string s
    """    
    curstate = D["q0"]
    if s=="":
        return curstate
    else:
        return run_dfa_h(D, s[1:], step_dfa(D,curstate,s[0]))

def run_dfa_h(D, s, q):
    """Helper for run_dfa. Compute the next state attained
       by s running on D starting from state q
    """
    if s=="":
        return q
    else:
        return run_dfa_h(D, s[1:], step_dfa(D,q,s[0]))

def accepts_dfa(D, s):
    """In : D (consistent DFA)
            s (string over D's sigma, including "")
       Out: Boolean (if state after s-run is in D's final).
    """
    return run_dfa(D, s) in D["F"]


# ### The language of a DFA state
# 
# Imagine you are a doctor walking around with a new type of stethoscope called the __language stethoscope__ (LScope). LScope can be applied to a given state of a DFA and you can listen to that state; you will then "hear" the language of that state! This metaphor can come in quite handy, for instance in describing DFA minimization.

# # Operations on DFA

# ## DFA complementation
# 
# DFA complementation works by flipping the final and non-final states. We must check that the DFA is totalized before we embark on that, as the 'black-hole' state will now become 'white-hole' (a final state from which all symbols lead back to itself).

# In[4]:

def comp_dfa(D):
    """In : D (DFA : partially consistent)
       Out: Consistent DFA that is D's complement.
       Before we begin, make D total. This is crucial, 
       as the black-hole states if any
       become "white-hole" states in the complemented DFA 
       (i.e. really turn into accepting 
       states from which one can't get out).
       Then flip the FINAL and NON-FINAL states.
    """
    Dt = totalize_dfa(D)
    return mk_dfa(Dt["Q"],
                  Dt["Sigma"],
                  Dt["Delta"],
                  Dt["q0"],
                  Dt["Q"]-Dt["F"])


# ## DFA Union
# 
# DFA union has a straightforward definition as in the book. We march the DFAs in tandem. We accept if either DFA accepts_dfa.

# In[5]:

def union_dfa(D1in, D2in):
    """In : D1in (consistent DFA)
            D2in (consistent DFA)
       Out: DFA for language union of D1in, D2in (consistent DFA). 
    """
    assert(is_consistent_dfa(D1in)), "Inconsist. DFA1 in union_dfa"
    assert(is_consistent_dfa(D2in)), "Inconsist. DFA2 in union_dfa"
    if (D1in["Sigma"] != D2in["Sigma"]):
        print("Union on DFA with different alphabets.")
        print("Making alphabets the same (taking unions).")
        Sigma = D1in["Sigma"] | D2in["Sigma"]
        D1   = copy.deepcopy(D1in)
        D2   = copy.deepcopy(D2in)
        D1["Sigma"] = Sigma
        D2["Sigma"] = Sigma
        D1 = totalize_dfa(D1)
        D2 = totalize_dfa(D2)
    else:
        D1 = totalize_dfa(D1in)
        D2 = totalize_dfa(D2in)
   
    # The states can be anything in the cartesian product
    Q     = set(product(D1["Q"], D2["Q"]))
    
    # Accept if one of the DFAs accepts
    F     = (set(product(D1["F"], D2["Q"])) | 
             set(product(D1["Q"], D2["F"])))
    
    # Start a lock-step march from the respective q0
    q0    = (D1["q0"], D2["q0"])
    
    # The transition function attempts to march both
    # DFAs in lock-step per their own transition functions
    Delta = { ((q1,q2),ch) : (q1p, q2p) 
               for q1 in D1["Q"] for q1p in D1["Q"] 
               for q2 in D2["Q"] for q2p in D2["Q"] 
               for ch in D1["Sigma"] 
               if D1["Delta"][(q1,ch)] == q1p and
                  D2["Delta"][(q2,ch)] == q2p }
                                                          
    return pruneUnreach(
        mk_dfa(Q, D1["Sigma"], Delta, q0, F))


# ## DFA Intersection
# 
# The change wrt DFA union is very little: basically in defining final states.

# In[6]:

def intersect_dfa(D1in, D2in):
    """In : D1in (consistent DFA)
            D2in (consistent DFA)
       Out: DFA for language intersection of D1in, D2in (consistent DFA). 
    """
    assert(is_consistent_dfa(D1in)), "Inconsist. DFA1 in intersect_dfa"
    assert(is_consistent_dfa(D2in)), "Inconsist. DFA2 in intersect_dfa"
    if (D1in["Sigma"] != D2in["Sigma"]):
        print("Intersection on DFA with different alphabets.")
        print("Making alphabets the same (taking unions).")
        Sigma = D1in["Sigma"] | D2in["Sigma"]
        D1   = copy.deepcopy(D1in)
        D2   = copy.deepcopy(D2in)
        D1["Sigma"] = Sigma
        D2["Sigma"] = Sigma
        D1 = totalize_dfa(D1)
        D2 = totalize_dfa(D2)
    else:
        D1 = totalize_dfa(D1in)
        D2 = totalize_dfa(D2in)
 
    Q     = set(product(D1["Q"], D2["Q"]))
    
    # This is the only difference with the union:
    # The final states are those when both DFA accept
    F     = set(product(D1["F"], D2["F"]))
           
    q0    = (D1["q0"], D2["q0"])
    Delta = { ((q1,q2),ch) : (q1p, q2p) 
               for q1 in D1["Q"] for q1p in D1["Q"] 
               for q2 in D2["Q"] for q2p in D2["Q"] 
               for ch in D1["Sigma"] 
               if D1["Delta"][(q1,ch)] == q1p and
                  D2["Delta"][(q2,ch)] == q2p }
                                                          
    return pruneUnreach(
        mk_dfa(Q, D1["Sigma"], Delta, q0, F))


# # DFA Minimization
# 
# This is a good juncture at which to introduce DFA minimization. 
# 
# ## Definition of DFA minimization
# 
# We define minimization only for consistent DFA.
#  
# > _A consistent DFA D is minimal if it satisfies two properties_
#  
# >  1. There should not be any unreachable states (from the start state) in it
#  
# >  2. For any pair of distinct states $(s_1,s_2)$ in $D$, we must not have the case that for all strings $s$ in $\Sigma^*$, $\hat{\delta}(s_1,s) = \hat{\delta}(s_2,s)$.
# 
# 
# Basically, we don't want useless states and redundant states. 
# 
# Minimization is achieved in two phases:
# 
# 1. Eliminate unreachable states
# 
# 2. Merge language-equivalent and redundant states. More specifically, if you apply our __language stethoscope__ LScope (mentioned in an earlier cell) to two states A and B and "hear" the same language, you can merge these states.

# ### Eliminating unreachable states
# 
# Let us write the code for eliminating unreachable states. Function pruneUnreach(DFA) returns a new DFA with unreachable states in the input DFA removed (all transitions from them are also removed).

# In[7]:

def pruneUnreach(D):
    """In : D (consistent DFA)
       Out: Consistent DFA.
       Given a consistent (and of course total) DFA D,
       returns a new (consistent) DFA with unreachable 
       states in D removed. Transitions from each unreachable 
       state are also removed. Reachable states are those that
       can be reached in |D["Q"]| - 1 steps or less.
    """
    Nsteps   = len(D["Q"]) - 1 # Search this far
    Frontier = set({D["q0"]})  # BFS frontier
    AccumF   = Frontier        # Used to accumulate Frontier changes
    for n in range(Nsteps):
        for q in Frontier:
            for ch in D["Sigma"]:
                AccumF = AccumF | set({step_dfa(D, q, ch)})
        Frontier = AccumF
        
    newQ     = Frontier
    newF     = D["F"] & Frontier
    newDelta = dict({ ((q,ch),qp) 
                      for ((q,ch),qp) in fn_trans(D["Delta"]) 
                      if q in Frontier })
    return mk_dfa(Frontier, D["Sigma"], newDelta, D["q0"], newF)


# ## DFA Isomorphism
# 
# This routine is handy to check whether two DFA are isomorphic. Given they are rooted at q0, the isomorphism-check is linear in the number of edges. 
# 
# These routines will be handy to test the functionality of DFA minimization, plus check whether two DFA obtained through different constructions are "the same."

# In[8]:

def iso_dfa(D1,D2):
    """Given consistent and total DFAs D1 and D2,
       check whether they are isomorphic. Two DFAs
       are isomorphic if they have the same number
       of states and are language-equivalent. (One would
       then be able to match-up state for state and transition
       for transition.)
    """
    assert(is_consistent_dfa(D1)), "Inconsist. DFA1 in iso_dfa"
    assert(is_consistent_dfa(D2)), "Inconsist. DFA2 in iso_dfa"
    return (len(D1["Q"]) == len(D2["Q"]) and
            langeq_dfa(D1, D2))


# ## DFA Language Equivalence
# 
# Now that DFA Isomorphism is defined in terms of DFA language equivalence (and having the same number of states), we define DFA language equivalence.

# In[9]:

def langeq_dfa(D1, D2, gen_counterex=False):
    """Given consistent and total DFAs D1 and D2,
       check whether they are language-equivalent. 
       gen_counterex is a flag that triggers the
        printing of a counter-example showing the
        pairs that were marched in tandem till a
        difference was found.
        
       Two DFAs are language-equivalent if they 
       accept the same set of strings. We determine
       this through a joint depth-first walk of the 
       two DFAs until we detect a difference (return
       False then) or all pairs of states have been
       visited (return True then).
    """
    if D1["Sigma"] != D2["Sigma"]:
        print("The DFA cannot be compared, as their", end="")
        print(" alphabets are different; namely:")
        print("Sigma1 = ", D1["Sigma"])
        print("Sigma2 = ", D2["Sigma"])
        return False
    else:
        (eqStatus, lastAdd, cex_path) = h_langeq_dfa(D1["q0"], D1,
                                                     D2["q0"], D2, 
                                                     Visited=dict({})) # was []
        if not eqStatus:
            if gen_counterex:
                print("The DFA are NOT language equivalent!")
                print("Last added pair @ mismatch site is: ", lastAdd) # print msg changed
                print("All visited state pairs are", cex_path)
        return eqStatus # True or False

def same_status(q1, D1, q2, D2):
    """Helper for h_langeq_dfa
       Check if q1,q2 are both accepting
       or both non-accepting wrt D1,D2 resply.
    """
    return (q1 in D1["F"]) == (q2 in D2["F"])

def h_langeq_dfa(q1, D1, q2, D2, Visited):
    """Helper for langeq_dfa. 
       If (q1,q2) is in Visited, no screw-up so far, so
        continue. Else if they agree in status, recursively
        check for all reachable configurations (a DFS in
        recursion). Else (if they differ in status),
        then return (False, Visited) where the latter is
        the counter-example trace.  
    """
    if (q1,q2) in Visited:
        return (True, (q1,q2), Visited)
    else:
        Visited[(q1,q2)] = "" # extVisited = [(q1,q2)] + Visited  
        if not same_status(q1,D1,q2,D2):
            return (False, (q1,q2), Visited)
        else:
            l_nxt_status = list(
            map(lambda symb:
                h_langeq_dfa(D1["Delta"][(q1,symb)], D1,
                             D2["Delta"][(q2,symb)], D2,
                             Visited),
                D1["Sigma"]))
            l_rejects = list(filter(lambda x: x[0]==False, l_nxt_status))
            if l_rejects==[]:
                return (True, (q1,q2), Visited)
            else:
                return l_rejects[0] # which is the first offending (status,cex)


# ## DFA minimization algorithm (high level)
# 
# We now define a minimization algorithm. Here is the gist. The actual algorithm is in the code that follows.
# 
# 1. Put the states into two equivalence classes (EC):
# 
#  a. All non-final states are in one EC, say NF
#  b. All final states are in another EC, say F
#  c. We call any (sa,sb) such that sa in NF and sb in F as **zero-distinguishable** states, as 
#     a $\varepsilon$ string can distinguish sa and sb (meaning, when sa is evolved through $\varepsilon$ or $sb$ is evolved through $\varepsilon$, the resulting state is the same -- sa or sb)
#     
#      * "Evolved through" means $\hat{\delta}(sa,\varepsilon) = sa$, and similarly for sb
#      
#      * In our example DFA d34bl, IF is zero-distinguishable from all other states
#  
# 2. In general, we have $k$-distinguishable states for $k>0$ (above step discussed $k=0$ as zero-distinguishability)
# 
# 3. Split states:
#  
#  a. Take a state pair $(s_1,s_2)$ such that they are not $k$ distinguishable.
#  b. Take $c\in\Sigma$
#  c. If $\delta(s_1,c) = sn_1$ and $\delta(s_2,c) = sn_2$ and $(sn_1,sn_2)$ are $k$-distinguishable, mark $(s_1,s_2)$ as $k+1$-distinguishable. 
#  
# 4. Repeat the above process till across one sweep, the distinguishability relation does not change.
# 
# 5. Take all maximal sets of pairs of states that have not been found distinguishable yet. Pick a representative from each such maximal set. These states are in the final DFA. 
# 
# 6. Go by the state transitions of the representative states. (The remaining states in the equivalence classes are not necessary.)
# 
#   * In our example, all pairs in $\{A,A1\} \times \{B,B1\}$ will be 1-distinguishable (distinction made by $0$)
#   
#   * The final equivalence classes will be $\{IF\}$, and then $\{A,A1\}$, and $\{B,B1\}$.
#   
# 
# <span style="color:blue"> **Clearly, the above algorithm cannot make full sense till you see how it can be worked out "by hand" using some pictures. This is what we will now do before showing you the actual code.
# 
# ** </span>
# 

# ## A fully worked-out example
# 
# <font size="3"> 
# 
# This is the initial display of a matrix (only the lower half shown, as the upper half is symmetric). The matrix shows "." which are points at which state pairs "collide." The dots in this figure allow for these pairs to collide (we show pairs only one way, i.e. (P,Q) and not the other way i.e. (Q,P) also).
# 
# </font>

# <font size="4"> 
# 
# 
# ```
# 
# A   .
# 
# A1  .   .
# 
# B   .   .   .
# 
# B1  .   .   .   .
# 
#     IF  A   A1  B
#     
# The above is a convenient arrangement to talk about these pairs:
# 
# 
# (A, IF),
# 
# (A1, IF), (A1, A)
# 
# (B, IF),  (B, A),  (B, A1)
# 
# (B1, IF), (B1, A), (B1, A1), (B1, B)
# 
# Now, here is how the computation proceeds for this example:
# ===========================================================
# 
# Frame-0              Frame-1                Frame-2                
#  
# A   -1                A   0                  A   0                 
# 
# A1  -1   -1           A1  0   -1             A1  0   -1            
#  
# B   -1   -1  -1       B   0   -1   -1        B   0   1   1         
# 
# B1  -1   -1  -1  -1   B1  0   -1   -1  -1    B1  0   1   1   -1    
# 
#     IF   A   A1  B        IF  A    A1  B         IF  A   A1  B         
#     
#     
# Frame-3 = Frame-2   
# 
# A   0 
# 
# A1  0   -1
# 
# B   0   1   1
# 
# B1  0   1   1   -1
# 
#     IF  A   A1  B   
# ``` 
# 
#  
# 
# </font>

# ## Code for DFA minimization
# 
# We now provide the code for DFA minimization, referring to the above narrative to keep us focused as to which part of the algorithm we are implementing.

# ### The heart of the algorithm is function fixptDist. This seeks the fixpoint (or "fixed-point") of the Dist (or Distinguishability) relation. Neat eh?
# 
# A fixpoint of a function f is a value x such that f(x) = x. In our case, the functiion in question is one that take the entire matrix (frame) and tries to spit out the next matrix (frame). When we get a matrix m such that f(m) = m, the matrix has stabilized.
# 
# In our case, we obtain a fixpoint of the function with respect to input value "ht" (hash-table) representing our matrix. We also pass along the DFA in question ("D") that is a read-only argument (to consult its transition function, etc).
# 
# See how the code speaks for itself:
# 
# * We set "changed = True" outside a while loop, and enter this loop "while changed".
# 
# * We set changed = False, hoping to get out
# 
#   - Any change-causing activity (n-distinguishability for some n) will set changed back to True
#   
#   - If not, we will "get out of the jail"
#   
#   - Termination is guaranteed. Why?
#     
#       * There are only a finite number of states
#       
#       * If we pump a long-enough string from a pair of states,
#       
#           - Clearly, it can try to meander, visiting fresh state pairs that are m-distinguishable for 
#              an m <= n (those other state pairs and their distinguishability distance
#              were generated in an earlier pass or the current pass)
#              
#       * In short, for any pair of states (p,q), there is a maximal (loop-free) string s such that 
#         $\hat{\delta}(p,s) \in F$ while $\hat{\delta}(q,s)\in (Q\setminus F)$. This is the highest the 
#         distinguishability number can get to.
#              
#            - If $s$ has a loop, there is a shorter string that establishes the distinguishability 
#               number.
#          
#          

# We now go through all aspects of the code:
# 
# * We first iterate across "kv" (key,value) pairs in ht.items(), i.e. we iterate through all 
#   the matrix entries (pairs) which are recorded in "ht" (the hash table). The value recorded is the
#   distinguishability number.
#   
# * We obtain s0 and s1, the states that this hash-table entry is modeling.
# 
# * We iterate across all $c\in\Sigma$
# 
# * We obtain the next state after sending s0 and s1 via $c$
# 
# * If we land in the same next state (ns0 == ns1), we continue (try to "get out of the jail" by not
#   resetting changed)
#   
# * If this is a visited pair (i.e. (ns0,ns1) in ht), then
# 
#   - If one is "-1" while the other is >= 0  (meaning they are distinguishable states)
#      
#        - then we set changed = True, and continue, breaking this iteration of the "for c"
#        
#        - else we examine it as pair (ns1, ns0). This is because "ht" does not store both 
#           (ns0,ns1) and (ns1,ns0). But we have to check both ways
#           
#        - we apply the same logic
#        
# * If we can find distinguishability, we increase the ht number
# 
# * else we will get out of the loop!

# In[10]:

def fixptDist(D, ht):
    """In : D (consistent DFA)
            ht (hash-table of distinguishability pair distances)
       Out: ht that has attained a fixpoint in distinguishability.
       Helper (but main workhorse) for min_dfa.
       Given an initial hash-table ht and a DFA D to be minimized,
       determine the min. distinguishability distances, going frame 
       by frame, as illustrated in the DFA minimization algorithm. 
       Return fixpoint ht. Fixpoint is when ht ceases to change.
    """
    changed = True
    while changed:
        changed = False
        for kv in ht.items():
            s0 = kv[0][0]
            s1 = kv[0][1]
            for c in D["Sigma"]:
                ns0 = D["Delta"][(s0,c)]
                ns1 = D["Delta"][(s1,c)]
                #
                # Distinguishable state pairs carry 
                # "distinguishability distance" in the ht
                if ns0 == ns1:
                    continue
                if (ns0, ns1) in ht:
                    # s0,s1 are distinguishable
                    if ht[(s0,s1)] == -1 and ht[(ns0, ns1)] >= 0: 
                        # acquire one more than the
                        # dist. number of (ns0,ns1)
                        ht[(s0,s1)] = ht[(ns0, ns1)] + 1          
                        changed = True                            
                        break
                else:
                    # ht stores only (ns0,ns1); 
                    # so check the other way
                    if (ns1, ns0) in ht:                              
                        if ht[(s0,s1)] == -1 and ht[(ns1, ns0)] >= 0:  
                            ht[(s0,s1)] = ht[(ns1, ns0)] + 1           
                            changed = True                             
                            break                                      
                    else:                                              
                        print("ht doesn't cover all reqd state combos.")
    return ht


# In[11]:

def min_dfa(D, state_name_mode='succinct'):  # Default state mode
    """In : D (consistent DFA to be minimized)
       Out: Minimized version of D.
       The top-level callable DFA minimizer.
       Given a DFA D, go through the state minimization algorithm.
       state_name_mode is 'verbose' or 'succinct', producing two 
       variants, as you can guess.
       If the state_name_mode is verbose, we will make state names
       by stringing together the state names in the equivalence
       classes. Else we keep the name of the representative of 
       eqch equivalence class.
    """
    if (len(D["Q"]) == 1): # Already minimal
        return D
    else:
        # Build a dict of all state combinations of DFA.
        # Function state_combos also imparts a -1 for each state pair,
        # initializing the separation distance at -1.  
        ht = dict(state_combos(list(D["Q"])))
    
        # Mark final and non-final states to be 0-distinguishable.
        # This is achieved by putting a 0 against those state pairs.
        sepFinNonFin(D, ht)
    
        # Main fixpoint computation: Assigning distinguishability dist. 
        #==============================================================
        ht = fixptDist(D, ht)
    
        # Pick out equivalent state-pairs, i.e. those that cannot be 
        # distinguished. These are still with a "-1" in ht.
        ht_1 = [ stpair for (stpair, dist) in ht.items() if dist == -1 ]
    
        # Now form equivalence classes
        # what's returned is 
        # [(rep_1, [all_eql_states_1]), (rep_2, [all_eql_states_2]),...]
        # which includes all equivalence classes of size 2 or more.
        rep_eqc = bash_eql_classes(ht_1)

        # Now we have to deal with singleton equivalence classes. 
        # These sit unmerged, OUTSIDE OF ALL (x,y) in ht_1
        # i.e. all the entries in ht_1 are PARTNERED STATE PAIRS.  
    
        # If we now take D["Q"] and subtract from it all those x and y
        # which are present in some pair in ht_1, we obtain completely
        # non-mergable states. These are states in their own eql. classes.
    
        # 1. Find all partnered states from ht_1
        Partnered_states = list({x for (x,y) in ht_1} |
                                {y for (x,y) in ht_1})
    
        # 2. Now who is left un-partnered?
        List_of_self_only_eqlt_states = listminus(D["Q"], Partnered_states)                     
    
        # 3. For these singletons, i.e. "self-only equivalent states", 
        # they are self-representative. Form pairs that indicate this fact.
        rep_eqc_1 = [(x, [x]) for x in List_of_self_only_eqlt_states]
    
        # 4. OK now, we can combine the set of pairs where each pair is 
        # (representative, [the list of equivalent states])
        # So finally we get the list of equivalence classes with 
        # representatives  which is of this form:
        # [(a0,[a0, a1, a2, a3, a4]), (b0,[b0, b1]), (c0,[c0]), ...] 
        final_rep_eqc = rep_eqc + rep_eqc_1
    
        # We are now ready to build a DFA out of final_rep_eqc. 
        # =====================================================
    
        # 1. First, form the set of minimized states, which are 
        # state representatives.
        minQ = {x for (x,y) in final_rep_eqc}
    
        # 2. The Alpbahet remains the same.
        minSigma = D["Sigma"]
    
        # 3. The starting state is the representative of D["q0"]
        minq0 = q0_of(D["q0"], final_rep_eqc)
    
        # 4. The final states are the representatives of the original
        #    final states. This is computed by helper F_of.
        minF = F_of(D["F"], final_rep_eqc)
    
        # 5. The transition relation of the minimized DFA is obtained
        #    by the helper Delta_of
        minDelta = Delta_of(D["Delta"], final_rep_eqc)
    
        # 6. We now need to rename the states if the user wants verbose 
        #    names (default is succinct). Verbose names are the name of 
        #    states in each equivalence class strung together sep by "_".
        if state_name_mode == 'verbose':
            # First build a state-renaming hash-table involving 
            # mk_state_eqc_name
            state_rename_ht = { x : mk_state_eqc_name(y) 
                                for (x,y) in final_rep_eqc }
        
            minQ            = { state_rename_ht[x] for x in minQ }
            minq0           = state_rename_ht[minq0]
            minF            = { state_rename_ht[f] for f in minF }
            minDelta = { (state_rename_ht[x], y) : state_rename_ht[z] 
                         for ((x,y),z) in minDelta.items() }
        #
        # Return the finished (minimized) DFA!
        return mk_dfa(minQ, minSigma, minDelta, minq0, minF)


# In[12]:

def pairFR(L):
    """In : L (list of states)
       Out: List of pairs with L[0] paired with each state in L[1:],
            with the distinguishability distance initialized to -1.
       Helper for generating state_combos.
    """
    return list(map(lambda x: ((L[0], x), -1), L[1:]))


# In[13]:

def state_combos(L):
    """In : L (list of states)
       Out: List of combinations of L's states (rep. as pairs),
            with distinguishability distances marked as -1. 
       Helper for min_dfa.
       Given a list of DFA states L (assume length >= 2),
       Form state combinations, paired up as (L[i], L[i+1]).
       This forms the 'ht' that is acted upon by fixptDist.
    """
    if len(L) <= 2:
        return([((L[0], L[1]), -1)])
    else:
        return (pairFR(L)) + (state_combos(L[1:]))


# In[14]:

def sepFinNonFin(D, ht):
    """In : D (consistent DFA)
            ht (hash table of distinguishability distances)
       Out: ht with (nonfinal,final) pairs in ht
            marked with a distinguishability distance of 0.
       Helper for min_dfa.
       Given a hash-table of separation distances and a DFA D,
       mark each state pair (final,non-final) with value 0
       indicating their 0-distinguishability.
    """
    # Form a separation predicate 
    sepPred = lambda x,y: (x in D["F"] and y in (D["Q"] - D["F"]) or 
                           y in D["F"] and x in (D["Q"] - D["F"]))
                         
    # Now separate all states where sepPred holds
    for kv in ht.items():
        if sepPred(kv[0][0], kv[0][1]):
            # Mark that this pair is 0-distinguishable
            ht[kv[0]] = 0


# In[15]:

def bash_eql_classes(eql_reln):
    """In : eql_reln (equivalence relation : list of pairs of states).
       Out: List of equivalence classes with representatives.
            I.e. a structure of the form
            [ (state0, [state0, state1, state2,]), ... ]
            where state0 is a representative for the three (for example)
            equivalent states state0, state1, state2. There are as many
            such pairs as equivalence classes.
       Helper for min_dfa.
       Given an Eql. reln. of the form 
       [(a,b),(a,c),(d,e),(f,h),(g,f),..].
       1. Grow eql classes 
       2. Elect a representative for each eql class
       3. Return "equivalence classes with representatives."
       This is a structure of the form
        [(a0,[a0, a1, a2, a3, a4]), (b0,[b0, b1]), (c0,[c0]), ...] 
       where "a0" is a state and a0,a1,a2,a3,a4 are equivalent to it
       The same goes for the bs, cs, etc.
    """
    return bash_1(eql_reln, []) # seed with empty list of eql class sets.


# In[16]:

def listminus(L1, L2):
    """In : L1 : list or set
            L2 : list or set
       Out: List of items in L1 that are not in L2.
       Helper for min_dfa and bash_1. Implements subtraction (L1 - L2).
    """
    return [x for x in L1 if x not in L2]


# In[17]:

def bash_1(eql_reln, L_eq_classes):
    """In : eql_reln (equivalence relation : list of pairs of eqlt states)
            L_eq_classes (list of eql classes which are SETS of states 
            for now.)
       Out: return list of equivalence classes with representatives.
       Helper for bash_eql_classes. 
       1) eql_reln is the current equivalence relation 
          (list of pairs)
       2) L_eq_classes is a list of sets that are the eqlt 
          classes coalesced thus far.
       3) We remove one pair at a time from the eql_reln and find
          existing equivalence classes to expand, thus modifying
          L_eq_classes each time. 
       Once the equivalence relation is emptied, we call mk_rep_eqc
       thus making a list of equivalence classes with representatives
       of the form 
       [(a0,[a0, a1, a2, a3, a4]), (b0,[b0, b1]), (c0,[c0]), ...]. 
    """
    if eql_reln == []:
        # When we have fully processed the given equivalence 
        # relation, return a list of equivalence classes with 
        # representatives of the form 
        # [(a0,[a0, a1, a2, a3, a4]), (b0,[b0, b1]), (c0,[c0]), ...]
        return mk_rep_eqc(L_eq_classes)
    else:
        # pick the next pair from the eql_reln being coalesced
        eq0 = eql_reln[0]   
        a = eq0[0]          
        b = eq0[1]   
        
        # We know that a is a state that is equivalent to b, since
        # they exist as a pair in eql_reln[0].
        
        # Now we must see if 'a' already lives in a COALESCED 
        # equivalence class
   
        # Set Sa is a typical equivalence class in L_eq_classes
        # See if 'a' is in Sa.
        
        SaL = [Sa for Sa in L_eq_classes if a in Sa]
        
        # There must be zero or one such set as Sa. 
        # Thus, |SaL| = 0 or 1
        
        # Similarly, see which (if any) eql class that b lives in
        SbL = [Sb for Sb in L_eq_classes if b in Sb]  
        
        # Now there are four cases:
        
        # 1. a,b pair is totally new (not in any eql. class so far)
        if (SaL == [] and SbL == []):
            # Add a fresh eql class {a,b} to L_eq_classes and recurse
            return bash_1(eql_reln[1:], [{a,b}] + L_eq_classes)
        
        # 2. a is in eql class SaL[0] while b is not in any eql class
        elif (SbL == [] and not(SaL == [])):
            # Remove the little eql. class in which 'a' sits
            # replace by a bigger eql. class that now also includes 'b'. 
            # That is, we must invite 'b' into the same eql class 
            # in which 'a' sits (this being SaL[0]).
            
            # Then we take away the eql class that 'a' sits in from 
            # L_eq_classes, and of course replace it with an expanded 
            # version that includes b
            New_L_eq_classes = (listminus(L_eq_classes, SaL) +
                                [SaL[0] | {b}])
            
            return bash_1(eql_reln[1:], New_L_eq_classes)
        
        # 3. b is in eql class SbL[0] while a is not in any eql class
        elif (SaL == [] and not(SbL == [])):
            # Similar steps as above, with 'a' being invited in.
            
            New_L_eq_classes = (listminus(L_eq_classes, SbL) +
                                [SbL[0] | {a}])
            
            return bash_1(eql_reln[1:], New_L_eq_classes)
        
        else:
            # a and b are both in their own little eql. classes
            # We must now collapse both the eql classes into a huge one
            # Remove both little pre-existing eql. classes. Replace 
            # with union-ed one. Neither 'a' nor 'b' is being invited in
            # afresh; rather, the eql classes they are in 
            # (i.e. SaL[0],SbL[0]) are being merged.
            
            New_L_eq_classes = (listminus(L_eq_classes,SaL+SbL) + 
                                [SaL[0] | SbL[0]])
            
            return bash_1(eql_reln[1:], New_L_eq_classes)


# In[18]:

def mk_rep_eqc(L_eq_classes):
    """Helper for bash_1 that finds the representative of a set of
       equivalent states. Given the final equivalence classes,
       make representatives for each; stick the repr. at the 
       head of a pair. Thus, (repr, eql-class-with-repr) list
       is returned.
    """
    Ll = list(map(lambda x: list(x), L_eq_classes))
    return list(map(lambda x: (x[0], x), Ll))


# In[19]:

def F_of(F, final_rep_eqc):
    """In : F (final states of DFA)
            final_rep_eqc : equivalence class with representatives
       Out: A set of representatives of the final states 
       Helper for min_dfa.
       Given F, the final states of a DFA and final equivalence
       classes with representatives of the form 
       [(rep,[states eql to rep], ...)
       obtain those equivalence classes in which the original final 
       states live. Form a set of the representatives of these states. 
       This will be the set of representatives of the final states.
    """
    return { x for (x,X) in final_rep_eqc 
             if not (set(F) & set(X)) == set({}) }


# In[20]:

def rep_of_s(s, final_rep_eqc):
    """Helper for min_dfa. Given a list 
       [(rep_of_s1, [states_eql_to_s1]),...]
       that has states paired with the list of equivalent states, 
       return the representative of s.
    """
    if final_rep_eqc == []:
        print("Error, did not find a rep for state s")
    else:
        x_X = final_rep_eqc[0]
        if s in x_X[1]:
            return x_X[0]
        else:
            return q0_of(s, final_rep_eqc[1:])    


# In[21]:

def q0_of(q0, final_rep_eqc):
    """Helper for min_dfa. Given the initial state of the DFA and
       the list [(rep, [eql states]), ...], find the representative
       of q0 in lieu of q0.
    """
    return rep_of_s(q0, final_rep_eqc)


# In[22]:

def Delta_of(Delta, final_rep_of_eqc):
    """In : Delta (transition function of the given DFA)
            final_rep_of_eqc (eql classes with representatives)
       Out: Form a dict of representatives' moves.
       Helper for min_dfa. 
       Given the original transition function Delta and the
       list [(rep_of_eqc, [equivalent states,...]), ...], 
       produce a new transition function with state representatives 
       (not the original states) jumping around!
       The nice thing is that if multiple states had jumped around, 
       their transitions AUTOMATICALLY GET MERGED when we pool 
       the transitions into a hash-table (dictionary). Thus, we are 
       merging transitions among equivalent states also.
    """
    return { (rep_of_s(s0, final_rep_of_eqc), a): 
              rep_of_s(s1, final_rep_of_eqc)  
              for  ((s0,a),s1) in Delta.items() }


# In[23]:

def mk_state_eqc_name(L):
    """In : List of states (in each eql class)
       Out: single state names by bashing the states separated by "_".
       Helper for min_dfa. 
       Given a list of states, bash the 
       state names together separated by an underscore. 
       This is useful when 'verbose mode' state name printing 
       is desired.
    """
    return "_".join(L)


# # Conclusions
# 
# This notebook covered the basics of DFA and many of the action routines. Run these help commands to learn more. 

# In[24]:

print('''You may use any of these help commands:
help(mkp_dfa)
help(mk_dfa)
help(totalize_dfa)
help(addtosigma_delta)
help(step_dfa)
help(run_dfa)
help(accepts_dfa)
help(comp_dfa)
help(union_dfa)
help(intersect_dfa)
help(pruneUnreach)
help(iso_dfa)
help(langeq_dfa)
help(same_status)
help(h_langeq_dfa)
help(fixptDist)
help(min_dfa)
help(pairFR)
help(state_combos)
help(sepFinNonFin)
help(bash_eql_classes)
help(listminus)
help(bash_1)
help(mk_rep_eqc)
help(F_of)
help(rep_of_s)
help(q0_of)
help(Delta_of)
help(mk_state_eqc_name)
''')


# In[ ]:





# coding: utf-8

# In[1]:

from jove.DotBashers          import *
from jove.TransitionSelectors import *
from jove.SystemImports       import *


# # Top-level functions in this module
# 
# ```
# This module contains the following functions that may be used in other modules to exercise concepts, compose functions, etc.
# Here are the argument types
# 
# D     : DFA
# Q     : set of states 
# q0    : initial state
# F     : Final set of states
# q     : state
# c     : character (symbol)
# s     : string
# Sigma : Alphabet (set)
# 
# Here are the functions
#  
# def mkp_dfa(Q, Sigma, Delta, q0, F):
# def mk_dfa(Q, Sigma, Delta, q0, F):
# def totalize_dfa(D):
# 
# def step_dfa(Q, q, c):
# def run_dfa(D, s):
# def accepts_dfa(D, s):
# 
# def comp_dfa(D):
# def union_dfa(D1, D2):
# def intersect_dfa(D1, D2):
# 
# def iso_dfa(D1,D2):
# def langeq_dfa(D1,D2):
# 
# def min_dfa(D, state_name_mode='succinct'):
# 
# ```

# # Chapter-3: Deterministic Finite Automata
# 
# 
# We begin our study of Deterministic Finite Automata. Please read the book. You *must* be doing two kinds of exercises:
# 
# * Do exercises on paper. That is the math you need from this course. There is no short-cut to it.
# 
# * Play with two tools, namely JFLAP and Sinap. The second tool is created by a team of SW Engg Lab Project students, namely Shayne Anderson, Daniel James, CJ Dimaano, and Dyllon Gagnier. They have contributed a _gem_ of a tool. But even gems need polish and development; hence your help in this matter will be greatly appreciated! The more you use Sinap, the more it will become better. 
# 
#  - Sinap also provides JFLAP file converters, and so you can actually play with JFLAP and then move to Sinap.
# 
# * Do the programming challenges (and play with the code) presented in this notebook (more exercises will be added). This programming part builds intuitions and helps knowledge stick. 
# 
# Notice that I recommend doing the math, playing with JFLAP/Sinap and then playing with the code in these notebooks. In reality, you must round-robin through these tasks.
# 
# > You do not understand anything unless you have studied it in multiple ways _(John McCarthy)_
# 

# # Coding Philosophy
# 
# Clearly, the code in this book can be cast into an object-oriented style. We avoid doing so for these reasons:
# 
# * We want to keep the barrier to entry as low as possible. In fact, we are extremely parsimonious in our use of Python constructs. 
# 
# * We prefer to modularize each concept into specific sections where we treat the math and code as being almost at the same level. We also want these Jupyter notes to resemble Knuth's "literate programs". More specifically,
# 
# - In math, when you present DFA as a quintuple $(Q, \Sigma, \delta, q_0, F)$, you are not thinking OOP; rather, math prefers flat structures (for simple ideas that span a few pages). We want the code to resemble math written at this level. Hence the notion of bringing in another layer (namely objects) is felt un-necessary.
# 
# - When math gets tedious, we _do_ need structuring. Leslie Lamport has written a paper "How to write a formula", explaining how long formulae need to be written as code. Thus, even math _may_ need structured programming principles at a certain higher level of complexity.  We feel that this subject matter hasn't reached that level of complexity, and hence "math dictates modularization", not code.
# 
# * With discipline, one can write readable code. The volume of code we have in these notes is not high. For that level of complexity, a functional / recursive / higher-order style with short segments of code tesselating with math is a better approach than lead one's mind totally away from math by showing more features of Python.
# 
# * By presenting my intellectual contribution of a large swath of _Models of Computation_ in this simple "mathy-coding" style, I am inviting others to prove me wrong and actually show that other modularization methods can work, too. I.e. this work is by no means the end of any story; it is just something I want to contribute and move on, hoping others will improve on my work far more!

# <span style="color:blue"> **We begin defining DFA by providing its structure. ** </span>
# 
# We will first set up a series of definitions ending at the mk_dfa function that helps build DFA. 
# 
# There are also two allied functions, namely mkp_dfa and totalize_dfa. mkp_dfa helps save labor by allowing you to specify just the main transitions you want in the DFA. Then typically one applies totalize_dfa which fills all the "gaps", sending the DFA to a "black-hole" state for those possibilities.  
# 
# Once functions are set up, we will define step_dfa, run_dfa and accepts_dfa. 
# 
# We will also be defining functions for displaying DFA with the help of the _dot_ tool. The first function dot_dfa_w_bh shows the full DFA (including black-hole moves). Another function dot_dfa (which has a shorter name, and hence more inviting to employ frequently) suppresses these black-hole moves (that may be distractingly many, which can clutter the dot-generated view). In defining these dot converters, we will be sanitizing certain strings so that the dot tool can handle these edge labels.
# 
# We will also provide dot_dfa_pdf and dot_dfa_w_bh_pdf that generates a PDF output.
# 
# <span style="color:blue"> **------** </span>
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

# <span style="color:blue"> **Here is how we will represent a DFA in Python (taking Figure 3.4's example from the book). You can clearly see how the traits of the DFA are encoded. We prefer a Python dictionary, as it supports a number of convenient operations, and also one can add additional fields easily. ** </span>

# In[2]:

DFA_fig34 = { 'Q': {'A', 'IF', 'B'},
              'Sigma': {'0', '1'},
              'Delta': { ('IF', '0'): 'A',
                         ('IF', '1'): 'IF',
                         ('A', '0'): 'B',
                         ('A', '1'): 'A',
                         ('B', '0'): 'IF',
                         ('B', '1'): 'B' },
              'q0': 'IF', 
              'F': {'IF'}   
            }


# <span style="color:blue"> 
# **
# We will now introduce extractors for the transitions contained in Delta.
# ** 
# </span>
# * Since we use many pairs, we introduce **fst** and **snd** to extract those components
# * Since we employ functions encoded as key/value pairs, we introduce **fn_dom** and **fn_range** to extract those
#   - We return the range elements (fn_range)
#      as a list so that NFA routines can also use this function   
#      (NFA would want to return a set of sets, but that's not representable
#      in Python; now, with fn_range returning a list, we will end up gettin
#      a list of sets, which is fine in Python.)
#   - Bowing to uniformity, we will return a list for fn_dom also.
# * Since a function itself is a set of _transitions_, we also introduce the extractor **fn_trans**. The transitions go from fn_dom to fn_range.
# * Since the members of Delta are _transitions_, we introduce three extractors. Notice that transitions Tr are of the form ((trSrc,trSymb), trTrg) where from and to are states, and symb is a symbol belonging to $\Sigma$. Here are the extractors:
# 
#  - **trSrc** that returns the source of a transition
#  - **trSymb** that returns the symbol that labels the transition
#  - **trTrg** that labels the target of the transition

# #### When we defined our DFA_fig34 (above), we just pasted the elements of the hash-table by hand. This approach has many problems: (1) mistakes are easily made (2) constraints on the DFA quintuple are not checked (3) we can't automate the generation of DFAs. To avoid these, we will now present three of the aforementioned functions, namely mk_dfa, mkp_dfa and totalize_dfa. Then we will provide the definitions of all supporting functions that these functions need.

# Note that the consistency checkers of DFA are in DotBashers.    

# In[3]:

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
        incoming_Delta = D["Delta"]
    
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
    


# # Routines to generate 'dot' graphs from DFA

# <span style="color:blue"> **We can now write routines to print DFA using dot. The main routines are listed below.** </span>
# 
# * dot_dfa_w_bh : lists all states of a DFA including black-hole states
# * dot_dfa      : lists all isNotBH states (see below for a defn), i.e. suppress black-holes
#      - Usually there are too many transitions to them and that clutters the view
#      

# ======

# ## Some Tests that were administered to debug the above code

# ### Let us now administer some tests to mk_dfa, mkp_dfa and totalize_dfa
# 
# 1. If you totalize_dfa a structurally consistent DFA, you get back that same DFA (it is a no op).
# 2. If you take a structurally consistent DFA, make it partial by dropping some of its mappings,  
#    and totalize it, you get a structurally consistent DFA.
# 
# In general, it is good to think of axioms that must be obeyed and derive tests based on them.

# In[4]:

# Some tests pertaining to totalize_dfa, is_consistent_dfa, etc

DFA_fig34 = { 'Q': {'A', 'IF', 'B'},
              'Sigma': {'0', '1'},
              'Delta': { ('IF', '0'): 'A',
                         ('IF', '1'): 'IF',
                         ('A', '0'): 'B',
                         ('A', '1'): 'A',
                         ('B', '0'): 'IF',
                         ('B', '1'): 'B' },
              'q0': 'IF', 
              'F': {'IF'}   
            }

def tests_dfa_consist():
    """Some tests wrt DFA routines.
    """
    DFA_fig34_Q     = DFA_fig34["Q"]
    DFA_fig34_Sigma = DFA_fig34["Sigma"]
    randQ           = random.choice(list(DFA_fig34_Q))
    randSym         = random.choice(list(DFA_fig34_Sigma))

    DFA_fig34_deepcopy  = copy.deepcopy(DFA_fig34)

    print('is_consistent_dfa(DFA_fig34) =', 
           is_consistent_dfa(DFA_fig34) )
    print('Removing mapping for ' + 
          "(" + randQ + "," + randSym + ")" + 
          "from DFA_fig34_deepcopy")
    DFA_fig34_deepcopy["Delta"].pop((randQ,randSym))
    print('is_consistent_dfa(DFA_fig34_deepcopy) =', 
         is_consistent_dfa(DFA_fig34_deepcopy) )

    totalized = totalize_dfa(DFA_fig34_deepcopy)
    print ( 'is_consistent_dfa(totalized) =', 
          is_consistent_dfa(totalized) )

    assert(totalized == totalize_dfa(totalized)) # Must pass  


# ### Let us now administer some tests to print dot-strings generated.
# 
# We will demonstrate two ways to print automata: 
# 
# 1. First generate a dot string via dot_dfa or dot_dfa_w_bh
#    (calling the result "dot_string") 
#    1. Then use the srcObj = Source(dot_string) call
#    2. Thereafter we can display the srcObj object directly into the browser
#    3. Or, one can also later convert the dot_string to svg or PDF
# 2. OR, one can directly generate a dot object via the dotObj_dfa or dotObj_dfa_w_bh call
#    (calling the result "dot_object")
#    1. Then directly display the dot_object
#    2. There are conversions available for dot_object to other formats too

# In[5]:

DFA_fig34 = { 'Q': {'A', 'IF', 'B'},
              'Sigma': {'0', '1'},
              'Delta': { ('IF', '0'): 'A',
                         ('IF', '1'): 'IF',
                         ('A', '0'): 'B',
                         ('A', '1'): 'A',
                         ('B', '0'): 'IF',
                         ('B', '1'): 'B' },
              'q0': 'IF', 
              'F': {'IF'}   
            }

def dfa_dot_tests():
    """Some dot-routine related tests.
    """
    dot_string = dot_dfa(DFA_fig34)
    dot_object1 = Source(dot_string)
    return dot_object1.source


# In[ ]:




# # Stepping and Running DFA
# 
# Now that we've managed to define DFA, check for its consistency, and also learned how to produce drawings of its state transition diagram, we come to the core aspects of DFA, namely
# 
# * How the state transition function $\delta$ "works"
#   - captured in step_dfa
# 
# * How to run a DFA on a string, thus obtaining the $\hat{\delta}$ function
#   - captured in run_dfa
#   
# * The check of whether a DFA accepts_dfa a string
#   - captured by the predicate accepts_dfa

# In[6]:

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
            q (state in D)
            s (string over D's sigma, including "")
       Out: next state of q via s (state in D) 
    """    
    state = D["q0"]
    while s != "":
        state = step_dfa(D, state, s[0])
        s = s[1:]
    return state

def accepts_dfa(D, s):
    """In : D (consistent DFA)
            s (string over D's sigma, including "")
       Out: Boolean (if state after s-run is in D's final).
    """
    return run_dfa(D, s) in D["F"]


# ## Let us test functions step_dfa, run_dfa, and accepts_dfa

# In[7]:

# Some tests of step, run, etc.

DFA_fig34 = { 'Q': {'A', 'IF', 'B'},
              'Sigma': {'0', '1'},
              'Delta': { ('IF', '0'): 'A',
                         ('IF', '1'): 'IF',
                         ('A', '0'): 'B',
                         ('A', '1'): 'A',
                         ('B', '0'): 'IF',
                         ('B', '1'): 'B' },
              'q0': 'IF', 
              'F': {'IF'}   
            }

def step_run_accepts_tests():
    print("step_dfa(DFA_fig34, 'IF', '1') = ", 
          step_dfa(DFA_fig34, 'IF', '1'))
    print("step_dfa(DFA_fig34, 'A', '0') = ", 
          step_dfa(DFA_fig34, 'A', '0'))

    print("run_dfa(DFA_fig34, '101001') = ", 
          run_dfa(DFA_fig34, '101001'))
    print("run_dfa(DFA_fig34, '101000') = ", 
          run_dfa(DFA_fig34, '101000'))

    print("accepts_dfa(DFA_fig34, '101001') = ", 
          accepts_dfa(DFA_fig34, '101001')) 
    print("accepts_dfa(DFA_fig34, '101000') = ", 
          accepts_dfa(DFA_fig34, '101000')) 


# In[8]:

dotObj_dfa(DFA_fig34, "DFA_fig34")


#  <span style="color:blue"> **Ideally one likes to have an "Recognizes a language" test also, but we don't have enough machinery to specify "a language". Well one can specif "a language" through another DFA, but then we are asking about "exactly the strings of the reference DFA D being accepted by the user-build DFA D1. I leave its implementation as an exercise, given that DFA union and complement are being defined.** </span>

# ### The language of a DFA state
# 
# Imagine you are a doctor walking around with a new type of stethoscope called the __language stethoscope__ (LScope). LScope can be applied to a given state of a DFA and you can listen to that state; you will then "hear" the language of that state!  Now if you take the DFA in Figure 3.4 (DFA_fig34 above), and apply LScope to the state IF, you will hear the language of the DFA (all strings that can start from IF and reach some final state). If you apply LScope to state A, you will hear a different language: its language is "two zeros, followed by a multiple (zero or more) of three 0s (with 1s appearing anywhere). If you apply LScope to state B, its language can be "heard as" a single 0 followed by a multiple of three 0s, with 1s appearing arbitrarily anywhere.
# 
# We will walk around with our __language stethoscope__ LScope a lot in this and future chapters, to explain things clearly. In fact, we will be using it to explain DFA minimization very soon.

# ## DFA complementation
# 
# DFA complementation works by flipping the final and non-final states. We must check that the DFA is totalized before we embark on that, as the 'black-hole' state will now become 'white-hole' (a final state from which all symbols lead back to itself).

# In[9]:

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
    Dtot = totalize_dfa(D)
    return mk_dfa(D["Q"],D["Sigma"],D["Delta"],D["q0"],D["Q"]-D["F"])


# In[10]:

# Run a complementation test
DFA_fig34_comp = comp_dfa(DFA_fig34)
dotObj_dfa(DFA_fig34_comp, "DFA_fig34_comp")
dotObj_dfa(DFA_fig34)
dotObj_dfa(DFA_fig34_comp, "DFA_fig34_comp")


# ## DFA Union
# 
# DFA union has a straightforward definition as in the book. We march the DFAs in tandem. We accept if either DFA accepts_dfa.

# In[11]:

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


# In[12]:

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


# In[13]:

dotObj_dfa(DFA_fig34_comp)


# The most surprising observation we can make is that the above diagram still represents a DFA!! A DFA can have isolated islands. While useless, the above meets ALL the consistency conditions of a DFA. 
# 
# However, it is annoying to have disconnected states. Clearly, they are totally redundant. We may also have reachable states that are redundant (are completely equivalent to an existing state). Both these types of redundancies can be eliminated through a suitable DFA minimization algorithm which will soon be discussed.
# 
# Minimization is achieved in two phases:
# 
# 1. Eliminate unreachable states
# 
# 2. Merge language-equivalent and redundant states. More specifically, if you apply our __language stethoscope__ LScope (mentioned in an earlier cell) to two states A and B and "hear" the same language, you can merge these states.
# 
# ### Exercise for you:
# 
# Write a more elaborate union_dfa that does not do an indiscriminate cartesian product. For instance, the state (A_IF) and also (B_IF) should not even have been generated if we had gone by the idea of "reachable in K hops". We can call this "lock-step cartesian product". That is
# 
#  * Situating a  DFA  and its complement in state IF, if we feed a $0$, they both go to their own states A.  
#  
#  * Thus, the state (IF_A) should not arise

# ### Eliminating unreachable states
# 
# Let us write the code for eliminating unreachable states. Function pruneUnreach(DFA) returns a new DFA with unreachable states in the input DFA removed (all transitions from them are also removed).

# In[14]:

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


# In[15]:

# One more test
du     = union_dfa(DFA_fig34, DFA_fig34_comp)
dotObj_dfa(du, "orig union")
pdu    = pruneUnreach(du)
pdu
pduObj = dotObj_dfa(pdu, "union of 34 and comp")
pduObj



# # DFA Isomorphism
# 
# This routine is handy to check whether two DFA are isomorphic. Given they are rooted at q0, the isomorphism-check is linear in the number of edges.

# In[16]:

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


# In[17]:

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
        (eqStatus, cex_path) = h_langeq_dfa(D1["q0"], D1,
                                            D2["q0"], D2, 
                                            Visited=[])
        if not eqStatus:
            if gen_counterex:
                print("The DFA are NOT language equivalent!")
                print("Path leading to counterexample is: ")
                print(cex_path)
        return eqStatus # True or False

def same_status(q1, D1, q2, D2):
    """Check if q1,q2 are both accepting
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
        return (True, Visited)
    else:
        extVisited = Visited + [(q1,q2)]
        if not same_status(q1,D1,q2,D2):
            return (False, extVisited)
        else:
            l_nxt_status = list(
            map(lambda symb:
                h_langeq_dfa(D1["Delta"][(q1,symb)], D1,
                             D2["Delta"][(q2,symb)], D2,
                             extVisited),
                D1["Sigma"]))
            l_rejects = list(filter(lambda x: x[0]==False, l_nxt_status))
            if l_rejects==[]:
                return (True, extVisited)
            else:
                return l_rejects[0] # which is the first offending (status,cex)


# In[18]:

D34 = {   'Q': {'A', 'IF', 'B'},
          'Sigma': {'0', '1'},
          'Delta': { ('IF', '0'): 'A',
                     ('IF', '1'): 'IF',
                     ('A', '0'): 'B',
                     ('A', '1'): 'A',
                     ('B', '0'): 'IF',
                     ('B', '1'): 'B' },
          'q0': 'IF', 
          'F': {'IF'}   
        }

D34bl = { 'Q': {'A', 'IF', 'B', 'A1', 'B1'},
          'Sigma': {'0', '1'},
          'Delta': { ('IF', '0'): 'A',
                     ('IF', '1'): 'IF',
                     ('A', '0'): 'B1',
                     ('A', '1'): 'A1',
                     ('A1', '0'): 'B',
                     ('A1', '1'): 'A',
                     ('B1', '0'): 'IF',
                     ('B1', '1'): 'B',
                     ('B','0') : 'IF',
                     ('B', '1'): 'B1' },
          'q0': 'IF', 
          'F': {'IF'}   
        }


d34 = dotObj_dfa(D34, "D34")
d34 # Display it!


# In[19]:

langeq_dfa(D34,D34bl,False)


# In[20]:

iso_dfa(D34,D34bl)


# In[21]:

DFA_fig34
d34 = DFA_fig34
d34


# In[22]:

d34c = DFA_fig34_comp
d34c


# In[23]:

iso_dfa(d34,d34)


# In[24]:

iso_dfa(d34,d34c)


# In[25]:

d34v1 = {'Delta': {('A', '0'): 'B',
  ('A', '1'): 'B',
  ('B', '0'): 'IF',
  ('B', '1'): 'B',
  ('IF', '0'): 'A',
  ('IF', '1'): 'IF'},
 'F': {'IF'},
 'Q': {'A', 'B', 'IF'},
 'Sigma': {'0', '1'},
 'q0': 'IF'}


# In[26]:

dotObj_dfa(d34v1)


# In[27]:

d34v2 = {'Delta': {('A', '0'): 'B',
  ('A', '1'): 'B',
  ('B', '0'): 'IF',
  ('B', '1'): 'B',
  ('IF', '0'): 'A',
  ('IF', '1'): 'IF'},
 'F': {'IF', 'B'},
 'Q': {'A', 'B', 'IF'},
 'Sigma': {'0', '1'},
 'q0': 'IF'}


# In[28]:

iso_dfa(d34,d34v1)


# In[29]:

iso_dfa(d34,d34v2)


# In[30]:

iso_dfa(d34v1,d34v2)


# In[31]:

div1 = pruneUnreach(intersect_dfa(d34v1,d34v2))
dotObj_dfa(div1)


# In[32]:

div2 = pruneUnreach(union_dfa(d34v1,d34v2))
dotObj_dfa(div2)


# In[33]:

iso_dfa(div1,div2)


# In[34]:

langeq_dfa(div1,div2,True)


# In[35]:

d34bl = dotObj_dfa(D34bl, "D34bl")
d34bl # Display it!


# In[36]:

iso_dfa(D34,D34bl)


# In[37]:

langeq_dfa(D34,D34bl)


# #### 

# In[38]:

du


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
# We don't want useless states and we don't want redundant states. For instance, let me make a redundant DFA with duplicate states, below. Then you can easily see how even bloated DFAs can recognize the same language. After seeing this fact, we will introduce you to a DFA minimization algorithm.
# 
# First, let's learn how to deliberately bloat a DFA:

# ## DFA minimization algorithm (high level)
# 
# Having seen two examples of bloated DFA, we now define a minimization algorithm. Here is the gist. The actual algorithm is in the code that follows.
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

# In[39]:

dotObj_dfa(pruneUnreach(D34bl), "D34bl")


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
# <br>
# <br>
# 
# Let's see another example as well. We will explain the second 
# example (we leave the above example wrt **D34bl** as something you can explain.
# 
# </font>

# In[40]:

### DFA minimization (another example)


# In[41]:

Bloat1 = {'Q': {'S1', 'S3', 'S2', 'S5', 'S4', 'S6' },
          'Sigma': {'b', 'a'},
          'Delta': { ('S1','b') : 'S3',
                     ('S1','a') : 'S2',
                     ('S3','a') : 'S5',
                     ('S2','a') : 'S4',
                     ('S3','b') : 'S4',
                     ('S2','b') : 'S5',
                     ('S5','b') : 'S6',
                     ('S5','a') : 'S6',
                     ('S4','b') : 'S6',
                     ('S4','a') : 'S6',
                     ('S6','b') : 'S6',
                     ('S6','a') : 'S6' },
          'q0': 'S1', 
          'F': {'S2','S3','S6'}   
        }


Bloat1O = dotObj_dfa(Bloat1, "Bloat1")
Bloat1O # Display it!


# 
# Now, here is how the computation proceeds for this example:
# -------------------------------------------------------- 
#  
#  <br>
#  
# <font size="3"> 
# 
# 
# ```
#  
# Frame-0                  Frame-1                   Frame-2                    
#                                                                                                      
# S2  -1                   S2   0                    S2   0                     
# 
# S3  -1  -1               S3   0  -1                S3   0  -1                 
# 
# S4  -1  -1  -1           S4  -1   0   0            S4   2   0   0             
# 
# S5  -1  -1  -1  -1       S5  -1   0   0  -1        S5   2   0   0  -1         
# 
# S6  -1  -1  -1  -1  -1   S6   0  -1  -1   0   0    S6   0   1   1   0   0     
# 
#     S1  S2  S3  S4  S5       S1  S2  S3  S4  S5        S1  S2  S3  S4  S5        
# 
# Initial                  0-distinguishable         1-distinguishable                         
#      
#      
# Frame-3                 Frame-4     
#                         =
#                         Frame-3
# 
# S2   0
# 
# S3   0  -1
# 
# S4   2   0   0
# 
# S5   2   0   0  -1
# 
# S6   0   1   1   0   0
# 
#     S1  S2  S3  S4  S5
#     
# 2-distinguishable 
#      
# ```
# </font>

# Here is the algorithm, going frame by frame.
# 
# - Initial Frame: 
# 
#      The initial frame is drawn to clash all _combinations_ of states taken two at a time.
#      Since we have 6 states, we have $6\choose 2$ = $15$ entries. We put a -1 against each
#      such pair to denote that they have not been found distinguishable yet.
# 
# - Frame *0-distinguishable*: We now put a 0 where a pair of states is 0-distinguishable. This means the states are distinguisable after consuming $\varepsilon$. This of course means that the states are themselves distinguishable. This is only possible if one is a final state and the other is not (in that case, one state, after consuming $\varepsilon$ accepts_dfa, and another state after consuming $\varepsilon$ does not accept.
# 
#   - So for instance, notice that (S3,S1) and (S4,S2) are 0-distinguishable, meaning that one is a final and the other is a non-final state.
# 
# - Frame *1-distinguishable*: We now put a 1 where a pair of states is 1-distinguishable. This means the states are distinguisable after consuming a string of length $1$ (a single symbol). This is only possible if one state transitions to a final state and the other transitions to a non-final state after consuming a member of $\Sigma$. 
# 
#   State pairs (S6,S2) and (S6,S3) are of this kind. While both S6 and S2 are final states (hence _0-indistinguishable_), after consuming an 'a' (or a 'b') they respectively go to a final/non-final state.
#  This means that
# 
#   - after processing **the same symbol** one state -- let's say pre_p -- finds itself landing in a state p and another state  -- let's say pre_q -- finds itself landing in a state q such that (p,q) is 0-distinguishable.
#   
#   - When this happens, states pre-p and pre-q are **1-distinguishable**.
# 
# - Frame *2-distinguishable*: We now put a 2 where a pair of states is 2-distinguishable. This means the states are distinguisable after consuming a string of length $2$ (a string of length $2$). This is only possible if one state transitions to a state (say p) and the other transitions to state (say q) after consuming a member of $\Sigma$ such that (p,q) is **1-distinguishable**. State pairs (S5,S1) and (S4,S1) are 2-distinguishable because
# 
#   - after processing **the same symbol** one state -- let's say pre_p -- finds itself landing in a state p and another state  -- let's say pre_q -- finds itself landing in a state q such that (p,q) is 0-distinguishable.
#   
#   - When this happens, states pre-p and pre-q are **1-distinguishable**.
#   
#   - One example is this:
#   
#     - S5 and S1 are 2-distinguishable.
#     
#     - This is because after seeing an 'aa', S1 lands in a non-final state while S5 lands in a final state
#     
#     - Observe that "aa" = "a" + "a" . Thus, after eating the first "a", S1 lands in S2 while S5 lands in S6, and (S2,S6) have already been deemed 1-distinguishable.
#     
#     - Thus, when we mark (S5,S1) as 2-distinguishable, we are sending the matrix entry at (S5,S2) from 
#       -1 to 2
#  
# 
# 
#   - Now, in search of 3-distinguishability, we catch hold of all pairs in the matrix and see if we can send another -1 entry to "3". This appears not to happen. 
#   
#      - Thus, if (S2,S3) is pushed via any sequence of symbols (any string) of any length, it
#        always stays in the same type of state. Thus, after seeing 'ababba', S2 is in S6, while S3 
#         is also in S6.
# 
# 
#  - Thus, given no changes in the matrix, we stop.

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

# In[42]:

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


# In[43]:

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


# In[44]:

def pairFR(L):
    """In : L (list of states)
       Out: List of pairs with L[0] paired with each state in L[1:],
            with the distinguishability distance initialized to -1.
       Helper for generating state_combos.
    """
    return list(map(lambda x: ((L[0], x), -1), L[1:]))


# In[45]:

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


# In[46]:

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


# In[47]:

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


# In[48]:

def listminus(L1, L2):
    """In : L1 : list or set
            L2 : list or set
       Out: List of items in L1 that are not in L2.
       Helper for min_dfa and bash_1. Implements subtraction (L1 - L2).
    """
    return [x for x in L1 if x not in L2]


# In[49]:

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


# In[50]:

def mk_rep_eqc(L_eq_classes):
    """Helper for bash_1 that finds the representative of a set of
       equivalent states. Given the final equivalence classes,
       make representatives for each; stick the repr. at the 
       head of a pair. Thus, (repr, eql-class-with-repr) list
       is returned.
    """
    Ll = list(map(lambda x: list(x), L_eq_classes))
    return list(map(lambda x: (x[0], x), Ll))


# In[51]:

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


# In[52]:

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


# In[53]:

def q0_of(q0, final_rep_eqc):
    """Helper for min_dfa. Given the initial state of the DFA and
       the list [(rep, [eql states]), ...], find the representative
       of q0 in lieu of q0.
    """
    return rep_of_s(q0, final_rep_eqc)


# In[54]:

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


# In[55]:

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


# In[56]:

dotObj_dfa(min_dfa(Bloat1), "shrunkBloat1")


# In[57]:

prd34b1 = pruneUnreach(D34bl)


# In[58]:

dotObj_dfa(prd34b1, "prd34b1")


# In[59]:

dotObj_dfa(min_dfa(prd34b1), "prd34b1min")


# # Conclusions
# 
# This notebook covered the basics of DFA including
# 
# * Representations, consistency conditions
# 
# * Making partial DFA and making them complete
# 
# * DFA representation generation in Dot and Dot Object formats
# 
# * DFA string and language acceptance
# 
# * DFA union
# 
# * DFA unreachable state elimination
# 
# * DFA minimization
# 
# Many of these routines have been tested extensively, especially DFA minimization (this is in the context of RE to NFA to DFA to min-DFA).
# 
# The part that remains pertaining to DFA is conversion of DFA to regular expressions. That is taken up in another Jupter notebook. 

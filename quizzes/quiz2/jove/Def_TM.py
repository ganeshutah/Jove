
# coding: utf-8

# # Turing Machines

# This module encodes non-deterministic Turing Machines with a doubly-infinite tape (call it the "dub TM" :-) ). We begin with a tape containing exactly the given input and let the computation begin facing the left-end of the given input string.
# 
# The given input string could be empty (epsilon). This situation translates to the TM's initial head facing a sea of blanks on the tape -- both to its left and to its right. No amount of "sniff-check" will let you sniff anything other than a sea (of blanks).
# 
# Each attempt to ``fall off either end of the tape'' is met with an allocation of some number (currently 8) of extra blank characters. Halting configurations as well as paths leading to them are maintained. All executions are bounded by a constant __fuel__ that the user can progressively increase till the desired acceptances are seen (or the user surmises nontermination). This is like the gas in your tank! When you run out of gas, you are forced to halt.
# 
# We maintain nsteps as remaining "fuel" per thread (non-deterministic) of execution. When a thread runs out of fuel, it stops running. A run ends with a printout of the terminal configurations plus the fuel remaining per thread. This is ideal from the point of explaining nondeterministic runtimes. We elaborate now.
# 
# An NDTM accepts a string in nondeterminstic polynomial time (NP) if there is an accepting computational history of polynomial length. In our NDTM simulation, you'll see the remaining fuel per thread. Any thread with the least fuel consumption and still accepts is the one we go by in measuring runtimes!

# In[1]:

from jove.SystemImports       import *
from jove.TransitionSelectors import *


# ## Basic Definitions
# 
# Turing Machines are structures 
# 
#   $(Q, Sigma, Gamma, Delta, q0, B, F)$
#   
# where
# 
#  * $Q$       : Finite non-empty set of states
# 
#  * $Sigma$   : Finite non-empty input alphabet
# 
#  * $Gamma$   : Finite non-empty tape alphabet (subsumes Sigma, so that the user-given input can be written on the tape; also, $Gamma$ always includes $B$, representing an empty space (``blank'') on the tape).
#  
#    - Computations are set up by writing the user-given input on the tape
#    
#    - The portion of the tape before and after the user input is filled with an infinite **sea of blanks** (we allocate it on demand).
#    
#        - Note: In our TMs, the blank character 
#        is user-selectable. The preferred 
#          blank symbol is "." (dot).
# 
#  * $Delta$   : A transition function that takes a state, a current tape
#  symbol being scanned
# 
# $Delta$'s signature is
#        
# $(Q \times Gamma) \rightarrow P(Q \times Gamma \times \{L,R,S\} )$
# 
# This means that the TM, in state q, while scanning tape symbol s will choose one of the (q1, g, Dir) tripes. Here, q1 is the next control state, is the new tape symbol that replaces what's being looked at, and Dir is one of Left, Right, or Same, encoded by "L", "R", or "S". 
# 
# A TM is ``stuck'' if it cannot fire __any__ transition from a given configuration. Such terminal configurations are halting configurations with a __reject__ status. All final states are also terminal configurations with an __accept__ status.
#  
# 
# ## Computation wrt Instantaneous Descriptions (ID)
# 
# Let us define the transition function (transition table) as follows:
# 
# * { (q, g) : { (q1, g1, D1), (q2, g2, D2), ... }
# 
# An ID of a TM is, mathematically, a triple
# 
#      (q, tape, position-of-tape-being-ogled-at)
#  
# For our (more practical) TM, the ID is a quadruple
# 
#      (q, hi, tape, fuel)
#     
# where 
# 
# - q is the present control state of the TM,
# 
# - hi is the head index (into the tape, 
# treating index=0 as the leftmost position of the tape).
# 
# - tape is the string that constitutes the tape, and
# 
# - fuel is the amount of "fuel" (computational steps) left
#   for this ID. 
#   
#     - Note that  when we split IDs, we convey the same
#       amount of remaining fuel to the threads being spawned.
# 
#  
# 
# Examples now follow, and they will drive home these ideas.
# 

#  Consistency checker(s) for TM have gone to DotBashers

# In[2]:

TAPE_ALLOC_SIZE = 8
def step_tm(T, q_hi_tape_fuel, path, haltList):
   """Helper for run_tm
      ---
      Inputs: * A TM T
              * An ID -- a tuple q_hi_tape_fuel capturing
              - q:  the present state of the TM
              - hi: the head index that is initialized to 0.
              - tape: The full string representing the tape. 
                tape[0] is the element at the leftmost position.
              - fuel: The amount of fuel left in this thread.
                When an NDTM splits, it imparts the currently
                remaining amount of fuel to all the progeny 
                threads.
              * A path that leads to q_hi_tape_fuel
              * A haltList of halting configurations that 
                builds up. Each halting config kept with path
                leading to it.
      Output: A pair (l_id_path, nhaltList)
              * l_id_path is a list  
                 [ ((nq, nhi, ntape, nfuel), npath) ]   
               where (nq, nhi, ntape, nfuel) is the new ID 
               and npath is the extended path reaching it.
              * nhaltList is the extended halting config list.
      Detail: When the head is about to fall off either end, we 
              allocate TAPE_ALLOC_SIZE blank characters, thus keeping
              the head on the tape.
   """ 
   (q, hi, tape, fuel) = q_hi_tape_fuel
   extpath             = path + [q_hi_tape_fuel]
   nl_id_path          = []
   
   if (hi == len(tape)):
       # Going beyond end of allocated tape; allocate more!
       print("Allocating ", TAPE_ALLOC_SIZE, " tape cells to the RIGHT!")
       tape = tape + T["B"]*TAPE_ALLOC_SIZE
       
   if (q, tape[hi]) not in T["Delta"]:
       # No move on (q, tape[hi]), so record halt lset; return
       return (nl_id_path, haltList + [(q_hi_tape_fuel, path)])
              
   l_nq_ng_dirn      = T["Delta"][(q, tape[hi])] 
   
   for nq_ng_dirn in l_nq_ng_dirn:
       (nq, ng, dirn) = nq_ng_dirn
       # Head attempts to move to the left of the left-end
       if (hi==0) and (dirn=="L"):
           print("Allocating ", TAPE_ALLOC_SIZE, " tape cells to the LEFT!")
           ntape = T["B"]*TAPE_ALLOC_SIZE + ng + tape[1:]  
           nhi   = TAPE_ALLOC_SIZE - 1  # Do the left move too!
       else:
           ntape = tape[0:hi] +  ng  + tape[hi+1:len(tape)]
           nhi = (hi+1 if dirn=="R"
                  else ((hi-1) if dirn=="L" 
                        else (hi if dirn=="S"
                             else print("Illegal direction!"))))
          
       if (fuel > 0):
           nl_id_path += [((nq, nhi, ntape, fuel-1), extpath)]
               
   return (nl_id_path, haltList)


      


# # Routines to run TM
# 
# We now devise a routine to run an NDTM.

# In[3]:

def run_tm(T, tape, fuel):
    """Helper for explore_tm
       ---
       Given a TM T and a tape, run the TM for fuel steps
       (e.g., gallons of gas in your tank), 
       collecting all halting configurations. 
       
       Return a triple
       (id_path_pairs, haltSet, nfuel) of
        - all resulting id_path_pairs 
        - the final haltSet
        - the remaining fuel
       This way, one can find all accepting and rejecting 
       IDs in the final haltSet and print paths to them.
    """
    q_hi_tape_fuel = (T["q0"], 0, tape, fuel)
    path         = []
    l_id_path    = [ (q_hi_tape_fuel, path) ]
    haltList     = [ ]
    l_trunc_path = [] # List of truncated paths
    
    while (l_id_path != []):
        (q_hi_tape_fuel, path)  = l_id_path[0] 
        (nq, nhi, ntape, nfuel) = q_hi_tape_fuel
        if (nfuel > 0):
            (nl_id_path, haltList) = step_tm(T, q_hi_tape_fuel, 
                                             path, haltList)
            l_id_path = nl_id_path + l_id_path[1:]
        else:
            l_trunc_path += [path]
            l_id_path = l_id_path[1:]
    
    return (l_trunc_path, haltList)


# In[4]:

def explore_tm(T, tape, nsteps):
    """A handy routine to print the result of run_tm plus making 
       future extensions to explore run-results.
    """
    (l_trunc_path, haltList) = run_tm(T, tape, nsteps)
    if (haltList == []):
        print("TM hasn't halted.")
        print("The truncated paths so far are as follows.")
        for trunc_path in l_trunc_path:
            print(trunc_path)
    else:
        if (l_trunc_path != []):
            print("There are still ", len(l_trunc_path), "truncated paths.")
        print("Detailing the halted configs now.")
        
        for (haltConfig, path) in haltList:
            (haltState, head, tape, fuel) = haltConfig
            if (haltState in T["F"]):
                print("Accepted at ", haltConfig)
            else:
                print("Rejected at ", haltConfig)
            print(" via .. ")
            for id in path:
                print(" ->", end="")
                print(id)
            print(" ->", end="")
            print(haltConfig)
   


# In[5]:

print('''You may use any of these help commands:
help(step_tm)
help(run_tm)
help(explore_tm)
''')


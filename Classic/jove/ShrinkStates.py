
# coding: utf-8

# Shrinks are needed for DFA and NFA state names in many contexts. House those shrinks in here. These shrinks don't attempt to mk_dfa or mk_nfa as those are "higher level" functionalities. They instead return a suitable dict.

# In[ ]:

from jove.SysConsts           import STATENAME_NFAMAX #--gone: STATENAME_MAXSIZE
from jove.StateNameSanitizers import isNotBH
from jove.TransitionSelectors import fn_trans


# In[1]:

def shrink_dfastates(D, STATENAME_MAXSIZE=20): # Made default param now!
   """In : D (DFA : partially consistent)
      Out: A DFA quintuple (Q,Sigma,Delta,q0,F).
      
      Given a DFA, shrink its state names if
      too long. Return the quintuple for a DFA.
   """
   maxStNam = max(map(len, D["Q"]))
   if maxStNam <= STATENAME_MAXSIZE:
       return D
   
   # Even if one state gets too long, we rename all state names.
   # This policy could be changed in future.

   # Sorting the list of states so that we hash 'em the same way
   # into the stateDict
   #
   StateL = list(D["Q"])
   StateL.sort()
   
   # Keep a state-renaming dictionary around... it stores the 
   # shrunken state names. When we return a DFA, we re-christen 
   # all state names to their shrunken counterparts.

   stateDict = {'BH' : 'BH'}
   for i in range(0, len(StateL)):
       for State_i in StateL:
           if (State_i == StateL[i]) and isNotBH(StateL[i]):
               stateDict[State_i] = ("St" + str(i))
               
   NewQ     = { stateDict[q] for q in D["Q"] }
   NewDelta = { (stateDict[a], b) : stateDict[c] 
                for ((a,b),c) in fn_trans(D["Delta"]) } 
   Newq0    = stateDict[D["q0"]]
   NewF     = { stateDict[f] for f in D["F"] }
   return {"Q"     : NewQ,
           "Sigma" : D["Sigma"],
           "Delta" : NewDelta,
           "q0"    : Newq0,
           "F"     : NewF}
  

def shrink_nfastates(N):
   """In : N (NFA)
      Out: NFA quintuple with state names shrunk.
   """
   maxStNam = max(map(len, N["Q"]))
   if maxStNam <= STATENAME_NFAMAX:   # Need smaller constant for NFA
       return N
   StateL = list(N["Q"])
   stateDict = { State_i : ("St" + str(i)) 
                    for i in range(0, len(StateL))
                    for State_i in StateL 
                    if State_i == StateL[i] }
   NewQ     = { stateDict[q] for q in N["Q"] }
   NewDelta = { (stateDict[a], b) : 
                 {stateDict[c] 
                  for c in C} 
                  for ((a,b),C) in N["Delta"].items() } 
   NewQ0    = { stateDict[q0] for q0 in N["Q0"] }
   NewF     = { stateDict[f] for f in N["F"] }
   return {"Q"     : NewQ,
           "Sigma" : N["Sigma"],
           "Delta" : NewDelta,
           "Q0"    : NewQ0,
           "F"     : NewF} 

def mkSSnam(S):
   """In : S (a set of states, possibly empty)
      Out: A string representing the set of states.
      Make the DFA state names the same as the NFA state 
      names bashed together. 
   """
   if S==set({}):
       return "BH"
   else:
       S1 = list(S)
       S1.sort()
       return "".join(
           map(lambda x: 
               "{" if x=="[" else "}" if x=="]" else x, 
               str(S1))) # to please "dot"


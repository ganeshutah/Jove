
# coding: utf-8

# In[1]:

from Imports.DotBashers import *
from Imports.Def_md2mc import *
from Imports.Def_NFA   import *


# In[2]:

nfa_ends0101 = md2mc(src="File", fname="nfafiles/endsin0101.nfa")


# In[3]:

nfa_ends0101


# In[4]:

dotObj_nfa(nfa_ends0101)


# In[5]:

NFA_fig61ab = { 'Q': {'I', 'S0', 'S1', 'S2', 'F'},
                'Sigma': {'0', '1'},
                'Delta': { # 
                             ('I', '0')  : {'I'},
                             ('I', '1')  : {'I', 'S0'},
                             ('I', '')   : {'S0'},
                             #
                             ('S0', '1') : {'S1'},
                             #
                             ('S1', '0') : {'S2'},
                             ('S1', '1') : {'S2'},
                             #
                             ('S2', '0') : {'F'},
                             ('S2', '1') : {'F'},
               },
                  'Q0': {'I'}, 
                  'F' : {'F'}   
                }
NFA_fig61ab


# In[6]:

step_nfa(NFA_fig61ab, "I", "")


# In[7]:

step_nfa(NFA_fig61ab, "I", "0")


# In[8]:

step_nfa(NFA_fig61ab, "I", "1")


# In[9]:

# NFA for ((aa)+(bbb)+)+
NFA23 = { 'Q': {'A0','A1','B0','B1','B2','F'},
          'Sigma': {'0', '1'},
          'Delta': { # 
                     ('A0', '0') : {'A1'},
                     ('A1', '0') : {'B0'},
                     #
                     ('B0', '')  : {'A0'},
                     #
                     ('B0', '1') : {'B1'},
                     ('B1', '1') : {'B2'},
                     ('B2', '1') : {'F'},
                     # 
                     ('F', '')   : {'B0'},
                   },
          'Q0': {'A0'}, 
          'F' : {'F'}   
        }
Source(dot_nfa(NFA23))


# In[10]:

Source(dot_nfa(NFA23, visible_eps=True))


# In[11]:

NFA23["Q0"]


# In[12]:

run_nfa(NFA23, NFA23["Q0"], '0', True)


# In[13]:

Source(dot_nfa(NFA_fig61ab))


# In[14]:

run_nfa(NFA23, set({'A0'}), '', True)


# In[15]:

Eclosure(NFA_fig61ab, {"I"})


# In[16]:

Eclosure(NFA_fig61ab, {"S0"})


# In[17]:

run_nfa(NFA_fig61ab,{"I"},"")


# In[18]:

run_nfa(NFA_fig61ab,{"I"},"", True)


# In[19]:

run_nfa(NFA_fig61ab,{"I"},"0")


# In[20]:

run_nfa(NFA_fig61ab,{"I"},"1")


# In[21]:

run_nfa(NFA_fig61ab,{"I"},"100")


# In[22]:

run_nfa(NFA_fig61ab,{"I"},"100", True)


# In[23]:

run_nfa(NFA_fig61ab,{"I"},"00110")


# In[24]:

run_nfa(NFA_fig61ab,{"I"},"00110", True)


# In[25]:

accepts_nfa(NFA_fig61ab, "")


# In[26]:

accepts_nfa(NFA_fig61ab, "", True)


# In[27]:

accepts_nfa(NFA_fig61ab, "0", True)


# In[28]:

accepts_nfa(NFA_fig61ab, "100", True)


# In[29]:

dotObj_nfa(NFA23, visible_eps=True, nfaName="NFA23")


# In[30]:

dotObj_nfa(NFA23, visible_eps=False, nfaName="NFA23")


# In[31]:

n2DFA23 = nfa2dfa(NFA23)
dotObj_dfa(n2DFA23, "n2dNFA23")


# In[32]:

n2DFA61 = nfa2dfa(NFA_fig61ab)
dotObj_dfa(n2DFA61, "n2dNFA_fig61ab")


# In[33]:

dotObj_nfa(NFA_fig61ab,visible_eps=False,nfaName="NFA_fig61ab")


# In[34]:

dotObj_nfa(NFA_fig61ab,visible_eps=True,nfaName="NFA_fig61ab")


# In[35]:

dotObj_dfa(nfa2dfa(NFA_fig61ab), 'n1')


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

# In[36]:

def inSets(D,trg,ch):
    """In : D   = partially consistent dfa,
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


# In[37]:

DFA34 = { 'Q': {'A', 'IF', 'B'},
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
dotObj_dfa(DFA34, "DFA34")


# In[38]:

DFA34_rev = rev_dfa(DFA34)
dotObj_nfa(DFA34_rev, "DFA34_rev")


# In[39]:

DFA34_rev_det = nfa2dfa(DFA34_rev)
dotObj_dfa(DFA34_rev_det, "DFA34_rev_det")


# In[40]:

DFA34_rev_det_rev = rev_dfa(DFA34_rev_det)
dotObj_nfa(DFA34_rev_det_rev, "DFA34_rev_det_rev")


# In[41]:

DFA34_rev_det_rev_det = nfa2dfa(DFA34_rev_det_rev)
dotObj_dfa(DFA34_rev_det_rev_det, "DFA34_rev_det_rev_det")


# __TRY NEW EXAMPLE HERE__

# In[42]:

dotObj_dfa(n2DFA23, "n2DFA23")


# In[43]:

rev_n2DFA23 = rev_dfa(n2DFA23)
dotObj_nfa(rev_n2DFA23, "rev23")


# In[44]:

det_rev_n2DFA23 = nfa2dfa(rev_dfa(n2DFA23))
dotObj_nfa(rev_n2DFA23, "rev23")


# In[45]:

n2DFA23
dotObj_dfa(nfa2dfa(rev_dfa(nfa2dfa(rev_dfa(n2DFA23)))), "rdrd")


# In[46]:

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

dotObj_dfa(D34bl, "D34bl")


# In[47]:

dotObj_dfa(nfa2dfa(rev_dfa(nfa2dfa(rev_dfa(D34bl)))), "D34bl_rdrd")


# In[48]:

nfaMultiQ0 = md2mc('''
NFA
I0 : a | b | c -> A, B
I0 : c -> F
I1 : a | b -> A, B
A  : c -> F
B  : d -> F
''')


# In[49]:

dotObj_nfa(nfaMultiQ0)


# In[50]:

dfaMQ0 = nfa2dfa(nfaMultiQ0)


# In[51]:

dotObj_dfa(dfaMQ0)


# In[52]:

dotObj_nfa(rev_dfa(dfaMQ0))


# In[53]:

help(min_dfa_brz)


# In[54]:

dotObj_dfa(min_dfa_brz(dfaMQ0))


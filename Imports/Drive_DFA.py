
# coding: utf-8

# In[1]:

from Imports.DotBashers import *
from Imports.Def_md2mc import *
from Imports.Def_DFA   import *


# In[2]:

ev0end1 = md2mc('''
DFA
I : 0 -> A
A : 0 | 1 -> I
I : 1 -> F
F : 0 | 1 -> I
''')


# In[3]:

doev0end1 = dotObj_dfa(ev0end1)


# In[4]:

ev0end1


# In[5]:

doev0end1.source


# In[6]:

is_partially_consistent_dfa(ev0end1)


# In[7]:

tev0end1 = totalize_dfa(ev0end1)


# In[8]:

dotObj_dfa_w_bh(tev0end1)


# In[9]:

ev0end1


# In[10]:

ev0 = md2mc('''
DFA
IF : 0 -> A
A  : 0 -> IF
''')


# In[11]:

ev0


# In[12]:

dev0 = dotObj_dfa(ev0)


# In[13]:

dev0


# In[14]:

dev0.source


# In[15]:

dev0


# In[16]:

ev0_bh =  addtosigma_dfa(ev0, set({'1'}))


# In[17]:

ev0_bh


# In[18]:

ev0_bh_totalize = totalize_dfa(ev0_bh)


# In[19]:

ev0_bh


# In[20]:

do_ev0_tot = dotObj_dfa_w_bh(ev0_bh_totalize)


# In[21]:

do_ev0_tot.source


# In[22]:

do_ev0_tot


# <span style="color:blue"> **Here is how we will represent a DFA in Python (taking Figure 3.4's example from the book). You can clearly see how the traits of the DFA are encoded. We prefer a Python dictionary, as it supports a number of convenient operations, and also one can add additional fields easily. ** </span>

# In[23]:

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


# <span style="color:blue"> **We can now write routines to print DFA using dot. The main routines are listed below.** </span>
# 
# * dot_dfa_w_bh : lists all states of a DFA including black-hole states
# * dot_dfa      : lists all isNotBH states (see below for a defn), i.e. suppress black-holes
#      - Usually there are too many transitions to them and that clutters the view
#      

# ======

# In[24]:

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

# In[25]:

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


# Let us test functions step_dfa, run_dfa, and accepts_dfa

# In[26]:

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


# In[27]:

dotObj_dfa(DFA_fig34, "DFA_fig34")


# In[28]:

# Run a complementation test
DFA_fig34_comp = comp_dfa(DFA_fig34)
dotObj_dfa(DFA_fig34_comp, "DFA_fig34_comp")
dotObj_dfa(DFA_fig34)
dotObj_dfa(DFA_fig34_comp, "DFA_fig34_comp")


# In[29]:

dotObj_dfa(DFA_fig34_comp)


# In[30]:

# One more test
du     = union_dfa(DFA_fig34, DFA_fig34_comp)
dotObj_dfa(du, "orig union")
pdu    = pruneUnreach(du)
pdu
pduObj = dotObj_dfa(pdu, "union of 34 and comp")
pduObj



# In[31]:

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


# In[32]:

langeq_dfa(D34,D34bl,False)


# In[33]:

iso_dfa(D34,D34bl)


# In[34]:

DFA_fig34
d34 = DFA_fig34
d34


# In[35]:

d34c = DFA_fig34_comp
d34c


# In[36]:

iso_dfa(d34,d34)


# In[37]:

iso_dfa(d34,d34c)


# In[38]:

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


# In[39]:

dotObj_dfa(d34v1)


# In[40]:

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


# In[41]:

iso_dfa(d34,d34v1)


# In[42]:

iso_dfa(d34,d34v2)


# In[43]:

iso_dfa(d34v1,d34v2)


# In[44]:

div1 = pruneUnreach(intersect_dfa(d34v1,d34v2))
dotObj_dfa(div1)


# In[45]:

div2 = pruneUnreach(union_dfa(d34v1,d34v2))
dotObj_dfa(div2)


# In[46]:

iso_dfa(div1,div2)


# In[47]:

langeq_dfa(div1,div2,True)


# In[48]:

d34bl = dotObj_dfa(D34bl, "D34bl")
d34bl # Display it!


# In[49]:

iso_dfa(D34,D34bl)


# In[50]:

langeq_dfa(D34,D34bl)


# #### 

# In[51]:

du


# In[52]:

dotObj_dfa(pruneUnreach(D34bl), "D34bl")


# In[53]:

### DFA minimization (another example)


# In[54]:

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

# In[55]:

dotObj_dfa(min_dfa(Bloat1), "shrunkBloat1")


# In[56]:

prd34b1 = pruneUnreach(D34bl)


# In[57]:

dotObj_dfa(prd34b1, "prd34b1")


# In[58]:

dotObj_dfa(min_dfa(prd34b1), "prd34b1min")


# In[59]:

third1dfa=md2mc(src="File", fname="dfafiles/thirdlastis1.dfa")


# In[60]:

third1dfa


# In[61]:

dotObj_dfa(third1dfa)


# In[62]:

ends0101 ="DFA I     : 0 -> S0 I     : 1 -> I S0    : 0 -> S0 S0    : 1 -> S01 S01   : 0 -> S010 S01   : 1 -> I S010  : 0 -> S0 S010  : 1 -> F0101 F0101 : 0 -> S010 F0101 : 1 -> I "


# In[63]:

ends0101


# In[64]:

dfaends0101=md2mc(ends0101)


# In[65]:

dfaends0101


# In[66]:

dped1 = md2mc(src="File", fname="dfafiles/pedagogical1.dfa")
#dfafiles/pedagogical1.dfa


# In[67]:

dped1


# In[68]:

dotObj_dfa(dped1)


# In[69]:

dotObj_dfa(md2mc(ends0101))


# In[70]:

thirdlastis1=md2mc(src="File", fname="dfafiles/thirdlastis1.dfa")
#dfafiles/thirdlastis1.dfa


# In[71]:

thirdlastis1


# In[72]:

dotObj_dfa(thirdlastis1)


# In[73]:

dped1=md2mc(src="File", fname="dfafiles/pedagogical2.dfa")
#dfafiles/pedagogical2.dfa


# In[74]:

dotObj_dfa(dped1)


# In[75]:

secondLastIs1 = md2mc('''
!!------------------------------------------------------------
!! This DFA looks for patterns of the form ....1.
!! i.e., the second-last (counting from the end-point) is a 1
!!
!! DFAs find such patterns "very stressful to handle",
!! as they are kept guessing of the form  'are we there yet?'
!! 'are we seeing the second-last' ?
!! They must keep all the failure options at hand. Even after
!! a 'fleeting glimpse' of the second-last, more inputs can
!! come barreling-in to make that "lucky 1" a non-second-last.
!!
!! We take 7 states in the DFA solution.
!!------------------------------------------------------------

DFA
!!------------------------------------------------------------
!! State : in ->  tostate !! comment
!!------------------------------------------------------------

I   :  0 ->  S0  !! Enter at init state I
I   :  1 ->  S1  !! Record bit seen in state letter
                     !! i.e., S0 means "state after seeing a 0"
			 
S0  :  0 ->  S00 !! continue recording input seen
S0  :  1 ->  S01 !! in state-letter. This is a problem-specific
                 !! way of compressing the input seen so far.

S1  :  0 ->  F10 !! We now have a "second last" available!
S1  :  1 ->  F11 !! Both F10 and F10 are "F" (final)

S00 :  0 ->  S00 !! History of things seen is still 00
S00 :  1 ->  S01 !! Remember 01 in the state

S01 :  0 ->  F10 !! We again have a second-last of 1
S01 :  1 ->  F11 !! We are in F11 because of 11 being last seen

F10 :  0 ->  S00 !! The second-last 1 gets pushed-out
F10 :  1 ->  S01 !! The second-last 1 gets pushed-out here too

F11 :  0 ->  F10 !! Still we have a second-last 1
F11 :  1 ->  F11 !! Stay in F11, as last two seen are 11

!!------------------------------------------------------------
''')


# In[76]:

from math import floor, log, pow
def nthnumeric(N, Sigma={'a','b'}):
    """Assume Sigma is a 2-sized list/set of chars (default {'a','b'}). 
       Produce the Nth string in numeric order, where N >= 0.
       Idea : Given N, get b = floor(log_2(N+1)) - need that 
       many places; what to fill in the places is the binary 
       code for N - (2^b - 1) with 0 as Sigma[0] and 1 as Sigma[1].    
    """
    if (type(Sigma)==set):
       S = list(Sigma)
    else:
       assert(type(Sigma)==list
       ), "Expected to be given set/list for arg2 of nthnumeric."
       S = Sigma
    if(N==0):
        return ''
    else:
        width = floor(log(N+1, 2))
        tofill = int(N - pow(2, width) + 1)
        relevant_binstr = bin(tofill)[2::] # strip the 0b 
                                           # in the leading string
        len_to_makeup = width - len(relevant_binstr)
        return (S[0]*len_to_makeup + 
                shomo(relevant_binstr,
                      lambda x: S[1] if x=='1' else S[0]))


# In[77]:

nthnumeric(20,['0','1'])


# In[78]:

run_dfa(secondLastIs1, '0101')


# In[79]:

accepts_dfa(secondLastIs1, '0101')


# In[80]:

tests = [ nthnumeric(i, ['0','1']) for i in range(12) ]
for t in tests:
    if accepts_dfa(secondLastIs1, t):
        print("This DFA accepts ", t)
    else:
        print("This DFA rejects ", t)


# In[81]:

help(run_dfa)


# This is an extensive illustration of union, intersection and complementation, DFA minimization, isomorphism test, language equivalence test, and an application of DeMorgan's law

# In[84]:

dfaOdd1s = md2mc('''
DFA
I : 0 -> I
I : 1 -> F
F : 0 -> F 
F : 1 -> I
''')


# In[85]:

dotObj_dfa(dfaOdd1s)


# In[86]:

ends0101 = md2mc('''
DFA 
I     : 0 -> S0  
I     : 1 -> I 
S0    : 0 -> S0 
S0    : 1 -> S01 
S01   : 0 -> S010 
S01   : 1 -> I 
S010  : 0 -> S0 
S010  : 1 -> F0101 
F0101 : 0 -> S010 
F0101 : 1 -> I 
''')


# In[87]:

dotObj_dfa(ends0101)


# In[88]:

odd1sORends0101 = union_dfa(dfaOdd1s,ends0101)


# In[89]:

dotObj_dfa(odd1sORends0101)


# In[90]:

Minodd1sORends0101 = min_dfa(odd1sORends0101)


# In[92]:

dotObj_dfa(Minodd1sORends0101)


# In[94]:

iso_dfa(odd1sORends0101, Minodd1sORends0101)


# In[96]:

langeq_dfa(odd1sORends0101, Minodd1sORends0101)


# In[97]:

odd1sANDends0101 = intersect_dfa(dfaOdd1s,ends0101)


# In[98]:

dotObj_dfa(odd1sANDends0101)


# In[99]:

Minodd1sANDends0101 = min_dfa(odd1sANDends0101)


# In[100]:

dotObj_dfa(Minodd1sANDends0101)


# In[101]:

CdfaOdd1s = comp_dfa(dfaOdd1s)


# In[102]:

Cends0101 = comp_dfa(ends0101)


# In[103]:

C_CdfaOdd1sORCends0101 = comp_dfa(union_dfa(CdfaOdd1s, Cends0101))


# In[104]:

dotObj_dfa(C_CdfaOdd1sORCends0101)


# In[106]:

MinC_CdfaOdd1sORCends0101 = min_dfa(C_CdfaOdd1sORCends0101)


# In[107]:

dotObj_dfa(MinC_CdfaOdd1sORCends0101)


# In[109]:

iso_dfa(MinC_CdfaOdd1sORCends0101, Minodd1sANDends0101)


# This shows how DeMorgan's Law applies to DFAs. It also shows how, using the tools provided to us, we can continually check our work.

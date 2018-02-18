
# coding: utf-8

# In[1]:

from Imports.DotBashers import *
from Imports.Def_DFA import *
from Imports.Def_NFA import *
from Imports.Def_RE2NFA import *
from Imports.Def_NFA2RE import *
from Imports.Def_md2mc import *


#  # Problem Set One

# 1) LOdd1Three0 : Set of strings over {0,1} with an odd # of 1s OR exactly three 0s. 
# 
# * Hint on how to arrive at the language:
# 
#   - develop NFAs for the two cases and perform their union. Obtain DFA
# 
#   - develop REs for the two cases and perform the union. 
# 
#   - Testing the creations:
# 
#     .   Come up with language for even # of 1s and separately for "other than three 0s". 
#  
#     .   Do two intersections. 
#  
#     .   Is the language empty?
# 
# 
# 2) Language of strings over {0,1} with exactly two occurrences of 0101 in it.
# 
#  * Come up with it directly (take overlaps into account, i.e. 010101 has two occurrences in it
# 
#  * Come up in another way
# 
# Notes:
# 
# * Most of the problem students will have in this course is interpreting English (technical English)
# 
# * So again, read the writeup at the beginning of Module6 (should be ready soon today) and work on using the tool.
# 
# 
# 
# 

# __Solutions__
# 
# 1) LOdd1Three0 : Set of strings over {0,1} with an odd # of 1s OR exactly three 0s. 
# 
# * Hint on how to arrive at the language:
# 
#   - develop NFAs for the two cases and perform their union. Obtain DFA
# 
#   - develop REs for the two cases and perform the union. 
# 
#   - Testing the creations:
# 
#     .   Come up with language for even # of 1s and separately for "other than three 0s". 
#  
#     .   Do two intersections. 
#  
#     .   Is the language empty?
# 
# 
# 2) Language of strings over {0,1} with exactly two occurrences of 0101 in it.
# 
#  * Come up with it directly (take overlaps into account, i.e. 010101 has two occurrences in it
# 
#  * Come up in another way
# 
# Notes:
# 
# * Most of the problem students will have in this course is interpreting English (technical English)
# 
# * So again, read the writeup at the beginning of Module6 (should be ready soon today) and work on using the tool.
# 
# 
# 
# 

# In[2]:

RE_Odd1s  = "0* 1 0* (1 0* 1 0*)*"
NFA_Odd1s = re2nfa(RE_Odd1s)
DO_Odd1s  = dotObj_dfa(min_dfa(nfa2dfa(NFA_Odd1s)))
DO_Odd1s


# In[3]:

RE_Ex3z = "1* 0 1* 0 1* 0 1* "
NFA_Ex3z = re2nfa(RE_Ex3z)
DO_Ex3z  = dotObj_dfa(min_dfa(nfa2dfa(NFA_Ex3z)))
DO_Ex3z


# In[4]:

RE_O13z  = "0* 1 0* (1 0* 1 0*)* + 1* 0 1* 0 1* 0 1* "
NFA_O13z = re2nfa(RE_O13z)
MD_O13z  = min_dfa(nfa2dfa(NFA_O13z))
DO_O13z  = dotObj_dfa(MD_O13z)
DO_O13z


# In[5]:

RE_O13z  = "0* 1 0* (1 0* 1 0*)* + 1* 0 1* 0 1* 0 1* "
NFA_O13z = re2nfa(RE_O13z)
NMD_O13z  = nfa2dfa(NFA_O13z)
MD_O13zB  = min_dfa_brz(NMD_O13z)
DO_O13zB  = dotObj_dfa(MD_O13zB)
DO_O13zB


# In[6]:

iso_dfa(MD_O13z,MD_O13zB)


# In[7]:

langeq_dfa(NMD_O13z,MD_O13z)


# In[8]:

iso_dfa(NMD_O13z, MD_O13z)


# In[9]:

dotObj_dfa(min_dfa(nfa2dfa(re2nfa("''"))))


# In[10]:

D1 = min_dfa(nfa2dfa(re2nfa("aa")))
dotObj_dfa(D1)


# In[11]:

D2 = min_dfa(nfa2dfa(re2nfa("bb")))
dotObj_dfa(D2)


# In[12]:

D1


# In[13]:

D2


# In[14]:

D1or2 = min_dfa(union_dfa(D1,D2))
D1or2p = pruneUnreach(D1or2)
dotObj_dfa(D1or2)


# In[15]:

dotObj_dfa(D1or2p)


# In[16]:

D1and2 = min_dfa(intersect_dfa(D1,D2))
D1and2p = pruneUnreach(D1and2)
dotObj_dfa(D1and2)


# In[17]:

dotObj_dfa(D1and2p)


# In[18]:

d1=nfa2dfa(re2nfa("abcde"))
d2=nfa2dfa(re2nfa("abced"))
langeq_dfa(d1,d2,True)


# In[19]:

dotObj_dfa(d1)


# In[20]:

dotObj_dfa(d2)


# In[21]:

d1a=nfa2dfa(re2nfa("aa*+bc"))
d2a=nfa2dfa(re2nfa("a(a*+bc)"))
langeq_dfa(d1a,d2a,True)


# In[22]:

dotObj_dfa(d1a)


# In[23]:

dotObj_dfa(d2a)


# In[24]:

d1b=nfa2dfa(re2nfa("aaa*+aa*bc+bcaa*+bcbc"))
d2b=nfa2dfa(re2nfa("(aa*+bc)(aa*+bc)"))
langeq_dfa(d1b,d2b,True)


# In[25]:

dotObj_dfa(d1b)


# In[26]:

dotObj_dfa(d2b)


# In[27]:

iso_dfa(d1b,d2b)


# In[28]:

d1c=min_dfa(d1b)


# In[29]:

d2c=min_dfa(d2b)


# In[30]:

iso_dfa(d1c,d2c)


# In[31]:

dotObj_dfa(d1c)


# In[32]:

dotObj_dfa(d2c)


# In[33]:

d1d=nfa2dfa(re2nfa("aaa*+aa*bc+bcaaa*+bcbc"))
d2d=nfa2dfa(re2nfa("(aa*+bc)(aa*+bc)"))
langeq_dfa(d1d,d2d,True)


# In[34]:

d1d=nfa2dfa(re2nfa("a a a*+a a* b c+ b c a a a*+b c b c"))
d2d=nfa2dfa(re2nfa("(a a*+b c)(a a*+b c)"))
langeq_dfa(d1d,d2d,True)


# In[35]:

dotObj_dfa(d1d)


# In[36]:

dotObj_dfa(d2d)


# In[37]:

d1d=nfa2dfa(re2nfa("james*+bond*"))
dotObj_dfa(d1d)


# In[38]:

d1d=nfa2dfa(re2nfa("ja mes*+bo nd*"))
dotObj_dfa(d1d)


# In[39]:

d1d=nfa2dfa(re2nfa("''"))
dotObj_dfa(d1d)


# In[40]:

help(md2mc)


# In[41]:

test = md2mc(src="File", fname="nfafiles/endsin0101.nfa")
dotObj_nfa(test)


# In[42]:

# NFA for 0101 within hamming dist of 2
nfamd1 = md2mc(src="File", fname="nfafiles/nfa0101h2.nfa")
dotObj_nfa(nfamd1)


# In[43]:

dfamd1=nfa2dfa(nfamd1)
dotObj_dfa(dfamd1)


# In[44]:

m1=min_dfa(dfamd1)


# In[45]:

m2=min_dfa_brz(dfamd1)


# In[46]:

dotObj_dfa(m1)


# In[47]:

dotObj_dfa(m2)


# In[ ]:




# In[48]:

iso_dfa(m1,m2)


# In[49]:

help(del_gnfa_states)


# In[50]:

gnfamd1=mk_gnfa(nfamd1)
dotObj_gnfa(gnfamd1)


# In[51]:

(Gfinal, dotObj_List, final_re_str) = del_gnfa_states(gnfamd1)


# In[52]:

dotObj_gnfa(Gfinal)


# In[53]:

dotObj_List[0]


# In[54]:

dotObj_List[1]


# In[55]:

dotObj_List[2]


# In[56]:

dotObj_List[3]


# In[57]:

dotObj_List[4]


# In[58]:

len(dotObj_List)


# In[59]:

dotObj_List[11]


# In[60]:

final_re_str


# In[61]:

fullcircle=min_dfa(nfa2dfa(re2nfa(final_re_str)))


# In[62]:

dotObj_dfa(fullcircle)


# In[63]:

h2_from_re = min_dfa(nfa2dfa(re2nfa("(0+1)(0+1)01 + (0+1)1(0+1)1 + (0+1)10(0+1) + 0(0+1)(0+1)1 + 0(0+1)0(0+1) + 01(0+1)(0+1)")))


# In[64]:

dotObj_dfa(h2_from_re)


# In[65]:

iso_dfa(fullcircle,h2_from_re)


# In[66]:

epsre = dotObj_nfa(re2nfa("''"), True)
epsre.source


# In[67]:

epsre


# In[68]:

are = dotObj_nfa(re2nfa("a"), True)
are.source


# In[69]:

are


# In[70]:

aplusbre = dotObj_nfa(re2nfa("a+b"), True)
aplusbre.source


# In[71]:

aplusbre


# In[72]:

abre = dotObj_nfa(re2nfa("ab"), True)
abre.source


# In[73]:

abre


# In[74]:

arestar = dotObj_nfa(re2nfa("a*"), True)
arestar.source


# In[75]:

arestar


# In[76]:

aplusbstar = dotObj_nfa(re2nfa("(a+b)*"), True)
aplusbstar.source


# In[77]:

aplusbstar


# In[78]:

aplusb_aplusbstar = dotObj_nfa(re2nfa("(a+b)(a+b)*"), True)
aplusb_aplusbstar.source


# In[79]:

aplusb_aplusbstar


# In[80]:

aplusb_aplusb = dotObj_nfa(re2nfa("(a+b)(a+b)"), True)


# In[81]:

aplusb_aplusb


# In[82]:

aplusb_aplusb.source


# In[83]:

DOodd1s_or_30s = dotObj_nfa(re2nfa("0* 1 0* (1 0* 1 0*)* + 1* 0 1* 0 1* 0 1* "), True)


# In[84]:

DOodd1s_or_30s


# In[85]:

DOodd1s_or_30s.source


# In[ ]:




# In[86]:

DOodd1s_or_30s_mind = dotObj_dfa(min_dfa(nfa2dfa(re2nfa("0* 1 0* (1 0* 1 0*)* + 1* 0 1* 0 1* 0 1* "))))
DOodd1s_or_30s_mind


# In[87]:

DOodd1s_or_30s_mind.source


# # Designing DFA that accept within a Hamming Distance

# Given a regular language, say (0+1)* 0101 (0+1)* (i.e., all bit-strings with an occurrence of 0101 in it), let us come up with 
# 
# 1. An RE that represents strings within a Hamming distance of 2 from strings in this language
# 
# 2. An NFA that represents strings within a Hamming distance of 2 from strings in this language
# 

# In[88]:

h2_0101_re = ("(0+1)* ( (0+1)(0+1)01 +" + 
                      " (0+1)1(0+1)1 +" + 
                      " (0+1)10(0+1) +" + 
                      " 0(0+1)(0+1)1 +" +
                      " 0(0+1)0(0+1) +" +
                      " 01(0+1)(0+1) )" +
              "(0+1)*")


# In[89]:

h2_0101_re


# In[90]:

minD_h2_0101_re = min_dfa(nfa2dfa(re2nfa(h2_0101_re)))


# In[91]:

DO_minD_h2_0101_re = dotObj_dfa(minD_h2_0101_re)


# In[92]:

DO_minD_h2_0101_re


# In[93]:

DO_minD_h2_0101_re.source


# In[101]:

h2_0101_nfa_md = '''
NFA
!!--------------------------------------------
!! We are supposed to process (0+1)*0101(0+1)*
!! with up to two "dings" allowed
!!
!! Approach: Silently error-correct, but remember
!! each "ding" in a new state name.
!! After two dings, do not error-correct anymore
!!--------------------------------------------

!!-- pattern for (0+1)* is the usual
!!-- no error-correction needed here :-)
I : 0 | 1 -> I

!!-- Now comes the opportunity to exit I via 0101
!!-- The state names are A,B,C,D with ding-count
!!-- Thus A0 is A with 0 dings
!!-- C2 is C with 2 dings; etc

!!-- Ding-less traversal -- how lucky!
I  : 0 -> A0
A0 : 1 -> B0
B0 : 0 -> C0
C0 : 1 -> F
!!-- Phew, finally at F
F  : 0 | 1 -> F

!!-- First ding in any of these cases
I  : 1 -> A1
A0 : 0 -> B1
B0 : 1 -> C1
C0 : 0 -> F  !!-- ding-recording un-nec.; just goto F

!!-- Second ding in any of these cases
A1 : 0 -> B2
B1 : 1 -> C2
C1 : 0 -> F  !!-- ding-recording un-nec.; just goto F

!!-- No more dings allowed!
B2 : 0 -> C2
C2 : 1 -> F

!!-- Allow one-dingers to finish fine
A1 : 1 -> B1
B1 : 0 -> C1
C1 : 1 -> F

'''


# In[102]:

h2_0101_nfa = md2mc(h2_0101_nfa_md)


# In[103]:

DO_h2_0101_nfa = dotObj_nfa(h2_0101_nfa)
DO_h2_0101_nfa


# In[104]:

DO_h2_0101_nfa.source


# In[105]:

minD_h2_0101_nfa = min_dfa(nfa2dfa(h2_0101_nfa))
DO_minD_h2_0101_nfa = dotObj_dfa(minD_h2_0101_nfa)
DO_minD_h2_0101_nfa


# In[106]:

DO_minD_h2_0101_nfa.source


# In[108]:

iso_dfa(minD_h2_0101_re, minD_h2_0101_nfa)


# In[ ]:




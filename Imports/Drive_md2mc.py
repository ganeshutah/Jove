
# coding: utf-8

# In[1]:

from Imports.DotBashers  import *
from Imports.Def_md2mc   import *
from Imports.Def_DFA     import addtosigma_dfa, totalize_dfa


#  # This is now a universal markdown!

# This is now a markdown that supports all machines!

# # We begin with several examples

# In[2]:

ev0end1 = md2mc('''
DFA
I : 0 -> A
A : 0 | 1 -> I
I : 1 -> F
F : 0 | 1 -> I
''')
dotObj_dfa(ev0end1)


# In[3]:

ev0end1plus = addtosigma_dfa(ev0end1, {'2'})
ev0end1plus


# In[4]:

dotObj_dfa_w_bh(totalize_dfa(ev0end1plus))


# In[5]:

third1dfa=md2mc(src="File", fname="dfafiles/thirdlastis1.dfa")
dotObj_dfa(third1dfa)


# In[6]:

# An NFA with multiple initial states
nfaMultiQ0 = md2mc('''
NFA
I0 : a | b | c -> A, B
I0 : c -> F
I1 : a | b -> A, B
A  : c -> F
B  : d -> F
''')
dotObj_nfa(nfaMultiQ0)


# In[7]:

nfa_ends0101 = md2mc(src="File", fname="nfafiles/endsin0101.nfa")
dotObj_nfa(nfa_ends0101)


# In[8]:

# generates syntax error correctly: md2mc(src="File", fname="pdafiles/erroneous3.pda")


# # Code for DFA Markdown

# In[9]:

nfa_ends0101 = md2mc(src="File", fname="nfafiles/endsin0101.nfa")


# In[10]:

nfa_ends0101


# In[11]:

dotObj_nfa(nfa_ends0101)


# __What's needed now : More testing, more use!__

# In[12]:

third1dfa=md2mc(src="File", fname="dfafiles/thirdlastis1.dfa")


# In[13]:

third1dfa


# In[14]:

dotObj_dfa(third1dfa)


# In[15]:

pdasip=md2mc(src="File", fname="pdafiles/f27sip.pda")


# In[16]:

pdasip


# In[17]:

dotObj_pda(pdasip)


# In[18]:

dotObj_pda(pdasip, True)


# In[19]:

wwndtm=md2mc(src="File", fname="tmfiles/wwndtm.tm")


# In[20]:

wwndtm


# In[21]:

dotObj_tm(wwndtm)


# In[22]:

wpwtm = '''
TM 
!!---------------------------------------------------------------------------
!! This is a DTM for recognizing strings of the form w#w where w is in {0,1}*
!! The presence of the "#" serves as the midpoint-marker, thus allowing the
!! TM to deterministically match around it.
!! 
!!---------------------------------------------------------------------------

!!---------------------------------------------------------------------------
!! State : rd ; wr , mv -> tostates !! comment
!!---------------------------------------------------------------------------

Iq0     : 0  ; X  , R  -> q1      !! All 0s are converted to X, and matching
	       	       	  	  !! 0s are then sought to the right of the #

Iq0     : 0  ; Y  , R  -> q7      !! All 1s are converted to Y, and matching
	       	       	  	  !! 1s are then sought to the right of the #				  
				  
Iq0     : #  ; #  , R  -> q5      !! If we see # rightaway, we are in the
	       	       	  	  !! situation of having to match eps # eps

q1      : 0 ; 0,R | 1 ; 1,R -> q1 !! In q1, skip over the remaining 0s and 1s

q1      : #  ; #  , R  -> q2      !! But upon seeing a #, look for a matching
	       	       	  	  !! 0 (since we are in q2, we know this).

q2      : X ; X,R | Y ; Y,R -> q2 !! All X and Y are "past stuff" to skip over

q2      : 0  ; X  , L  -> q3      !! When we find a matching 0, turn that to
	       	       	  	  !! an X, and sweep left to do the next pass
				  
q3      : X ; X,L | Y ; Y,L -> q3 !! In q3, we move over all past X, Y

q3      : #  ; #  , L  -> q4      !! but when we reach the middle marker, we
	       	       	  	  !! know that the next action is to seek the
				  !! next unprocessed 0 or 1
				  
q4      : 0 ; 0,L | 1 ; 1,L -> q4 !! In q4, wait till we hit the leftmost 0/1

q4      : X ; X,R | Y ; Y,R -> Iq0 !! When we hit an X or Y, we know that we've
	      	      	       	  !! found the leftmost 0/1. Another pass begins.

q5	: X ; X,R | Y ; Y,R -> q5 !! In q5, we skip over X and Y (an equal number
	      	      	       	  !! of X and Y lie to the left of the #)
				  
q5      : .  ; .  , R  -> Fq6	  !! .. and we accept when we see a blank (.)

q7      : 0 ; 0,R | 1 ; 1,R -> q7 !! q7 is similar to q1

q7      : #  ; #  , R  -> q8      !! and q8 is similar to q2

q8      : X ; X,R | Y ; Y,R -> q8 

q8      : 0  ; X  , L  -> q9      !! and q9 is similar to q3

q9      : X ; X,L | Y ; Y,L -> q9 !! In q9, we move over all past X, Y

q9      : #  ; #  , L  -> q10     !! and q10 is similar to q4

q10      : 0 ; 0,L | 1 ; 1,L -> q10 !! In q10, wait till we hit the leftmost 0/1

q10      : X ; X,R | Y ; Y,R -> Iq0 !! When we hit an X or Y, we know that we've
	      	      	       	   !! found the leftmost 0/1. Another pass begins.

!!---------------------------------------------------------------------------
!! You may use the line below as an empty shell to populate for your purposes
!! Also serves as a syntax reminder for entering DFAs.
!!
!! State : r1 ; w1 , m1 | r2 ; w2 , m2 -> s1 , s2   !! comment
!!
!! ..    : .. ; .. , .. | .. ; .. , .. -> .. , ..  !!  ..
!!---------------------------------------------------------------------------
!!
!! Good commenting and software-engineering methods, good clean indentation,
!! grouping of similar states, columnar alignment, etc etc. are HUGELY
!! important in any programming endeavor -- especially while programming
!! automata. Otherwise, you can easily make a mistake in your automaton
!! code. Besides, you cannot rely upon others to find your mistakes, as
!! they will find your automaton code impossible to read!
!!
!!---------------------------------------------------------------------------
'''


# In[23]:

wpwmd = md2mc(wpwtm)


# In[24]:

do_wpwmd = dotObj_tm(wpwmd)


# In[25]:

#do_wpwmd.source


# In[26]:

wwndtm_do=dotObj_tm(wwndtm)


# In[27]:

#wwndtm_do.source


# In[28]:

do_wpwmd


# In[29]:

ev0end1 = md2mc('''
DFA
I : 0 -> A
I : 1 -> F
A : 0 | 1 -> I
F : 0 | 1 -> I
''')


# In[30]:

dotObj_dfa(ev0end1)


# In[31]:

pedpda = md2mc(src="File",fname="pdafiles/f27sip.pda")
dotObj_pda(pedpda)


# In[32]:

dotObj_pda(pedpda)


# In[33]:

pedpda


# In[34]:

pedpda = md2mc(src="File", fname="pdafiles/pedagogical2.pda")
dotObj_pda(pedpda)


# In[35]:

dotObj_tm(md2mc(src="File", fname="tmfiles/shift_left_tm.tm"))


# In[36]:

dotObj_tm(md2mc(src="File", fname="tmfiles/shift_right_tm.tm"))


# In[37]:

dotObj_tm(md2mc(src="File", fname="tmfiles/decimal_double_tm.tm"))


# In[38]:

dotObj_tm(md2mc(src="File", fname="tmfiles/collatz_tm.tm"))


# In[ ]:




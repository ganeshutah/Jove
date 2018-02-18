
# coding: utf-8

#  # Tests on PDA

# In[1]:

from Imports.SystemImports import *
from Imports.DotBashers    import *
from Imports.Def_md2mc      import *
from Imports.Def_PDA        import *


# __IMPORTANT: Must time-bound explore-pda, run-pda, explore-tm, etc so that loops are caught__

# In[2]:

repda = md2mc('''PDA
!!R -> R R | R + R | R* | ( R ) | 0 | 1 | e
I : '', #  ; R#  -> M
M : '', R  ; RR  -> M
M : '', R  ; R+R -> M
M : '', R  ; R*  -> M
M : '', R  ; (R) -> M
M : '', R  ; 0   -> M
M : '', R  ; 1   -> M
M : '', R  ; e   -> M
M : 0,  0  ; ''  -> M
M : 1,  1  ; ''  -> M
M : (,  (  ; ''  -> M
M : ),  )  ; ''  -> M
M : +,  +  ; ''  -> M
M : e,  e  ; ''  -> M
M : '', #  ; #   -> F
'''
)


# In[3]:

repda


# In[4]:

DO_repda = dotObj_pda(repda, FuseEdges=True)


# In[5]:

DO_repda


# In[6]:

explore_pda("0", repda, STKMAX=4)


# In[7]:

explore_pda("00", repda)


# In[8]:

explore_pda("(0)", repda)


# In[9]:

explore_pda("(00)", repda)


# In[10]:

explore_pda("(0)(0)", repda)


# In[11]:

explore_pda("(0)(0)", repda)


# In[12]:

explore_pda("0+0", repda, STKMAX=3)


# In[13]:

explore_pda("0+0", repda)


# In[14]:

explore_pda("(0)(0)", repda)


# In[15]:

explore_pda("(0)+(0)", repda)


# In[16]:

explore_pda("00+0", repda)


# In[17]:

explore_pda("000", repda, STKMAX=3)


# In[18]:

explore_pda("00+00", repda, STKMAX=4)


# In[19]:

explore_pda("00+00", repda, STKMAX=6)


# In[20]:

explore_pda("0000+0", repda, STKMAX=5)


# In[21]:

brpda = md2mc('''PDA
 I : '', '' ; S     -> M
 M : '', S  ; (S) -> M
 M : '', S  ; SS   -> M
 M : '', S  ; e     -> M
 M : (,  (  ; ''    -> M
 M : ),  )  ; ''    -> M
 M : e,  e  ; ''    -> M
 M : '', #  ; ''    -> F''')
dotObj_pda(brpda, FuseEdges=True)


# In[22]:

explore_pda("(e)", brpda, STKMAX=3)


# In[23]:

brpda1 = md2mc('''PDA
 I : '', '' ; S     -> M
 M : '', S  ; (S) -> M
 M : '', S  ; SS   -> M
 M : '', S  ; ''    -> M
 M : (,  (  ; ''    -> M
 M : ),  )  ; ''    -> M
 M : '',  ''  ; ''  -> M
 M : '', #  ; ''    -> F''')
dotObj_pda(brpda1, FuseEdges=True)


# In[ ]:




# In[24]:

explore_pda("('')", brpda1, STKMAX=0)


# In[25]:

brpda2 = md2mc('''PDA
 I : a, #; '' -> I
 I : '', '' ; '' -> I''')
dotObj_pda(brpda2, FuseEdges=True)


# In[26]:

explore_pda("a", brpda2, STKMAX=1)


# In[27]:

explore_pda("a", brpda1, STKMAX=1)


# In[28]:

brpda3 = md2mc('''PDA
 I : a, #; '' -> I
 I : '', '' ; b -> I''')
dotObj_pda(brpda3, FuseEdges=True)


# In[29]:

explore_pda("a", brpda3, STKMAX=7)


# In[ ]:




# In[39]:

# Parsing an arithmetic expression
exppda = md2mc('''PDA
!!R -> R * R | R + R | ~R | ( R ) | 0 | 1
I : '', #  ; R#  -> M
M : '', R  ; ~R  -> M
M : '', R  ; R+R -> M
M : '', R  ; R*R -> M
M : '', R  ; (R) -> M
M : '', R  ; 0   -> M
M : '', R  ; 1   -> M
M : ~,  ~  ; ''  -> M
M : 0,  0  ; ''  -> M
M : 1,  1  ; ''  -> M
M : (,  (  ; ''  -> M
M : ),  )  ; ''  -> M
M : +,  +  ; ''  -> M
M : *,  *  ; ''  -> M
M : '', #  ; #   -> F
'''
)


# In[40]:

dotObj_pda(exppda, FuseEdges=True)


# In[66]:

explore_pda("1+0*1", exppda, STKMAX=7)


# In[78]:

explore_pda("1+0*1+0*1", exppda, STKMAX=7)


# In[63]:

# Parsing an arithmetic expression
exppdaGood = md2mc('''PDA
!!E -> E+T | T
!!T -> T*F | F
!!F -> 0 | 1 | ~F | (E)
I : '', #  ; E#  -> M
M : '', E  ; E+T -> M
M : '', E  ; T   -> M
M : '', T  ; T*F -> M
M : '', T  ; F   -> M
M : '', F  ; 0   -> M
M : '', F  ; 1   -> M
M : '', F  ; ~F  -> M
M : '', F  ; (E) -> M
M : ~,  ~  ; ''  -> M
M : 0,  0  ; ''  -> M
M : 1,  1  ; ''  -> M
M : (,  (  ; ''  -> M
M : ),  )  ; ''  -> M
M : +,  +  ; ''  -> M
M : *,  *  ; ''  -> M
M : '', #  ; #   -> F
'''
)


# In[64]:

dotObj_pda(exppdaGood, FuseEdges=True)


# In[65]:

explore_pda("1+0*1", exppdaGood, STKMAX=7)


# In[68]:

explore_pda("1+0*1+0*1", exppdaGood, STKMAX=7)


# In[81]:

explore_pda("0*1*~1+~~1*~1", exppdaGood, STKMAX=10)


# In[82]:

explore_pda("0*1*~1+~~1*~1", exppda, STKMAX=6)


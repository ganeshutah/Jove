
# coding: utf-8

#  # Tests on PDA

# In[1]:

from Imports.SystemImports import *
from Imports.DotBashers    import *
from Imports.Def_md2mc      import *
from Imports.Def_PDA        import *


# In[2]:

# Example PDA that recognizes balanced parentheses

P1bp  = { "Q"     : {"s0", "s1", "s2"},
           "Sigma" : {'(',')'},
           "Gamma" : {"(",")",'z'},
           "Delta" : { ('s0','(','z') : { ('s1','(z') }, # push z; push (
                       ('s1','(','z') : { ('s1','(z') }, # push z; push (
                       ('s1','(','(') : { ('s1','((') }, # push (; push (
                       ('s1','(',')') : { ('s1','()') }, # push ); push (
                       ('s1',')','(') : { ('s1','')   }, # push nothing
                       ('s1','','z')  : { ('s2','')   }  # push nothing
                     },
           "q0"    : "s0",
           "z0"    : 'z',
           "F"     : {"s2"}
         }
chk_consistent_pda(P1bp)


# In[3]:

# A variant of P1bp with some redundant transitions added (to take the PDA out of a 
P2bp    = { "Q"     : {"s0", "s1", "s2"},
           "Sigma" : {'(',')'},
           "Gamma" : {"(",")","z"},
           "Delta" : { ('s0','(','z') : { ('s1','(z') }, # push z; push (
                       ('s1','(','z') : { ('s1','(z') }, # push z; push (
                       ('s1','(','(') : { ('s1','((') }, # push (; push (
                       ('s1','(',')') : { ('s1','()') }, # push ); push (
                       ('s1',')','(') : { ('s1','')   }, # push nothing
                       ('s1','','z')  : { ('s2','')   },  # push nothing
                       ('s2','','')   : { ('s2','')   }
                     },
           "q0"    : "s0",
           "z0"    : 'z',
           "F"     : {"s2"}
         }

chk_consistent_pda(P2bp)


# In[4]:

# A variant of P2bp with some redundant transitions added (to take the PDA out of a 
P3bp    = { "Q"     : {"s0", "s1", "s2","s3"},
           "Sigma" : {'(',')'},
           "Gamma" : {"(",")","z"},
           "Delta" : { ('s0','(','z') : { ('s1','(z') }, # push z; push (
                       ('s1','(','z') : { ('s1','(z') }, # push z; push (
                       ('s1','(','(') : { ('s1','((') }, # push (; push (
                       ('s1','(',')') : { ('s1','()') }, # push ); push (
                       ('s1',')','(') : { ('s1','')   }, # push nothing
                       ('s1','','z')  : { ('s2','')   },  # push nothing
                       ('s2','','')   : { ('s3','')   } # run away to s3
                     },    # still it matters that a fleeting glimpse of
           "q0"    : "s0", # 's2' has been had, with input consumed!
           "z0"    : 'z',  # That is enough for acceptance. Tsk, tsk!
           "F"     : {"s2"}
         }

chk_consistent_pda(P3bp) 


# In[5]:

Pev = { "Sigma" : {'a','b'},
        "Q"     : {"S0", "S1", "S2","S3"},
        "Gamma" : {'a','b','1','Z'},
        "Delta" : {('S0','a','Z'): {('S1','1Z')},
                   ('S1','a','1'): {('S1','11')},
                   ('S1','b','1'): {('S2','')},
                   ('S2','b','1'): {('S2','')},
                   ('S2','','Z') : {('S3','')} },
        "q0"    : "S0",
        "z0"    : "Z",
        "F"     : { "S3" } }

chk_consistent_pda(Pev)


# In[6]:

dotObj_pda(Pev)


# In[7]:

list(P2bp["Delta"].items())


# In[8]:

dotObj_pda(P2bp)


# In[9]:

dotObj_pda(P1bp)


# In[10]:

dotObj_pda(P3bp)


# # Routines to run PDA 
# 
# We now devise a routine to run a PDA according to either the "accept by final state" criterion or "accept by empty stack" criterion. We call these "ACCEPT_F" and "ACCEPT_S" with the default being ACCEPT_F.  The main difference is that the "final" configurations are collected differently.

# In[11]:

test = {"Sigma" : {'0','1'},
        "Q"     : {'q1','q2','q3','q4','q33','q44','q22'},
        "Gamma" : {'0','1','$'},
        "Delta" : {('q1','',''): {('q2','$')},
                   
                   ('q2','0',''): {('q2','0')},  
                   ('q2','','0'): {('q22','0')}, 
                   
                   ('q2','1',''): {('q2','1')},
                   ('q2','','1'): {('q33','1')},
                   ('q2','1','1'): {('q44','1')},
                   ('q2','',''): {('q3','')}, 
                   
                   ('q3','0','0'): {('q3','')},
                   ('q3','1','1'): {('q3','')},
                   ('q3','','$') : {('q4','')}
                  },
        "z0"    : "$",
        "q0"    : "q1",
        "F"     : {'q1','q4'} }
chk_consistent_pda(test)


# In[12]:

dotObj_pda(P2bp)


# In[13]:

explore_pda("()", P2bp)


# In[14]:

dotObj_pda(Pev)


# In[15]:

explore_pda("ab", Pev)


# In[16]:

Pev1 = { "Sigma" : {'a','b'},
        "Q"     : {"S0", "S1", "S2","S3"},
        "Gamma" : {'a','b','1',"Z"},
        "Delta" : {('S0','a','Z'): {('S1','1Z')},
                   ('S1','a','1'): {('S1','11')},
                   ('S1','b','1'): {('S2','')},
                   ('S2','b','1'): {('S2','')},
                   ('S2','','Z') : {('S3','')},
                   ('S3','', '') : {('S2', '111')}
                  },
        "q0"    : "S0",
        "z0"    : "Z",
        "F"     : { "S3" } }


# In[17]:

dotObj_pda(Pev1)


# In[18]:

dotObj_pda(Pev1, visible_eps=True)


# In[19]:

Pev1 = { "Sigma" : {'a','b'},
        "Q"     : {"S0", "S1", "S2","S3"},
        "Gamma" : {'a','b','1',"Z"},
        "Delta" : {('S0','a','Z'): {('S1','1Z')},
                   ('S1','a','1'): {('S1','11')},
                   ('S1','b','1'): {('S2','')},
                   ('S2','b','1'): {('S2','')},
                   ('S2','','Z') : {('S3','')},
                   ('S3','', '') : {('S2', '111')}
                  },
        "q0"    : "S0",
        "z0"    : "Z",
        "F"     : { "S3" } }
chk_consistent_pda(Pev1)


# In[20]:

explore_pda("aabb", Pev1)


# In[21]:

Pev2 = {"Sigma" : {'a','b'},
        "Q"     : {"S0", "S1", "S2","S3"},
        "Gamma" : {'a','b','1',"Z"},
        "Delta" : {('S0','a','Z'): {('S1','1Z')},
                   ('S1','a','1'): {('S1','11')},
                   ('S1','b','1'): {('S2','')},
                   ('S2','b','1'): {('S2','')},
                   ('S2','','Z') : {('S3','')},
                   ('S3','', '') : {('S2', '111')}
                  },
        "q0"    : "S0",
        "z0"    : "Z",
        "F"     : set({  }) }
chk_consistent_pda(Pev2)


# In[22]:

dotObj_pda(Pev2)


# In[23]:

# Acceptance by final state is impossible because there are no final states
explore_pda("aabb", Pev2)


# In[24]:

# Acceptance by empty stack is possible, as in S3
# the input is fully consumed and the stack is empty
explore_pda("aabb", Pev2, "ACCEPT_S")


# In[25]:

Pev3 = {"Sigma" : {'a','b'},
        "Q"     : {"S0", "S1", "S2","S3"},
        "Gamma" : {'a','b','1',"Z"},
        "Delta" : {('S0','a','Z'): {('S1','1Z')},
                   ('S1','a','1'): {('S1','11')},
                   ('S1','b','1'): {('S2','')},
                   ('S2','b','1'): {('S2','')},
                   ('S2','','Z') : {('S3','')},
                   ('S3','', '') : {('S2', '111')}
                  },
        "q0"    : "S0",
        "z0"    : "Z",
        "F"     : {"S2", "S3"} }
chk_consistent_pda(Pev3)


# In[26]:

dotObj_pda(Pev3)


# In[27]:

# Acceptance at S2, but also continuing on, at S3 and back at S2 also
explore_pda("aabb", Pev3)


# In[28]:

explore_pda("aaabbb", Pev3)


# In[29]:

dotObj_pda(Pev)


# In[30]:

# Rejection because of mismatched lengths of a's and b's
explore_pda("aaaabbb", Pev)


# In[31]:

explore_pda("aaaabbbb", Pev1)


# In[32]:

explore_pda("aaaabbbb", Pev2)


# In[33]:

dotObj_pda(Pev2)


# In[34]:

F27sip = {"Sigma" : {'a','b','c'},
        "Q"     : {"q1","q2","q3","q4","q5","q6","q7"},
        "Gamma" : {'a','b','c','$'},
        "Delta" : {('q1','','')  : { ('q2','$')},
                   
                   ('q2','a',''): { ('q2','a') },
                   ('q2','',''): { ('q3',''), ('q5','') },
                   
                   ('q3','b','a'): { ('q3','') },
                   ('q3','','$'): { ('q4','') },
                   
                   ('q4','c',''): { ('q4','') },
                   
                   ('q5','b',''): { ('q5','') },
                   ('q5','',''): { ('q6','') },
                   
                   ('q6','c','a'): { ('q6','') },
                   ('q6','','$'): { ('q7','') }
                  },
        "q0"    : "q1",
        "z0"    : "$",
        "F"     : {'q4','q7'} }
chk_consistent_pda(F27sip)


# In[35]:

dotObj_pda(F27sip)


# In[36]:

wwr = {"Sigma" : {'0','1'},
        "Q"     : {'q1','q2','q3','q4'},
        "Gamma" : {'0','1','$'},
        "Delta" : {('q1','',''): {('q2','$')},
                   ('q2','0',''): {('q2','0')},  
                   ('q2','1',''): {('q2','1')}, 
                   ('q2','',''): {('q3','')}, 
                   ('q3','0','0'): {('q3','')},
                   ('q3','1','1'): {('q3','')},
                   ('q3','','$') : {('q4','')}
                  },
        "q0"    : "q1",
        "z0"    : "$",
        "F"     : {'q1','q4'} }
chk_consistent_pda(wwr)


# In[37]:

dotObj_pda(wwr)


# In[38]:

dotObj_pda(F27sip)


# In[39]:

explore_pda("aabcc",F27sip)


# In[40]:

dotObj_pda(F27sip, visible_eps=True)


# In[41]:

dotObj_pda(F27sip, visible_eps=False)


# In[42]:

onestpda = {"Sigma" : {'a','b','c'},
        "Q"     : { "q7"},
        "Gamma" : { 'a','b','c','$'},
        "Delta" : { 
                   ('q7','',''): {('q7','aa')}
                  },
        "q0"    : "q7",
        "z0"    : "$",
        "F"     : set({ }) }
chk_consistent_pda(onestpda)


# In[43]:

dotObj_pda(onestpda)


# In[44]:

explore_pda("a",onestpda)


# In[45]:

# This accepts nondeterministically by matching a's and b's
# as well as a's and c's
explore_pda("aabbcc",F27sip)


# In[46]:

explore_pda("aaabbbccc",F27sip)


# In[47]:

onestpda1 = {"Sigma" : {'a','b','c'},
        "Q"     : { "q7"},
        "Gamma" : { 'a','b','c','$'},
        "Delta" : { 
                   ('q7','',''): {('q7','aa')}
                  },
        "q0"    : "q7",
        "z0"    : "$",
        "F"     : set({ }) }
chk_consistent_pda(onestpda1)


# In[48]:

dotObj_pda(onestpda1)


# In[49]:

explore_pda("",onestpda1, "ACCEPT_S")


# In[50]:

explore_pda("",onestpda1, "ACCEPT_S", chatty=True)


# In[51]:

explore_pda("",onestpda1, "ACCEPT_F")


# In[ ]:




# In[52]:

run_pda("",onestpda1, "ACCEPT_S", chatty=False)


# In[53]:

run_pda("",onestpda1, "ACCEPT_S", chatty=True)


# In[54]:

a1b2_s = md2mc(src="File", fname="pdafiles/a1b2_accept_s.pda")
dotObj_pda(a1b2_s) 


# In[55]:

help(explore_pda)


# In[56]:

explore_pda("abb", a1b2_s, acceptance='ACCEPT_S')


# In[57]:

explore_pda("bab", a1b2_s, acceptance='ACCEPT_S')


# In[58]:

explore_pda("bba", a1b2_s, acceptance='ACCEPT_S')


# In[59]:

explore_pda("bbaabbbabaabbabbbb", a1b2_s, acceptance='ACCEPT_S')


# In[60]:

explore_pda("babaababbbaabbbbbb", a1b2_s, acceptance='ACCEPT_S')


# In[61]:

explore_pda("abbaababbbabbbbbba", a1b2_s, acceptance='ACCEPT_S')


# In[62]:

a1b2_f = md2mc(src="File", fname="pdafiles/a1b2_accept_f.pda")
dotObj_pda(a1b2_f) 


# In[63]:

explore_pda("abbaababbbabbbbbba", a1b2_f) # Default is accept_f


# In[64]:

explore_pda("babaababbbaabbbbbb", a1b2_f, acceptance='ACCEPT_F') # default acceptance


# In[65]:

explore_pda("bbaabbbabaabbabbbb", a1b2_f)


# In[ ]:




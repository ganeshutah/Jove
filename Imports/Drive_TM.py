
# coding: utf-8

# # Turing Machines

# In[1]:

from Imports.Def_TM     import *
from Imports.Def_md2mc  import *
from Imports.DotBashers import *


# # DTM: accepts "w#w" (markdown)

# In[2]:

help(explore_tm)


# In[3]:

wpw_tm = md2mc(src='File', fname="tmfiles/wpw.tm")
dotObj_tm(wpw_tm)


# In[4]:

explore_tm(wpw_tm, "001#001", 120)


# In[5]:

wwndtm_md = md2mc(src='File', fname="tmfiles/wwndtm.tm")
dotObj_tm(wwndtm_md)


# In[6]:

explore_tm(wwndtm_md, "001001", 170)


# # DTM: accepts "w#w" (direct)
# 
# This TM is made deterministic by going to exactly one new ID (the set of next states in the transition table has a cardinality of one). We will enter the TM (called wpw) and use dotObj_tm to plot it.

# In[7]:

# Example TM that recognizes w#w. We use "." to denote blanks.
# Blanks are of course user-selectable
wpw = {
 "Q": {"q0","q1","q2","q3","q4","q5","q6","q7","q8","q9","q10"},
 "Sigma" : {'0','1'},
 "Gamma" : {'0','1','X','Y','#','.'},
 "Delta" : {  
     ("q0","0") : { ("q1","X","R")},
     ("q0","#") : { ("q5","#","R")},
     ("q0","1") : { ("q7","Y","R")},
     #
     ("q1","0") : { ("q1","0","R")},     
     ("q1","1") : { ("q1","1","R")},
     ("q1","#") : { ("q2","#","R")},
     #
     ("q2","X") : { ("q2","X","R")},
     ("q2","Y") : { ("q2","Y","R")},     
     ("q2","0") : { ("q3","X","L")},
     #
     ("q3","X") : { ("q3","X","L")},  
     ("q3","Y") : { ("q3","Y","L")},
     ("q3","#") : { ("q4","#","L")}, 
     #
     ("q4","0") : { ("q4","0","L")},
     ("q4","1") : { ("q4","1","L")},     
     ("q4","X") : { ("q0","X","R")},
     ("q4","Y") : { ("q0","Y","R")},
     #
     ("q5","X") : { ("q5","X","R")},     
     ("q5","Y") : { ("q5","Y","R")},
     ("q5",".") : { ("q6",".","R")},  
     #
     ("q7","0") : { ("q7","0","R")},
     ("q7","1") : { ("q7","1","R")},     
     ("q7","#") : { ("q8","#","R")},
     #
     ("q8","X") : { ("q8","X","R")},     
     ("q8","Y") : { ("q8","Y","R")},
     ("q8","1") : { ("q9","Y","L")}, 
     #
     ("q9","X") : { ("q9","X","L")},     
     ("q9","Y") : { ("q9","Y","L")},
     ("q9","#") : { ("q10","#","L")},  
     #
     ("q10","0") : { ("q10","0","L")},     
     ("q10","1") : { ("q10","1","L")},
     ("q10","X") : { ("q0","X","R")},
     ("q10","Y") : { ("q0","Y","R")},
 },
 "q0"    : "q0",
 "B"     : '.',
 "F"     : {"q6"}
}


# In[8]:

wpw


# In[9]:

wpwobj = dotObj_tm(wpw)


# In[10]:

wwndtm = {
 "Q": {"q0","q1","q2","q3","q4","q5","q6","q7","q8","q9","q10",
       "q11","q12","q13","q14"},
 "Sigma" : {'0','1'},
 "Gamma" : {'0','1','X','Y','2','3',
            'P','Q','.'},
 "Delta" : {  
     ("q0",".") : { ("q1",".","R")},
     ("q0","0") : { ("q14","0","S")},
     ("q0","1") : { ("q14","1","S")},
     #
     ("q14","0") : { ("q14","0","R"), ('q2','X','L')},
     ("q14","1") : { ("q14","1","R"), ('q2','Y','L')},
     #
     ("q2","0") : { ("q2","0","L")},
     ("q2","1") : { ("q2","1","L")},     
     ("q2",".") : { ("q3",".","R")},
     #
     ("q3","X") : { ("q6","X","R")},  
     ("q3","Y") : { ("q7","Y","R")},
     #
     ("q3","0") : { ("q4","P","R")},
     ("q3","1") : { ("q5","Q","R")},          
     #
     ("q3","2") : { ("q12","2","R")},
     ("q3","3") : { ("q12","3","R")},
     #
     #--
     ("q4","0") : { ("q4","0","R")},
     ("q4","1") : { ("q4","1","R")},
     ("q4","2") : { ("q4","2","R")},
     ("q4","3") : { ("q4","3","R")},
     ("q4","X") : { ("q10","2","R")},     
     #
     ("q5","0") : { ("q5","0","R")},
     ("q5","1") : { ("q5","1","R")},
     ("q5","2") : { ("q5","2","R")},
     ("q5","3") : { ("q5","3","R")},
     ("q5","Y") : { ("q11","3","R")},     
     #     
     ("q10","0") : { ("q8","X","L")},     
     ("q10","1") : { ("q8","Y","L")},
     ("q10",".") : { ("q8",".","L")},
     #     
     ("q11","0") : { ("q9","X","L")},     
     ("q11","1") : { ("q9","Y","L")},
     ("q11",".") : { ("q9",".","L")},     
     #
     ("q8","0") : { ("q8","0","L")},     
     ("q8","1") : { ("q8","1","L")},
     ("q8","2") : { ("q8","2","L")},
     ("q8","3") : { ("q8","3","L")},
     ("q8","P") : { ("q3","P","R")},
     #
     ("q9","0") : { ("q9","0","L")},     
     ("q9","1") : { ("q9","1","L")},
     ("q9","2") : { ("q9","2","L")},
     ("q9","3") : { ("q9","3","L")},
     ("q9","Q") : { ("q3","Q","R")},
     #
     ("q12","2") : { ("q12","2","R")},
     ("q12","3") : { ("q12","3","R")},
     ("q12",".") : { ("q13",".","R")}
 },
 "q0"    : "q0",
 "B"     : '.',
 "F"     : {"q1","q13"}
}


# In[11]:

step_tm(wpw, ("q0",0,"0#1", 3), [], set({}))


# In[12]:

step_tm(wwndtm, ("q14",0, "00", 100), [], set({}))


# In[13]:

run_tm(wpw, "01#01..", 19)


# In[14]:

explore_tm(wpw, "01#01..", 19)


# In[15]:

run_tm(wwndtm, "0100101001", 888)


# In[16]:

explore_tm(wwndtm, "0100101001", 888)


# In[17]:

explore_tm(wpw, "010#010", 44)


# In[18]:

explore_tm(wpw, "010#011", 33)


# In[19]:

explore_tm(wpw, "1#1", 54)


# In[20]:

explore_tm(wpw, "01#01", 18)
#run_tm(wpw, "01#01", 18)


# In[21]:

explore_tm(wpw, "010001101#010001101", 300)


# In[22]:

wwndtm


# In[23]:

dotObj_tm(wwndtm)


# In[24]:

wwndtmobj = dotObj_tm(wwndtm)


# In[25]:

explore_tm(wwndtm, "010010", 88)


# In[26]:

explore_tm(wwndtm, "0101", 45)


# In[27]:

explore_tm(wwndtm, "0100101001", 666)


# In[28]:

explore_tm(wwndtm, "0100101001", 666)


# In[29]:

explore_tm(wwndtm, "0100101001", 66)


# In[30]:

addtm = {
    # This TM adds two numbers in base 2.
    #
    # Input: matches the regex "[01][01]*\+[01][01]*"
    #        Interpreted as a+b where a and b are unsigned integers in big-endian
    #          form
    # Output: Occurs on a halt in the "done" state.
    #         The sum of the numbers in big endian form.
    #         No other characters will be on the tape.
    #         There willbe no leading zeros on the answer.
    # Errors: The only errors that can occur are input errors which lead to
    #           a halt on the "error" state. This indicates the input does
    #           not conform to the input requirement.
    # Detail: There is no length maximums on the input.
    #         The numbers can be of different lengths.
    #         Leading zeros on inputs only cause a longer runtime.
    "Q": {
        # final states
        "done", "error",

        # input validation states
        "start",
        "check_a",
        "check_b_start",
        "check_b",

        # adder states
        "read_next_b_digit",
        "0_scan_to_a",
        "1_scan_to_a",
        "n_scan_to_a",
        "0_scan_to_a_digit",
        "1_scan_to_a_digit",
        "n_scan_to_a_digit",
        "0_scan_to_output",
        "1_scan_to_output",
        "c0_scan_to_output",
        "write_carry",
        "scan_to_b",
        "scan_to_b_digit",

        # answer formatting states
        "erase_until_sum",
        "find_end_of_sum",
        "read_msb_of_sum",
        "0_check_end_of_sum",
        "1_check_end_of_sum",
        "0_write_last_digit",
        "1_write_last_digit",
        "write_last_0",
        "write_last_1",
        "0_find_end_of_sum",
        "1_find_end_of_sum",
        "0_find_answer",
        "1_find_answer",
        "write_0",
        "write_1",
        "find_start_of_sum",
        "find_start_of_answer",
        "erase_leading_zeros",
    },

    "Sigma" : {'0', '1', '+'},

    "Gamma" : {'.',
               '0', '1', '+',
               'a', # right side marker for a input
               'b', # right side marker for b input
               'c', # carry indicator
               'X', # 0 used indicator
               'Y', # 1 used indicator
               's', # left side of answer space marker
               },

    "Delta" : {
        # Begin input validation
        ("start", '.') : { ("error", '.', 'S') },
        ("start", '+') : { ("error", '.', 'S') },
        ("start", '0') : { ("check_a", '0', 'R') },
        ("start", '1') : { ("check_a", '1', 'R') },
        #
        ("check_a", '0') : { ("check_a", '0', 'R') },
        ("check_a", '1') : { ("check_a", '1', 'R') },
        ("check_a", '.') : { ("error", '.', 'S') },
        ("check_a", '+') : { ("check_b_start", 'a', 'R') },
        #
        ("check_b_start", '0') : { ("check_b", '0', 'R') },
        ("check_b_start", '1') : { ("check_b", '1', 'R') },
        ("check_b_start", '.') : { ("error", '.', 'S') },
        ("check_b_start", '+') : { ("error", '+', 'S') },
        #
        ("check_b", '0') : { ("check_b", '0', 'R') },
        ("check_b", '1') : { ("check_b", '1', 'R') },
        ("check_b", '.') : { ("read_next_b_digit", 'b', 'L') },
        ("check_b", '+') : { ("error", '+', 'S') },
        # End input validation

        # Begin adder
        ("read_next_b_digit", '0') : { ("0_scan_to_a", 'X', 'L') },
        ("read_next_b_digit", '1') : { ("1_scan_to_a", 'Y', 'L') },
        #
        ("0_scan_to_a", '0') : { ("0_scan_to_a", '0', 'L') },
        ("0_scan_to_a", '1') : { ("0_scan_to_a", '1', 'L') },
        ("0_scan_to_a", 'a') : { ("0_scan_to_a_digit", 'a', 'L') },
        #
        ("1_scan_to_a", '0') : { ("1_scan_to_a", '0', 'L') },
        ("1_scan_to_a", '1') : { ("1_scan_to_a", '1', 'L') },
        ("1_scan_to_a", 'a') : { ("1_scan_to_a_digit", 'a', 'L') },
        #
        ("n_scan_to_a", '0') : { ("n_scan_to_a", '0', 'L') },
        ("n_scan_to_a", '1') : { ("n_scan_to_a", '1', 'L') },
        ("n_scan_to_a", 'a') : { ("n_scan_to_a_digit", 'a', 'L') },
        #
        ("0_scan_to_a_digit", 'X') : { ("0_scan_to_a_digit", 'X', 'L') },
        ("0_scan_to_a_digit", 'Y') : { ("0_scan_to_a_digit", 'Y', 'L') },
        ("0_scan_to_a_digit", '0') : { ("0_scan_to_output", 'X', 'R') },
        ("0_scan_to_a_digit", '1') : { ("1_scan_to_output", 'Y', 'R') },
        ("0_scan_to_a_digit", '.') : { ("0_scan_to_output", 's', 'R') },
        ("0_scan_to_a_digit", 's') : { ("0_scan_to_output", 's', 'R') },
        #
        ("1_scan_to_a_digit", 'X') : { ("1_scan_to_a_digit", 'X', 'L') },
        ("1_scan_to_a_digit", 'Y') : { ("1_scan_to_a_digit", 'Y', 'L') },
        ("1_scan_to_a_digit", '0') : { ("1_scan_to_output", 'X', 'R') },
        ("1_scan_to_a_digit", '1') : { ("c0_scan_to_output", 'Y', 'R') },
        ("1_scan_to_a_digit", '.') : { ("1_scan_to_output", 's', 'R') },
        ("1_scan_to_a_digit", 's') : { ("1_scan_to_output", 's', 'R') },
        #
        ("n_scan_to_a_digit", 'X') : { ("n_scan_to_a_digit", 'X', 'L') },
        ("n_scan_to_a_digit", 'Y') : { ("n_scan_to_a_digit", 'Y', 'L') },
        ("n_scan_to_a_digit", '0') : { ("0_scan_to_output", 'X', 'R') },
        ("n_scan_to_a_digit", '1') : { ("1_scan_to_output", 'Y', 'R') },
        ("n_scan_to_a_digit", '.') : { ("erase_until_sum", 's', 'R') },
        ("n_scan_to_a_digit", 's') : { ("erase_until_sum", 's', 'R') },
        #
        ("0_scan_to_output", '0') : { ("0_scan_to_output", '0', 'R') },
        ("0_scan_to_output", '1') : { ("0_scan_to_output", '1', 'R') },
        ("0_scan_to_output", 'X') : { ("0_scan_to_output", 'X', 'R') },
        ("0_scan_to_output", 'Y') : { ("0_scan_to_output", 'Y', 'R') },
        ("0_scan_to_output", 'a') : { ("0_scan_to_output", 'a', 'R') },
        ("0_scan_to_output", 'b') : { ("0_scan_to_output", 'b', 'R') },
        ("0_scan_to_output", '.') : { ("scan_to_b", '0', 'L') },
        ("0_scan_to_output", 'c') : { ("scan_to_b", '1', 'L') },
        #
        ("1_scan_to_output", '0') : { ("1_scan_to_output", '0', 'R') },
        ("1_scan_to_output", '1') : { ("1_scan_to_output", '1', 'R') },
        ("1_scan_to_output", 'X') : { ("1_scan_to_output", 'X', 'R') },
        ("1_scan_to_output", 'Y') : { ("1_scan_to_output", 'Y', 'R') },
        ("1_scan_to_output", 'a') : { ("1_scan_to_output", 'a', 'R') },
        ("1_scan_to_output", 'b') : { ("1_scan_to_output", 'b', 'R') },
        ("1_scan_to_output", '.') : { ("scan_to_b", '1', 'L') },
        ("1_scan_to_output", 'c') : { ("write_carry", '0', 'R') },
        #
        ("c0_scan_to_output", '0') : { ("c0_scan_to_output", '0', 'R') },
        ("c0_scan_to_output", '1') : { ("c0_scan_to_output", '1', 'R') },
        ("c0_scan_to_output", 'X') : { ("c0_scan_to_output", 'X', 'R') },
        ("c0_scan_to_output", 'Y') : { ("c0_scan_to_output", 'Y', 'R') },
        ("c0_scan_to_output", 'a') : { ("c0_scan_to_output", 'a', 'R') },
        ("c0_scan_to_output", 'b') : { ("c0_scan_to_output", 'b', 'R') },
        ("c0_scan_to_output", '.') : { ("write_carry", '0', 'R') },
        ("c0_scan_to_output", 'c') : { ("write_carry", '1', 'R') },
        #
        ("write_carry", '.') : { ("scan_to_b", 'c', 'L') },
        #
        ("scan_to_b", '0') : { ("scan_to_b", '0', 'L') },
        ("scan_to_b", '1') : { ("scan_to_b", '1', 'L') },
        ("scan_to_b", 'b') : { ("scan_to_b_digit", 'b', 'L') },
        #
        ("scan_to_b_digit", 'X') : { ("scan_to_b_digit", 'X', 'L') },
        ("scan_to_b_digit", 'Y') : { ("scan_to_b_digit", 'Y', 'L') },
        ("scan_to_b_digit", '0') : { ("read_next_b_digit", '0', 'S') },
        ("scan_to_b_digit", '1') : { ("read_next_b_digit", '1', 'S') },
        ("scan_to_b_digit", 'a') : { ("n_scan_to_a", 'a', 'S') },
        # End adder

        # Begin answer formatting
        ("erase_until_sum", '0') : { ("erase_until_sum", '.', 'R') },
        ("erase_until_sum", '1') : { ("erase_until_sum", '.', 'R') },
        ("erase_until_sum", 'X') : { ("erase_until_sum", '.', 'R') },
        ("erase_until_sum", 'Y') : { ("erase_until_sum", '.', 'R') },
        ("erase_until_sum", 'a') : { ("erase_until_sum", '.', 'R') },
        ("erase_until_sum", 'b') : { ("find_end_of_sum", '.', 'R') },
        #
        ("find_end_of_sum", '0') : { ("find_end_of_sum", '0', 'R') },
        ("find_end_of_sum", '1') : { ("find_end_of_sum", '1', 'R') },
        ("find_end_of_sum", 'c') : { ("read_msb_of_sum", '1', 'S') },
        ("find_end_of_sum", '.') : { ("read_msb_of_sum", '.', 'L') },
        #
        ("read_msb_of_sum", '0') : { ("0_check_end_of_sum", '.', 'L') },
        ("read_msb_of_sum", '1') : { ("1_check_end_of_sum", '.', 'L') },
        #
        ("0_check_end_of_sum", '0') : { ("0_find_end_of_sum", '0', 'L') },
        ("0_check_end_of_sum", '1') : { ("0_find_end_of_sum", '1', 'L') },
        ("0_check_end_of_sum", '.') : { ("0_write_last_digit", '.', 'L') },
        #
        ("1_check_end_of_sum", '0') : { ("1_find_end_of_sum", '0', 'L') },
        ("1_check_end_of_sum", '1') : { ("1_find_end_of_sum", '1', 'L') },
        ("1_check_end_of_sum", '.') : { ("1_write_last_digit", '.', 'L') },
        #
        ("0_write_last_digit", '.') : { ("0_write_last_digit", '.', 'L') },
        ("0_write_last_digit", '0') : { ("write_last_0", '0', 'R') },
        ("0_write_last_digit", '1') : { ("write_last_0", '1', 'R') },
        ("0_write_last_digit", 's') : { ("write_last_0", '.', 'R') },
        #
        ("1_write_last_digit", '.') : { ("1_write_last_digit", '.', 'L') },
        ("1_write_last_digit", '0') : { ("write_last_1", '0', 'R') },
        ("1_write_last_digit", '1') : { ("write_last_1", '1', 'R') },
        ("1_write_last_digit", 's') : { ("write_last_1", '.', 'R') },
        #
        ("write_last_0", '.') : { ("find_start_of_answer", '0', 'S') },
        #
        ("write_last_1", '.') : { ("find_start_of_answer", '1', 'S') },
        #
        ("0_find_end_of_sum", '0') : { ("0_find_end_of_sum", '0', 'L') },
        ("0_find_end_of_sum", '1') : { ("0_find_end_of_sum", '1', 'L') },
        ("0_find_end_of_sum", '.') : { ("0_find_answer", '.', 'L') },
        #
        ("1_find_end_of_sum", '0') : { ("1_find_end_of_sum", '0', 'L') },
        ("1_find_end_of_sum", '1') : { ("1_find_end_of_sum", '1', 'L') },
        ("1_find_end_of_sum", '.') : { ("1_find_answer", '.', 'L') },
        #
        ("0_find_answer", '.') : { ("0_find_answer", '.', 'L') },
        ("0_find_answer", '0') : { ("write_0", '0', 'R') },
        ("0_find_answer", '1') : { ("write_0", '1', 'R') },
        ("0_find_answer", 's') : { ("write_0", '.', 'R') },
        #
        ("1_find_answer", '.') : { ("1_find_answer", '.', 'L') },
        ("1_find_answer", '0') : { ("write_1", '0', 'R') },
        ("1_find_answer", '1') : { ("write_1", '1', 'R') },
        ("1_find_answer", 's') : { ("write_1", '.', 'R') },
        #
        ("write_0", '.') : { ("find_start_of_sum", '0', 'R') },
        #
        ("write_1", '.') : { ("find_start_of_sum", '1', 'R') },
        #
        ("find_start_of_sum", '.') : { ("find_start_of_sum", '.', 'R') },
        ("find_start_of_sum", '0') : { ("find_end_of_sum", '0', 'S') },
        ("find_start_of_sum", '1') : { ("find_end_of_sum", '1', 'S') },
        #
        ("find_start_of_answer", '0') : { ("find_start_of_answer", '0', 'L') },
        ("find_start_of_answer", '1') : { ("find_start_of_answer", '1', 'L') },
        ("find_start_of_answer", '.') : { ("erase_leading_zeros", '.', 'R') },
        #
        ("erase_leading_zeros", '0') : { ("erase_leading_zeros", '.', 'R') },
        ("erase_leading_zeros", '1') : { ("done", '1', 'S') },
        ("erase_leading_zeros", '.') : { ("done", '0', 'S') },
        # End answer formatting
    },

    "q0"    : "start",

    "B"     : '.',

    "F"     : {"done"}
}


# In[31]:

dotObj_tm(addtm)


# In[32]:

addtmobj = dotObj_tm(addtm)


# In[33]:

explore_tm(addtm, "11111101+11111101", 735)


# In[34]:

dec_doub = md2mc(src='File', fname='tmfiles/decimal_double_tm.tm')
dotObj_tm(dec_doub)


# In[35]:

# Doubles the number given on the tape in decimal!
explore_tm(dec_doub, "231", 100)


# In[36]:

collatz_tm = md2mc(src='File', fname='tmfiles/collatz_tm.tm')
dotObj_tm(collatz_tm)


# In[37]:

# Will loop if the Collatz ("3x+1") program will ever loop!
explore_tm(collatz_tm, "0110", 100)


# In[38]:

shiftl_tm = md2mc(src='File', fname='tmfiles/shift_left_tm.tm')
dotObj_tm(shiftl_tm)


# In[39]:

explore_tm(shiftl_tm, "abaaba", 100)


# In[40]:

shiftr_tm = md2mc(src='File', fname='tmfiles/shift_right_tm.tm')
dotObj_tm(shiftr_tm)


# In[41]:

explore_tm(shiftr_tm, "ababba", 100)


# In[ ]:




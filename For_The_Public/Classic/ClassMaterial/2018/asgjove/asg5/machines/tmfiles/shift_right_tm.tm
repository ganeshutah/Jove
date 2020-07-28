!!shift_right_tm_str = """
!! Input: a string matching the regex "[ab]*"
!!
!! Output: the same input string with a gap after the first character
!!
!! Errors: None
TM
i_move_right : a;a,R | b;b,R -> read
i_move_right : .;.,S -> f_done

read : a;.,R -> a_next
read : b;.,R -> b_next
read : .;.,S -> f_done

a_next : a;a,R -> a_next
a_next : b;a,R -> b_next
a_next : .;a,S -> f_done

b_next : a;b,R -> a_next
b_next : b;b,R -> b_next
b_next : .;b,S -> f_done
!!"""

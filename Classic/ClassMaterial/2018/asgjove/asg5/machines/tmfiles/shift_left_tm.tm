!! shift_left_tm_str = """
!! Input: a string matching the regex "[ab]*"
!!
!! Output: the same input string with a gap before the last character
!!
!! Errors: None
TM
i_start : a;a,R | b;b,R -> scan_to_end
i_start : .;.,S -> f_done

scan_to_end : a;a,R | b;b,R -> scan_to_end
scan_to_end : .;.,L -> move_left

move_left : a;a,L | b;b,L -> read

read : a;.,L -> a_next
read : b;.,L -> b_next

a_next : a;a,L -> a_next
a_next : b;a,L -> b_next
a_next : .;a,L -> f_done

b_next : a;b,L -> a_next
b_next : b;b,L -> b_next
b_next : .;b,L -> f_done

!! """

!!decimal_double_tm_str = """
TM
i_start : 0;.,R -> erase_leading_0
i_start : 1;1,R | 2;2,R | 3;3,R | 4;4,R | 5;5,R | 6;6,R | 7;7,R | 8;8,R | 9;9,R -> goto_lsd
i_start : .;.,S -> error

erase_leading_0 : 0;.,R -> erase_leading_0
erase_leading_0 : 1;1,R | 2;2,R | 3;3,R | 4;4,R | 5;5,R | 6;6,R | 7;7,R | 8;8,R | 9;9,R -> goto_lsd
erase_leading_0 : .;0,S -> f_done

goto_lsd : 0;0,R | 1;1,R | 2;2,R | 3;3,R | 4;4,R | 5;5,R | 6;6,R | 7;7,R | 8;8,R | 9;9,R -> goto_lsd
goto_lsd : .;.,L -> 0_carry

0_carry : 0;0,L | 1;2,L | 2;4,L | 3;6,L | 4;8,L -> 0_carry
0_carry : 5;0,L | 6;2,L | 7;4,L | 8;6,L | 9;8,L -> 1_carry
0_carry : .;.,S -> f_done

1_carry : 0;1,L | 1;3,L | 2;5,L | 3;7,L | 4;9,L -> 0_carry
1_carry : 5;1,L | 6;3,L | 7;5,L | 8;7,L | 9;9,L -> 1_carry
1_carry : .;1,S -> f_done
!!"""

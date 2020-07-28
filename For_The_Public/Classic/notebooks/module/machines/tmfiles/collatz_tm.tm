!!collatz_tm_str = """
TM

i_start      : 0; ., R -> i_start             !! erase this zero and try to find more
i_start      : 1; 1, R -> goto_lsb            !! we have a proper number, go to the lsb
i_start      : .; ., S -> error               !! error on no input or input == 0


goto_lsb     : 0; 0,R | 1; 1,R -> goto_lsb    !! scan off the right edge of the number
goto_lsb     : .; .,L -> branch               !! take a step back to be on the lsb and start branch


branch       : 0; .,L -> branch               !! number is even, divide by two and re-branch
branch       : 1; 1,L -> check_n_eq_1         !! number is odd, check if it is 1


check_n_eq_1 : 0; 0,R | 1; 1,R -> 01_fma      !! number wasn't 1, goto 3n+1
check_n_eq_1 : .; .,R -> f_halt               !! number was 1, halt


!! carrying 0 we see a 0 so write 0 and carry 0 forward
00_fma       : 0; 0,L -> 00_fma

!! carrying 0 we see a 1 (times 3 is 11) so write 1 and carry 1 forward
00_fma       : 1; 1,L -> 01_fma

!! reached the end of the number, go back to the start
00_fma       : .; .,R -> goto_lsb             


!! carrying 1 we see a 0 so write 1 and carry 0 forward
01_fma       : 0; 1,L -> 00_fma  

!! carrying 1 we see a 1 (times 3 is 11, plus our carry is 100) so write 0 and carry 10 forward
01_fma       : 1; 0,L -> 10_fma  

!! reached the end of the number, write our 1 and go back to the start
01_fma       : .; 1,R -> goto_lsb             


!! carrying 10 we see a 0, so write 0 and carry 1 forward
10_fma       : 0; 0,L -> 01_fma

!! carrying 10 we see a 1 (times 3 is 11, plus our carry is 101), so write 1 and carry 10 forward
10_fma       : 1; 1,L -> 10_fma

!! reached the end of the number, write a 0 from our 10 and carry 1
10_fma       : .; 0,L -> 01_fma

!!"""

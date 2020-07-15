TM 
!!---------------------------------------------------------------------------
!! This is a TM for ww processing. Guesses midpoint using nondet.
!! 
!!---------------------------------------------------------------------------

!!---------------------------------------------------------------------------
!! State : rd ; wr , mv -> tostates !! comment
!!---------------------------------------------------------------------------

Iq0     : 0  ; 0  , S  -> q14      !! This simulates the TM taking a guess
Iq0     : 1  ; 1  , S  -> q14      !! that it hasn't seen the midpoint. It
                                   !! moves to q14

Iq0     : .  ; .  , R  -> Fq1      !! yay! shortest acceptance is for eps eps
	                           !! i.e. facing a sea of blanks that encodes
				   !! an epsilon followed by another epsilon.

!!---------------------------------------------------------------------------
				   
q14     : 0  ; 0 , R   -> q14      !! The TM skips over 0s or
				   !! 1s for a while, and then chooses a cell,
				   
q14     : 0  ; X , L   -> q2       !! declaring it the midpoint, or more specifically
	       	       	  	   !! FIRST CHARACTER PAST MIDPOINT, by marking it 'X' 				   
				   !! and then moves to q2 (to march around the
				   !! chosen midpoint).
				   
q14     : 1  ; 1 , R   -> q14      !! Similar actions as with 0 in state q14,
q14     : 1  ; Y , L   -> q2       !! except that it "dings" the "1" with a "Y"
	       	       	  	   !! to mark it the FIRST CHARACTER PAST MIDPOINT.
				   
                                   !! Then we march around it. While the separate
				   !! use of "X" and "Y" may not be necessary,
				   !! it improves understandability when you
				   !! finally see the result of TM executions.

q2      : 0  ; 0 , L   -> q2       !! The TM is now winding back, seeking the
q2      : 1  ; 1 , L   -> q2       !! left-end of the tape till hit hits a '.'
                                   !! (blank).

q2      : .  ; . , R   -> q3       !! When that happens, the TM goes to state q3
                                   !! to begin its work of "matching around."
				   
				   !! We describe the q3,q5,q11,q9,q3 loop well.
				   !! The other loop q3,q4,q10,q8,q3 is similar.

!!-----------------------------------------------------------------

q3      : X ; X , R    -> q6       !! This state is a stuck state (no progress)
	      	       	  	   !! WE came to q3 because we dinged a 0->X
				   !! or a 1->Y while in q14; so its matching
				   !! "partner" 0 or 1 must be found to the
				   !! left. Unfortunately, we are finding an
				   !! X or a Y.  Thus, no "match around the middle"
				   !! is likely to happen.

q3      : Y ; Y , R    -> q7	   !! This state is ALSO a stuck state for similar
	      	       	  	   !! reasons as expressed in the comments
				   !! associated with q3 : X ; X ...

!!-----------------------------------------------------------------
!! Description of the q3,q5,q11,q9,q3 loop :

q3      : 1 ; Q , R    -> q5       !! Upon seeing a 1, change to Q. Then MUST see a 
                                   !! matching Y, then change to 3, and go right, and to state q5.

				   !! We do this because 'Y' represents what
				   !! was '1' and got marked as midpoint (well,
				   !! one-past midpoint..).				   

!!-- What will happen in q5,q11,q9,q3 --
				   
!! So we have to get past this assumed
!! midpoint and choose the next
!! "one past midpoint that has not been seen so far".
   
!! We enter q11 to then ding a matching
!! 0 to X or 1 to Y, moving left.
			   
!! A blank sends us leftwards, as well.
			   
!! We sweep left till we hit a Q. We MUST see a Q
!! because we entered "this lobe" by dinging a 1->Q.

!! The process repeats from state q3.



q5      : 0;0,R | 1;1,R | 2;2,R | 3;3,R -> q5  !! punt the 0/1/2/3; we need a "Y".

q5      : Y  ; 3, R               -> q11 !! ah-ha , got a Y. Ding to 3, seek 0/1/.

q11     : 1;Y,L | .;.,L | 0;X,L   -> q9  !! phew! got to sweep left now!

q9      : 0;0,L | 1;1,L | 2;2,L | 3;3,L -> q9  !! whee! going left!

q9      : Q ; Q , R                     -> q3  !! Boiinggg - now gonna go right!

!!-----------------------------------------------------------------
!! Description of the q3,q4,q10,q8,q3 loop :

q3      : 0 ; P , R    -> q4    !! This is similar to q3 : 1 ; Q , R -> q5 above


q4      : 0;0,R | 1;1,R | 2;2,R | 3;3,R -> q4  !! punt the 0/1/2/3; we need a "X".

q4      : X  ; 2, R               -> q10 !! ah-ha , got a X. Ding to 2, seek 0/1/.

q10     : 1;Y,L | .;.,L | 0;X,L   -> q8  !! phew! got to sweep left now!

q8      : 0;0,L | 1;1,L | 2;2,L | 3;3,L -> q8  !! whee! going left!

q8      : P ; P , R                     -> q3  !! Boiinggg - now gonna go right!

!!-----------------------------------------------------------------

q3      : 2;2,R | 3;3,R -> q12     !! Seeing every sign of acceptance!!

				   !! We are seeing piles of 2 and 3
				   !! ALSO did not get stuck in q6 or q7
				   !! That means all the matches went fine

q12     : 2 ; 2 , R | 3 ; 3 , R -> q12 !! Skip over piles of past 2s and 3s

q12     : . ; . , R     -> Fq13    !! Yay, acceptance when we hit a blank!


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

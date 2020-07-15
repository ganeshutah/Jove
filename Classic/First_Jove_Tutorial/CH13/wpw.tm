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

Iq0     : 1  ; Y  , R  -> q7      !! All 1s are converted to Y, and matching
	       	       	  	  !! 1s are then sought to the right of the #				  
				  
Iq0     : #  ; #  , R  -> q5      !! If we see # rightaway, we are in the
	       	       	  	  !! situation of having to match eps # eps

!!---				  
q5	: X ; X,R | Y ; Y,R -> q5 !! In q5, we skip over X and Y (an equal number
	      	      	       	  !! of X and Y lie to the left of the #)

q5      : .  ; .  , R  -> Fq6	  !! .. and we accept when we see a blank (.)
!!---				  				  

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

!!---				  
q7      : 0 ; 0,R | 1 ; 1,R -> q7 !! q7 is similar to q1

q7      : #  ; #  , R  -> q8      !! and q8 is similar to q2

q8      : X ; X,R | Y ; Y,R -> q8 

q8      : 1  ; Y  , L  -> q3      



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

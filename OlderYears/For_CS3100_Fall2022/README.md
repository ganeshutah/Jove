* -------------------------------------------------------

* Week-1 **Reading**: Chapters 1, 2, 3. __Outcomes:__
  Emerge with complete understanding of the basics of
  computability, why studying formal language matters, and know how to construct
  languages using set operations, concatenation, and exponentiation. They also
  begin studying Kleene-star. As for practical matters, they understand the course
  objectives, how to run the course software and submit the required material for
  grades.

   - 1:8/22
     - Run the Notebooks within 01_Computability_Languages/ 
     - Quiz-1 covers L1,2
     - Asg-1  covers L1,2
   - 2:8/24
     - Run the Notebooks within 01_Computability_Languages/
   
* Week-2 **Reading**: Chapters 3, 4 (except 4.6 thru 4.8), 5, 6. __Outcomes:__
  Finish understanding Kleene-star, and are able to design
  DFA using two methods: By knowing how to encode salient information in DFA states
  (by naming DFA states to retain this info) and by Boolean operations on DFA (union,
  intersection, complement). They know how to document DFA using literate-programming
  methods of annotating comments within a simple DFA markdown. They are able to
  automatically build, and test DFA, following important principles of software testing.

   - 3:8/29
     - Run the Notebooks within 02_Basic_DFA/
     - Quiz-2 covers L3,4
     - Asg-2  covers L3,4
   - 4:9/2
     - Run the Notebooks within 03_Advanced_DFA/

* Week-3 **Reading** Chapter 6 (skip 6.4 and 6.5), 7.  __Outcomes:__
Outcomes: Understand the importance of nondeterminism in computer
  science, and what nondeterministic finite-state automata are. They understand how to
  convert NFA to DFA via subset construction. They are able to witness, through actual
  hands-on activity, that NFA can blow up exponentially when converted to DFA. They
  may also obtain a DFA directly, and check against results from NFA2DFA using a
  DFA graph isomorphism check, thus showing the power of the Myhill-Nerode theorem to
  help check one software construction method against the other, to catch bugs.

     9/2: Quiz-3 covers L5
   
   - 5:9/7
     - Run the Notebooks within 04_NFA/
     - Run the Notebooks within 05_NFA2DFA/
   
* Week-4 **Reading** Chapter 8, 9.  __Outcomes:__
  Understand what regular expressions are, and how they
  can be converted into NFA, and back to RE. They understand all the algorithmic
  details, solving interesting real-world problems using regular expressions, including
  error-correcting finite-state machines, and the encoding of the Postage Stamp Problem
  (also known as the Coin Problem).

   - 6:9/12
     - Run the Notebooks within 06_RE/
     
   - 7:9/14
     - Run the Notebooks within 07_NFA2RE/

* Week-5 **Reading** Chapter 8, 9.  __Outcomes:__
  Complete the aforesaid readings.

   - 8:9/19
     - Review of nfa2dfa, Brzozowski minimization,
       classical minimization
     - Run the Notebooks within 08_Min_DFA/
     
   - 9:9/21
     - Study the notes in 09_Reg_PL/


* Week-6 **Reading** Chapter 4.6 through 4.8.  __Outcomes:__
  Understand the limitations of finite automata by
  studying the regular language Pumping Lemma. Also begin introducing
  Pushdown Automata.
  
   - 12:
     - Run the Notebooks within 10_PDA/

* Week-7 **Reading** Chapters 11 (except 11.9), 12.  __Outcomes:__
  More details of pushdown automata followed by an introduction to
  context-free grammars and languages.  Ambiguity.
  Consistency and Completeness.
  
   - 13:
     - Run the Notebooks within 11_CFG/
     - Run the Notebooks within 12_CFG2PDA/
     
   - 14:
     - Conversion of CFG to PDA
   
* Week-8 **Reading** Chapters 11 (except 11.9), 12.  __Outcomes:__
 Designing a calculator.
 Understand how NFA can be translated into Linear CFGs.
 The notions of Consistency and Completeness. Demonstration on simple grammars.
 Chapters 10 (derivatives).
  
   - 15:
     - Run the Notebooks provided within 13_Linearity_Amb/
     - Run the Notebooks provided within 14_Calculator/
     
   - 16: (Tentative)
     - The basics of derivative-based Pattern Matching.
     - Run the Notebooks  provided within 15_Derivatives/     
   
* Week-9 **Reading** Start reading Chapter 13, TMs
  
   - 17: Ch13, TMs
     - Run the Notebooks within 17_DTMs_and_NDTMs/
       and 18_More_TM_Exs/
     
   - 18: Begin Ch14, Ch15
     - Run the notebooks in 19_Algo_Proc_PCP/


* -------------------------------------------------------


* -------------------------------------------------------

* Week-1 **Reading**: Chapters 1, 2, 3. __Outcomes:__
  Emerge with complete understanding of the basics of
  computability, why studying formal language matters, and know how to construct
  languages using set operations, concatenation, and exponentiation. They also
  begin studying Kleene-star. As for practical matters, they understand the course
  objectives, how to run the course software and submit the required material for
  grades.

   - 1:8/25
     - Run the Notebooks within 01_Computability_Languages/ 
     - Quiz-1 given; due 8/28 11:59pm, covers L1,2
     - Asg-1 given, due 9/4/20 11:59pm, covers L1,2
   - 2:8/27
     - Run the Notebooks within 01_Computability_Languages/
   
* Week-2 **Reading**: Chapters 3, 4 (except 4.6 thru 4.8), 5, 6. __Outcomes:__
  Finish understanding Kleene-star, and are able to design
  DFA using two methods: By knowing how to encode salient information in DFA states
  (by naming DFA states to retain this info) and by Boolean operations on DFA (union,
  intersection, complement). They know how to document DFA using literate-programming
  methods of annotating comments within a simple DFA markdown. They are able to
  automatically build, and test DFA, following important principles of software testing.

   - 3:9/1
     - Run the Notebooks within 02_Basic_DFA/
     - Quiz-2 given; due 9/4 11:59pm, covers L3,4
     - Asg-2 given, due 9/11/20 11:59pm, covers L3,4
   - 4:9/3
     - Run the Notebooks within 03_Advanced_DFA/ 
   
* Week-3 **Reading** Chapter 6 (skip 6.4 and 6.5), 7.  __Outcomes:__
Outcomes: Understand the importance of nondeterminism in computer
  science, and what nondeterministic finite-state automata are. They understand how to
  convert NFA to DFA via subset construction. They are able to witness, through actual
  hands-on activity, that NFA can blow up exponentially when converted to DFA. They
  may also obtain a DFA directly, and check against results from NFA2DFA using a
  DFA graph isomorphism check, thus showing the power of the Myhill-Nerode theorem to
  help check one software construction method against the other, to catch bugs.
   
   - 5:9/8 (CLASS CANCELLED due to weather; NOTE NEW DUE DATES) 
     - Run the Notebooks within 04_NFA/
     - Quiz-3 given; due 9/18 11:59pm, covers L5,6
     - Asg-3 given, due 9/25 11:59pm, covers L5,6
   - 6:9/10
     - Run the Notebooks within 05_NFA2DFA/
   
* Week-4 **Reading** Chapter 8, 9.  __Outcomes:__
  Understand what regular expressions are, and how they
  can be converted into NFA, and back to RE. They understand all the algorithmic
  details, solving interesting real-world problems using regular expressions, including
  error-correcting finite-state machines, and the encoding of the Postage Stamp Problem
  (also known as the Coin Problem).

   - 7:9/15
     - Run the Notebooks within 06_RE/
     - Quiz-4 given; due 9/18 11:59pm, covers L7,8
     - Asg-4 given, due 9/25 11:59pm, covers L7,8    
   - 8:9/17
     - Run the Notebooks within 07_NFA2RE/
   
* Week-5 **Reading** Chapter 6.4.  __Outcomes:__
  Take a midterm to assess the previous objectives. Ungraded practice
  problems would have been given out each week; discuss those in class. The exam is
  a take-home timed exam on Canvas. After the exam, learn two algorithms for DFA
  minimization, one based on dynamic programming, and the other based on Brzozowski's
  minimization which can be realized using one line of code as ("reverse; determinize;
  reverse; determinize").

   - 9:9/22
     - Quiz-5 given; due 9/25 11:59pm, covers L9,10
     - Review of Asg 1-3
   - 10:9/24
     - Run the Notebooks within 08_Min_DFA/

   - **MIDTERM EXAM-1**
     - **COVERING Asg 1-3 given out 9/26/20 9 AM**
     - **DUE MONDAY 9/28 11:59pm**
     - **TWO ATTEMPTS of 80 mins each - SECOND ATTEMPT COUNTS**
     

* Week-6 **Reading** Chapter 4.6 through 4.8.  __Outcomes:__
  Understand the limitations of finite automata by
  studying the regular language Pumping Lemma 
   - 11:9/29
     - Run the Notebooks within 09_Reg_PL/
     - Quiz-6 given; due 10/2 11:59pm, covers L11,12
     - Asg-5 given; due 10/9 11:59pm, covers L11,12
   - 12:10/1
     - Run the Notebooks within 09_Reg_PL/
   
   
* Week-7 **Reading** Chapters 11 (except 11.9), 12.  __Outcomes:__
  Learn the basics of pushdown automata followed by
  context-free grammars and languages. 
  
   - 13:10/6
     - Run the Notebooks within 10_PDA/
     - Quiz-7 given; due 10/9 11:59pm, covers L113,14
     - Asg-6 given; due 10/16/20 11:59pm, covers L113,14      
   - 14:10/8
     - Run the Notebooks within 11_CFG/  
   
* Week-8 **Reading** Chapters 11 (except 11.9), 12.  __Outcomes:__
  Learn how to convert CFG to PDA, basic notions about
  ambiguous grammars, and linearity.
  
   - 15:10/13
     - Run the Notebooks within 12_CFG2PDA/
     - Quiz-8 given; due 10/16 11:59pm, covers L15,16
     - Asg-7 given; due 10/23/20 11:59pm, covers L15,16         
   - 16:10/15
     - Run the Notebooks within 13_Linearity_Amb/
   
   
* Week-9 **Reading** Chapters 10, 11 (except 11.9).  __Outcomes:__
  The basics of derivative-based parsing.
  
   - 17:10/20
     - Run the Notebooks within 14_Calculator/
     - Run the Notebooks within 15_Derivatives/
     - Quiz-9 given; due 10/23 11:59pm, covers L117,18
   - 18:10/22
     - Review-2
     - MIDTERM EXAM-2 covering Asg 4-6 given out
     - Due Monday 10/26 11:59pm

* Week-10 **Reading** Chapters 11.9, 13.  __Outcomes:__
  Limitations of pushdown automata and context-free grammars
  learned via the CFL Pumping Lemma. Learn the basics of
  designing Turing machines.
  
   - 19:10/27
     - Run the Notebooks within 16_CFL_PL/		
     - Quiz-10 given; due 10/30pm, covers L19,20
     - Asg-8 given; due 11/6/20 11:59pm, covers L19,20
   - 20:10/29
     - Run the Notebooks within 17_DTM/  
   
   
* Week-11 **Reading** Chapters 13, 14  __Outcomes:__
  NDTMs and the Chomsky Hierarchy. Halting problem,
  and the basics of undecidability proofs.
  
   - 21:11/3
     - Run the Notebooks within 18_NDTM/
     - Quiz-11 given; due 11/5 11:59pm, covers L21,22
     - Asg-9 given; due 11/13/20 11:59pm, covers L21,22  
   - 22:11/5
     - Run the Notebooks within 19_Formal_TM/  
   
   
* Week-12 **Reading** Chapters 14, 15.  __Outcomes:__
  The Post Correspondence Problem. Systematic approaches
  to mapping reductions.
   - 23:11/10
     - Run the Notebooks within 20_Algo_Proc_PCP/
     - Quiz-12 given; due 11/13 11:59pm, covers L23,24
     - Asg-10 given; due 11/20/20 11:59pm, covers L23,24  
   - 24:11/12
     - Run the Notebooks within 21_Mapping_Redn/  
   
   
* Week-13 **Reading** Chapters 16, 17.  __Outcomes:__
  Basics of Boolean reasoning, conjunctive normal form
  formulae, validity versus satisfiability, NP-completeness.
   - 25:11/17
     - Run the Notebooks within 22_Bool_Basics/
     - Quiz-13 given; due 11/20 11:59pm, covers L25,26
     - Asg-11 given; due MONDAY 11/30/20 11:59pm, covers L25,26 
   - 26:11/19
     - Run the Notebooks within 23_NPC/  
   
   
* Week-14 **Reading** Chapters 16, 17.  __Outcomes:__
  How mapping reduction looks in the area of NP-completeness proofs.
   - 27:11/24
     - Run the Notebooks within 24_NPC_Redn/
     - Quiz-14 given; due 12/4 11:59pm, covers L27,28
     - Asg-12 given; due 12/11/20 11:59pm, covers material after L26
   
* Week-15 **Reading** Chapter 18.  __Outcomes:__  Learn the basics of
  Lambda calculus and show how it models programs.
   - 28:12/1
     - Run the Notebooks within 25_Lambda_Calc/    
   - 29:12/3
     - Review for Finals
   
* FINAL EXAM is on Canvas, Thursday 12/10/20, 10:30am - 12:30pm on Canvas)
  
* -------------------------------------------------------
   

* Begin by running the notebook in 00_Overview_Of_CS3100_Fall2020/. Then start with the remaining directories such as
01_Computability_Languages/, 02_Basic_DFA/, etc.

* This is a directory prepared for the CS 3100, Fall 2020 students.

* It contains a description of how various Jove modules will be
  covered in our lectures.
  
* I'll now straight present the syllabus and the schedule of
  lectures. 
  
  - All Quizzes will be assigned on Canvas:
  
    - They are given out before a PAIR of lectures (occurring in a week).
    
    - They must be solved and submitted the same week Friday 11:59pm.
    
  - All our Assignments will be provided via Jove notebooks, with a PDF
    summarizing them as well. The PDF is kept on Canvas.
  
  - All our Exams (MT-1, MT-2 and Finals) will be given on Canvas.

  - **Practice problems** for the exams will be assigned each week, 
    but won't be graded. These will help you study for the exams
    in an incremental fashion. Find the Practice Problems on Canvas.

* CS 3100 is running in a *FLIPPED CLASS* style.

* You MUST run each Jove notebook mentioned below *BEFORE* you come
  to a lecture. These notebooks contain a video recording PLUS practice
  material for you.
  
* Some notebooks will last across multiple lectures, and some lectures
  will involve multiple notebooks.
  
* Assignments are to be turned in as finished Jove notebooks. There may
  also be uploads of other files, as specified.

* Each question of an assignment will be in a separate ".ipynb" Jove file.

* In some cases, we will allow documents to be scanned and uploaded as PDF. We require
  you to be using Adobe Scan - a free app you can get for iPhone or Android.

* For more info, see the PDF documents on Canvas that describe our course policies.


* -----------------------------------------------------------------

* **SYLLABUS** is as follows (if I write `` 1:8/25 '' it means Lec1 on 8/25, and so on)
* Some of the chapters are read across multiple weeks.

* -------------------------------------------------------

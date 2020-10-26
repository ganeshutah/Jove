
* TL; DR
  - THE CONTENTS of this webpage are based on my textbook
  [Automata and Computability: A Programmer's Perspective][bookurl],
        ISBN-13: 978-1138552425, ISBN-10: 1138552429 which may be
	used according to the lesson plans described below. Slides, videos,
	and solutions are available! (The book is coming out in an inexpensive
	paperback edition also.)

  - [Additional coverage of Jove][cacmnote]
     is in a CACM note published in October, 2020.

  - Watch https://youtu.be/vhZGUFhm9fY
  - Now go to https://github.com/ganeshutah/Jove.git and go to For_CS3100_Fall2020
  - See my weekly lesson plans for a class I'm teaching
  - Go to 00_Overview_Of_CS3100_Fall2020 and play Overview_Of_CS3100.ipynb
    - It gives another 5-minute overview of Jove
    - You can see the Full Animation Panel as well as individualized animations for various machine-types
  - Now go through the directories whose names begin with 01, 02, etc., and see my weekly lessons
  - Assignments are delivered as notebooks and the students
    - answer the theoretical questions using Latex markdowns
    - answer the Jove (experimental) questions using Colab, submitting finished notebooks
  - For instructors: I have all the solutions for Assignments, Quizzes, and End-of-Chapter exercises 
  - Last but not least, see the practical tie-in by visiting the various notebook (here is a sampling):
    - 01_Computability_Languages/1c_Language_Basics.ipynb
      - use of Widgets to show "star" working
    - 02_Basic_DFA/Basic_DFA.ipynb
      - DFA definition and animation
    - 07_NFA2RE/NFA_to_RE.ipynb
      - NFA to RE conversion
    - 11_CFG/ 
      - Calculator_with_Parse_Tree_Drawing.ipynb
        - explains Expression Parsing, comparing different programming languages
      - Drive_PDA_Based_Parsing.ipynb
        - explains how CFG are turned into PDA and parsed, revealing grammar ambiguity, etc.
    - 12_CFG2PDA/
      - RE2_NFA_PT.ipynb
        - explains how regular-expressions (RE) are parsed using Context-Free Grammars
        - explains how "code generation" (NFA generation) from REs works
    - 17_DTMs_and_NDTMs/CH13-Asg8.ipynb
      - DTM and NDTM animation
	
  - I am *VERY* keen on making Jove a community project where YOU CAN CONTRIBUTE!
    - We can talk more; drop me an email at ganesh@cs.utah.edu (or issue Git pull-requests)
  
* ***NOW FOR THE LONGER VERSION***

* Jove helps you learn about various Models of Computation as well as what is usually called ``Automata Theory''

* There are two directories here:

  - For_CS3100_Fall2020 is tailor-made for the Fall 2020 offering of the CS 3100 class. That directory will have self-contained instructions
    and this is where my current class students must be working initially.

  - For_The_Public is for the general public or CS 3100 students who want more examples to look at

* There is no secret in any of these directories! So, For_The_Public folks are welcome to use the
  contents of For_CS3100_Fall2020 (and vice-versa).

* Under For_The_Public, there are two directories:

  - Classic has Jove as described in the book Automata and Computability.
    Its documentation of files and directories matches the book more closely.
    It is a bit too complex in layout, but since many of the files are referred to in the book,
    I'm not deleting anything.

  - Recommended has a more modern presentation of the content.

* Jove can be run on your own laptop if you have Anaconda and Jupyter on your laptop.
  Or it can run via Colab **without needing any installations.**

* For the Colab path,

  - Visit https://github.com/ganeshutah/Jove.git on a web browser
    that has a Colab Chrome extension.

  - Then visit an ipynb and hit the Chrome Extension to run the code

  -  Here is a video that tells you how exactly how:

     --> YOUTUBE VIDEO: https://youtu.be/vhZGUFhm9fY <--

     (The paths mentioned in this video are subject to change;
      basically navigate up-to an ipynb and then click on the Chrome
      Colab extension icon.)

* If you are running it on your laptop (**highly recommended for speed, etc**),

  - Follow the instructions in For_The_Public/Classic/README.md
    or README_Short.md or read Jupyter_Notebook_Installation.pdf

  - Once installed, type "jupyter notebook" in this directory



[bookurl]: https://www.amazon.com/Automata-Computability-Programmers-Ganesh-Gopalakrishnan-dp-036765654X/dp/036765654X/ref=mt_other?_encoding=UTF8&me=&qid=

[cacmnote]: https://cacm.acm.org/magazines/2020/10/247591-using-computer-programs-and-search-problems-for-teaching-theory-of-computation/fulltext

**[The End, ... but Marvel at Jove, creator of the "double anti-whammy!"](https://www.nytimes.com/2009/07/26/weekinreview/26overbye.html) **





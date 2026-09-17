  
* TL; DR
  - THE CONTENTS of this webpage are based on my textbook
  [Automata and Computability: A Programmer's Perspective][bookurl],
        ISBN-13: 978-1138552425, ISBN-10: 1138552429 which may be
	used according to the lesson plans described below. Slides, videos,
	and solutions are available! (The book is coming out in an inexpensive
	paperback edition also.)

  - [Additional coverage of Jove][cacmnote]
     is in a CACM note published in October, 2020.

  - For Binary Decision Diagrams, go into the "pbl" folder and run BDD.ipynb

  - Watch bit.ly/TeachJoveAutomata
  - Now go to https://github.com/ganeshutah/Jove.git and go to For_CS3100_Fall2024

  - **Every chapter of the book now has a folder of concept notebooks:**
    `Chapter1-Intro/` through `Chapter18-Lambda/`, plus `Basics/` for Appendix A.
    **266 notebooks, one per concept**, all of them auto-generated and all of
    them runnable on Colab with no installation. See just below.

* ***CONCEPT NOTEBOOKS, ONE PER IDEA*** (`Chapter1-Intro/` ... `Chapter18-Lambda/`, `Basics/`)

  - Each chapter folder holds one directory per *concept*, and each of those
    holds a notebook:

    ```
    Chapter4-DFA/Concept-Pumping-Lemma-Predicate-Logic/
             Concept-Pumping-Lemma-Predicate-Logic.ipynb
    ```

    All eighteen chapters are covered, plus Appendix A under `Basics/`:
    **266 notebooks**, **88** of which animate a machine you can step through
    (`AnimateDFA`, `AnimateNFA`, `AnimatePDA`, `AnimateTM`).

  - **They run on Colab with nothing installed.** The first cell clones Jove on
    its first run and pulls on every run after that, and tells you which of the
    two it did. Open any notebook on GitHub and hit the Colab extension, or go
    straight there:

    ```
    https://colab.research.google.com/github/ganeshutah/Jove/blob/master/
        Chapter4-DFA/Concept-Designing-A-DFA/Concept-Designing-A-DFA.ipynb
    ```

    They run just as well on a local checkout --- the same cell detects that
    case and uses the checkout it is sitting in.

  - Every notebook has the same five parts: **the idea**, the **definitions**,
    **tests** that exercise them, an **animation** where there is a machine to
    step through, and **exercises**. A previous/index/next link strip sits in
    the middle of each one, so you can read straight through all 266 in order.

  - Folders are named for the *idea*, not for a lecture number or a course
    year, so they stay correct when the course is renumbered or re-run.
    [Chapters-README.md](Chapters-README.md) has the full layout and a
    per-chapter table.

  - **These notebooks are generated, not hand-maintained.** The generators live
    in the companion workbook repo, under
    `Concepts/tools-concept/nbgen/` (`ch1_nb.py` ... `ch18_nb.py`,
    `appA_nb.py`). To change a notebook, change its generator and regenerate.
    Editing the `.ipynb` by hand works until the next regeneration overwrites
    it.

* ***NOW FOR THE LONGER VERSION***

* Jove helps you learn about various Models of Computation as well as what is usually called ``Automata Theory''

* There are two directories here:

  - For_CS3100_Fall2020 is tailor-made for the Fall 2020 offering of the CS 3100 class. That directory will have self-contained instructions
    and this is where my current class students must be working initially.

  - For_The_Public is for the general public or CS 3100 students who want more examples to look at

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


  - We have ported Dr. Tyler Sorensen's BDD tool into Jove (discussed in 21_NPC_Lambda)
  - This was given via a web interface (http://formal.cs.utah.edu:8080/pbl/BDD.php) which is under maintenance (sometimes)
  - Check it out by running BDD.ipynb :) where this web dependency is removed!


**[The End, ... but Marvel at Jove, creator of the "double anti-whammy!"](https://www.nytimes.com/2009/07/26/weekinreview/26overbye.html) **





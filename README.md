# Introduction to Jove

This git project presents the Jupyter notebooks that go with
Ganesh Gopalakrishnan's book 

 _Automata and Computability: Programmer's Perspective_

We may abbreviate this book's title by ``ACPP''
 
The code collection is called "Jove" (which the reader may
recognize as another name for planet Jupiter). We will refer
to the software offering as a whole as "Jove notebooks" but
sometimes also as Jupyter notebooks (when referring to the
individual notebooks).

Jove is a collection of Jupyter notebooks illustrating many
principles:
* Sets, strings and languages
* Language operations
* Construction of and operations on DFA and NFA
* Regular expression parsing and automata inter-conversion
* Derivate-based parsing
* Pushdown automata
* The construction of parsers using context-free productions
* Studies of parsing: ambiguity, associativity, precedence
* Turing machines

Some of the Jupyter notebooks start with a Youtube video link
describing the notebook's content and operation. This can serve
as a handy ``self-tutorial'' of the notebook. Even without such
a video, all notebooks are documented to some extent as are the
functions introduced.

This README also contains a mini
[Jove Reference Manual](#jove-reference-manual).

# Jove's Design and Code Organization

Jove's structure is kept deliberately simple to cater to a broad
audience. We do not employ classes or objects. All automata are
simple structs. A functional style of programming is preferred
where each function takes an automaton-struct and returns another.

We often prefer a side-effect-free functional/recursive/higher-order
style of coding to make the logic of the function stand out.
When iteration makes sense (e.g. NFA to RE conversion) we do employ
the more familiar iterative style.

Most automata (NFA, DFA, PDA, and Turing machines) have "Def_..."
files that define basic operations on these machine-types. We then
provide "Drive_..." files that drive these definitions to illustrate
the use of the functions.

In order to include the "Def_..." files into the "Drive_..." files,
we prefer to generate Python [.py] files from the former, store these
files into an Imports/ directory, and include those [.py] files into
the "Drive_..." files. While the direct importing of Jupyter notebooks
into other notebooks is supported, we once ran into bugs, and felt
that this arrangement was more foolproof.

A key requirement is to have **lex.py** and **yacc.py** in the top-level
directory. This will be invoked during parsing.

All automata are displayed using Graphiviz for which your Jupyter
notebook must have Graphiviz installed.

# Obtaining and Setting up Jupyter for running Jove

In order to run Jove, you need to set up Jupyter on your machine.
Detailed instructions for setting up Jupyter are provided
[IN THIS OVERLEAF DOCUMENT.](https://www.overleaf.com/read/zbdvqwxmcknm).

# A Tutorial Introduction to Jove

We now provide a tutorial introduction to Jove. We encourage you to
load-up these [.ipynb] files, watch the Youtube video at its beginning
(assuming it has one), and then experiment with its contents. We will
mention the names of the [.ipynb] files below, and in case they are
backed by a Youtube video, then mention that video's link as well.
We mention the youtube links because in case you have not successfully
set up Jupyter notebooks, you can still experience Jove.

## Prerequisites to running the Jove code

There are no prerequisites. Once you follow the instructions
listed under
[Obtaining and Setting up Jupyter for running Jove]
(#obtaining-and-setting-up-jupyter-for-running-jove), 
you should be able to run _any_ file under Jupyter.
You can run the Jupyter file [.ipynb] either cell by cell
or by the ``run all cells'' command. All that is needed is:

 * The lex.py and yacc.py files

 * The Imports/ directory

**Please note:** Some of the Youtubes are live class-lecture recordings,
and may contain material that you do not care about. Feel free to zoom
forward till I illustrate things on Jupyter notebooks.

## Basics of Computability

  * [THIS YOUTUBE VIDEO]
    (https://youtu.be/FQJ4qN44Syg)
    sets the stage for the ACPP book, and introduces some basics,
    including how you can become proficient in Jupyter notebooks
    and also learn a subset of the markdown language (usable to
    create documentation within Jupyter notebooks.

  * The associated Jupyter notebook is
    *Module1_Computability.ipynb*
        
## Strings, Languages, and Language Operations

  * [THIS YOUTUBE VIDEO]
    (https://youtu.be/gaWmjvJ-mP4)
    demonstrates how to define strings and languages in Jove. 
    It also describes how one can perform language operations, including
    union, intersection, and Kleene-star.

  * The Jupyter notebook to practice these ideas is
    *Module2_LanguageOps.ipynb*
  
## Basic DFA definitions and operations

  * DFA definition and operations on DFA are presented in
   [THIS YOUTUBE VIDEO](https://youtu.be/Bdr926TeQyQ)

  * The associated Jupyter notebooks are *Def_DFA.ipynb* and
    *Drive_DFA_Unit1.ipynb* go with the above video.

  * These notebooks introduce the
    markdown syntax, how to build a DFA, etc. Testing DFAs can be achieved
    by introducing a way to generate strings as per the _numeric order_.
    This ensures that all short strings are exhaustively tested before
    longer strings are tried.

  * Another useful Youtube that introduces DFA is in
   [THIS YOUTUBE VIDEO](https://youtu.be/dGcLHtYLgDU)

  * The Jupyter file *DFAUnit2.ipynb* goes with this video. This covers more DFA
   operations.

## The Pumping Lemma illustrated using cellphone word completion (courtesy Prof. Suresh Venkat)

  * [THIS YOUTUBE VIDEO](https://youtu.be/7U5iQGnCKN4)
  demonstrates that hidden in most products today is an automaton,
  and it shows its true color when pushed :)

## NFA operations, EClosure, etc

  * NFA operations, including using Jupyter widgets to show EClosure
    are shown in [THIS YOUTUBE VIDEO](https://youtu.be/xjFtLF95uBc)
    and also [THIS YOUTUBE VIDEO](https://youtu.be/T-akdMIXOGY)

  * The associated Jupyter notebook is *Drive_NFA.ipynb*.

## NFA to RE Conversion
  * [THIS YOUTUBE VIDEO](https://youtu.be/jqdz5s6VWWY) describes the material.

  * The associated Jupyter notebook is *Drive_NFA_9_26_17_Class.ipynb*
  
## Solving the Postage-Stamp Problem using Minimal DFA, and also DFA Minimization using Brzozowski's algorithm
  * These two neat topics are presented in
    [THIS YOUTUBE VIDEO](https://youtu.be/L6l3c17mpi4)

  * The associated Jupyter notebook is *Drive_NFA_9_28_17_Class.ipynb*

## Derivative-based Parsing (Brzozowski's Derivatives)

  * [THIS YOUTUBE VIDEO](https://youtu.be/xGvCjoWemWg) presents the
    basics

  * The associated Jupyter notebooks are *A4J.ipynb* and *A4JSoln.ipynb*

## Pushdown Automata

  * Pushdown Automata (with a CFG-parsing perspective) are explained here in
    [THIS YOUTUBE VIDEO](https://youtu.be/cvVl1lQ4agU)

  * The associated Jupyter notebook is *Drive_PDA_Ch12_Recording.ipynb*
  
  * PDA design with acceptance of various inputs (by empty stack or final
    state) are explained in
    [THIS YOUTUBE VIDEO](https://youtu.be/zKeHDwKXF7E)

  * The associated Jupyter notebook is *Drive_PDA_w_asg5_possibilities_emptystk_a1b2.ipynb*

## Turing Machines

  * Turing Machines are explained in
    [THIS YOUTUBE VIDEO](https://youtu.be/E1X8OTWUxJ0)

  * The associated Jupyter Notebook is *Ch13_Recording.ipynb*

# Jove Reference Manual


# Introduction

This git project presents the Jupyter notebooks that go with
Ganesh Gopalakrishnan's book 

 _Automata and Computability: Programmer's Perspective_
 
The code collection is called "Jove" which the reader may
recognize as another name for planet Jupiter.

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

All automata are displayed using Graphiviz for which your Jupyter
notebook must have Graphiviz installed.

# Obtaining and Setting up Jupyter for running Jove

In order to run Jove, you need to set up Jupyter on your machine.
Detailed instructions for setting up Jupyter are provided
[in this Overleaf document.](https://www.overleaf.com/read/zbdvqwxmcknm).

# A Tutorial Introduction to Jove

We now provide a tutorial introduction to Jove. We encourage you to
load-up these [.ipynb] files, watch the Youtube video at its beginning
(assuming it has one), and then experiment with its contents. We will
mention the names of the [.ipynb] files below, and in case they are
backed by a Youtube video, then mention that video's link as well.
We mention the youtube links because in case you have not successfully
set up Jupyter notebooks, you can still experience Jove.

* Strings, Languages, and Language Operations

  [This Youtube video]
  (https://www.youtube.com/watch?v=gaWmjvJ-mP4&feature=youtu.be)
  demonstrates how to define strings and languages in Jove. It
  also describes how one can perform language operations, including
  union, intersection, and Kleene-star.

  The Jupyter notebook to practice these ideas is
  Module2_LanguageOps.ipynb

  
  



# Jove Reference Manual


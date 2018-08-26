<header> 
    <font size="6">
    Jove: Jupyter Notebooks for Automata and Computability 
    </font>
</header>

# Introduction to Jove

This git project presents the Jupyter notebooks that go with
Ganesh L. Gopalakrishnan's book 

 _Automata and Computability: Programmer's Perspective_

We may abbreviate this book's title by ``ACPP''

The Github URL for this README.md is https://github.com/ganeshutah/Jove.git

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
* The construction of parsers using context-free productions, including
  a full lexer/parser for Jove's own markdown syntax
* Studies of parsing: ambiguity, associativity, precedence
* Turing machines (including one for the Collatz problem)
* Solver for the Post Correspondence Problem (Ling Zhao's PCP
  solver made available through a convenient Jupyter notebook)

Some of the Jupyter notebooks start with a Youtube video link
describing the notebook's content and operation. This can serve
as a handy ``self-tutorial'' of the notebook. Even without such
a video, all notebooks are documented to some extent as are the
functions introduced.

**PLEASE NOTE: The Youtube videos often contain class lecture
screen recordings. Feel free to scroll around in these videos
to locate Jove (Jupyter notebook) sessions, and follow those.**

Read [a newly added note to Windows users](#note-to-windows-users)

# Jove's Design and Code Organization

Jove's structure is kept deliberately simple to cater to a broad
audience. We do not employ classes or objects. All automata are
simple structs. A functional style of programming is preferred
where each function takes an automaton-struct and returns another.

We often prefer a side-effect-free functional/recursive/higher-order
style of coding to make the logic of the function stand out.
When iteration makes sense (e.g. NFA to RE conversion) we do employ
the more familiar iterative style.

[The section contents](#contents) specifies how we offer all the
files belonging to Jove.

Most automata (NFA, DFA, PDA, and Turing machines) have "Def_..."
files that define basic operations on these machine-types. We then
provide "Drive_..." files that drive these definitions to illustrate
the use of the functions.

In order to include the "Def_..." files into the "Drive_..." files,
we prefer to generate Python [.py] files from the former, store these
files into an jove/ directory, and include those [.py] files into
the "Drive_..." files. While the direct importing of Jupyter notebooks
into other notebooks is supported, we once ran into bugs, and felt
that this arrangement was more foolproof.

A key requirement is to have **lex.py** and **yacc.py** in the top-level
directory. This will be invoked during parsing.

All automata are displayed using Graphiviz for which your Jupyter
notebook must have Graphiviz installed; we provide
[complete instructions in this section.]
(#obtaining-and-setting-up-jupyter-for-running-jove).

# Obtaining and Setting up Jupyter for running Jove

**Please consider installing Jupyter Lab after you setup Jupyter. It makes Jove shine! Here is info on the just-released [Jupyter Lab](https://blog.jupyter.org/jupyterlab-is-ready-for-users-5a6f039b8906)**

In order to run Jove, you need to set up Jupyter on your machine.
Detailed instructions for setting up Jupyter are provided 
[IN THIS OVERLEAF DOCUMENT](https://www.overleaf.com/read/zbdvqwxmcknm).
(which will be kept updated) and also in [THIS SECTION](#installing-jupyter-and-jove)
(which may become obsolete; hopefully not)

# CONTENTS

Salient contents of this git directory are now described:

* 3rdparty -- contains 3rd-party stuff (lex.py and yacc.py for now)
* **jove**     -- all the key Jove include files [.py]
* machines -- examples of machines in Jove markdown syntax you can study
* tools    -- a Python script to clear output cells before you save [.ipynb]
* notebooks
  - **tutorial** -- Jupyter notebooks you can run and study (has Youtube videos)
  - module   -- More Jupyter notebooks you can run and study (some Youtube)
  - src      -- These are the Def_*.ipynb from which the aforesaid **jove** [.py] files obtained
  - driver   -- These are still more Jupyter notebooks to run and study 'src'

## NOTE TO WINDOWS USERS

 Update of 8/21/18: For Windows users, the Jove repo provided should work fine without changes!

 But we have ended up copying the jove/ directory and lex.py as well as yacc.py into
 all the directories that need them. This is code-replication, and we may go back to our
 "old instructions".

 The old instructions to windows users is included [AT THE END] 
 (#obsolete-but-perhaps-interesting). It consisted of using
 symbolic links etc. It is a pain, so we have moved away from this.
 But look at that section if you are curious.

## Begin by taking a few tutorials

 Begin by taking tutorials from the **tutorials** directory.
 This directory contains [.ipynb] notebooks that have embedded
 Youtube links. The 
 [Jove Tutorials are described in detail here]
 (#jove-tutorials-are-described-in-detail-here).
 Just go to this directory and type 'jupyter notebook'
 and execute the cells in tutorial notebooks you see here.

## Learn Jove's markdown syntax for creating well-documented machines

While drawing is a good way to create small machines, larger machines
are like assembly code: you must create them with good documentation
and well-chosen state names. For this, we provide a convenient markdown
syntax.
* Learn this syntax by running notebooks/driver/Drive_md2mc.ipynb
* Learn the construction of a mini-compiler including lexer and parser
  for parsing the markdown syntax and turning them into Jove's
  internal representation (structs) by a parser present in
  notebooks/src/Def_md2mc.ipynb. This is what is driven by
  notebooks/driver/Drive_md2mc.ipynb.
 
## Other Directory Contents

You may descend into any of these directories and execute the
Jupyter notebooks you find there. Here are more specifics:

  * Module_... contained in the **notebooks/modules** directory:

  >* These files were created before we designed Jove's input markdown
     language. They are still valuable illustrations.

  *  Notice that some of the very well-coded Turing machines (by Ian
     Briggs) are available only in the ``low-level'' form (specifically
     inside *Module10_TM.ipynb*) -- and **not** in the markdown form yet.
     Thus, this **module** directory has great value for studying some
     non-trivial TMs.

  * The **machines** directory contains
    four directories dfafiles, nfafiles, pdafiles, and tmfiles that
    contain examples of Jove markdown files. This is how you can
    build machines using an editor and load into Jove via the
    command **md2mc**. 

  * Def_.. files contained in **notebooks/src** directory

  >* This is a directory containing Jove definitions. We exported
     these Jupyter notebooks into [.py] and stuck them within the
     **jove** directory

  * Drive_... files contained in the **notebooks/driver**

  >* This is a directory containing many useful illustrations of Jove.
     Some are called out in the Jove tutorial to follow in the next
     section. All these Drive_... files have a fairly high pedagogical
     value (in our estimate, anyway)

# Jove Tutorials are described in detail here

We now provide a tutorial introduction to Jove. We encourage you to
load-up these [.ipynb] files, watch the Youtube video at its beginning
(assuming it has one), and then experiment with its contents. We will
mention the names of the [.ipynb] files below, and in case they are
backed by a Youtube video, then mention that video's link as well.
We mention the youtube links because in case you have not successfully
set up Jupyter notebooks, you can still experience Jove.

Once you follow the instructions
listed under
[Obtaining and Setting up Jupyter for running Jove]
(#obtaining-and-setting-up-jupyter-for-running-jove), 
you can run the Jupyter file [.ipynb] either cell by cell
or by the ``run all cells'' command. 

**PLEASE NOTE:** Some of the Youtubes are live class-lecture recordings,
and may contain material that you do not care about. Feel free to zoom
forward till I illustrate things on Jupyter notebooks.

We now describe the tutorials provided.

## Basics of Computability

  * [THIS YOUTUBE VIDEO]
    (https://youtu.be/FQJ4qN44Syg)
    sets the stage for the ACPP book, and introduces some basics,
    including how you can become proficient in Jupyter notebooks
    and also learn a subset of the markdown language (usable to
    create documentation within Jupyter notebooks.

  >* The associated Jupyter notebook is
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

  >* The associated Jupyter notebooks are *Def_DFA.ipynb* and
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
  demonstrates that the word-completion automaton
  hidden in cellphones gets trapped in a cycle when
  given a huge succession of words to complete.

## NFA operations, EClosure, etc

  * NFA operations, including using Jupyter widgets to show EClosure
    are shown in [THIS YOUTUBE VIDEO](https://youtu.be/xjFtLF95uBc)
    and also [THIS YOUTUBE VIDEO](https://youtu.be/T-akdMIXOGY)

  >* The associated Jupyter notebook is *Drive_NFA.ipynb*.

## NFA to RE Conversion
  * [THIS YOUTUBE VIDEO](https://youtu.be/jqdz5s6VWWY) describes the material.

  >* The associated Jupyter notebook is *Drive_NFA_9_26_17_Class.ipynb*
  
## Solving the Postage-Stamp Problem using Minimal DFA, and also DFA Minimization using Brzozowski's algorithm
  * These two neat topics are presented in
    [THIS YOUTUBE VIDEO](https://youtu.be/L6l3c17mpi4)

  >* The associated Jupyter notebook is *Drive_NFA_9_28_17_Class.ipynb*

## Derivative-based Parsing (Brzozowski's Derivatives)

  * [THIS YOUTUBE VIDEO](https://youtu.be/xGvCjoWemWg) presents the
    basics

  >* The associated Jupyter notebooks are *A4J.ipynb* and *A4JSoln.ipynb*

## Pushdown Automata

  * Pushdown Automata (with a CFG-parsing perspective) are explained here in
    [THIS YOUTUBE VIDEO](https://youtu.be/cvVl1lQ4agU)

  >* The associated Jupyter notebook is *Drive_PDA_Ch12_Recording.ipynb*
  
  * PDA design with acceptance of various inputs (by empty stack or final
    state) are explained in
    [THIS YOUTUBE VIDEO](https://youtu.be/zKeHDwKXF7E)

  >* The associated Jupyter notebook is *Drive_PDA_w_asg5_possibilities_emptystk_a1b2.ipynb*

## Turing Machines

  * Turing Machines are explained in
    [THIS YOUTUBE VIDEO](https://youtu.be/E1X8OTWUxJ0)

  >* The associated Jupyter Notebook is *Ch13_Recording.ipynb*

## Post Correspondence Problem (PCP) solver

  * Since this requires a third-party software system, namely
    Ling Zhao's PCP solver, kindly read the README.md file in
    the 3rdparty directory.
  
  >* The associated Jupyter Notebook is *Drive_pcp.ipynb*

  
  

  
# How to read and extend the code of Jove

## Understanding and extending Jove's markdown processing

   * Much of the convenience of defining machines stems from Jove's
     ability to handle machines described via a markdown syntax.
   
   >* Please peruse *Def_md2mc.ipynb* and *Drive_md2mc.ipynb* to
      fully appreciate how Jove's own markdown processing works.
      In a sense, this is a _mini compiler_ that takes Jove's markdown
      and produces the ``machine'' (hash-table) version of Jove's code

      Code written prior to this markdown facility being developed
      is in ModuleN_... files
   
## Extending the Dot display routines

   * We perform all the processing of ``machine'' (hash-table) descriptions
     and convert them into Graphviz objects.

   >* File DotBashers.ipynb is the heart of this markdown processing.
      This file also checks for the well-formedness of machines.
      It also has utilities such as __fuse-edges__ to collapse
      multiple machine-edges into one

## Extending other aspects of Jove's functionality

   * For all aspects of Jove's functionality, refer to the Def_... files.
     If/when you change the functionality of any of the Def_... files,
     kindly generate a [.py] file and deposit that into the jove/
     directory


# Installing Jupyter and Jove

## Download Anaconda for Python 3

   * Linux: 64-bit or 32-bit
   * Mac:   64-bit
   * Windows: 64-bit or 32-bit 

## Linux Install

   1. Start the installer (instructions assume 64-bit)

   2. To install system-wide:
      - sudo -H bash Anaconda3-4.4.0-Linux-x86_64.sh

   3. To install only for your user:
      - bash Anaconda3-4.4.0-Linux-x86_64.sh

   4. In the installer, do the following:
       - View the license and accept it
       - Choose where to install (you can press enter for the default)
       - Answer ``yes'' to having the Anaconda path prepended to your PATH

   5. Exit that terminal and open a new one.
       - Make sure that the
         'jupyter' found is the one you installed, via command 'which jupyter'.
       - This should return a path in the directory where you
         installed Anaconda 3.
       - It will be similar to /home/username/anaconda3/bin/jupyter

   6. Install the graphviz command-line module (use
      'sudo -H' if you installed Anaconda 3 system-wide)
       - conda install graphviz

   7. Now install the python module for using graphviz.  First, make sure the 'pip'
      tool used is the one from the Anaconda 3 install.
       - which pip

   8. Now for the installing of the graphviz python module.  If you installed
      Anaconda 3 into your home directory, then do the following:
       - pip install graphviz

   9. If you installed Anaconda 3 system-wide, you can install the graphviz module
      system-wide:
       - sudo -H $(which pip) install graphviz
       - Notice the '$(which pip)' since the root account may not have the same
         PATH as you.  Or you can install graphviz into only your home directory
	 as follows: 'pip install --user graphviz'

   10. Go to [Make sure the install works](#make-sure-the-install-works) section at the
       end to verify correct installation.

       
## Mac Install

### Download
```
$ curl https://repo.anaconda.com/archive/Anaconda3-5.2.0-MacOSX-x86_64.sh -o install.sh
```
### Run
```
$ bash install.sh 
```
### Interactive Installation
```
Welcome to Anaconda3 5.2.0

In order to continue the installation process, please review the license
agreement.
Please, press ENTER to continue
>>> 
```
```
===================================
Anaconda End User License Agreement
===================================
```

Press `SPACE BAR`

```
Do you accept the license terms? [yes|no]
[no] >>> yes
```
```
Anaconda3 will now be installed into this location:
/Users/yourname/anaconda3

  - Press ENTER to confirm the location
  - Press CTRL-C to abort the installation
  - Or specify a different location below

[/Users/vinuj/anaconda3] >>> 
PREFIX=/Users/yourname/anaconda3
```

### Finishing Installation
```
installation finished.
Do you wish the installer to prepend the Anaconda3 install location
to PATH in your /Users/yourname/.bash_profile ? [yes|no]
[yes] >>> yes
```

### Check .bash_profile
```
Appending source /Users/yourname/anaconda3/bin/activate in
newly created /Users/yourname/.bash_profile

For this change to become active, you have to open a new terminal.

Thank you for installing Anaconda3!

===========================================================================
```


### No Need to install Any Editors
```
To install Visual Studio Code, you will need:
  - Internet connectivity

Visual Studio Code License: https://code.visualstudio.com/license

Do you wish to proceed with the installation of Microsoft VSCode? [yes|no]
>>> no
```

### Testing

#### Same Terminal
`.bash_profile` is activated only when you start a new `terminal`, which means 
that if you try the following, in the same terminal as the installation then 
you will get the following message.
```
$ conda
-bash: conda: command not found
```

#### New Terminal
```
$ which conda
/Users/yourname/anaconda3/bin/conda
```

### Checks


```
$ cat ~/.bash_profile 
```
You should notice.
```
# added by Anaconda3 installer
export PATH="/Users/yourname/anaconda3/bin:$PATH"
```

### Jove Dependencies
* Install the graphviz command-line tools.
```
- conda install graphviz
```

* Install the graphviz python module
```
pip install graphviz
```

* Go to [Make sure the install works](#make-sure-the-install-works) section at the 
end to verify correct installation.

## Windows Install

   1. Run the installer installing into your home directory.
      You do not need to add the Anaconda 3 directories to your system PATH.

   2. After the install, open an Anaconda Prompt (go to the start menu and search
      ``Anaconda Prompt'').
      - Note that if you ignored the advise to install in your
        home directory, you will want to right-click on the Anaconda Prompt icon and
        select ``Run as Administrator''.

   3. In this prompt, install graphviz
      - conda install graphviz

   4. Now install the python graphviz module
      - pip install graphviz


   5. Now the graphviz module (or arguably the subprocess module) has a bug that we
      will need to work around.
      Basically, calling subprocess.check_call(['dot'])
      doesn't match with dot.bat that is in the system PATH.
      There are two fixes for this. Choose whichever one you want.

    6. The first is to add the graphviz command-line tool directory to your system path
       - Open the control panel
       - Search for 'environment' and click on 'Edit environment variables for your
         account'.
       - Double click on ``Path'' in the top half of the window.  Add the
         path for graphviz, which should be something like this:
	    C:\$Users\username>\Anaconda3\Library\bin\graphviz
       - Close all command prompts and open them again to have updated PATH variables

    7. The second is to replace 'dot' with 'dot.bat' in the graphviz python module.
       - Navigate to the graphviz python module directory, for example
       - C:\Users\<Username>\Anaconda3\Lib\site-packages\graphviz
       - Open in a text editor files.py and backend.py
       - Around line 19 in both files, replace
          'dot' with 'dot.bat'.  (In files.py, it is the value of
	   '_engine', and in 'backend.py, it is a value
         in the ENGINES set.

    8. Go to the section [Make sure the install works](#make-sure-the-install-works) 
    

## Make sure the install works

   1. Now, start the Jupyter notebook

   2. jupyter notebook

   3. If this doesn't open a browser to your notebook, it should print instructions
      on what to do.  Primarily it should give you something to copy and paste into a
      browser.
      
   4. Try out some graph generation in your Jupyter notebook.
      Enter the following in the first cell and press Shift-Enter.

      - import graphviz
      - g = graphviz.Graph()
      - g.edges(['AB', 'BC', 'CD', 'DA'])
      - g


# Obsolete but perhaps interesting

 If you downloaded Jove before 8/21/18, you perhaps got a repo with symlinks etc.
 You had to do these adjustments. These are obsolete now.

 1. Go to the jove folder
    - remove the Unix-style symlinks lex.py and yacc.py  
    - and run these commands:
       * mklink lex.py .. \ 3rdparty \ lex.py (symlink works apparently)
       * mklink yacc.py .. \ 3rdparty \ yacc.py (symlink works apparently)

 2. Go to **EACH** of these folders: driver, module, src, tutorial:
    - remove the Unix-style symlinks jove, machines, lex.py and yacc.py
    - and run these commands:
       * mklink lex.py .. \ .. \ 3rdparty \ lex.py (symlink works apparently)
       * mklink yacc.py .. \ .. \ 3rdparty \ yacc.py (symlink works apparently)
       * copy over the folder jove from .. \ .. \ jove (symlink does not work)
       * copy over the folder machines from .. \ .. \ machines (symlink does not work)
       


# END

   






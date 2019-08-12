<header> 
    <font size="6">
    Description of the contents of this directory
    </font>
</header>

* Launch\_Jove\_in\_This\_Folder.md : A reminder to launch Jove in this directory! This is
  only to make your directory traversals within a browser easier (Jove will work fine
  wherever you launch it, provided its dependencies are met).

* README\_Short.md and README.md : A description of what Jove is about, and which tutorial
  to do first, once you get Jove installed and running

* notebooks : These are a copious collection of notebooks. Look inside
  the notebooks/ directory to learn more about them.
  The first thing 

* machines : These are example NFA, DFA, PDA, and TM in the Jove markdown
  syntax that you can play with using Jove

* asgjove : Some of my assignments and their files ( --> moved to ClassMaterial/2018)

* quizzes : Some of my quizzes and their files ( --> moved to ClassMaterial/2018)

* MISSING-FILES-WHERE-ARE-THEY : Documents all file relocations

* ClassMaterial : where I'll be adding material useful/relevant for teaching
  
* 3rdparty : Things that came from other sources. We have some of these:

  - lex.py and yacc.py : these came from David Beazley's PLY tools. I have
   made one change within yacc.py (look for my name): it had a line
   "import ply.lex as lex". I changed it to "import lex". I think this is
   important to use lex.py and yacc.py within Jupyter notebooks (it was
   once dying with a 'module not found' error till I did this)

  - Ling Zhao's PCP Solver is required in Drive_pcp.ipynb lives (which
    is Jove/notebooks/driver). The PCP solver is obtainable from
    https://github.com/chrozz/PCPSolver.git and you are requested to
    clone it somewhere, build it, and move the executable, namely "pcp",
    to the directory where Drive_pcp.ipynb lives. In the repo, I provide
    a Mac binary; you will have to do this for other platforms

* jove : These are Python files that are imported into almost all the
  Jove ipynb files. These Python files were (in all cases I can recall)
  generated from similarly named ipynb files. It is better to include
  these .py files (I once tried to import an .ipynb file - say
  foo.ipynb - into another - say bar.ipynb and got a strange JSON-parsing
  error. So to side-step that, I'm now generating foo.py and importing
  that into bar.ipynb)

* tools : It currently only has one tool, namely jupyter-clear.py. This
  is designed to clear the output cells of Jupyter notebooks before saving
  them (causes fewer git conflicts and also reduces the .ipynb file size)

* License.md, README.md, Directory_Contents_Overview.md : serve obvious purposes. Study them.

* Directory_Contents_Overview.md : explains this file

* WishList.md : A growing wishlist of future additions to Jove

# END

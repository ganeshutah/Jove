<header> 
    <font size="6">
    Third-party files
    </font>
</header>

# Lex and Yacc

lex.py and yacc.py originate from David Beazley's PLY tool (see
http://www.dabeaz.com/ply/). I may not have the latest pair of
these files, but what I obtained seems to work fine.

# PCP Solver

Ling Zhao's PCP Solver is required in Drive_pcp.ipynb lives (which
is Jove/notebooks/driver). The PCP solver is obtainable from
https://github.com/chrozz/PCPSolver.git and you are requested to
clone it somewhere, build it, and move the executable, namely "pcp",
to the directory where Drive_pcp.ipynb lives.

To make the Jove version complete, I've put in the "pcp" executable
compiled for Macs in this directory. You may need to change this for
other machines.

Each run of the PCP solver will produce these files (that are put in
.gitignore so you won't accidentally commit them):

sol.txt
temp.txt
unsol.txt
nosol.txt

See the documentation of Zhao's solver to know what these files contain
(you may also guess their contents somewhat easily after each PCP session)

# END

   






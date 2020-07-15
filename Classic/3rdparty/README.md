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

To make the Jove version complete, there are compiled binaries of the pcp solver present in 'driver/pcpbinaries/' as 'pcp_linux', 'pcp_win.exe' and 'pcp_mac' for linux, windows and mac respectively. The underlying os is determined at run-time and links the appropriate binary. You may be required to recompile these binaries for your machine dependencies. The function 'pcp_oslink()' returns the correctly linked binary for the underlying os. This function might require edits to predicate new machine/os types .

Each run of the PCP solver will produce these files (that are put in
.gitignore so you won't accidentally commit them):

sol.txt
temp.txt
unsol.txt
nosol.txt

See the documentation of Zhao's solver to know what these files contain
(you may also guess their contents somewhat easily after each PCP session)

# END

   






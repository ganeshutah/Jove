Tyler Sorensen
February 14, 2012
University of Utah

Summary:
PyBool is a general purpose library for Python for handling
boolean formula. It can parse standard cnf DIMACS files as
well as an in-house language for general formula. The motivation
for creating this library was to allow programmers to do 
interesting projects (like BDDs and SAT) quickly, focusing
on the core algorithms rather than boolean expression. Also
the code was written with readability in mind, so the algorithms
and representation approach can be easily read, studied, or 
modified. 

A lot of the algorithms were gotten from the text:

"Calculus of Computation"
by
Aaron Bradley and Zohar Mana

-------------------------------------------------------------
---Representation Overview-----------------------------------
-------------------------------------------------------------

While the public interface attempts to hide many of these
details, it still may be good to know the representation
strategy for debugging or general understanding.

The boolean formula are represented in two different ways
with functionality for converting between the two.

--Recursive--

A general boolean expression is represented recursively as a
dictionary. It has a "type" field describing what type of
expression it is. Currently the supported types are:

const - constant type (True of False)
var   - variable type
neg   - a negated type
and   - an and expression
or    - an or expression
XOR   - an XOR expression (not supported in all algorithms)
impl  - an implication expression
eqv   - an iff statement

The expressions also contain a recursive field "expr" if it is
a unary operator (neg) and "expr1" and "expr2" if it is a
binary operator. The terminal case is var which has a tuple
"name" field, giving it a string name and a number (used for
converting to cnf).

The recursive representation makes the algorithms very simple.

--List--

A cnf formula is much more simple. It can be represented as
a list of lists, where the inner lists represent the clauses. 
In this form, variables are simply integers (starting with 1)
and the negation of a variable is it's negative value. This
type of representation is consistent with the DIMACS cnf file
format.

Because of the simplicity of the representation many simple
functions are left up to the user to implement. (such as add 
clause)

-------------------------------------------------------------
---Expression Builder----------------------------------------
-------------------------------------------------------------

If you are simply using this interface to parse files, you do
not have to deal with the builder as the parse methods do it 
for you. These are found in PyBool_builder.py

--Recursive--

To build a recursive expression you have the following self
explanatory methods which return expressions:

mk_var_expression(name):
Where name is the string name you want to give to the variable

mk_neg_expression(expr):
make a negation of expr

mk_[and or impl eqv XOR]_expr(expr1, expr2)
make the given binary expression

--List--

Lists are simple data structures and the Python language
gives plenty of support for manipulating them as it is,
so no real public interface for making cnf formulas is given


-------------------------------------------------------------
---Public Interface------------------------------------------
-------------------------------------------------------------

Here are the general methods you will want to use on your
expressions found in PyBool_public_interface.py:

************************************************************
--Recursive--
These are the methods you can use on recursively represented
boolean formula

---------------------------------------------------------------
--propagate(expr, tup):
This function propagates an assignment to a variable.

tup is a tuple of the form (STRING, BOOL) where STRING is
the name of the variable and BOOL is the boolean value to 
assign the variable to. It simplifies the formula as well 
when it can. expr is the expression to propagate through.

It is destructive and the expr pass to it will be modified
so make sure to make a deep copy of it if the original needs
to be preserved.

It returns the new expression 

---------------------------------------------------------------
--apply_sol_expr(expr, sol)
apply the solution SOL to EXPR.

SOL is a DictType of the form {STRING: BOOL}
where STRING is the name of the variable and 
BOOL is the assignment. This method assumes 
all variables are given and is undefined if not,
so make sure to check!

---------------------------------------------------------------
--print_expr(expr)
returns a readable string of EXPR. Good for debugging and
visualization.

NOTE: This needs work as precedence is not considered and
parenthesis are not included in string. (FIXED)

---------------------------------------------------------------
--nne(expr)
Converts EXPR into negation normal form

---------------------------------------------------------------
--exp_cnf(expr)
Converts EXPR into a cnf form exponentially sized 

---------------------------------------------------------------
--poly_cnf(expr)
Converts EXPR into cnf form polynomially sized by introducing
new variables.

---------------------------------------------------------------
--cnf_list(expr)
Given an expression EXPR represented recursively in cnf form,
return a list form of that expression.

---------------------------------------------------------------

***************************************************************
--List--
these are methods you can use on List represented formula

---------------------------------------------------------------
--cnf_propagate(clauses, variable, truth_value)
propagates the assignment of VARIABLE to TRUTH_VALUE in CLAUSES

VARIABLE should be an int greater than 1, TRUTH_VALUE should
be a boolean and CLAUSES should be a list of lists representing
the expression.

---------------------------------------------------------------
--cnf_apply_sol(clauses, sol)
Apply the solution SOL to the expression CLAUSES

CLAUSES should be a list of lists representing the expression
and SOL should be a list of boolean values where the index of
corresponds to the value the variable should be assingned to.

---------------------------------------------------------------
--cnf_get_unit_clauses(clauses)
returns a list of literals (signed integers)
that appear in unit clauses in CLAUSES

---------------------------------------------------------------
--cnf_get_pure_literals(clauses)
returns a list of literals (signed integers)
that appear as pure literals in CLAUSES.

(These are literals that only appear in one polarity in 
the expression)

---------------------------------------------------------------
--cnf_to_rec(clauses)
returns a recursive representation of the cnf expression described
by CLAUSES.

---------------------------------------------------------------
--cnf_get_var(literal)
given a literal LITERAL (signed integer) returns an integer
greater than 0 that represents the variable of LITERAL

---------------------------------------------------------------
--cnf_get_sign(literal)
given a literal LITERAL (signed integer) returns TRUE if it is
greater than 0 (not negated) false otherwise

---------------------------------------------------------------

***************************************************************
--Files

These are the methods that parse and write to files.
---------------------------------------------------------------
--parse_dimacs(fname)
given a dimacs file name FNAME return a dictionary of the form:

"num_vars"    : integer (number of variables)
"num_clauses" : integer (number of clauses)
"clauses"     : list of lists (list representation of expression)

---------------------------------------------------------------
--parse_general(fname)
given a file written in the in-house language FNAME parse it
and return a recursively represented boolean expression

---------------------------------------------------------------
--write_dimacs(clauses, fname)
given a list representation of a boolean formula CLAUSES, write
a dimacs file FNAME

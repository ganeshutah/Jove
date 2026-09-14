"""Binary Decision Diagrams, for the NP-completeness chapter.

The BDD engine lives under ``BDD/`` (also reachable through the ``pbl``
symlink), outside the ``jove`` package, and wants seven directories on
``sys.path`` before any of it will import.  This module puts them there and
wraps the engine in something a notebook can use in one line::

    from jove.Bdd import *
    bdd('''
    Var_Order : a b c d
    f = a | (b & c & d)
    Main_Exp : f
    ''')

The call returns a :class:`Bdd`, which *draws itself* when it is the last
expression in a cell, and which carries its results as DATA -- ``.count``,
``.models``, ``.nodes`` -- so a notebook can assert on them rather than
print a table and invite the reader to agree.

Written against Tyler Sorensen's PyBool/BDD code, ported into Jove.
"""

import contextlib
import io
import os
import sys

__all__ = ['bdd', 'Bdd', 'BDD_PATHS', 'cnf', 'dnf', 'paths',
           'side_by_side', 'decision_tree', 'tree_vs_bdd']


def _paths():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub = ['BDD/python',
           'BDD/python/BDD_V2',
           'BDD/python/BDD_V2/BDD_V2',
           'BDD/python/BDD_V2/BDD_V2/include',
           'BDD/python/PyBool',
           'BDD/python/PyBool/include',
           'BDD/python/PyBool/include/ply']
    return [os.path.join(root, *p.split('/')) for p in sub]


BDD_PATHS = _paths()
for _p in reversed(BDD_PATHS):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

def _import_engine():
    """Import the engine quietly, and without littering the notebook's
    working directory.

    Two things need containing.  The engine chatters on import and ply
    announces its LALR tables on stderr, so both streams are swallowed.
    And ply's yacc() drops `parser.out` and `parsetab.py` into the CURRENT
    directory -- which on Colab is the one the student is working in -- so
    the import happens inside a temporary directory that is then thrown
    away.  Nothing in the engine records the cwd, so this is safe.

    The throwaway parse at the end is deliberate: ply builds its tables on
    the FIRST parse, so spending that here means the reader's first bdd()
    call is silent, quick, and leaves nothing behind either.
    """
    import tempfile
    here = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            os.chdir(tmp)
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                import BDD as engine
                try:
                    engine.bdd_init(['Var_Order : x', 'f = x',
                                     'Main_Exp : f'])
                except Exception:
                    pass
            return engine
        finally:
            os.chdir(here)


_engine = _import_engine()


class Bdd:
    """One built BDD: its diagram, and its answers as data.

    The engine's own entry point prints a report and throws the structure
    away.  This keeps the structure, so that `b.count` is a number you can
    compare and `b.models` is a list you can search.
    """

    def __init__(self, spec):
        self.spec = spec if isinstance(spec, str) else '\n'.join(spec)
        lines = self.spec.splitlines()
        with contextlib.redirect_stdout(io.StringIO()):
            self._b = _engine.bdd_init(lines)
            _engine.ite_build(self._b)
        self.vars = list(self._b['var_order'])

    # ---- answers ------------------------------------------------------
    @property
    def count(self):
        """How many assignments satisfy it."""
        return _engine.sat_count(self._b)

    @property
    def models(self):
        """Every satisfying assignment, as {variable: 0 or 1}."""
        out = []
        with contextlib.redirect_stdout(io.StringIO()):
            for cube in _engine.all_sat(self._b):
                out.append({lit.lstrip('~'): (0 if lit.startswith('~') else 1)
                            for lit in cube})
        return out

    @property
    def nodes(self):
        """Nodes in the drawn diagram: those REACHABLE from the root.

        This is the number that matters -- a BDD answers SAT by being
        looked at, so all the work is in how big it got -- and it is
        counted the way the picture is drawn.  The engine's node table
        always holds both terminals even when the diagram uses only one,
        so counting the table would report 2 nodes for an unsatisfiable
        formula whose diagram is a lone `0`.
        """
        t, seen, stack = self._b['t_table'], set(), [self._b['u']]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            if u not in (0, 1):
                _, lo, hi = t[u]
                stack += [lo, hi]
        return len(seen)

    @property
    def is_sat(self):
        return self.count > 0

    @property
    def is_taut(self):
        return self.count == 2 ** len(self.vars)

    # ---- the picture ---------------------------------------------------
    @property
    def dot(self):
        """The diagram as Graphviz source."""
        tmp = '_jove_bdd_%d.dot' % id(self)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                _engine.dot_bdd(self._b, tmp)
            with open(tmp) as fh:
                return fh.read()
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

    def drawing(self):
        """A graphviz object: the diagram, drawn."""
        import graphviz
        return graphviz.Source(self.dot)

    # A cell ending in bdd(...) shows the diagram, the way a cell ending in
    # dotObj_dfa(...) does.  Delegating the mimebundle rather than defining
    # _repr_svg_ keeps whatever formats graphviz itself offers.
    def _repr_mimebundle_(self, **kw):
        try:
            return self.drawing()._repr_mimebundle_(**kw)
        except Exception:
            return {'text/plain': repr(self)}

    def __repr__(self):
        return ('<Bdd %s: %d node%s, %d of %d assignments satisfy it>'
                % (' '.join(self.vars), self.nodes,
                   '' if self.nodes == 1 else 's',
                   self.count, 2 ** len(self.vars)))

    def report(self):
        """The engine's own summary, printed."""
        print('variables (in order) :', ' '.join(self.vars))
        print('nodes in the diagram :', self.nodes)
        print('satisfying           : %d of %d'
              % (self.count, 2 ** len(self.vars)))
        return self


def bdd(spec):
    """Build the BDD described by `spec`.  See the module docstring."""
    return Bdd(spec)


# ---- reading formulas back off a diagram ------------------------------
#
# A node is (variable index, low, high): `low` is the 0-edge, `high` the
# 1-edge, and nodes 0 and 1 are the terminals.  Every root-to-terminal path
# is therefore a CUBE -- a conjunction of the literals along it -- and the
# variables the path skipped are don't-cares.  That is why both normal
# forms fall straight out of the picture.


def paths(b, to=1):
    """Every root-to-terminal path, as a list of literals.

    `to=1` gives the paths that make the formula true, `to=0` the ones
    that make it false.
    """
    t, out = b._b['t_table'], []

    def walk(u, acc):
        if u in (0, 1):
            if u == to:
                out.append(list(acc))
            return
        i, lo, hi = t[u]
        v = b.vars[i - 1]
        walk(lo, acc + ['~' + v])
        walk(hi, acc + [v])

    walk(b._b['u'], [])
    return out


def dnf(b):
    """Sum of products, read off the paths to the 1 terminal.

    One product per path -- not one per satisfying assignment.  A path
    that skipped a variable did so because the variable does not matter
    there, so this is already far shorter than listing the minterms.
    """
    ps = paths(b, 1)
    if not ps:
        return '0'          # nothing reaches 1: unsatisfiable
    if ps == [[]]:
        # the root IS the 1 terminal, so the single path carries no
        # literals at all -- an empty product, which is TRUE
        return '1'
    return ' | '.join(p[0] if len(p) == 1 else '(%s)' % ' & '.join(p)
                      for p in ps)


def cnf(b):
    """Product of sums, read off the paths to the 0 terminal.

    Each such path is one way to make the formula false, so forbidding it
    is one clause: negate every literal on the path and join with OR.
    That is De Morgan doing the work, and it is why the 0 terminal is
    worth as much as the 1 terminal.
    """
    ps = paths(b, 0)
    if not ps:
        return '1'          # nothing reaches 0: a tautology
    if ps == [[]]:
        # the root IS the 0 terminal: the single path carries no literals,
        # and an EMPTY CLAUSE is false -- the formula is unsatisfiable
        return '0'
    neg = lambda l: l[1:] if l.startswith('~') else '~' + l
    return ' & '.join(neg(p[0]) if len(p) == 1
                      else '(%s)' % ' | '.join(neg(l) for l in p)
                      for p in ps)


# ---- pictures that make a point ---------------------------------------

_STYLE = ('  fontsize=12;\n  node [fontname="Helvetica"];\n'
          '  edge [fontname="Helvetica"];\n')


def _body(dot):
    """The Node/edge lines of a dot file, without its wrapper."""
    return [l.strip() for l in dot.splitlines()
            if l.strip().startswith('Node')]


def side_by_side(*labelled, **kw):
    """Several diagrams in one picture, each in its own captioned box.

    Pass ``(label, Bdd)`` pairs.  Comparing two diagrams is the whole point
    of half the BDD material -- two orders, or a tree against its reduction
    -- and a comparison the reader has to make by scrolling is a comparison
    the reader does not make.
    """
    import graphviz
    import re
    out = ['digraph G {', _STYLE, '  rankdir=TB;', '  compound=true;']
    for i, (label, b) in enumerate(labelled):
        src = b if isinstance(b, str) else b.dot
        out.append('  subgraph cluster_%d {' % i)
        out.append('    label="%s";' % label)
        out.append('    labelloc=t; fontsize=14; color=gray70;')
        for line in _body(src):
            out.append('    ' + re.sub(r'\bNode(\d+)', r'g%d_Node\1' % i, line))
        out.append('  }')
    out.append('}')
    return graphviz.Source('\n'.join(out))


def decision_tree(b, dot_only=False):
    """The UNREDUCED decision tree for the same function.

    One node per prefix of the variable order, $2^n$ leaves, nothing
    shared.  This is what a BDD would be without reduction, and putting it
    beside the BDD is the clearest possible statement of what reduction
    does.  Keep it to five or six variables.
    """
    vs = b.vars
    truth = {tuple(m[v] for v in vs) for m in b.models}
    lines, nid = [], [0]

    def emit(prefix):
        me = nid[0]
        nid[0] += 1
        if len(prefix) == len(vs):
            val = 1 if tuple(prefix) in truth else 0
            lines.append('Node%d [label=%d, shape=box, peripheries=2, '
                         'color=%s]' % (me, val, 'Blue' if val else 'Red'))
            return me
        lines.append('Node%d [label=%s, shape=circle]' % (me, vs[len(prefix)]))
        for bit in (0, 1):
            kid = emit(prefix + [bit])
            lines.append('Node%d->Node%d [label="%d", color=%s]'
                         % (me, kid, bit, 'blue' if bit else 'red'))
        return me

    emit([])
    src = 'digraph G {\n' + _STYLE + '\n'.join('  ' + l for l in lines) + '\n}'
    if dot_only:
        return src
    import graphviz
    return graphviz.Source(src)


def tree_vs_bdd(b):
    """The decision tree and the BDD, side by side.  Reduction, in one look."""
    return side_by_side(('decision tree: %d nodes' % (2 ** (len(b.vars) + 1) - 1),
                         decision_tree(b, dot_only=True)),
                        ('reduced BDD: %d nodes' % b.nodes, b.dot))

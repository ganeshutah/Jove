"""The Post Correspondence Problem, via Ling Zhao's PCPSolver.

Chapter 15's notebooks carry their own ``pcp_search()``: a breadth-first
walk bounded by tile count.  It is honest, and it is slow -- the search is
exponential and the bound is a guess.  This module wraps the real solver
that ships under ``jove/pcpbinaries/``, so an instance the breadth-first
search cannot reach becomes something you can actually run.

The contrast is the lesson.  A faster search does not make an undecidable
problem decidable: the solver still answers ``unsolved`` when it runs out
of depth, and no depth you choose is the right one for every instance.

    from jove.Pcp import *
    pcp([('1', '111'), ('10111', '10'), ('10', '0')])

Indices are **0-based**, matching Chapter 15's ``pcp_check(tiles, sol)``.
The solver itself reports 1-based indices, sometimes reversed; both are
normalised here, and the sequence is VERIFIED by concatenation before it is
returned (see ``_read_order``).

The binary is Linux x86-64, which is what Colab runs.  Off Colab this
module says so rather than failing obscurely.

Solver: PCPSolver 0.0.3, Ling Zhao <zhao@cs.ualberta.ca>, 2003.
"""

import os
import platform
import re
import subprocess
import tempfile

__all__ = ['pcp', 'PcpResult', 'pcp_binary', 'pcp_available']

_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'pcpbinaries', 'pcp_linux')


def pcp_binary():
    """Path to the solver, or None if it is not usable here."""
    if not os.path.exists(_BIN):
        return None
    if not os.access(_BIN, os.X_OK):
        # a checkout can lose the executable bit; git records 100755, but
        # an unzipped archive or a copied folder may not
        try:
            os.chmod(_BIN, 0o755)
        except OSError:
            return None
    return _BIN


def pcp_available():
    """(ok, reason).  Linux x86-64 only -- which is what Colab is."""
    if pcp_binary() is None:
        return False, 'jove/pcpbinaries/pcp_linux is missing or not executable'
    if platform.system() != 'Linux':
        return False, ('the solver is a Linux x86-64 binary and this is %s; '
                       'run this notebook on Colab' % platform.system())
    return True, ''


# ---------------------------------------------------------------- result ---

class PcpResult:
    """What the solver said, with the tile order checked rather than trusted."""

    def __init__(self, tiles, status, order=None, nodes=None, seconds=None,
                 raw='', note=''):
        self.tiles, self.status = list(tiles), status
        self.order, self.nodes, self.seconds = order, nodes, seconds
        self.raw, self.note = raw, note

    @property
    def top(self):
        return ''.join(self.tiles[i][0] for i in self.order) if self.order else None

    @property
    def bottom(self):
        return ''.join(self.tiles[i][1] for i in self.order) if self.order else None

    @property
    def matches(self):
        return bool(self.order) and self.top == self.bottom

    def __repr__(self):
        if self.status == 'solvable' and self.order:
            return ('<PCP solvable: %d tiles, order %s, |match| = %d>'
                    % (len(self.tiles), self.order, len(self.top)))
        return '<PCP %s: %d tiles%s>' % (self.status, len(self.tiles),
                                         ' -- ' + self.note if self.note else '')

    def report(self):
        print('tiles     :', '  '.join('[%s/%s]' % t for t in self.tiles))
        print('status    :', self.status)
        if self.note:
            print('note      :', self.note)
        if self.order:
            print('order     :', self.order, ' (0-based)')
            print('top       :', self.top)
            print('bottom    :', self.bottom)
            print('match     :', self.matches)
        if self.nodes is not None:
            print('nodes     :', self.nodes)
        if self.seconds is not None:
            print('seconds   : %.6f' % self.seconds)
        return self

    def _repr_html_(self):
        """The domino chain, drawn, with the two rows aligned."""
        if not self.order:
            return '<pre>%s</pre>' % repr(self)
        cell = ('border:1px solid #888;padding:3px 7px;'
                'font-family:monospace;text-align:center')
        head = ''.join('<td style="%s;border-bottom:none">%s</td>'
                       % (cell, self.tiles[i][0]) for i in self.order)
        foot = ''.join('<td style="%s;border-top:none">%s</td>'
                       % (cell, self.tiles[i][1]) for i in self.order)
        idx = ''.join('<td style="border:none;font-size:80%%;color:#666;'
                      'text-align:center">%d</td>' % i for i in self.order)
        return ('<table style="border-collapse:collapse">'
                '<tr>%s</tr><tr>%s</tr><tr>%s</tr></table>'
                '<pre style="margin-top:4px">top    %s\nbottom %s\nmatch  %s</pre>'
                % (head, foot, idx, self.top, self.bottom, self.matches))


# ----------------------------------------------------------------- driver ---

def _instance_text(tiles):
    widest = max(max(len(t), len(b)) for t, b in tiles)
    return ('%d %d\n%s\n%s\n'
            % (len(tiles), widest,
               ' '.join(t for t, _ in tiles),
               ' '.join(b for _, b in tiles)))


def _read_order(sol_text, tiles):
    """The tile order, 1-based in the file, verified and returned 0-based.

    Ling Zhao's solver searches from both ends and keeps whichever side
    expanded fewer nodes; when it keeps the reverse one it prints the
    sequence backwards.  That is a heuristic, so rather than parse the
    "Choose the reverse direction" line and trust it, CHECK: concatenate
    the tiles both ways and keep whichever actually matches.  If neither
    does, say so instead of returning a sequence that does not work.
    """
    m = re.search(r'Find the solution in depth:.*?\n\s*([\d ]+?)\s*\n', sol_text)
    if not m:
        return None, 'solver reported a solution but printed no tile order'
    seq = [int(x) - 1 for x in m.group(1).split()]
    if any(i < 0 or i >= len(tiles) for i in seq):
        return None, 'solver printed tile indices outside the instance'
    for cand, how in ((seq, ''), (seq[::-1], 'sequence was printed reversed')):
        top = ''.join(tiles[i][0] for i in cand)
        bot = ''.join(tiles[i][1] for i in cand)
        if top == bot:
            return cand, how
    return None, ('solver printed an order that does not concatenate to a '
                  'match, in either direction: %s' % [i + 1 for i in seq])


def pcp(tiles, depth=None, increment=None, runs=None, quiet=True):
    """Solve a PCP instance.

    `tiles` is a list of (top, bottom) strings.  `depth` caps the search,
    `increment` is the iterative-deepening step, `runs` the number of
    random restarts.  Returns a PcpResult, which draws itself.
    """
    tiles = [(str(t), str(b)) for t, b in tiles]
    if not tiles:
        return PcpResult(tiles, 'unsolvable', note='no tiles')
    if any(not t and not b for t, b in tiles):
        raise ValueError('a tile with both sides empty is not allowed')

    ok, why = pcp_available()
    if not ok:
        return PcpResult(tiles, 'unavailable', note=why)

    # Run inside a temporary directory: the solver writes sol.txt,
    # nosol.txt and unsol.txt into the CURRENT directory, which on Colab
    # is the one the student is working in.
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'in.txt'), 'w') as fh:
            fh.write(_instance_text(tiles))
        cmd = [pcp_binary(), '-i', 'in.txt']
        for flag, val in (('-d', depth), ('-di', increment), ('-r', runs)):
            if val is not None:
                cmd += [flag, str(int(val))]
        try:
            p = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True,
                               timeout=600)
        except subprocess.TimeoutExpired:
            return PcpResult(tiles, 'unsolved', note='solver timed out')
        out = p.stdout

        def read(n):
            q = os.path.join(tmp, n)
            return open(q).read() if os.path.exists(q) else ''
        sol, nosol, unsol = read('sol.txt'), read('nosol.txt'), read('unsol.txt')

    nodes = None
    mn = re.search(r'Total nodes searched:\s*(\d+)', out)
    if mn:
        nodes = int(mn.group(1))
    secs = None
    ms = re.search(r'time:\s*([\d.]+)', out)
    if ms:
        secs = float(ms.group(1))

    if 'Solvable!' in sol:
        order, note = _read_order(sol, tiles)
        status = 'solvable' if order else 'unverified'
        r = PcpResult(tiles, status, order, nodes, secs, sol, note)
    elif 'Unsolvable!' in nosol:
        r = PcpResult(tiles, 'unsolvable', None, nodes, secs, nosol,
                      'proved unsolvable by the solver')
    else:
        r = PcpResult(tiles, 'unsolved', None, nodes, secs, unsol or out,
                      'not settled at this depth -- raise depth, or it may '
                      'have no solution the solver can rule out')
    if not quiet:
        print(out)
    return r

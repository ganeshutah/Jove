"""SKI combinator reduction, animated -- Chapter 18's laboratory.

Chapter 18 argues that computation needs no machine: three combinators and
application suffice.  That is easy to assert and hard to believe, so here
it is running.

    from jove.AnimateSKI import *
    AnimateSKI()                       # 2 + 3, one step at a time

The rules are the whole language::

    I x     -> x
    K x y   -> x
    S x y z -> x z (y z)

COLOUR TRACES THE STEP.  At each step the **redex** -- the subterm about to
be rewritten -- is highlighted in the current term, and after the step the
**contractum** it turned into is highlighted in the same colour.  So a
single reduction can be followed by eye: find the box, press step, see what
the box became.  S, K and I each keep their own colour throughout, because
which rule is firing is most of what you want to know.

WHAT YOU CAN COMPUTE.  Church numerals encode n as "apply f n times", so a
numeral is a function and arithmetic is application:

    encode(3)                    the SKI term for 3
    decode(t)                    apply t to free f and x, count the f's
    PLUS, MULT, SUCC, PRED       arithmetic
    TRUE, FALSE, ISZERO          a conditional, since ISZERO n a b picks
    Y                            a fixed point, hence recursion

That is enough for `sumto(5)` = 5+4+...+0 = 15, which is a recursion with a
base case and therefore needs all of it.  It runs in 3,519 steps.

THE HONEST PART.  Those 3,519 steps pass through a term of 1,145,178
symbols -- if you write it out.  Written as a GRAPH, sharing every repeated
subterm, the same term is 374 symbols: three thousand times smaller.  The
gap is not a curiosity, it is why every real implementation reduces graphs
rather than trees, and `sharing_table()` prints it.
"""

import sys

import ipywidgets as widgets
from IPython.display import HTML, display

__all__ = ['AnimateSKI', 'app', 'show', 'size', 'dag_size', 'step_at',
           'trace', 'encode', 'decode', 'reduce_ski', 'bracket', 'lam',
           'S', 'K', 'I', 'PLUS', 'MULT', 'SUCC', 'PRED', 'TRUE', 'FALSE',
           'ISZERO', 'Y', 'sumto', 'fact', 'sharing_table']

sys.setrecursionlimit(20000)

S, K, I = 'S', 'K', 'I'

COL = {'S': '#1a53c0', 'K': '#b3251f', 'I': '#0f8a4a'}   # one hue per rule
HILITE = '#ffe680'                                       # the redex box
VAR = '#444444'


# ---- terms ---------------------------------------------------------------

def app(*ts):
    """Application, associating to the left: app(a,b,c) is ((a b) c)."""
    out = ts[0]
    for t in ts[1:]:
        out = (out, t)
    return out


def show(t):
    if isinstance(t, str):
        return t
    f, a = t
    return show(f) + ('(%s)' % show(a) if isinstance(a, tuple) else show(a))


def size(t):
    """Symbols if the term is written out as a TREE, copies and all."""
    return 1 if isinstance(t, str) else size(t[0]) + size(t[1])


def dag_size(t, seen=None):
    """Distinct sub-objects: the size if repeated subterms are SHARED.

    Reduction copies: S x y z builds (x z)(y z), and the two z's are the
    same object, not two.  Counting the tree counts that z twice; counting
    the graph counts it once.  For a recursion the two numbers diverge by
    three orders of magnitude, which is the whole argument for graph
    reduction.
    """
    if seen is None:
        seen = set()
    if id(t) in seen:
        return 0
    seen.add(id(t))
    return 1 if isinstance(t, str) else 1 + dag_size(t[0], seen) + dag_size(t[1], seen)


def _spine(t):
    args = []
    while isinstance(t, tuple):
        args.append(t[1])
        t = t[0]
    return t, args[::-1]


def step_at(t):
    """One leftmost-outermost step: (new term, rule, path to the redex).

    The path is a list of 0/1 turns, so the caller can highlight exactly
    the subterm that fired -- which is what makes the colour tracing work.
    """
    head, args = _spine(t)
    # The redex is the combinator with exactly the arguments it consumes,
    # NOT the whole spine: in `S x y z f g` the rule fires on `S x y z`
    # and leaves `f g` alone.  Highlighting the whole term would colour
    # everything and say nothing, so the path descends past the extra
    # arguments -- one 0-turn each -- to land on the part that changes.
    for rule, arity in (('I', 1), ('K', 2), ('S', 3)):
        if head == rule and len(args) >= arity:
            spare = [0] * (len(args) - arity)
            if rule == 'I':
                return app(args[0], *args[1:]), 'I', spare
            if rule == 'K':
                return app(args[0], *args[2:]), 'K', spare
            x, y, z = args[0], args[1], args[2]
            return app(app(x, z), app(y, z), *args[3:]), 'S', spare
    for i, a in enumerate(args):
        r = step_at(a)
        if r is not None:
            new = list(args)
            new[i] = r[0]
            return (app(head, *new), r[1],
                    [0] * (len(args) - 1 - i) + [1] + r[2])
    return None


def reduce_ski(t, limit=200000):
    """Reduce to normal form.  Returns (term, steps taken)."""
    n = 0
    while n < limit:
        r = step_at(t)
        if r is None:
            return t, n
        t = r[0]
        n += 1
    return t, n


def trace(t, limit=6000):
    """[(term, rule, path)] for each step, then (normal form, None, None)."""
    out = []
    while len(out) < limit:
        r = step_at(t)
        if r is None:
            break
        out.append((t, r[1], r[2]))
        t = r[0]
    out.append((t, None, None))
    return out


# ---- lambda terms, and bracket abstraction -------------------------------

class Lam:
    def __init__(self, v, body):
        self.v, self.body = v, body


def lam(v, body):
    return Lam(v, body)


def _free(t, v):
    if isinstance(t, str):
        return t == v
    if isinstance(t, Lam):
        return t.v != v and _free(t.body, v)
    return _free(t[0], v) or _free(t[1], v)


def bracket(t):
    """Lambda term to SKI, by the standard bracket abstraction.

    No eta rule, so lambda f x. f x becomes a ten-symbol term rather than
    the textbook I.  That is what the transform actually produces, and the
    difference is worth seeing before anyone optimises it away.
    """
    if isinstance(t, str):
        return t
    if isinstance(t, tuple):
        return (bracket(t[0]), bracket(t[1]))
    v, b = t.v, t.body
    if isinstance(b, Lam):
        return bracket(Lam(v, bracket(b)))
    if isinstance(b, str):
        return 'I' if b == v else ('K', b)
    if not _free(b, v):
        return ('K', bracket(b))
    return app('S', bracket(Lam(v, b[0])), bracket(Lam(v, b[1])))


# ---- Church numerals and the standard combinators ------------------------

def encode(n):
    """The SKI term for the Church numeral n."""
    body = 'x'
    for _ in range(n):
        body = ('f', body)
    return bracket(lam('f', lam('x', body)))


def decode(t, limit=2000000):
    """Apply t to free f and x, reduce, and count the f's.

    Pure SKI has no numbers to read off, so the only way to ask a numeral
    what it is, is to give it something to do n times.
    """
    nf, steps = reduce_ski(app(t, 'f', 'x'), limit)
    k, cur = 0, nf
    while isinstance(cur, tuple) and cur[0] == 'f':
        k += 1
        cur = cur[1]
    return (k if cur == 'x' else None), steps


_L = lam
PLUS = bracket(_L('m', _L('n', _L('f', _L('x',
    app('m', 'f', app('n', 'f', 'x')))))))
MULT = bracket(_L('m', _L('n', _L('f', app('m', app('n', 'f'))))))
SUCC = bracket(_L('n', _L('f', _L('x', app('f', app('n', 'f', 'x'))))))
TRUE = bracket(_L('t', _L('f', 't')))
FALSE = bracket(_L('t', _L('f', 'f')))
ISZERO = bracket(_L('n', app('n', _L('y', _L('t', _L('f', 'f'))),
                             _L('t', _L('f', 't')))))
PRED = bracket(_L('n', _L('f', _L('x', app('n',
    _L('g', _L('h', app('h', app('g', 'f')))),
    _L('u', 'x'), _L('u', 'u'))))))
Y = bracket(_L('f', app(_L('x', app('f', app('x', 'x'))),
                        _L('x', app('f', app('x', 'x'))))))

# recursion: a base case chosen by ISZERO, and Y to tie the knot
SUMTO = app(Y, bracket(_L('r', _L('n', app(app(ISZERO, 'n'), encode(0),
    app(PLUS, 'n', app('r', app(PRED, 'n'))))))))
FACT = app(Y, bracket(_L('r', _L('n', app(app(ISZERO, 'n'), encode(1),
    app(MULT, 'n', app('r', app(PRED, 'n'))))))))


def sumto(n):
    """n + (n-1) + ... + 0, computed in SKI.  Returns (value, steps)."""
    return decode(app(SUMTO, encode(n)))


def fact(n):
    """n!, computed in SKI.  Returns (value, steps).  Keep n small."""
    return decode(app(FACT, encode(n)))


def sharing_table(upto=5, kind='sumto'):
    """Tree size against graph size, for the recursive computations."""
    root = SUMTO if kind == 'sumto' else FACT
    print('%3s %8s %16s %14s %9s'
          % ('N', 'steps', 'tree (copied)', 'graph (shared)', 'ratio'))
    for n in range(upto + 1):
        t, k, peak, pdag = app(root, encode(n), 'f', 'x'), 0, 0, 0
        while True:
            if k % 100 == 0:
                s = size(t)
                if s > peak:
                    peak, pdag = s, dag_size(t)
            r = step_at(t)
            if r is None:
                break
            t, k = r[0], k + 1
        print('%3d %8d %16d %14d %8.0fx'
              % (n, k, peak, pdag, peak / max(pdag, 1)))
    print()
    print('Same computation, two ways of writing the same term down.')
    print('Copying is what the rules say; sharing is what every real')
    print('implementation does, and the gap is why.')


# ---- the animation -------------------------------------------------------

MAXCHARS = 1400


def _render(t, path, colour_redex=True):
    """The term as coloured HTML, with the subterm at `path` boxed."""
    out = []

    def walk(u, here, parens):
        boxed = colour_redex and here == path
        if boxed:
            out.append('<span style="background:%s;border-radius:3px;'
                       'padding:0 1px">' % HILITE)
        if isinstance(u, str):
            out.append('<span style="color:%s;font-weight:%s">%s</span>'
                       % (COL.get(u, VAR), 'bold' if u in COL else 'normal', u))
        else:
            f, a = u
            if parens:
                out.append('(')
            walk(f, here + [0], False)
            walk(a, here + [1], isinstance(a, tuple))
            if parens:
                out.append(')')
        if boxed:
            out.append('</span>')

    walk(t, [], False)
    html = ''.join(out)
    return html if len(html) < MAXCHARS * 8 else None


class AnimateSKI:
    """Step through an SKI reduction, with the redex highlighted."""

    def __init__(self, term=None, label='PLUS 2 3', limit=4000):
        display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn'
                     '.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
        if term is None:
            term = app(PLUS, encode(2), encode(3), 'f', 'x')
            label = 'PLUS 2 3 f x'
        self.label = label
        self.tr = trace(term, limit)
        last = len(self.tr) - 1

        self.slider = widgets.IntSlider(
            value=0, min=0, max=last, description='step',
            continuous_update=False, layout=widgets.Layout(width='520px'))
        self.play = widgets.Play(value=0, min=0, max=last, interval=550,
                                 description='run')
        widgets.jslink((self.play, 'value'), (self.slider, 'value'))
        self.out = widgets.Output()
        self.slider.observe(self._draw, names='value')

        display(widgets.VBox([widgets.HBox([self.play, self.slider]),
                              self.out]))
        self._draw()

    def _ipython_display_(self):
        return None

    def _draw(self, _=None):
        i = self.slider.value
        t, rule, path = self.tr[i]
        head = ('<div style="font-family:sans-serif;font-size:90%%">'
                '<b>%s</b> &nbsp; step %d of %d &nbsp;'
                '<span style="color:#666">tree %d &middot; graph %d</span>'
                '%s</div>'
                % (self.label, i, len(self.tr) - 1, size(t), dag_size(t),
                   ('' if rule is None else
                    ' &nbsp; next rule: <b style="color:%s">%s</b>'
                    % (COL[rule], rule))))
        body = _render(t, path)
        if body is None:
            body = ('<i style="color:#888">term too large to draw '
                    '(%d symbols as a tree, %d as a graph)</i>'
                    % (size(t), dag_size(t)))
        legend = ('<div style="font-family:sans-serif;font-size:80%;'
                  'color:#666;margin-top:3px">'
                  '<b style="color:#1a53c0">S</b> x y z &rarr; x z (y z) '
                  '&nbsp; <b style="color:#b3251f">K</b> x y &rarr; x '
                  '&nbsp; <b style="color:#0f8a4a">I</b> x &rarr; x '
                  '&nbsp;&middot;&nbsp; highlight = the redex about to fire'
                  '</div>')
        with self.out:
            self.out.clear_output(wait=True)
            display(HTML(head + '<div style="border:1px solid #bbb;'
                         'border-radius:5px;padding:6px;margin-top:4px;'
                         'font-family:monospace;font-size:13px;'
                         'word-break:break-all;max-height:260px;'
                         'overflow-y:auto;background:#fcfcfc">%s</div>%s'
                         % (body, legend)))

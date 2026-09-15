"""Beta reduction on lambda terms, animated -- Chapter 18.

`AnimateSKI` reduces the *combinator* calculus, where substitution has
already been compiled away.  This animates the thing underneath it, and the
part students actually get wrong:

    (lam x. M) N   ->   M with N put where x was

    from jove.AnimateLambda import *
    AnimateLambda()                       # (lam x.lam y. x) applied twice

COLOUR SHOWS THE SUBSTITUTION.  In the term about to be rewritten, the
**bound variable** and each of its occurrences are one colour and the
**argument** is another, so before pressing step you can see exactly which
letters are about to be replaced and by what.  After the step, the copies
that landed keep the argument's colour, so you can count them: one per
occurrence, none if the variable was unused, several if it appeared
several times.

AND IT SHOWS THE RENAMING.  Substituting naively into

    (lam x. lam y. x) y

would capture the free `y`: it would walk under the `lam y` and become
bound, turning a constant function into the identity.  Real substitution
renames the binder first.  The animation says so when it happens, and
prints the renaming -- because a rule you are told about and never see
fire is a rule you do not believe.

Numerals, arithmetic and a fixed point are provided, so `PLUS 2 3` can be
reduced the same way, in far fewer steps than SKI needs.
"""

import itertools

import ipywidgets as widgets
from IPython.display import HTML, display

__all__ = ['V', 'L', 'Ap', 'Var', 'Lam', 'App', 'show', 'size', 'free_vars',
           'beta_step', 'reduce_lam', 'trace_lam', 'AnimateLambda',
           'church', 'unchurch', 'PLUS', 'MULT', 'SUCC', 'TRUE', 'FALSE',
           'ISZERO', 'IF', 'Y', 'parse', 'LAM', 'subst']

LAM = 'λ'                                  # the lambda glyph

C_BOUND = '#b3251f'      # the variable being replaced
C_ARG = '#1a53c0'        # what replaces it
C_BIND = '#7b3fb8'       # the binder that is disappearing
HILITE = '#ffe680'


# ---- terms ---------------------------------------------------------------

class Var:
    def __init__(self, n): self.n = n
class Lam:
    def __init__(self, v, b): self.v, self.b = v, b
class App:
    def __init__(self, f, a): self.f, self.a = f, a


def V(n): return Var(n)
def L(v, b): return Lam(v, b)
def Ap(*ts):
    out = ts[0]
    for t in ts[1:]:
        out = App(out, t)
    return out


def show(t, top=True):
    if isinstance(t, Var):
        return t.n
    if isinstance(t, Lam):
        s = '%s%s.%s' % (LAM, t.v, show(t.b, True))
        return s if top else '(%s)' % s
    f = show(t.f, False) if not isinstance(t.f, Lam) else '(%s)' % show(t.f)
    a = show(t.a, False)
    if isinstance(t.a, (App, Lam)):
        a = '(%s)' % show(t.a)
    return f + ' ' + a


def size(t):
    if isinstance(t, Var): return 1
    if isinstance(t, Lam): return 1 + size(t.b)
    return size(t.f) + size(t.a)


def free_vars(t):
    if isinstance(t, Var): return {t.n}
    if isinstance(t, Lam): return free_vars(t.b) - {t.v}
    return free_vars(t.f) | free_vars(t.a)


def _fresh(base, avoid):
    for i in itertools.count(1):
        cand = '%s%d' % (base.rstrip('0123456789') or base, i)
        if cand not in avoid:
            return cand


def subst(t, x, s, renamed):
    """t[x := s], renaming binders that would capture a free name of s.

    `renamed` collects the (old, new) pairs so the animation can report
    them.  Capture is the whole reason substitution is not textual, and a
    reader who never sees a rename happen has no reason to believe it.
    """
    if isinstance(t, Var):
        return s if t.n == x else t
    if isinstance(t, App):
        return App(subst(t.f, x, s, renamed), subst(t.a, x, s, renamed))
    if t.v == x:
        return t                                  # x is rebound; done here
    if t.v in free_vars(s) and x in free_vars(t.b):
        new = _fresh(t.v, free_vars(s) | free_vars(t.b) | {x})
        renamed.append((t.v, new))
        body = subst(t.b, t.v, Var(new), renamed)
        return Lam(new, subst(body, x, s, renamed))
    return Lam(t.v, subst(t.b, x, s, renamed))


def beta_step(t, path=()):
    """Leftmost-outermost beta step.

    Returns (contractum, path, var, arg, renamed), where `contractum`
    replaces the subterm AT `path` -- it is not the whole new term.  The
    first version returned a rebuilt whole term *and* a path, so
    reduce_lam() substituted it a second time at that path; the result
    was nonsense that still looked plausible on the identity.
    """
    if isinstance(t, App) and isinstance(t.f, Lam):
        renamed = []
        return subst(t.f.b, t.f.v, t.a, renamed), path, t.f.v, t.a, renamed
    if isinstance(t, App):
        return (beta_step(t.f, path + ('f',))
                or beta_step(t.a, path + ('a',)))
    if isinstance(t, Lam):
        return beta_step(t.b, path + ('b',))
    return None


def _replace(t, path, new):
    if not path:
        return new
    h, rest = path[0], path[1:]
    if h == 'f': return App(_replace(t.f, rest, new), t.a)
    if h == 'a': return App(t.f, _replace(t.a, rest, new))
    return Lam(t.v, _replace(t.b, rest, new))


def reduce_lam(t, limit=5000):
    n = 0
    while n < limit:
        r = beta_step(t)
        if r is None:
            return t, n
        t = _replace(t, r[1], r[0])
        n += 1
    return t, n


def trace_lam(t, limit=400):
    """[(term, path, var, arg, renamed)], then (normal form, None, ...)."""
    out = []
    while len(out) < limit:
        r = beta_step(t)
        if r is None:
            break
        out.append((t, r[1], r[2], r[3], r[4]))
        t = _replace(t, r[1], r[0])
    out.append((t, None, None, None, []))
    return out


# ---- a tiny parser, so terms can be typed ------------------------------

def parse(s):
    r"""Parse a lambda term.  Use \ or L for lambda:  \x.\y. x y"""
    toks, i = [], 0
    s = s.replace(LAM, '\\')
    while i < len(s):
        c = s[i]
        if c.isspace(): i += 1; continue
        if c in '().\\': toks.append(c); i += 1; continue
        j = i
        while j < len(s) and (s[j].isalnum() or s[j] == '_'): j += 1
        toks.append(s[i:j]); i = j
    pos = [0]

    def peek(): return toks[pos[0]] if pos[0] < len(toks) else None

    def atom():
        t = peek()
        if t == '(':
            pos[0] += 1
            e = expr()
            pos[0] += 1                      # ')'
            return e
        if t == '\\':
            pos[0] += 1
            v = toks[pos[0]]; pos[0] += 1
            if peek() == '.': pos[0] += 1
            return Lam(v, expr())
        pos[0] += 1
        return Var(t)

    def expr():
        e = atom()
        while peek() not in (None, ')', '.'):
            e = App(e, atom())
        return e

    return expr()


# ---- Church encodings, as lambda terms ---------------------------------

def church(n):
    b = V('x')
    for _ in range(n):
        b = Ap(V('f'), b)
    return L('f', L('x', b))


def unchurch(t, limit=20000):
    """Reduce t f x and count the f's."""
    nf, _ = reduce_lam(Ap(t, V('f'), V('x')), limit)
    k = 0
    while isinstance(nf, App) and isinstance(nf.f, Var) and nf.f.n == 'f':
        k += 1; nf = nf.a
    return k if isinstance(nf, Var) and nf.n == 'x' else None


PLUS = parse(r'\m.\n.\f.\x. m f (n f x)')
MULT = parse(r'\m.\n.\f. m (n f)')
SUCC = parse(r'\n.\f.\x. f (n f x)')
TRUE = parse(r'\t.\f. t')
FALSE = parse(r'\t.\f. f')
IF = parse(r'\p.\a.\b. p a b')
ISZERO = parse(r'\n. n (\y.\t.\f. f) (\t.\f. t)')
Y = parse(r'\f. (\x. f (x x)) (\x. f (x x))')


# ---- rendering ----------------------------------------------------------

def _html(t, path, var, arg, top=True):
    """The term, with the redex boxed and the substitution coloured.

    Inside the redex the BINDER and every bound occurrence go red and the
    argument goes blue, so the reader can see which letters are about to be
    replaced and by what before pressing step.  An earlier version computed
    that flag in a helper it never called, so the box appeared but the
    letters inside it stayed black -- the one thing the colour was for.
    """
    out = []

    def col(txt, c, bold=False):
        return ('<span style="color:%s%s">%s</span>'
                % (c, ';font-weight:bold' if bold else '', txt))

    def walk(u, here, binder):
        """binder is the variable being replaced, or None outside the redex."""
        boxed = (here == path)
        if boxed:
            out.append('<span style="background:%s;border-radius:3px;'
                       'padding:0 2px">' % HILITE)
        if isinstance(u, Var):
            if binder is not None and u.n == binder:
                out.append(col(u.n, C_BOUND, True))
            else:
                out.append(u.n)
        elif isinstance(u, Lam):
            mark = (binder is not None and u.v == binder)
            out.append(col('%s%s.' % (LAM, u.v), C_BIND, True) if mark
                       else '%s%s.' % (LAM, u.v))
            walk(u.b, here + ('b',), binder)
        else:
            # the redex itself: (lam v. body) arg -- body in red, arg in blue
            inner = u.f.v if (boxed and isinstance(u.f, Lam)) else binder
            need_f = isinstance(u.f, Lam)
            if need_f:
                out.append('(')
            walk(u.f, here + ('f',), inner)
            if need_f:
                out.append(')')
            out.append(' ')
            need_a = isinstance(u.a, (App, Lam))
            if boxed:
                sub = []
                _sub_html(u.a, sub)
                body = ''.join(sub)
                out.append(col('(%s)' % body if need_a else body, C_ARG))
            else:
                if need_a:
                    out.append('(')
                walk(u.a, here + ('a',), binder)
                if need_a:
                    out.append(')')
        if boxed:
            out.append('</span>')

    walk(t, (), None)
    return ''.join(out)


def _sub_html(u, out, parens=False):
    if isinstance(u, Var):
        out.append(u.n)
    elif isinstance(u, Lam):
        out.append('%s%s.' % (LAM, u.v)); _sub_html(u.b, out)
    else:
        f_needs = isinstance(u.f, Lam)
        if f_needs: out.append('(')
        _sub_html(u.f, out)
        if f_needs: out.append(')')
        out.append(' ')
        a_needs = isinstance(u.a, (App, Lam))
        if a_needs: out.append('(')
        _sub_html(u.a, out)
        if a_needs: out.append(')')


class AnimateLambda:
    """Step through a beta reduction, with the substitution coloured."""

    def __init__(self, term=None, label=None, limit=400):
        display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn'
                     '.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
        if term is None:
            term = parse(r'(\x.\y. x) a b')
            label = r'(\x.\y. x) a b'
        if isinstance(term, str):
            label = label or term
            term = parse(term)
        self.label = label or show(term)
        self.tr = trace_lam(term, limit)
        last = len(self.tr) - 1
        self.slider = widgets.IntSlider(value=0, min=0, max=last,
                                        description='step',
                                        continuous_update=False,
                                        layout=widgets.Layout(width='520px'))
        self.play = widgets.Play(value=0, min=0, max=last, interval=900)
        widgets.jslink((self.play, 'value'), (self.slider, 'value'))
        self.out = widgets.Output()
        self.slider.observe(self._draw, names='value')
        display(widgets.VBox([widgets.HBox([self.play, self.slider]), self.out]))
        self._draw()

    def _ipython_display_(self):
        return None

    def _draw(self, _=None):
        i = self.slider.value
        t, path, var, arg, renamed = self.tr[i]
        note = ''
        if var is not None:
            note = (' &nbsp; next: <span style="color:%s;font-weight:bold">%s'
                    '</span> := <span style="color:%s">%s</span>'
                    % (C_BOUND, var, C_ARG, show(arg)))
        warn = ''
        if renamed:
            warn = ('<div style="margin-top:4px;padding:4px 7px;'
                    'background:#fff3cd;border:1px solid #e0c97f;'
                    'border-radius:4px;font-family:sans-serif;font-size:85%%">'
                    '<b>alpha-renamed</b> to avoid capture: %s'
                    '<br><span style="color:#666">the argument has a free '
                    'name that this binder would have swallowed</span></div>'
                    % ', '.join('%s &rarr; %s' % r for r in renamed))
        head = ('<div style="font-family:sans-serif;font-size:90%%">'
                '<b>%s</b> &nbsp; step %d of %d &nbsp;'
                '<span style="color:#666">size %d</span>%s</div>'
                % (self.label, i, len(self.tr) - 1, size(t), note))
        legend = ('<div style="font-family:sans-serif;font-size:80%;'
                  'color:#666;margin-top:3px">highlight = the redex '
                  '&nbsp;&middot;&nbsp; <span style="color:#b3251f">'
                  '<b>red</b></span> = the variable being replaced '
                  '&nbsp;&middot;&nbsp; <span style="color:#1a53c0">blue</span>'
                  ' = what replaces it</div>')
        with self.out:
            self.out.clear_output(wait=True)
            display(HTML(head + '<div style="border:1px solid #bbb;'
                         'border-radius:5px;padding:7px;margin-top:4px;'
                         'font-family:monospace;font-size:15px;'
                         'word-break:break-word;max-height:240px;'
                         'overflow-y:auto;background:#fcfcfc">%s</div>%s%s'
                         % (_html(t, path, var, arg), warn, legend)))

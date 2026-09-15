"""An animated view of the language operations of Chapter 2.

Chapter 2 defines union, intersection, concatenation, exponentiation and
star on languages, and until now there was nothing in it to run: sixteen
consecutive concepts of set notation.  This is the missing laboratory.

    from jove.AnimateLang import *
    AnimateLang()

Two languages, two sliders.  Slider m builds star(L1, m), slider n builds
star(L2, n), and every operation below is computed on THOSE -- so moving a
slider regrows all of them at once.  Press play and watch the sets fill.

COLOUR CARRIES THE ARGUMENT.  L1's strings are blue and L2's are red, and
the colours survive the operations:

  * in star(L1, m) each string is shown with its PIECES in alternating
    shades of blue, so you can see which elements of L1 were concatenated
    to make it -- the decomposition, not just the result;
  * in a concatenation the blue pieces come first and the red after, which
    is what concatenation IS, made visible;
  * in a union a string is blue if only the left set has it, red if only
    the right, and purple if both -- so the overlap is a colour, not a
    claim;
  * in an intersection everything is purple, necessarily.

Sets grow fast.  |star(L, m)| is about |L|^m, so the display caps what it
draws and always reports the true size beside it.  Watching the count race
ahead of the box is the point, not a limitation.
"""

import itertools

import ipywidgets as widgets
from IPython.display import HTML, display

__all__ = ['AnimateLang', 'star_pieces', 'parse_language', 'render_language']

# L1 blue, L2 red, both purple, neither grey.  The two ramps are shades of
# one hue each, so a string's pieces read as "these came from L1" at a
# glance while still showing where each piece ends.
BLUE = ['#1a53c0', '#3f7bd8', '#6fa0e8']
RED = ['#b3251f', '#d4534a', '#e58079']
BOTH = '#7b3fb8'
NEITHER = '#777777'

EPS = 'ε'                     # what the empty string is drawn as


def parse_language(text):
    """A set of strings from a comma-separated box.

    Empty entries, '' and the word eps all mean the empty string, which is
    a member like any other and the one students most often forget.
    """
    out = set()
    for piece in text.split(','):
        p = piece.strip()
        if p in ('', "''", '""', 'eps', 'epsilon', EPS):
            out.add('')
        else:
            out.add(p)
    return out


def star_pieces(L, m, cap=4000):
    """{string: pieces} for the union of L^0 .. L^m.

    Keeps ONE decomposition per string -- the first found, shortest first.
    A string can often be built more than one way; showing every way would
    be a different lesson (ambiguity, Chapter 11) and would bury this one.
    """
    out = {'': []}
    frontier = [('', [])]
    for _ in range(m):
        nxt = []
        for s, pieces in frontier:
            for w in sorted(L):
                t = s + w
                if t not in out:
                    out[t] = pieces + [w]
                    nxt.append((t, out[t]))
                    if len(out) >= cap:
                        return out
        frontier = nxt
    return out


def _spans(pieces, ramp, fallback):
    """[(text, colour)] for one string's pieces, EMPTY PIECES DROPPED.

    An empty piece contributes no symbols, so drawing it would be a lie:
    epsilon concatenated with "ab" is "ab", and rendering it as a visible
    "epsilon-a-b" invents a three-symbol string that does not exist.  The
    epsilon glyph is for a whole string that is empty, and for nothing
    else.
    """
    out, k = [], 0
    for p in pieces:
        if not p:
            continue
        out.append((p, ramp[k % len(ramp)] if ramp else fallback))
        k += 1
    return out


def _draw(spans, fallback=NEITHER):
    """Coloured spans as HTML; an empty result is the empty string."""
    if not spans:
        return ('<span style="color:%s;font-style:italic">%s</span>'
                % (fallback, EPS))
    return ''.join('<span style="color:%s">%s</span>' % (c, t)
                   for t, c in spans)


def _chip(pieces, ramp, fallback):
    """One string, drawn as its coloured pieces."""
    return _draw(_spans(pieces, ramp, fallback), fallback)


def render_language(items, title, total, shown_cap=120):
    """A growing, wrapping box of coloured strings, with the true size."""
    more = total - len(items)
    chips = ''.join(
        '<span style="display:inline-block;border:1px solid #ddd;'
        'border-radius:4px;padding:1px 6px;margin:2px;'
        'font-family:monospace;white-space:nowrap">%s</span>' % c
        for c in items[:shown_cap])
    tail = ('<span style="color:#888;font-size:90%%;padding-left:6px">'
            '+%d more</span>' % more) if more > 0 else ''
    return ('<div style="margin:6px 0">'
            '<div style="font-family:sans-serif;font-size:90%%;color:#333">'
            '<b>%s</b> &nbsp;<span style="color:#888">|&nbsp;%d string%s'
            '</span></div>'
            '<div style="border:1px solid #bbb;border-radius:5px;padding:4px;'
            'min-height:26px;max-height:190px;overflow-y:auto;'
            'background:#fcfcfc">%s%s</div></div>'
            % (title, total, '' if total == 1 else 's', chips, tail))


class AnimateLang:
    """The Chapter 2 operations, animated.  See the module docstring."""

    MAX_EXP = 5
    SHOW = 120

    def __init__(self, L1='a, b, bc, def', L2='ab, c, cdef',
                 m=1, n=1, lam='lambda A, B: A - B'):
        # The play buttons are font-awesome glyphs, and on Colab each cell
        # output is its own sandboxed iframe, so the stylesheet has to be
        # loaded HERE -- the same reason AnimateDFA does it in __init__.
        display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn'
                     '.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))

        box = widgets.Layout(width='340px')
        self.w_L1 = widgets.Text(value=L1, description='L1 (blue)',
                                 layout=box,
                                 style={'description_width': 'initial'})
        self.w_L2 = widgets.Text(value=L2, description='L2 (red)',
                                 layout=box,
                                 style={'description_width': 'initial'})
        self.w_m = widgets.IntSlider(value=m, min=0, max=self.MAX_EXP,
                                     description='m: star(L1, m)',
                                     continuous_update=False,
                                     style={'description_width': 'initial'})
        self.w_n = widgets.IntSlider(value=n, min=0, max=self.MAX_EXP,
                                     description='n: star(L2, n)',
                                     continuous_update=False,
                                     style={'description_width': 'initial'})
        self.play_m = widgets.Play(value=m, min=0, max=self.MAX_EXP,
                                   interval=1100, description='sweep m')
        self.play_n = widgets.Play(value=n, min=0, max=self.MAX_EXP,
                                   interval=1100, description='sweep n')
        widgets.jslink((self.play_m, 'value'), (self.w_m, 'value'))
        widgets.jslink((self.play_n, 'value'), (self.w_n, 'value'))
        self.w_lam = widgets.Text(
            value=lam, description='your op  LE(A, B) =',
            layout=widgets.Layout(width='430px'),
            style={'description_width': 'initial'})
        self.out = widgets.Output()

        for w in (self.w_L1, self.w_L2, self.w_m, self.w_n, self.w_lam):
            w.observe(self._refresh, names='value')

        display(widgets.VBox([
            widgets.HBox([self.w_L1, self.w_L2]),
            widgets.HBox([widgets.VBox([self.w_m, self.play_m]),
                          widgets.VBox([self.w_n, self.play_n])]),
            self.w_lam,
            self.out]))
        self._refresh()

    def _ipython_display_(self):
        # __init__ already displayed everything; this stops the cell also
        # echoing <jove.AnimateLang.AnimateLang at 0x...>.
        return None

    # ---- the six rows ----------------------------------------------------
    def _refresh(self, _=None):
        L1, L2 = parse_language(self.w_L1.value), parse_language(self.w_L2.value)
        A = star_pieces(L1, self.w_m.value)
        B = star_pieces(L2, self.w_n.value)
        setA, setB = set(A), set(B)

        def by_origin(strings):
            # blue if only A has it, red if only B, purple if both, grey if
            # the operation invented it (a concatenation, say)
            out = []
            for s in strings:
                if s in setA and s in setB:
                    out.append(_chip([s], None, BOTH))
                elif s in setA:
                    out.append(_chip(A[s], BLUE, BLUE[0]))
                elif s in setB:
                    out.append(_chip(B[s], RED, RED[0]))
                else:
                    out.append(_chip([s], None, NEITHER))
            return out

        html = []
        html.append(render_language([_chip(A[s], BLUE, BLUE[0])
                                     for s in sorted(A, key=_ord)],
                                    'star(L1, %d)' % self.w_m.value, len(A),
                                    self.SHOW))
        html.append(render_language([_chip(B[s], RED, RED[0])
                                     for s in sorted(B, key=_ord)],
                                    'star(L2, %d)' % self.w_n.value, len(B),
                                    self.SHOW))

        uni = sorted(setA | setB, key=_ord)
        html.append(render_language(by_origin(uni), 'union', len(uni),
                                    self.SHOW))

        # concatenation keeps both decompositions, blue pieces then red
        cat, seen = [], set()
        for a in sorted(setA, key=_ord):
            for b in sorted(setB, key=_ord):
                s = a + b
                if s in seen:
                    continue
                seen.add(s)
                if len(cat) < self.SHOW:
                    cat.append(_draw(_spans(A[a], BLUE, BLUE[0])
                                     + _spans(B[b], RED, RED[0])))
        html.append(render_language(cat, 'concat', len(seen), self.SHOW))

        inter = sorted(setA & setB, key=_ord)
        html.append(render_language([_chip([s], None, BOTH) for s in inter],
                                    'intersection', len(inter), self.SHOW))

        html.append(self._user_op(setA, setB, by_origin))
        with self.out:
            self.out.clear_output(wait=True)
            display(HTML(''.join(html)))

    def _user_op(self, setA, setB, by_origin):
        """Whatever the reader typed, evaluated on the two starred sets."""
        src = self.w_lam.value.strip()
        if not src:
            return ''
        try:
            f = eval(src, {'__builtins__': {}}, {})
            res = f(setA, setB)
            got = sorted(res, key=_ord)
        except Exception as e:
            return ('<div style="color:#b3251f;font-family:monospace;'
                    'font-size:90%%">your op: %s: %s</div>'
                    % (type(e).__name__, e))
        return render_language(by_origin(got), 'your op: %s' % src,
                               len(got), self.SHOW)


def _ord(s):
    """Numeric order: by length, then alphabetically.  Chapter 2's own order."""
    return (len(s), s)

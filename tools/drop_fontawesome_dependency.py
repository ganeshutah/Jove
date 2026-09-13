#!/usr/bin/env python3
"""Remove Jove's font-awesome dependency from the Animate* classes.

WHY THIS EXISTS
---------------
Every animation cell in every Jove notebook carries this boilerplate:

    from jove.AnimateDFA import *
    AnimateDFA(myDFA, FuseEdges=True)
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/
                  font-awesome/4.7.0/css/font-awesome.min.css"/>'))

That one line is doing two unrelated jobs, which is why it cannot simply be
hoisted to the top of the notebook:

  1. It loads the font-awesome stylesheet.  It has to be repeated per cell
     because Colab renders each cell's output in its OWN sandboxed iframe, so
     a <link> injected by cell A does not reach cell B's output.
  2. It returns None, which stops Jupyter echoing the constructor's value.
     Animate*.__init__ already calls display() on the widget, so a cell ending
     in the constructor prints `<jove.AnimateDFA.AnimateDFA at 0x...>` on top
     of the toolbar.

Both jobs can be retired at the source.

WHAT THIS SCRIPT CHANGES
------------------------
(1) The ONLY font-awesome consumers in the whole library are two buttons per
    Animate class -- `Button(icon='step-backward')` and `Button(icon='step-
    forward')`, eight lines in total.  ipywidgets renders `icon=` as
    <i class="fa fa-step-forward">, which is empty without the stylesheet.
    Replacing `icon=` with a Unicode `description=` removes the dependency
    outright: no CDN, no per-cell link, and it works offline.

    The `Play` widget needs nothing -- under ipywidgets 8 it draws its own
    controls -- so it was never the reason for the link.

(2) A no-op `_ipython_display_` is added to each Animate class.  IPython then
    produces an EMPTY mimebundle for the object, so no `Out[n]` appears.
    (`__repr__ = ''` does not achieve this: it still emits a text/plain of
    '', leaving a blank output area.)

    This is backward compatible.  Existing notebooks end the cell with the
    font-awesome line, so the constructor's value is never echoed and the
    hook is never reached; the widget still comes from __init__ exactly as
    before.  Only cells that END with the constructor are affected, which is
    precisely the simplified form this change enables.

AFTER THIS, AN ANIMATION CELL IS JUST

    from jove.AnimateDFA import *
    AnimateDFA(myDFA, FuseEdges=True)

Idempotent.  Use git to revert.  Run with --write to apply; default is a
dry run.  --ascii uses '<<' / '>>' instead of the arrow glyphs.
"""
import argparse, os, re, sys

HERE  = os.path.dirname(os.path.abspath(__file__))
JOVE  = os.path.abspath(os.path.join(HERE, '..', 'jove'))
MODS  = ['AnimateDFA.py', 'AnimateNFA.py', 'AnimatePDA.py', 'AnimateTM.py']

# U+25C0 / U+25B6 are BMP geometric shapes, present in essentially every
# system font -- unlike the U+23EE/U+23ED media glyphs, which need an emoji
# font and box-render without one.
GLYPH = {'step-backward': '|◀', 'step-forward': '▶|'}
ASCII = {'step-backward': '<<',      'step-forward': '>>'}

HOOK = '''
    def _ipython_display_(self):
        """Take over display and emit nothing.

        __init__ has already called display() on the widget, so there is
        nothing left to show.  Defining this hook makes IPython produce an
        empty mimebundle, which suppresses the `<jove.AnimateDFA.AnimateDFA
        at 0x...>` echo when a cell ends with the constructor -- the job the
        trailing display(HTML(...)) line used to do by accident.
        """
        return None
'''


def patch_icons(src, table):
    """icon='step-forward' -> description='>|', widening the button a little."""
    n = 0
    for fa, glyph in table.items():
        pat = re.compile(r"icon=(['\"])%s\1" % re.escape(fa))
        src, k = pat.subn("description=%r" % glyph, src)
        n += k
    # a text label needs a touch more room than a 40px icon square
    src, w = re.subn(r"layout=Layout\(width='40px'\)",
                     "layout=Layout(width='45px')", src)
    return src, n, w


def patch_hook(src, cls):
    """Insert the no-op display hook right after __init__'s body."""
    if '_ipython_display_' in src:
        return src, 0
    # anchor: the first `def ` at class-body indent AFTER __init__
    m = re.search(r"\n    def __init__\(", src)
    if not m:
        return src, 0
    nxt = re.search(r"\n    def (?!__init__)", src[m.end():])
    if not nxt:
        return src, 0
    at = m.end() + nxt.start()
    return src[:at] + '\n' + HOOK.rstrip('\n') + '\n' + src[at:], 1


def patch_docstring(src):
    """The class docstring tells users to add the font-awesome line."""
    old_hint = re.compile(
        r"\s*For producing drawings in Colab, it is important to have these in\s*\n"
        r"\s*every cell that calls animation\.\s*\n(.*?)"
        r"\s*Then the animation works in one's own install or Colab\.\s*\n",
        re.S)
    new_hint = ("\n    Just call it; nothing else is needed:\n\n"
                "    AnimateDFA(myDFA, FuseEdges='True/False')\n\n"
                "    The toolbar no longer depends on the font-awesome stylesheet,\n"
                "    so the old per-cell display(HTML(...)) line is unnecessary.\n")
    src, n = old_hint.subn(new_hint, src, count=1)
    return src, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='apply the changes')
    ap.add_argument('--ascii', action='store_true',
                    help="use '<<' / '>>' instead of arrow glyphs")
    a = ap.parse_args()
    table = ASCII if a.ascii else GLYPH

    tot_i = tot_h = tot_d = 0
    for m in MODS:
        p = os.path.join(JOVE, m)
        src = open(p, encoding='utf-8').read()
        orig = src
        src, ni, nw = patch_icons(src, table)
        src, nh = patch_hook(src, m[:-3])
        src, nd = patch_docstring(src)
        tot_i += ni; tot_h += nh; tot_d += nd
        status = 'unchanged' if src == orig else ('written' if a.write else 'would change')
        print("  %-16s icons %d, widths %d, hook %d, docstring %d   %s"
              % (m, ni, nw, nh, nd, status))
        if a.write and src != orig:
            open(p, 'w', encoding='utf-8').write(src)

    print()
    print("%s: %d icon buttons, %d display hooks, %d docstrings"
          % ('patched' if a.write else 'would patch', tot_i, tot_h, tot_d))
    if not a.write:
        print("(dry run -- pass --write to apply)")


if __name__ == '__main__':
    main()

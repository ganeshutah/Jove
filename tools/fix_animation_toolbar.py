#!/usr/bin/env python3
"""Make Jove's animation toolbar work without per-cell boilerplate.

THE PROBLEM
-----------
Every animation cell had to carry three lines instead of two:

    from jove.AnimateDFA import *
    AnimateDFA(myDFA, FuseEdges=True)
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/
                  font-awesome/4.7.0/css/font-awesome.min.css"/>'))

That third line was doing two unrelated jobs.

  1. Loading font-awesome, which the toolbar needs.  It could not be hoisted
     to the top of the notebook because COLAB RENDERS EACH CELL'S OUTPUT IN
     ITS OWN SANDBOXED IFRAME -- a <link> injected by one cell never reaches
     another cell's output area.

  2. Returning None.  Animate*.__init__ already calls display() on the widget,
     so a cell ENDING in the constructor also echoed
     `<jove.AnimateDFA.AnimateDFA at 0x...>` over the toolbar.  display()
     returns None, and a cell ending in None echoes nothing -- which is the
     entire reason the line had to come LAST.

WHICH BUTTONS NEED FONT-AWESOME
-------------------------------
All of them, and not for the reason you would guess from the Python source.

  * `Button(icon='step-backward')` and `Button(icon='step-forward')` -- Jove's
    own two stepping buttons -- render as <i class="fa fa-step-backward">.

  * The `Play` widget's play / pause / stop buttons are built by the
    IPYWIDGETS FRONTEND, in JavaScript, which emits fa-play, fa-pause and
    fa-stop.  (Confirmed in widgetsnbextension/static/extension.js.)  No
    Python-side change can reach those, because no Python trait controls
    them -- `Play` does not even expose an `icon` trait.

So font-awesome cannot be designed away.  It has to be loaded.

THE FIX
-------
Load it from inside __init__.

__init__ runs in the very cell that creates the widget, so a display(HTML(...))
there lands in THAT cell's output area -- the same iframe the widget goes
into, on Colab and everywhere else.  Every animation cell therefore gets the
stylesheet automatically, with nothing written by hand.

And a no-op _ipython_display_ handles job 2: IPython then produces an empty
mimebundle for the object, so a cell ending in the constructor echoes nothing.
(__repr__ returning '' does NOT work -- it still emits a text/plain part,
leaving a blank output area.)

AFTER THIS, AN ANIMATION CELL IS JUST

    from jove.AnimateDFA import *
    AnimateDFA(myDFA, FuseEdges=True)

and every button -- play, pause, stop, step-back, step-forward -- appears.

Idempotent.  Dry run by default; --write to apply.  Git is the revert path.
"""
import argparse, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
JOVE = os.path.abspath(os.path.join(HERE, '..', 'jove'))
MODS = ['AnimateDFA.py', 'AnimateNFA.py', 'AnimatePDA.py', 'AnimateTM.py']

FA_URL = ('//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/'
          'font-awesome.min.css')

LOADER = '''        # ---- toolbar stylesheet -------------------------------------
        # The toolbar glyphs are font-awesome icons: Jove's own step buttons
        # via Button(icon=...), and the Play widget's play/pause/stop buttons
        # via the ipywidgets frontend, which emits fa-play/fa-pause/fa-stop.
        #
        # This runs in the cell that creates the widget, so the stylesheet
        # lands in that cell's output area -- which matters on Colab, where
        # each cell's output is a separate sandboxed iframe and a link loaded
        # by one cell cannot reach another.  Doing it here is what lets the
        # notebook drop the old per-cell display(HTML(...)) line.
        display(HTML('<link rel="stylesheet" href="%s"/>'))
''' % FA_URL

HOOK = '''
    def _ipython_display_(self):
        """Take over display and emit nothing.

        __init__ has already called display() on the widget, so there is
        nothing left to show.  Defining this hook makes IPython produce an
        empty mimebundle, which suppresses the
        `<jove.AnimateDFA.AnimateDFA at 0x...>` echo when a cell ends with the
        constructor -- the job the trailing display(HTML(...)) line used to do
        by accident.  (__repr__ returning '' does not work: it still emits a
        text/plain part, leaving a blank output area.)
        """
        return None
'''

DOC_OLD = re.compile(
    r"\n\s*For producing drawings in Colab, it is important to have these in\s*\n"
    r"\s*every cell that calls animation\.\s*\n(.*?)"
    r"\s*Then the animation works in one's own install or Colab\.\s*\n",
    re.S)


def doc_new(cls):
    return ("\n    Just call it; nothing else is needed:\n\n"
            "    %s(myMachine, FuseEdges='True/False')\n\n"
            "    The font-awesome stylesheet the toolbar glyphs need is loaded by\n"
            "    __init__ itself, into the same cell output the widget goes into,\n"
            "    so the old per-cell display(HTML(...)) line is unnecessary.\n" % cls)


def patch(src, cls):
    changed = {}

    # 1. the stylesheet loader, as the first statement of __init__
    if 'toolbar stylesheet' in src:
        changed['loader'] = 0
    else:
        m = re.search(r"\n    def __init__\(.*?\):\n", src, re.S)
        if not m:
            raise SystemExit('%s: no __init__ found' % cls)
        src = src[:m.end()] + LOADER + src[m.end():]
        changed['loader'] = 1

    # 2. the no-op display hook, after __init__'s body
    if '_ipython_display_' in src:
        changed['hook'] = 0
    else:
        m = re.search(r"\n    def __init__\(", src)
        nxt = re.search(r"\n    def (?!__init__)", src[m.end():])
        at = m.end() + nxt.start()
        src = src[:at] + '\n' + HOOK.rstrip('\n') + '\n' + src[at:]
        changed['hook'] = 1

    # 3. the class docstring, which still tells users to add the line
    src, n = DOC_OLD.subn(doc_new(cls), src, count=1)
    changed['doc'] = n
    return src, changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='apply the changes')
    a = ap.parse_args()

    tot = {'loader': 0, 'hook': 0, 'doc': 0}
    for m in MODS:
        p = os.path.join(JOVE, m)
        src = open(p, encoding='utf-8').read()
        new, ch = patch(src, m[:-3])
        for k in tot:
            tot[k] += ch[k]
        state = ('unchanged' if new == src
                 else ('written' if a.write else 'would change'))
        print("  %-16s loader %d, hook %d, docstring %d   %s"
              % (m, ch['loader'], ch['hook'], ch['doc'], state))
        if a.write and new != src:
            open(p, 'w', encoding='utf-8').write(new)

    print()
    print("%s: %d stylesheet loaders, %d display hooks, %d docstrings"
          % ('patched' if a.write else 'would patch',
             tot['loader'], tot['hook'], tot['doc']))
    if not a.write:
        print("(dry run -- pass --write to apply)")


if __name__ == '__main__':
    main()

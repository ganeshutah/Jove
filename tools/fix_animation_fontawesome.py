#!/usr/bin/env python3
"""Make every Jove animation cell actually show its toolbar.

Symptom
-------
A cell ends with

    <jove.AnimateDFA.AnimateDFA at 0x7853472c5e50>

instead of the animation controls.

Cause
-----
The Animate* class docstrings require the font-awesome stylesheet to be
loaded **in every cell that calls animation**:

    AnimateNFA(ThirdLastIs1NFAalt, FuseEdges=True)
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))

Two things go wrong without that trailing line:

  * the toolbar glyphs ARE font-awesome icons, so no controls appear; and
  * Animate*.__init__ already calls display() on the widget, so leaving the
    constructor as the cell's last expression makes Jupyter additionally
    echo the object's repr -- which is the text above.

This script appends the line to any animation cell that lacks an *active*
one, and uncomments it where it was commented out.

Usage
-----
    python3 tools/fix_animation_fontawesome.py            # report, exit 1 if any
    python3 tools/fix_animation_fontawesome.py --write    # fix in place
    python3 tools/fix_animation_fontawesome.py --write PATH...
"""
import json, sys, glob, os, io, re

CALL = re.compile(r'^\s*(?:\w+\s*=\s*)?Animate(?:DFA|NFA|PDA|TM)\s*\(', re.M)
FA_LINE = ("display(HTML('<link rel=\"stylesheet\" href=\"//stackpath."
           "bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css\"/>'))")


def fix_cell(src_lines):
    """Enforce the invariant: an ACTIVE font-awesome display line is the LAST
    statement of the cell, i.e. it FOLLOWS the Animate* call.

    Returns (new_lines, what) or (None, None) if the cell is already correct.
    """
    text = ''.join(src_lines)
    if not CALL.search(text):
        return None, None

    lines = text.split('\n')
    calls = [i for i, l in enumerate(lines) if CALL.match(l)]
    fas   = [i for i, l in enumerate(lines) if 'font-awesome' in l]
    active = [i for i in fas if not lines[i].lstrip().startswith('#')]

    # already correct: an active line, and it comes after the last call
    if active and max(active) > max(calls) and \
            not any(l.strip() for l in lines[max(active) + 1:]):
        return None, None

    if not fas:
        what = 'appended'
    elif not active:
        what = 'uncommented+moved'
    else:
        what = 'moved'

    kept = [l for i, l in enumerate(lines) if i not in set(fas)]
    while kept and not kept[-1].strip():
        kept.pop()
    kept.append(FA_LINE)
    return kept, what


def to_source(lines):
    return [l + '\n' for l in lines[:-1]] + [lines[-1]]


def main(argv):
    write = '--write' in argv
    paths = [a for a in argv[1:] if not a.startswith('--')]
    if not paths:
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        paths = sorted(glob.glob('**/*.ipynb', recursive=True))

    hits = []
    for p in paths:
        try:
            with io.open(p, encoding='utf-8') as f:
                nb = json.load(f)
        except Exception:
            continue
        changed = False
        for i, c in enumerate(nb.get('cells', [])):
            if c.get('cell_type') != 'code':
                continue
            new, what = fix_cell(c['source'])
            if new is None:
                continue
            hits.append((p, i, what))
            if write:
                c['source'] = to_source(new)
                changed = True
        if write and changed:
            with io.open(p, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=1, ensure_ascii=False)
                f.write('\n')

    verb = 'fixed' if write else 'would fix'
    print('%s: %d animation cells' % (verb, len(hits)))
    for p, i, what in hits:
        print('   %-11s %s  cell %d' % (what, p, i))
    return 1 if hits and not write else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

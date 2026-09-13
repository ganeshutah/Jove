#!/usr/bin/env python3
"""Drop the now-redundant font-awesome line from animation cells.

Run tools/drop_fontawesome_dependency.py FIRST.  Once the Animate* classes no
longer use font-awesome icons and no longer echo their repr, the trailing

    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/
                  font-awesome/4.7.0/css/font-awesome.min.css"/>'))

serves no purpose and can be deleted, leaving

    from jove.AnimateDFA import *
    AnimateDFA(myDFA, FuseEdges=True)

Removing it is SAFE but not required: with the library patched, leaving the
line in place is merely a redundant stylesheet fetch.

Only cells that actually call an Animate* constructor are touched, and only
the font-awesome display line within them.  Use --scope to limit which tree
is rewritten.  Dry run by default.
"""
import argparse, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))

FA_RE   = re.compile(r"^\s*display\(HTML\(\s*'<link rel=\"stylesheet\".*font-awesome.*\)\)\s*$")
ANIM_RE = re.compile(r"\bAnimate(DFA|NFA|PDA|TM)\s*\(")


def simplify(src_lines):
    """Return (new_lines, n_removed) for one code cell."""
    text = ''.join(src_lines)
    if not ANIM_RE.search(text):
        return src_lines, 0
    out, removed = [], 0
    for ln in src_lines:
        if FA_RE.match(ln.rstrip('\n')):
            removed += 1
            continue
        out.append(ln)
    while out and out[-1].strip() == '':          # tidy a trailing blank
        out.pop()
    if out:
        out[-1] = out[-1].rstrip('\n')
    return out, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--scope', default='**/*.ipynb',
                    help="glob under the Jove root, e.g. 'Chapter*/*/*.ipynb'")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, a.scope), recursive=True))
    touched = cells = lines = 0
    for f in files:
        try:
            nb = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        n_here = 0
        for c in nb.get('cells', []):
            if c.get('cell_type') != 'code':
                continue
            new, k = simplify(c['source'])
            if k:
                c['source'] = new
                n_here += 1; lines += k
        if n_here:
            touched += 1; cells += n_here
            if a.write:
                with open(f, 'w', encoding='utf-8') as fh:
                    json.dump(nb, fh, indent=1)
                    fh.write('\n')
    print("scope            : %s   (%d notebooks scanned)" % (a.scope, len(files)))
    print("notebooks %s : %d" % ('rewritten' if a.write else 'that would change', touched))
    print("animation cells  : %d" % cells)
    print("lines removed    : %d" % lines)
    if not a.write:
        print("(dry run -- pass --write to apply)")


if __name__ == '__main__':
    main()

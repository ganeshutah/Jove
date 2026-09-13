#!/usr/bin/env python3
"""Repair notebooks that GitHub / nbviewer refuse to render with

    Invalid Notebook -- the 'state' key is missing from 'metadata.widgets'.
    Add 'state' to each, or remove 'metadata.widgets'.

Why it happens
--------------
nbconvert's HTML exporter reads

    metadata["widgets"]["application/vnd.jupyter.widget-state+json"]["state"]

(see nbconvert/filters/widgetsdatatypefilter.py). Two older layouts in this
repo do not provide that path, and both raise the error above:

  A.  models stored directly under the mimetype key, with no "state" wrapper
        widgets: { "<mimetype>": { "<model-id>": {model_name, state, ...} } }

  B.  the pre-mimetype layout, holding only view references
        widgets: { "state": { "<id>": {"views": [{"cell_index": 20}]} },
                   "version": ... }

What this does
--------------
  A -> non-destructive. The models are moved under "state" and the schema's
       version fields are added. No widget data is lost.

  B -> the block is removed. There is nothing to preserve: view references
       alone cannot reconstruct a widget, and the modern renderer needs
       model specs. This is the "or remove 'metadata.widgets'" remedy that
       the error message itself proposes.

Neither case touches a single cell; only notebook-level metadata changes.

Usage
-----
    python3 tools/fix_widget_metadata.py            # report only (exit 1 if any)
    python3 tools/fix_widget_metadata.py --write    # repair in place
    python3 tools/fix_widget_metadata.py --write PATH...
"""
import json, sys, glob, os, io

MIME = 'application/vnd.jupyter.widget-state+json'


def classify(nb):
    """-> (kind, detail).  kind in {'ok', 'none', 'wrap', 'drop'}"""
    w = nb.get('metadata', {}).get('widgets')
    if not w:
        return 'none', ''
    inner = w.get(MIME)
    if isinstance(inner, dict) and 'state' in inner:
        return 'ok', ''
    if isinstance(inner, dict) and inner:
        n_models = sum(1 for v in inner.values()
                       if isinstance(v, dict) and 'model_name' in v)
        return 'wrap', '%d models' % n_models
    # no mimetype key: the old layout, or an empty block
    n = len(w.get('state', {})) if isinstance(w.get('state'), dict) else 0
    return 'drop', '%d view-refs' % n


def main(argv):
    write = '--write' in argv
    paths = [a for a in argv[1:] if not a.startswith('--')]
    if not paths:
        os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        paths = sorted(glob.glob('**/*.ipynb', recursive=True))

    wrapped, dropped, unreadable = [], [], []
    for p in paths:
        try:
            with io.open(p, encoding='utf-8') as f:
                nb = json.load(f)
        except Exception as e:
            unreadable.append((p, str(e)[:60]))
            continue

        kind, detail = classify(nb)
        if kind in ('ok', 'none'):
            continue

        if kind == 'wrap':
            nb['metadata']['widgets'][MIME] = {
                'version_major': 2, 'version_minor': 0,
                'state': nb['metadata']['widgets'][MIME],
            }
            wrapped.append((p, detail))
        else:
            del nb['metadata']['widgets']
            dropped.append((p, detail))

        if write:
            with io.open(p, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=1, ensure_ascii=False)
                f.write('\n')

    verb = 'repaired' if write else 'would repair'
    print('scanned                  : %d notebooks' % len(paths))
    print('%-25s: %d  (models re-nested under "state")' % (verb + ' [wrap]', len(wrapped)))
    print('%-25s: %d  (view-only block removed)'        % (verb + ' [drop]', len(dropped)))
    if unreadable:
        print('UNREADABLE               : %d' % len(unreadable))
        for p, e in unreadable:
            print('   ', p, '--', e)
    if not write:
        for p, d in wrapped:
            print('   wrap %-70s %s' % (p, d))
        for p, d in dropped:
            print('   drop %-70s %s' % (p, d))
    return 1 if (wrapped or dropped) and not write else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

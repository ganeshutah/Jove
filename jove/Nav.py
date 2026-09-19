"""Move between Jove concept notebooks from inside a notebook.

    from jove.Nav import nav
    nav()                 # searchable picker + prev/next links
    nav('Chapter7')       # opens pre-filtered

ONE THING TO KNOW FIRST
-----------------------
In Colab every notebook gets its OWN runtime.  Following a link here opens a
new page with a fresh VM: the Jove clone is re-made and Python state does not
come along.  That is Colab's model, not something a link can change.

So there are two different moves, and this module offers both:

  nav()          -> pick a concept and follow the link.  New tab, new runtime.
                    This is the normal way to read the next concept.

  load_here(q)   -> run another concept's DEFINITIONS in THIS kernel.  No new
                    runtime, no re-clone, state preserved.  Use it when you
                    want another concept's machines available right here.

The index is built by reading the notebooks in this checkout, so it is always
in step with what is actually on disk -- there is no generated list to drift.
"""
import glob
import json
import os
import re

GITHUB = 'https://github.com/ganeshutah/Jove/blob/master'
COLAB = 'https://colab.research.google.com/github/ganeshutah/Jove/blob/master'

_HEADER = re.compile(
    r'\*\*Concept (\d+) of the (.+?) decomposition:\*\* \*(.+?)\*')
_CACHE = None


# The concept notebooks live under this one directory of the checkout.
# Paths handed to nav(here=...) and load_here() stay RELATIVE TO IT --
# 'Chapter7-NFA/Concept-Subset-Construction', not the full path -- so that
# moving the notebooks did not have to rewrite a string in all 266 of them,
# and so that anything a reader has typed before still works.
NBDIR = 'Concept-Notebooks'


def _root():
    """The directory holding jove/ -- i.e. the Jove checkout."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _nbroot():
    """The directory holding the concept notebooks."""
    return os.path.join(_root(), NBDIR)


def _unit_key(unit):
    """Basics first, then Chapter 1..18 numerically (not '10' before '2')."""
    m = re.match(r'Chapter (\d+)', unit)
    return (1, int(m.group(1))) if m else (0, 0)


def index(refresh=False):
    """[(unit, n, title, relpath)] for every concept notebook, in reading order."""
    global _CACHE
    if _CACHE is not None and not refresh:
        return _CACHE
    root, rows = _nbroot(), []
    for f in glob.glob(os.path.join(root, 'Chapter*', 'Concept-*', '*.ipynb')) + \
             glob.glob(os.path.join(root, 'Basics', 'Concept-*', '*.ipynb')):
        try:
            cells = json.load(open(f, encoding='utf-8'))['cells']
        except Exception:
            continue
        m = _HEADER.search(''.join(cells[0]['source'])) if cells else None
        if m:
            rows.append((m.group(2), int(m.group(1)), m.group(3),
                         os.path.relpath(f, root).replace(os.sep, '/')))
    _CACHE = sorted(rows, key=lambda r: (_unit_key(r[0]), r[1]))
    return _CACHE


_TITLES = None


def chapter_titles():
    """{'Chapter 3': 'Kleene Star: ...'} parsed from Chapters-README.md.

    The notebooks carry their CONCEPT title but not their CHAPTER's, so
    without this "ch3 kleene" finds nothing even though Chapter 3 is the
    Kleene Star chapter.  Optional: if the file is missing or changes shape,
    search simply loses that one extra thing to match on.
    """
    global _TITLES
    if _TITLES is not None:
        return _TITLES
    _TITLES = {}
    try:
        txt = open(os.path.join(_root(), 'Chapters-README.md'),
                   encoding='utf-8').read()
        # Tolerate an optional leading cell: the table gained a `Folder`
        # column when the chapter directories were renamed to carry a topic
        # tag, and an anchored `^\|\s*(\d+)` stopped matching every row.
        # It failed SILENTLY -- see the except below -- and the only symptom
        # was that "ch3 kleene" quietly stopped finding anything.
        for n, title in re.findall(
                r'^\|(?:[^|]*\|)?\s*(\d+)\s*&mdash;\s*([^|]+?)\s*\|',
                txt, re.M):
            _TITLES['Chapter %s' % n] = title.strip()
    except Exception:
        pass
    return _TITLES


def _short(unit):
    m = re.match(r'Chapter (\d+)', unit)
    return 'Ch%s' % m.group(1) if m else unit


def _label(row):
    unit, n, title, _ = row
    return '%-7s %2d. %s' % (_short(unit), n, title)


def _haystack(row):
    """Everything a query might reasonably match, lowercased."""
    unit, n, title, rel = row
    return ' '.join((unit, unit.replace(' ', ''), _short(unit),
                     chapter_titles().get(unit, ''), title, rel)).lower()


def search(query):
    """Rows matching every whitespace-separated term in `query`.

    Each term must appear at a WORD BOUNDARY, as a prefix.  Plain substring
    matching looked fine until "chapter 7" also returned Chapter 17 -- the
    "7" was matching inside "chapter17".  Prefix-at-a-boundary keeps
    progressive typing working ("subs" still finds "subset") while making
    numbers behave.
    """
    terms = [re.escape(t) for t in query.lower().split()]
    return [r for r in index()
            if all(re.search(r'\b' + t, _haystack(r)) for t in terms)]


def _url(rel):
    # `rel` is relative to NBDIR; the Colab link needs the full repo path.
    return '%s/%s/%s' % (COLAB, NBDIR, rel)


def _neighbours(here):
    """(previous, next) rows around `here`, a 'Chapter2-Lang/Concept-Foo' prefix."""
    rows = index()
    if not here:
        return None, None
    here = here.strip('/')
    i = next((k for k, r in enumerate(rows) if r[3].startswith(here)), None)
    if i is None:
        return None, None
    return (rows[i - 1] if i else None,
            rows[i + 1] if i + 1 < len(rows) else None)


def _current(here):
    if not here:
        return None
    here = here.strip('/')
    return next((r for r in index() if r[3].startswith(here)), None)


def links(here=None):
    """Plain HTML: where you are, and prev/next. No ipywidgets needed."""
    from IPython.display import display, HTML
    cur = _current(here)
    prev, nxt = _neighbours(here)
    bits = []
    if cur:
        same = [r for r in index() if r[0] == cur[0]]
        bits.append('<b>You are here:</b> %s &middot; concept %d of %d '
                    '&mdash; <i>%s</i>' % (cur[0], cur[1], len(same), cur[2]))
    nav_bits = []
    if prev:
        nav_bits.append('<a href="%s" target="_blank">&larr; %s</a>'
                        % (_url(prev[3]), _label(prev).strip()))
    if nxt:
        nav_bits.append('<a href="%s" target="_blank">%s &rarr;</a>'
                        % (_url(nxt[3]), _label(nxt).strip()))
    if nav_bits:
        bits.append(' &nbsp;|&nbsp; '.join(nav_bits))
    display(HTML('<div style="font-family:sans-serif;line-height:1.7">%s</div>'
                 % '<br>'.join(bits)))


def nav(query='', here=None, rows=10):
    """Searchable picker for every concept notebook.

    Type a chapter ("Chapter7", "ch7") or any words from a title ("pumping",
    "subset"); the list narrows as you type and the link below it follows the
    selection.  Following the link opens a NEW Colab runtime -- see load_here()
    to stay in this one.
    """
    from IPython.display import display, HTML
    try:
        import ipywidgets as W
    except ImportError:                       # no widgets: links are still useful
        links(here)
        return

    all_rows = index()
    if not all_rows:
        display(HTML('<i>No concept notebooks found under %s</i>' % _nbroot()))
        return

    box = W.Text(value=query, placeholder='Chapter7   ch2 kleene   pumping ...',
                 description='Find:', continuous_update=True,
                 layout=W.Layout(width='560px'))
    picker = W.Select(rows=rows, layout=W.Layout(width='560px'))
    out = W.HTML()
    count = W.HTML()

    def refresh(_=None):
        hits = search(box.value) if box.value.strip() else all_rows
        picker.options = [(_label(r), r[3]) for r in hits]
        count.value = ('<span style="color:#666">%d of %d concepts</span>'
                       % (len(hits), len(all_rows)))
        if hits:
            picker.value = hits[0][3]
        else:
            out.value = '<i>nothing matches</i>'

    def pick(_=None):
        rel = picker.value
        if not rel:
            return
        row = next(r for r in index() if r[3] == rel)
        out.value = (
            '<div style="font-family:sans-serif;line-height:1.8">'
            '<a href="%s" target="_blank" style="font-size:115%%">'
            '&#9654;&nbsp;Open <b>%s</b> in a new tab</a>'
            '<br><span style="color:#666">%s &mdash; new tab means a new Colab '
            'runtime. To stay in this one:</span> '
            '<code>load_here(%r)</code></div>'
            % (_url(rel), row[2], rel, rel))

    box.observe(refresh, names='value')
    picker.observe(pick, names='value')
    refresh()
    pick()

    if here:
        links(here)
    display(W.VBox([box, count, picker, out]))


def load_here(query, quiet=False, _depth=1):
    """Run another concept's code in THIS kernel -- no new runtime.

        load_here('Chapter7-NFA/Concept-Subset-Construction')
        load_here('subset construction')

    Its definitions land in your namespace, so its machines are available
    right here.  The setup cell is skipped (Jove is already imported) and so
    is the empty scratch cell at the end.  Names can collide with yours: this
    executes the other notebook, it does not sandbox it.
    """
    import sys
    hits = [r for r in index() if r[3].startswith(query.strip('/'))] or search(query)
    if not hits:
        print('No concept matches %r. Try nav() to browse.' % query)
        return
    if len(hits) > 1 and not any(r[3].startswith(query.strip('/')) for r in hits):
        print('%r matches %d concepts; be more specific:' % (query, len(hits)))
        for r in hits[:10]:
            print('   ', _label(r))
        return
    row = hits[0]
    path = os.path.join(_nbroot(), row[3])
    g = sys._getframe(_depth).f_globals
    ran = 0
    for c in json.load(open(path, encoding='utf-8'))['cells']:
        if c['cell_type'] != 'code':
            continue
        src = ''.join(c['source'])
        if 'import google.colab' in src:
            # Its setup cell.  Skip the clone/pull machinery -- this session
            # already has Jove -- but DO run its import lines.  The concept you
            # are loading may need modules this notebook never imported (a PDA
            # concept pulled into a Chapter 2 notebook, say), and without them
            # it fails with a bare NameError.
            for line in src.split('\n'):
                if line.startswith('from jove.') and 'import' in line:
                    exec(line, g)
            continue
        if src.strip().startswith('# Your work'):  # the empty scratch cell
            continue
        exec(compile(src, row[3], 'exec'), g)
        ran += 1
    if not quiet:
        print('Loaded %s (%d cells) into this session.' % (row[3], ran))
    return row[3]

# Moving between concept notebooks

**Date:** 2026-09-13
**Adds:** `jove/Nav.py`, and a "Where next" cell at the end of all 245 generated
notebooks.

---

## The constraint that shapes the design

**In Colab, every notebook gets its own runtime.** Following a link to another
notebook opens a new page with a fresh VM: the `Jove/` clone is re-made and Python
state does not come along. That is Colab's model; no link can change it.

So "go to the next concept" and "keep my session" are two different wishes, and they
need two different mechanisms. `jove/Nav.py` provides both.

## `nav()` — the search picker, at the end

The last cell of every concept notebook is:

```python
from jove.Nav import nav, load_here
nav(here='Chapter2-Lang/Concept-Zero-And-One-For-Languages')
```

which renders:

* **where you are** — `Chapter 2 · concept 10 of 16 — The Zero and One for Language
  Concatenation` — with **← previous** and **next →** links;
* a **filter box**, a **list**, and a **link that follows the selection**.

Type a chapter (`Chapter7`, `ch7`) or words from a title (`pumping`, `subset`,
`ch3 kleene`). The list narrows as you type; the link under it always points at the
highlighted concept. Clicking opens it in a new tab — and a new runtime.

`here` is baked in at generation time because Colab runs with `cwd=/content` and the
notebook file is not on disk, so the module cannot work out which concept called it.

## The static strip — mid-notebook, no execution needed

A markdown cell sits in the **middle** of every notebook, just before `## 3. Tests`:

```
---
← Ch2 9. Language Concatenation  ·  **Chapter 2** index  ·  Ch2 11. Python Encodings →
---
```

Plain links, so they need **no execution at all**. They render the moment the page
loads — before the setup cell has run — and they work on GitHub's static preview,
where a widget shows nothing.

Two placement decisions:

* **Middle, not top.** A strip under the title pushes the actual content below the
  fold. The middle is reachable with little scrolling from either end.
* **Snapped to a section heading.** Inserting at a raw cell midpoint would sometimes
  land between a definition and the test that exercises it. Snapping to the nearest
  `##` heading puts it on a seam that is already there — in practice always just
  before `## 3. Tests`.

It is injected by a **post-pass**, `nbgen/insert_nav_strip.py`, not by `nbuild`: a
generator builds one notebook at a time and does not know the global reading order
across chapters. The post-pass reads `jove.Nav.index()`, so the links are correct by
construction. It is idempotent — an existing strip is replaced, never stacked.

Verified across all 245: exactly one strip each, **every linked path checked against
disk**, prev/next matching the index order, and the two chain endpoints correctly
missing their back and forward arrows.

## `load_here()` — stay in this session

```python
load_here('Chapter7-NFA/Concept-Subset-Construction')
load_here('subset construction')          # search terms work too
```

Runs another concept's code **in this kernel**. No new runtime, no re-clone, existing
state preserved, and its machines land in your namespace ready to use.

It executes the target notebook, it does not sandbox it: names can collide with yours.
It skips the target's clone/pull machinery but **does** run its `from jove.… import *`
lines, so pulling a Chapter 12 PDA concept into a Chapter 2 session works even though
that session never imported `Def_PDA`. Without that, it failed with a bare
`NameError: name 'md2mc' is not defined` — which names the symptom and hides the cause.

## The nav cell has to stand on its own

First version of the picker cell opened with a bare

```python
from jove.Nav import nav, load_here
```

which threw `ModuleNotFoundError: No module named 'jove'` at anyone who ran it without
having run the Setup cell in that session — exactly what someone testing navigation
does: land on a notebook, scroll to the end, run the last cell.

A cell that depends on an earlier cell must either recover or say so. It now does both:

```python
import os, sys
try:                       # usually already done by the Setup cell
    import jove
except ModuleNotFoundError:
    _p = next((p for p in ('Jove', '../..', '../../..', '..', '.')
               if os.path.isdir(os.path.join(p, 'jove'))), None)
    if _p:
        sys.path.insert(0, _p)
try:
    from jove.Nav import nav, load_here
    nav(here='...')
except ModuleNotFoundError:
    print('Jove is not on the path yet.')
    print('Run the Setup cell at the top of this notebook, then re-run this one.')
```

Three situations, all exercised:

| Situation | Result |
|---|---|
| Colab-style: `Jove/` cloned in cwd, Setup never run | finds it, widget builds |
| local: run from inside the concept folder, Setup never run | finds it, widget builds |
| no Jove anywhere | **advises**, does not raise |

> **Lesson.** A generated cell inherits none of the context its author had in mind.
> Anything that can be run out of order eventually will be.

## The index

Built by reading the notebooks in the checkout — chapter, concept number and title come
from each notebook's own header. **There is no generated list to drift out of step**;
add a notebook and it appears. 245 concepts index in about 0.01s, cached per session.

Chapter *titles* come from `Chapters-README.md`, because a notebook carries its concept
title but not its chapter's. Without them `ch3 kleene` found nothing, even though
Chapter 3 is the Kleene Star chapter. If that file is missing or changes shape, search
simply loses that one extra thing to match on.

## Search: prefix at a word boundary

Each whitespace-separated term must appear at a **word boundary, as a prefix**.

Plain substring matching looked fine until `chapter 7` returned **19** hits — the `7`
was matching inside `chapter17`. Requiring a boundary fixes numbers while keeping
progressive typing usable, since `subs` still finds `subset`.

| query | hits | first |
|---|---:|---|
| `Chapter7` / `ch7` / `chapter 7` | 12 | Ch7 1. Nondeterminism as Forking Tokens |
| `ch17` | 7 | Ch17 1. Boolean Functions, Truth-Table Personalities |
| `pumping` | 7 | Ch4 13. Visitation Numbers, Pumping Up and Down |
| `ch7 subset` | 1 | Ch7 8. Subset Construction |
| `ch3 kleene` | 16 | Ch3 1. Star: Three Equivalent Definitions |

## Verification

| Check | Result |
|---|---|
| 245 concepts indexed, in reading order (Basics, then Ch1–18 numerically) | pass |
| Widget built and its callbacks driven headlessly: typing filters, link follows selection, no-match message | pass |
| Every notebook's `here=` resolves to a real concept | 0 dead |
| Exactly two notebooks sit at a chain end (first and last) | pass |
| `load_here` into a **bare** session — target's imports carried | pass |
| `load_here` cross-chapter: a Ch12 PDA into a session holding only `LangDef` | pass |
| All 245 notebooks still execute | pass |

## Degradation

Without `ipywidgets`, `nav()` falls back to `links()` — plain HTML for where-you-are
and prev/next. The search box is the only thing lost.

## If you would rather not have it

The cell is generated, so removing it is a two-line change in
`nbuild.build()` followed by regeneration. `jove/Nav.py` is standalone and importable
on its own regardless.

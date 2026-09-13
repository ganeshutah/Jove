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

## `nav()` — find and follow

The last cell of every concept notebook is:

```python
from jove.Nav import nav, load_here
nav(here='Chapter2/Concept-Zero-And-One-For-Languages')
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

## `load_here()` — stay in this session

```python
load_here('Chapter7/Concept-Subset-Construction')
load_here('subset construction')          # search terms work too
```

Runs another concept's code **in this kernel**. No new runtime, no re-clone, existing
state preserved, and its machines land in your namespace ready to use.

It executes the target notebook, it does not sandbox it: names can collide with yours.
It skips the target's clone/pull machinery but **does** run its `from jove.… import *`
lines, so pulling a Chapter 12 PDA concept into a Chapter 2 session works even though
that session never imported `Def_PDA`. Without that, it failed with a bare
`NameError: name 'md2mc' is not defined` — which names the symptom and hides the cause.

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

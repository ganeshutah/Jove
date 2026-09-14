# Naming the chapter folders for their topic

`Chapter12` told a reader nothing. The folder name is what shows in a URL, a
Colab tab title and a search box, so each now carries a topic tag of at most
six characters:

```
Chapter1-Intro     Chapter7-NFA       Chapter13-TM
Chapter2-Lang      Chapter8-RE        Chapter14-Interp
Chapter3-Star      Chapter9-NFA2RE    Chapter15-PCP
Chapter4-DFA       Chapter10-Deriv    Chapter16-NPC
Chapter5-DFADsg    Chapter11-CFG      Chapter17-BDD
Chapter6-DFAOps    Chapter12-PDA      Chapter18-Lambda
```

`Basics` keeps its name. Four tags are six characters (`DFADsg`, `DFAOps`,
`NFA2RE`, `Interp`); the rest are five or fewer.

## One table owns them

The tags live in **`TAG`**, in the workbook's `nbgen/nbuild.py`. Folder
names, the Colab URL in every notebook header, the prev/index/next strips,
the per-chapter READMEs and the concept audit all derive from it through
`unit_of()`. Renaming a chapter is a one-line edit there plus a
regeneration — which is what made this worth doing properly rather than with
`sed`.

`audit_concepts.py` **imports** `TAG` rather than keeping a second copy,
which is exactly the failure that table exists to prevent.

## What did not change

The unit **label** stays `Chapter 12`. It is what the reader is told, what
the notebook header records, and what the search index sorts on. So
`jove/Nav.py` needed no change to keep working: its glob already matched, and
its ordering reads the label, not the folder.

## What the tags buy

They are searchable for free, because the search haystack includes the
relative path. Typing `BDD`, `PDA`, `NFA2RE` or `Interp` now finds the
chapter, and `ch7` / `Chapter7` / `pumping` still work as before.

## One thing broke silently, and it is the reason to write this down

Adding a `Folder` column to the table in `Chapters-README.md` moved the
chapter number out of the first cell. `Nav.chapter_titles()` anchors its
regex at the start of the row, and it parses that table inside a
`try/except` that passes **by design** — so the failure was invisible:

* 18 parsed titles became **0**;
* the only symptom was that a search for `ch3 kleene` quietly returned
  nothing.

The regex now tolerates an optional leading cell, and the comment says why.
A `try/except: pass` that guards an *optional enhancement* is reasonable; it
also means a shape change downstream costs you the enhancement without
telling you.

## Verification

Every link was chased, not sampled: **754 Colab notebook URLs** and **252
chapter-index links** all resolve to files that exist. Suite clean, 252 nav
strips.

## Consequence

Any external link to an old `Chapter4/...` path is now dead. Nothing inside
either repository points at them; course materials elsewhere may.

## Reverting

`git mv` each folder back and revert `TAG`; everything else regenerates.

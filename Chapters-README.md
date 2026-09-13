# Concept-directed chapter folders

`Chapter<N>/Concept-<Name>/` replaces the old
`For_CS3100_Fall2024/<NN>_<Topic>/` layout.

The old names hardwired two things that age badly:

* **the year** &mdash; `For_CS3100_Fall2024`,
* **the lecture number** &mdash; `04_NFA` means "the 4th lecture, on NFA".

A concept-directed layout hardwires neither. A folder is named for the *idea* it
teaches, so it stays correct when the course is renumbered or re-run in a different
year, and it can hold anything that helps with that idea &mdash; notebooks, data files,
exercises.

```
Jove/
  Chapter1/
    README.md
    Concept-Turing-Machine-Definition/
      Concept-Turing-Machine-Definition.ipynb
    Concept-Context-Free-Patterns/
      Concept-Context-Free-Patterns.ipynb
    ...
  Chapter2/  ...
  Chapter3/  ...
```

## What is in each notebook

1. a header that runs **both on Colab and on a local install**;
2. the `from jove.<module> import *` lines that notebook needs;
3. **definitions** that exercise the concept;
4. **tests** that exercise it &mdash; these carry real `assert`s, so a broken notebook
   fails loudly instead of printing something wrong;
5. an **animation** (`AnimateDFA` / `AnimateNFA` / `AnimatePDA` / `AnimateTM`)
   wherever the concept has a machine worth stepping through;
6. **exercises** to take it further.

## Status

| Chapter | Concepts | Notebooks | With animation |
|---|---:|---:|---:|
| 1 &mdash; What Machines Think | 17 | 17 | 7 |
| 2 &mdash; Defining Languages | 16 | 16 | 0 |
| 3 &mdash; Kleene Star | 16 | 16 | 2 |

Chapters 2 and 3 are about **language operations** rather than machines, so most of
their notebooks have nothing to animate; the two that do (the $\Sigma^*$ machine and
DFA complementation) are animated.

The old `For_CS3100_Fall2024/` tree is **untouched** &mdash; every existing Colab link
still works.

## Provenance

These notebooks are generated, not hand-edited. The generators live in the companion
workbook repo at `Concepts/tools-concept/nbgen/`, alongside the prose decomposition
(`Concepts/Chapter-<N>-Concept-<M>.md`) that each notebook illustrates.

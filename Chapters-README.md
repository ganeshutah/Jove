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

All eighteen chapters of the book are covered: **232 notebooks**, one per concept in
the workbook's decomposition.

| Chapter | Concepts | With animation |
|---|---:|---:|
| 1 &mdash; What Machines Think | 17 | 7 |
| 2 &mdash; Defining Languages: Patterns in Sets of Strings | 16 | 0 |
| 3 &mdash; Kleene Star: Basic Method of Defining Repetitious Patterns | 16 | 2 |
| 4 &mdash; Basics of DFA | 22 | 6 |
| 5 &mdash; Designing DFA | 14 | 9 |
| 6 &mdash; Operations on DFA | 12 | 6 |
| 7 &mdash; Nondeterministic Finite Automata | 12 | 11 |
| 8 &mdash; Regular Expressions and NFA | 12 | 12 |
| 9 &mdash; NFA to RE Conversion | 8 | 5 |
| 10 &mdash; Derivative-Based Regular Expression Matching | 8 | 2 |
| 11 &mdash; Context-Free Languages and Grammars | 21 | 3 |
| 12 &mdash; Pushdown Automata | 11 | 7 |
| 13 &mdash; Turing Machines | 13 | 6 |
| 14 &mdash; Interplay between Formal Languages | 12 | 3 |
| 15 &mdash; Post Correspondence, and Other Undecidability Proofs | 9 | 0 |
| 16 &mdash; NP-Completeness | 12 | 0 |
| 17 &mdash; Binary Decision Diagrams as Minimal DFA | 7 | 1 |
| 18 &mdash; Computability Using Lambdas | 10 | 0 |
| **Total** | **232** | **80** |

A chapter has few animations when its subject is not a machine. Chapters 2, 3 and 11
are about languages and grammars; 15 and 16 are about reductions and complexity;
18 is about lambda terms. Where there *is* a machine worth stepping through, it is
animated.

Some chapters need machinery Jove does not ship, and the notebooks build it
themselves rather than importing something that is not there:

* **Chapter 11** &mdash; a small CFG toolkit (grammar constructor, bounded language
  generator, parse-tree enumerator, leftmost derivations);
* **Chapter 15** &mdash; a bounded Post-correspondence solver;
* **Chapter 16** &mdash; a CNF/DIMACS toolkit, a DPLL solver, and a Tseitin encoder;
* **Chapter 17** &mdash; a hash-consed BDD package;
* **Chapter 18** &mdash; Church encodings and fixpoint combinators.

Each such toolkit is inlined into the notebooks that use it, so every notebook still
stands alone on Colab.

The old `For_CS3100_Fall2024/` tree is **untouched** &mdash; every existing Colab link
still works.

## Provenance

These notebooks are generated, not hand-edited. The generators live in the companion
workbook repo at `Concepts/tools-concept/nbgen/`, alongside the prose decomposition
(`Concepts/Chapter-<N>-Concept-<M>.md`) that each notebook illustrates.

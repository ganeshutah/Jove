# Checking that the notebooks and the workbook still agree

Four artefacts have to describe the same set of concepts:

1. the **notebooks** in the Jove repo,
2. the concept **index**, `gen/idx/ch<NN>.json`,
3. the workbook **prose**, `Concepts/Chapter-<N>-Concept-<n>.md`,
4. **`Concepts-Taught.md`**.

(2) is the source of truth: the notebook generators read it through
`concept_meta()`, and `emit.py` writes (3) and (4) from it. Nothing checked
that they actually agreed.

## What the audit found

**The counts were perfect** — 252 notebooks, 252 index entries, a prose file
for each, all listed in `Concepts-Taught.md`, the six BDD concepts and the
Jove tour included.

**Twenty-seven names disagreed**, all in Chapters 1–3 — eleven in Chapter 1,
eight in Chapter 2, nine in Chapter 3. (Regenerating changed twenty-eight
headers; the extra one differed only in how an em dash was encoded, which the
audit correctly ignored.) Those three generators
predate `concept_meta()` and kept their own copies of the concept names.
Chapters 4–18 and appendix A read the index and therefore *could not* drift;
those three could, and had — ten of Chapter 1's names had lost their
subtitles ("Hilbert's Program, and its Refutation" against the index's
"…: Undecidability and Incompleteness"), and the Pattern Class names had a
plain double hyphen where the index has an em dash.

All three now fill `concept_name` from `concept_meta(CH)`, and the hardcoded
copies are **deleted** rather than left behind to disagree again. The short
display `title` is untouched — that one *is* the generator's to choose, and
the split between the two is the design.

## The auditor's own bugs, which are the more useful lesson

Three of the first thirty "problems" were the auditor's:

* a non-greedy match up to the next `*` truncated every concept name
  containing `$\Sigma^*$` or an emphasised word;
* `strip('*')` then ate the closing marker of a name ending in emphasis
  (`…Called *Enumerable*`).

Both were fixed before any of its output was trusted. **An auditor that cries
wolf is quickly ignored**, and a check nobody believes is worse than no
check.

## What it cannot say

The workbook's `Builds on` sections are concept-level *within* a chapter (565
edges) but only chapter-level *across* chapters (210 edges). So when eight
chapters name "Chapter 4" as a prerequisite, the data cannot distinguish
"needs DFA basics" from "needs the pumping lemma".

That limit matters for course design: making those cross-chapter references
name **concepts** would turn re-ordering from an argument into a check — you
could ask "is this set closed under its dependencies?" and get an answer.

## Running it

```sh
python3 Concepts/tools-concept/gen/audit_concepts.py
```

`regen.sh` now ends with it, so this cannot drift again in silence.

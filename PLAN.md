# PLAN.md — how commits are made in this repository

This file exists because the same mistake was made eight times in a row and
shipped. It is a standing instruction, not a suggestion. Read it before
committing.

## The mistake

Every concept notebook carried a comment line naming the **total number of
concepts in the repository**:

```python
# Previous / next, and a search box for all 258 concepts.
```

So adding one concept to Chapter 12 rewrote that line in all ~250 other
notebooks. Those 250 files then landed inside the feature commit, and the
result is that `git log Chapter17-BDD/Concept-BDD-As-Minimal-DFA/...` reported
its most recent change as

> *Karpathy's GPT meets the stack and the tape: six new concepts*

which has nothing whatsoever to do with BDDs. The BDD notebooks were touched
by five consecutive unrelated commits this way (SKI, lambda, transformers,
Chapter 2's animator, the Jove tour). The messages were fine in isolation; the
commits they were attached to were not.

Measured, the worst offender was 268 files changed of which **253 were a
one-line count bump** and 15 were the actual work.

## The rules

**1. One commit is one coherent change.** If the subject line cannot honestly
describe every file in the commit, it is more than one commit.

**2. A mechanical sweep is its own commit.** Reformatting, renumbering,
regenerating boilerplate, bumping a version string across many files: commit
that alone, with a subject that says so (`Nav cell: ...`, `Renumber ...`). Never
let it ride along with feature work.

**3. Prefer deleting the cause over remembering the rule.** A global fact
(a total, a version, a date) embedded in every generated file guarantees this
problem forever. The fix is not discipline, it is to stop embedding it. The
count above was already displayed at runtime by `jove/Nav.py`, so the copy in
each notebook was redundant and is now gone. **Adding a concept should change
only the files that concept touches.**

**4. Check before committing, do not trust your memory of what you edited:**

```sh
# files whose entire change is a single line -- the sweep fingerprint
git diff --cached --numstat | awk '$1==1 && $2==1' | wc -l
git diff --cached --numstat | wc -l
```

If the first number is a large fraction of the second, stop and split.
`tools/check-commit.sh` in this repo does exactly this and prints what to do.

**5. Same-scope renumbering is fine.** Adding Chapter 12's concept 12 may
renumber `Concept N of M` in Chapter 12's *own* files. That is part of the
change. Rewriting Chapter 17 is not.

## Pushing

- **`origin` only.** This repository has a second remote, `autocratiq-remote`,
  which must never be pushed to. Always name the remote explicitly:
  `git push origin master`. Never a bare `git push`.
- History rewrites: tag a backup first (`backup/pre-rewrite-<date>`), rewrite,
  verify with the checks above, then `git push --force-with-lease origin master`.

## What was done about it

The eight polluted commits were rewritten so the notebook count line never
appears in history. After the rewrite each of them contains only the files its
subject describes; the BDD notebooks are no longer touched by the transformer,
SKI or lambda commits. The generator (`nbuild.py`, in the Jove-Workbook repo)
no longer emits a count into the nav cell at all, so the failure cannot recur.

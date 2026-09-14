# Rebuilding the Pumping Lemma notebook

`Chapter4-DFA/Concept-Pumping-Lemma-Predicate-Logic` (concept 22) was rewritten
twice.  This note records both designs, because the first one failed for a
reason worth keeping.

Only one thing survives from the original notebook: the statement of
`Cond(L)` and its negation in predicate logic.  Every worked split, the
general-lemma window machinery, `in_Lif` and the JFLAP line-up are gone.

## The problem

The old notebook enumerated splits and showed a few of them breaking.  That
is the habit the lemma punishes: try three splits, watch them break, declare
victory --- when a *regular* language would have survived those same three.
Worked examples teach the ritual instead of the argument, and a student can
lift one wholesale without ever meeting the quantifier.

The faked step is always the same one: the `forall` over splits.

## Attempt 1: hand the whole thing to a string solver

The first rewrite made a split a symbolic `(x, y, z)` of z3 `String` sort and
asked the solver to answer the `forall` in one shot.  `0^n 1^n` is not
regular, so no regex states it; the trick was to split the job --- the shape
`0*1*` *is* a regex z3 takes directly, and under that shape `#0s` is the
index of the first `1`, so counting becomes a subtraction.

It worked, and it was the wrong notebook.

The student now supplies `N` and `w` and a list of y-shapes, and the solver
does the rest.  Nothing that made the proof a *proof* --- choosing `w` so the
cases collapse, splitting into cases, doing the pumping arithmetic --- was
left in the student's hands.  It replaced one oracle with another.  It was
also fragile: the solver went `unknown` on languages only slightly harder
than the stock one, and a three-letter alphabet was out of reach entirely.

## Attempt 2: the student writes the proof, the solver closes it

The shipped design walks the refutation the way the chapter does on paper,
and the student supplies every step as a **parametric string**.

    w = 0^M 1^M        the student's choice, with a constant of their own
    x = 0^X            X = |x| and Y = |y| ARE the split
    y = 0^Y
    z = 0^(M-X-Y) 1^M
    xy^2z = 0^(M+Y) 1^M     written out by the student, not computed for them

Every one of those steps is arithmetic over the constants the student
introduced.  `Lin` is a linear expression (a constant plus integer multiples
of named constants); `PStr` is a list of runs, each with a `Lin` exponent.
Concatenation adds, `y^i` repeats, and two parametric strings are equal
exactly when they are equal for every value of the constants.  So:

* `x y z == w` is checked by normalising both sides --- instantly, exactly,
  with no solver;
* `xy^i z` is recomputed and compared against what the student wrote;
* `|x| == X` and `|y| == Y` are checked the same way.

That last check is the load-bearing one.  A case written with lengths of its
own (`x = 0^(X+1)`) is a case standing for *some* splits; a case written in
terms of the split point stands for *all* of them.  Rejecting the first is
what keeps "case" from silently meaning "example".

**`qed()` asks the solver exactly one question.**  Everything the walk
recorded becomes an obligation, each paired with the formula that would break
it, each flagged:

    w is a member of L
    |w| >= N, whichever N the adversary meant
    your k cases cover EVERY admissible split
    case k: xy^i z falls OUTSIDE L

with `flag_j == And(base, breaks_j)` and `Or(flag_1 ... flag_n)` added to a
single solver.  One `check()`.  UNSAT means not one obligation can be broken
--- and since the flags track their conditions exactly, a SAT model names
which one broke and hands back a concrete counterexample.

Keeping it to one call required making every obligation quantifier-free.
The first cut used `Exists` for the per-case locals and a nested
`Exists`-under-`Not` for coverage; z3 then returned a model in which the
coverage flag evaluated to *an unreduced quantified formula* rather than to
`True` or `False`, so the report silently listed nothing as broken.  Pinning
`X = |x|` and `Y = |y|` removed every quantifier, which is why that check
earns its place twice over.

A related detail: `X >= 0, Y >= 1, X + Y <= N` live in the shared `base`
rather than in the individual obligations.  They constrain nothing else (`X`
and `Y` appear nowhere else in `base`), but without them the solver was free
to report a witness like `X = -1, Y = 0` for an obligation that does not
mention the split --- values no split could ever take, in a message whose
whole job is to be believed.

## What the notebook demonstrates

Both directions, because only showing success proves nothing about the tool:

* the book's walk, pumping **up**, and the same walk pumping **down** --- UNSAT;
* three ways to get it wrong: bad concatenation and a mis-sized `x`, both
  caught by algebra before any solver runs, and a `w` never tied to `N`,
  which needs the query to expose;
* **why `w` must be chosen well**: declare `2M >= N` instead of `M >= N` and
  `|w| >= N` still holds, but `y` is no longer trapped in the `0`s.  One case
  becomes a hole and the solver hands back the split left out.  Supplying all
  three cases closes it --- and the cost of the sloppy `w` is now visible
  rather than asserted;
* the control that matters: **the identical walk on a regular language**,
  `0*1*`.  It comes back SAT.  If the machinery said QED here it would be
  worthless.

## Testing

The notebook runs end to end against z3 5.1.0 in about a tenth of a second,
with every branch above exercised.  `z3-solver` is not a Jove dependency, so
the notebook pip-installs it on first use.

The harness on this machine skips the notebook **whole** and says so, because
the system z3 here is an x86_64 build on an arm64 Mac and cannot load.
Skipping only the cells that mention z3 drops the *definitions* and leaves
the cells that use them, which then fail with `NameError` and look like real
bugs --- that is what the first version of the skip did.

## One thing that bit twice

`build()` writes each notebook from scratch, so anything a **post-pass**
added is gone after a regeneration.  The nav strip is such a post-pass, and
losing it is silent: the notebook still runs, it just loses its prev/next
links.  Regenerating Chapter 4 for this rewrite dropped the strip from all 22
of its notebooks, and the first commit of this work shipped that way.

Both the generator and `nbgen/README.md` now say so out loud: every
regeneration prints a reminder, and the documented recipe ends with
`insert_nav_strip.py --write`.

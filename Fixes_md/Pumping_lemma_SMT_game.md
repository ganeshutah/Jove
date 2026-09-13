# Rebuilding the Pumping Lemma notebook around a solver

**Date:** 2026-09-13
**Replaces:** `Chapter4/Concept-Pumping-Lemma-Predicate-Logic/` in full.
Only the predicate-logic statement of the lemma survives from the old version.

---

## Why it was rewritten

The old notebook enumerated splits and showed a few of them breaking. That is exactly
the habit the lemma punishes: try three splits, watch them break, declare victory —
when a *regular* language would have survived those same three. Worked examples teach
the ritual instead of the argument, and students then reproduce the ritual on exams.

The faked step is always the same one:

$$\neg Cond(L) \equiv \forall N : \exists w \in L : |w|\ge N \wedge \underbrace{\forall x,y,z}_{\text{this}} : [\ldots \Rightarrow \exists i : xy^iz\notin L]$$

So the $\forall x,y,z$ goes to **z3**. A split becomes a symbolic $(x,y,z)$ and the
solver answers for all of them at once. **UNSAT** means no split survives — and
nothing can be cherry-picked, because nothing was picked.

## Expressing a non-regular language to a string solver

z3 has a theory of strings with regexes, but $0^n1^n$ is not regular, so no regex
states it. The way through is to split the job:

```python
def zeros_then_ones(f):          # f is a condition on (#0s, #1s)
    def P(s):
        shape = InRe(s, Concat(Star(Re(StringVal("0"))), Star(Re(StringVal("1")))))
        i = IndexOf(s, StringVal("1"), IntVal(0))
        a = If(i == -1, Length(s), i)          # under 0*1*, #0s is the index of the first 1
        return And(shape, f(a, Length(s) - a))
    return P

P_anbn = zeros_then_ones(lambda a, b: a == b)
```

The **shape** is a regex, which z3 takes directly; the **counting** rides on top of it.
That is what lets a theory whose regexes cannot express $0^n1^n$ nevertheless decide
membership in it. Students write their own languages by passing a different `f`.

## The game

```python
game = PumpGame(P_anbn, '0^n 1^n')
game.adversary(4)                  # the adversary fixes N
game.choose_w('0000' + '1111')     # your move -- checked for membership and length
game.y_shapes(['all 0s'])          # claim the cases; the solver marks your work
game.refute(2)                     # the discharge: the whole quantifier at once
```

Each step pushes back:

| Move | The solver's answer |
|---|---|
| `choose_w('0001')` | REJECTED — not in the language; the lemma constrains only members |
| `choose_w('01')` with N=6 | REJECTED — `\|w\| < N`; the lemma says nothing about short strings |
| `y_shapes(['all 0s'])` on `w='0000'+'1111'` | COMPLETE — the other two shapes are *impossible* under `\|xy\| ≤ N` |
| `y_shapes(['all 0s'])` on `w='0011'` | **MISSED: all 1s, straddles** — a short `w` leaves three cases |
| `refute(2)` | UNSAT — no split survives; ¬Cond, not regular, QED |

That fourth row is the point of choosing $w$ well, and the student discovers it rather
than being told: the good $w$ collapses the case analysis to one case, the careless one
leaves three.

## Two things the design had to get right

**`unknown` is not `unsat`.** z3's string theory can give up. Reporting that as "no
split survives" would manufacture a proof out of a timeout — precisely the sin the
notebook exists to prevent. `_ask()` is three-valued and every caller distinguishes the
three.

**The lemma lets each split choose its own $i$.** So checking one fixed $i$ against
every split is *sufficient* to refute but not *necessary*. `refute(K)` asks the honest
question — "is there a split surviving **every** $i \le K$?" — while `pump(i)` remains
as a single-$i$ probe, labelled as such.

I had the second one wrong at first and the difference is not cosmetic: for
$\{0^n1^m : n \ne m\}$ each split needs a *different* $i$, so a single-$i$ check reports
a survivor where none exists.

## The solver's limits are part of the lesson

The last cell runs a query z3 cannot decide and prints

```
UNKNOWN -- the solver gave up. That is NOT a proof.
```

$\{0^n1^m : n\ne m\}$ *is* non-regular, but the $w$ chosen for it is poor — pumping the
0s keeps the counts unequal — and a $w$ that works needs $(\#1 - \#0)$ divisible by
every possible $|y|$, the classic $N!$ trick. The solver will not invent that.

This is Chapter 4 Concept 19's lesson — *failing to falsify proves nothing* — now
observable rather than asserted, and it doubles as an honest statement about what an
SMT solver is.

## Verification

The whole notebook executes end to end against z3 5.1.0 in **3.2 seconds**, with every
branch exercised: membership, both rejections, the complete and the incomplete case
analysis, `refute` reaching UNSAT, `pump` at $i=2$ and $i=0$, and the `unknown` demo.

`z3-solver` is not a Jove dependency; the notebook pip-installs it on first use.

**Note for this machine:** the system z3 here is an x86_64 build on an arm64 Mac and
cannot load — the same pre-existing breakage as `rpds`. The main notebook harness
therefore skips z3 cells, and this notebook is verified separately against a working
z3 in a venv.

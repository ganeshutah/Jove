# Getting BDDs into the notebooks, and drawing them

Jove has carried a BDD engine under `BDD/` (Tyler Sorensen's code, reached
through the `pbl` symlink) for years. Nothing could use it from a notebook.

## The symptom

Three obstacles, none of them the engine's fault:

* it wants **seven directories** on `sys.path` before anything imports;
* its entry point, `buildBDDmain()`, prints a report and **throws the
  structure away** — you cannot ask it how many nodes, or which assignments;
* the only notebook using it carried stale `./Jove/pbl/...` paths from a 2022
  assignment.

Meanwhile Chapter 17 — *the BDD chapter* — drew **no BDD at all**. All seven
of its notebooks used `AnimateDFA`, on the "a BDD is the minimal DFA of the
on-set" reading, because until now there was no way to draw the real thing.

## `jove/Bdd.py`

```python
from jove.Bdd import *
bdd('''
Var_Order : a b c d
f = a | (b & c & d)
Main_Exp : f
''')
```

The call draws the diagram in the cell and carries its answers as **data** —
`.count`, `.models`, `.nodes`, `.is_sat`, `.is_taut` — so a notebook can
assert on them instead of printing a table and inviting the reader to agree.
`paths()`, `dnf()` and `cnf()` read the normal forms off the diagram by
walking to the `1` and `0` terminals.

Two containment details worth keeping:

* The engine is imported **inside a temporary directory**, because ply's
  `yacc()` drops `parser.out` and `parsetab.py` into the *current* one —
  which on Colab is the student's. The first-parse table build is spent there
  too, so the reader's first `bdd()` call is silent and leaves nothing behind.
  Verified from a foreign cwd, which is what Colab actually does.
* `.nodes` counts nodes **reachable from the root**, not the engine's node
  table. The table always holds both terminals, so an unsatisfiable formula
  reported 2 nodes while its picture showed 1 — and the notebook text said
  "one node" three lines later.

## Three drawing tools, each earning its place by making a comparison

Half the BDD material *is* a comparison, and a comparison split across two
outputs is one the reader does not make.

* **`side_by_side((label, bdd), ...)`** — diagrams in one captioned picture.
* **`decision_tree(b)` / `tree_vs_bdd(b)`** — the unreduced tree beside its
  reduction. For `(a & b) | c` that reads *"decision tree: 15 nodes"* against
  *"reduced BDD: 5 nodes"*.
* **`draw(mgr, node)`** — renders a node of the **teaching package** Chapter
  17 builds from scratch, in the same blue/red convention. Hash consing
  becomes visible: a shared sub-diagram is one node with two arrows into it,
  not two copies.

## Six new NPC-facing concepts (Chapter 16, 13–18)

| | |
|---|---|
| 13 | A BDD decides SAT **by being built** — an unsatisfiable formula's reduced diagram *is* the single `0` node |
| 14 | Both normal forms off one diagram: paths to `1` give a DNF, paths to `0` give a CNF by De Morgan |
| 15 | Why converting CNF to DNF is not a free lunch |
| 16 | Counting is #P, not NP: a solver returns one model, the diagram returns how many |
| 17 | Graph colouring as a formula, on the UT/NV/AZ/CO map |
| 18 | Variable ordering, and the honest accounting |

## Three claims that changed when measured

Each became a better lesson for having been wrong first.

* Concept 15 was going to argue the BDD's DNF is **smaller** than the
  multiplied-out one. It is not: paths-to-1 is exactly $4^k$, the
  distribution law's own count. What is linear is the **diagram** — four
  nodes per clause. So the sharper point is that a BDD stores the
  65536-term DNF compactly and still cannot enumerate it any faster.
* Concept 18 was going to say interleaving beats grouping. On the colouring
  map it **loses**, 49 nodes against 35 — the reverse of what the pairing
  family teaches. That is what makes NP-completeness of ordering land.
* The 48 colourings were checked against the chromatic polynomial
  $k(k-1)(k-2)^2$ for $K_4$ minus an edge, not just eyeballed.

## Verification, and a check that was testing nothing

The notebook suite stubs `graphviz`, so a diagram that real `dot` would
reject passes it. A second check pushes every diagram through the real
binary.

That check initially reported **"1 diagram rendered" across six notebooks —
and passed.** It used `exec()`, which discards a cell's trailing expression,
so a cell ending in `f` never drew anything. It now evaluates the trailing
expression and asks for its display bundle, the way a kernel does. All 14
diagrams render.

## Reverting

```sh
git checkout <commit>~1 -- jove/Bdd.py Chapter16-NPC Chapter17-BDD
```

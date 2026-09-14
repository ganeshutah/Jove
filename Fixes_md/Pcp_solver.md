# Making the PCP solver runnable

Chapter 15 had **zero** runnable concepts and sits at 83–86% of the reading
order — April, in a spring semester. Its notebooks carried a breadth-first
`pcp_search()` bounded by tile count: honest, exponential, and able to answer
only *"nothing found up to 8"*.

A real solver had shipped under `jove/pcpbinaries/` since 2023. What was
missing was a way into a notebook.

## The symptom

`jove/PcpJupyter.py` — the module a Chapter 15 notebook would import — **did
not parse at all**:

```
TabError: inconsistent use of tabs and spaces in indentation, line 40
```

Nothing imported it, so nobody noticed. It had been dead long enough that the
four Chapter 15 notebooks had grown their own pure-Python search instead.

## Confirming the binary before writing anything

The solver is a compiled binary, so the first question is whether it runs on
Colab at all. Checked rather than assumed:

* `pcp_linux` is **ELF 64-bit x86-64** — which is what Colab is.
* It is tracked in git at mode **100755**, so a `git clone` lands it
  *already executable*. No `chmod` step is needed, and that is worth knowing
  because an unzipped archive would lose the bit.
* Its only shared libraries are `libstdc++.so.6`, `libm.so.6`,
  `libgcc_s.so.1` and `libc.so.6` — all stock on Colab's Ubuntu.
* The highest glibc symbol version it references is **2.14**; Colab's Ubuntu
  22.04 ships 2.35. Forward-compatible by a wide margin.
* There is no RPATH or RUNPATH, so nothing is hardcoded to break.

The program itself was then exercised through the x86 Mach-O twin under
Rosetta: **PCPSolver 0.0.3, Ling Zhao, 2003**. Only the architecture differs
from Colab, and the ELF analysis covers that.

## Two bugs the verification caught

Both would have shipped silently in a wrapper that printed the solver's
output instead of checking it.

**The tile order wraps.** The solver prints twenty indices to a line, for as
many lines as it takes. A 66-tile solution arrives as four lines, and reading
only the first yields a prefix that concatenates to nothing. `_read_order()`
reads the whole block.

**The solver is binary only.** Hand it dominoes over `a, b, c` — which is
what Chapter 15's own examples use — and it reports `unsolved` for instances
that plainly have solutions. `_encode()` recodes any alphabet to fixed-width
binary first. Fixed width matters: a variable-length code could let two
different strings encode to the same bits and manufacture a match that is not
there. The coding is a homomorphism applied to both rows, so it preserves
solutions in both directions and leaves the tile **order** untouched — which
is why the answer needs no decoding.

## The reversal, which is a heuristic and not a rule

Ling Zhao's solver searches from both ends and keeps whichever direction
expanded fewer nodes. When it keeps the reverse one it prints the sequence
**backwards**. Instances of both kinds exist.

So rather than parse the `Choose the reverse direction` line and believe it,
`_read_order()` concatenates the tiles both ways and keeps whichever actually
matches. If neither does, it says so instead of returning a sequence that
does not work. Verification runs against the **original** tiles, so an error
in the alphabet encoding cannot slip through either.

A wrapper printing the sequence verbatim hands the student an index list that
fails their own `pcp_check()` — which looks like the notebook is broken.

## `jove/Pcp.py`

```python
from jove.Pcp import *
r = pcp([('1', '111'), ('10111', '10'), ('10', '0')])
r.report()     # status, order (0-based), top, bottom, nodes, seconds
r              # draws the domino chain, the two rows aligned
```

* Indices come back **0-based**, matching Chapter 15's own
  `pcp_check(tiles, sol)`. The solver is 1-based.
* Status is `solvable` / `unsolvable` / **`unsolved`** / `unavailable`, and
  `unsolved` is reported as *unsettled*, never as "no solution". That
  distinction is the chapter's whole point.
* It runs inside a **temporary directory**. The solver writes `sol.txt`,
  `nosol.txt` and `unsol.txt` into the *current* directory, which on Colab is
  the student's own — the same containment `jove/Bdd.py` needed for ply.
* Off Linux it returns a result saying so, rather than calling `sys.exit()`,
  which is what the old wrapper did to the kernel.

## Where it is used

Three Chapter 15 concepts, each answering something the chapter previously
had to leave open:

| Concept | What the solver adds |
|---|---|
| 1. The PCP | `NOSOL` was *"is there none, or longer than 8?"* — **proved unsolvable**. And `HARD`, whose solution the text called long, needs **66 dominoes** for a 154-symbol match. |
| 2. PCP is Undecidable | A depth table: `unsolved` at 10, 20, 40; found at 80. Undecidability from the driver's seat rather than in a proof. |
| 4. Stepping Stone | The instance the chapter had to name `UNSOLVED` is **provably unsolvable**, so the grammar has no ambiguous string at *any* length. |

**Not** concept 3, Tile Construction. Its `tm_tiles()` builds a teaching
fragment — copy tiles only, no start or cleanup tiles — so the instance
genuinely has no solution, and running a solver there would mislead.

## Verification

Both ways, because either alone proves little:

* All nine Chapter 15 notebooks pass the harness with the solver
  **unavailable** (the macOS case), because `pcp()` returns a result rather
  than raising and every new cell branches on `pcp_available()`.
* The three modified notebooks were then run again with the solver
  **available**, and their real output checked — including the 66-domino
  solution verified by concatenation.

## Also changed

* The mac, windows and generic binaries are gone, per the decision to
  standardise on Colab. The `For_The_Public/Classic` copies carry their own
  `pcpbinaries/` and are untouched.
* `jove/PcpJupyter.py` (which did not parse) and `jove/old-PcpJupyter.py` are
  retired. **`PcpJupyterNew.py` stays** — the archived `OlderYears/`
  notebooks import it.

## Reverting

```sh
git checkout HEAD~1 -- jove/Pcp.py Chapter15-PCP
```

The old wrappers and the other binaries are in git history.

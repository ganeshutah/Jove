# Fixes

One note per piece of work that was not simply "write the thing": what the
symptom was, what changed, what it exposed, and how to undo it.

| Note | What it covers |
|---|---|
| [Font_awesome_fix.md](Font_awesome_fix.md) | Removing the per-cell `display(HTML(...))` line the animation toolbars needed — and why the first attempt was wrong |
| [Help_banner_noise.md](Help_banner_noise.md) | Collapsing the multi-line help banners printed on import |
| [Notebook_navigation.md](Notebook_navigation.md) | Moving between concept notebooks: the search picker, the static strip, `load_here()` |
| [Pumping_lemma_SMT_game.md](Pumping_lemma_SMT_game.md) | Rebuilding the Pumping Lemma notebook so the student writes the proof and a solver closes it |
| [BDD_in_notebooks.md](BDD_in_notebooks.md) | `jove/Bdd.py`, six NPC-facing BDD concepts, and 14 diagrams that carry the argument |
| [Concept_drift_audit.md](Concept_drift_audit.md) | Checking that the notebooks, the index and the workbook prose still describe the same concepts |
| [Chapter_folder_names.md](Chapter_folder_names.md) | `Chapter12-PDA` rather than `Chapter12`, from one table |
| [Pcp_solver.md](Pcp_solver.md) | `jove/Pcp.py` — making the PCP solver that already shipped actually runnable |

## A theme worth reading them for

Most of these were found by a check, and several of the checks were wrong
first. Four recurring lessons, each of which cost real time more than once:

* **One place must own each fact.** Every drift bug had the same shape: the
  same fact written down twice.
* **Silent failure is the real enemy.** A navigation strip lost on every
  regeneration; a `try/except: pass` that turned 18 parsed titles into 0 with
  no symptom beyond a search returning nothing.
* **A check that cannot fail is worse than no check.** One diagram checker
  reported "1 diagram rendered" across six notebooks and *passed* — it was
  testing nothing.
* **Measure before asserting.** Several design claims changed when measured,
  and each became a better lesson for having been wrong first.

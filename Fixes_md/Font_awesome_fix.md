# The animation toolbar: removing the font-awesome boilerplate

**Status:** resolved and confirmed working in Colab.
**Date:** 2026-09-13
**Touches:** `jove/Animate{DFA,NFA,PDA,TM}.py`, `tools/`, and the 245 generated
notebooks under `Chapter1–18/` and `Basics/`.

---

## Summary

Every animation cell used to carry a third line:

```python
from jove.AnimateDFA import *
AnimateDFA(has01, FuseEdges=True)
display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

It is now two lines. The stylesheet is loaded by `Animate*.__init__`, and a no-op
`_ipython_display_` stops Jupyter echoing the constructor's `repr` over the toolbar.

Getting here took **three wrong answers about the bug and four traps in my own
tooling**, all recorded below, because every one of them is the kind of thing that
would otherwise be rediscovered the hard way.

---

## The symptom

Without that third line, one of two things happened:

* the toolbar's **buttons were invisible** — play, pause, stop, step-back and
  step-forward all rendered as blank space; or
* the cell printed **`<jove.AnimateDFA.AnimateDFA at 0x7853472c5e50>`** where the
  toolbar should have been.

It was also load-bearing in a way that felt arbitrary: the line had to come **after**
the `Animate*` call. Put it first and the animation broke again.

## Why the obvious fixes don't work

The natural reaction is "load the stylesheet once at the top of the notebook". It
fails, and the reason is the crux of the whole problem:

> **Colab renders each cell's output inside its own sandboxed iframe.**

A `<link>` injected into cell 3's output area is in a *different document* from cell
9's. So a setup-cell `display(HTML(...))`, a `%%html` cell, a `custom.css`, an
import-time hook — all fix the local Jupyter case and none fix Colab. The stylesheet
has to reach **the output area of the cell that draws the toolbar**.

## Diagnosis: one line doing two unrelated jobs

The line resisted tidying because it was two fixes stapled together.

**Job 1 — load the CSS.** Font-awesome supplies the toolbar glyphs. Per the above, it
has to arrive per cell.

**Job 2 — return `None`.** `Animate*.__init__` already calls `display()` on the widget.
So a cell whose **last expression** is the constructor gets the widget *and* Jupyter's
echo of the returned object's `repr`. `display(...)` returns `None`, and a cell ending
in `None` echoes nothing. That is the entire explanation for "it must come last".

## Which buttons need font-awesome, and why it cannot be designed away

All of them — and not for the reason the Python source suggests.

| Button | Rendered by | Needs font-awesome |
|---|---|---|
| step-backward, step-forward | Jove, `Button(icon='step-…')` | yes — becomes `<i class="fa fa-step-forward">` |
| play, pause, stop | **the ipywidgets frontend, in JavaScript** | yes — it emits `fa-play`, `fa-pause`, `fa-stop` |
| "Animate" | Jove, `Button(description='Animate')` | no — plain text |

The `Play` widget is decisive. Its buttons are constructed by the ipywidgets
**frontend**, confirmed in `widgetsnbextension/static/extension.js`. No Python-side
change reaches them, and `Play` does not even expose an `icon` trait:

```
>>> [t for t in widgets.Play(...).trait_names() if 'icon' in t]
[]
```

**Font-awesome cannot be removed. It has to be loaded.** The only question is by whom.

## The fix

**Load it from inside `__init__`**, which runs in the very cell that creates the
widget — so the `<link>` lands in that cell's output area, the same iframe the widget
goes into, on Colab and everywhere else:

```python
def __init__(self, m_desc, FuseEdges=False, ...):
    # ---- toolbar stylesheet ----
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

And a no-op display hook handles job 2:

```python
def _ipython_display_(self):
    return None
```

IPython honours `_ipython_display_` by handing display over to it entirely; returning
nothing produces an **empty mimebundle**, so no `Out[n]` is emitted:

```
class                mimebundle keys
-------------------  ---------------
plain object         ['text/plain']   -> '<__main__.Plain at 0x1073aed20>'
__repr__ = ''        ['text/plain']   -> ''
_ipython_display_    []               -> nothing
```

Note the middle row: **`__repr__` returning `''` does not work.** It still emits a
`text/plain` part, leaving a blank output area under the toolbar. `_repr_mimebundle_`
returning `{}` does not work either — IPython falls back to `text/plain`. Only
`_ipython_display_` suppresses the output.

## What a cell looks like now

```python
from jove.AnimateDFA import *
AnimateDFA(has01, FuseEdges=True)
```

Every button appears: play, pause, stop, step-back, step-forward.

## Backward compatibility

No existing notebook needed changing, and none broke. An existing cell ends with the
font-awesome line, so:

* the widget is displayed by `__init__`, exactly as before;
* the constructor's value is **not** the cell's last expression, so it is never echoed,
  so the new hook is never reached;
* the stylesheet is loaded twice. A duplicate `<link>` is harmless.

Only cells that *end* with the constructor are affected — precisely the simplified form
this enables.

---

## Three wrong answers about the bug

Each looked right, was committed, and was disproved by actually running the notebook.

### 1. "The `Play` widget doesn't need font-awesome"

I saw that `Play` has no `icon` **trait** and concluded it drew its own controls. That
inference does not follow: a trait describes the Python-side API and says nothing about
what the frontend renders.

On that premise I replaced Jove's two `Button(icon='step-…')` with Unicode labels
(`|◀`, `▶|`) and declared the dependency gone — *"works offline, on a plane, behind a
firewall"*. It fixed exactly the two buttons Jove controls in Python and left play,
pause and stop invisible: a toolbar that looked **half**-broken, which is worse than
one that is obviously broken.

The Unicode labels were reverted; the icons are back as they were.

> **Lesson.** A Python-side trait tells you nothing about frontend rendering. And the
> assertion I wrote (`icon == ''`) confirmed only that my *edit had been applied*, not
> that the toolbar *worked*.

### 2. A stale Colab clone

With the library fixed and pushed, the toolbar was still broken — and the tell was the
`<jove.AnimateDFA.AnimateDFA at 0x...>` echo, which is impossible with the patched
library. The cause was in the setup cell, inherited from the older notebooks:

```sh
! if [ ! -d Jove ]; then git clone -q ... Jove; fi
```

**It never updates an existing clone.** A Colab session reuses `/content`, so once any
Jove notebook has run, every later one uses whatever was cloned first. Testing a fix
repeatedly in one session is exactly the workflow that guarantees you never see it.

> **Lesson.** Repeated testing in one session can pin you to the very version you are
> trying to replace.

### 3. A cached module — `pull` is not `reload`

Clone-or-pull was now correct, the cell printed `Jove: PULLED`, and the toolbar was
*still* broken. `PULLED` describes the **files on disk**. It says nothing about what is
**loaded**. Python caches imported modules in `sys.modules`:

```
1. imported OLD module. has _ipython_display_?  False
2. pulled. does the FILE on disk have the fix?  True
3. re-imported. has _ipython_display_?          False   <-- the bug
4. after purging sys.modules:                   True
```

One cause, both symptoms: the cached class neither suppresses the repr nor loads the
stylesheet. The setup cell now drops them before importing:

```python
for _m in [k for k in list(sys.modules) if k == 'jove' or k.startswith('jove.')]:
    del sys.modules[_m]
```

> **Lesson, and the thread running through all three.** My self-check tested the
> **file** on disk, so it reported "present" throughout the entire period the loaded
> module was stale. It now tests the **loaded class**:
> `hasattr(_a.AnimateDFA, '_ipython_display_')`.
> **Verify the object you are about to use, not the bytes it was built from.**

---

## Four traps in the tooling

### 1. The old checker became a foot-gun

`fix_animation_fontawesome.py` existed to enforce "the font-awesome line must come last
in every animation cell". With the library fixed, running it would **add the line back**
into the cells it had just been removed from. It is now guarded — and the guard must key
off **the loader in `__init__`, not off the icons**, because the icons are still there:

```
$ python3 tools/fix_animation_fontawesome.py
Animate*.__init__ now loads the font-awesome stylesheet itself
(see tools/fix_animation_toolbar.py), so the per-cell line is
redundant and this check has nothing to enforce. Nothing to do.
```

### 2. The remover silently missed 30 cells

There are **two quoting variants** of the same line in this repo. Generated notebooks
store it as `display(HTML('<link rel="stylesheet" ... />'))`; older hand-written ones
store it with **literal backslash-escaped quotes**, `rel=\"stylesheet\"`.

Matching the exact inner markup saw only the first — 268 of 298 repo-wide, and 43 of 54
in `For_CS3100_Fall2024/`. It now matches the *shape* of the call (a lone
`display(HTML(...))` mentioning font-awesome) while still rejecting unrelated
`display(HTML(...))` calls and the `Animate*` call itself.

### 3. Two tools keyed on a string their own rewrite removed

Both located the setup cell by a marker the cleanup deleted:

* `update_setup_cells.py` keyed on `OWN_INSTALL`. It stopped recognising cells it had
  itself just rewritten, and silently reported all 245 as **"skipped"**.
* the notebook-execution harness keyed on the `#~~~~` banner the cell used to open
  with. It then tried to `exec` the `!` shell line as Python, and **all 245 notebooks
  "failed"** with `SyntaxError` — a full-red test run caused entirely by the test rig.

Both now key on `import google.colab`, the one line Colab detection cannot do without.

> **Lesson.** A tool that rewrites something must not key on a string its own rewrite
> removes — and a sudden **uniform** failure across every target is far more likely to
> be the harness than the subject.

### 4. `git diff` against an uncommitted change

Checking that an in-place edit matched what regeneration produces, I regenerated one
chapter and read `git diff`. It showed the setup cell changing, which looked like the
edit had failed. It had not: `git diff` compares against **HEAD**, the edit was
uncommitted, so the diff showed *both* pending changes and proved nothing. Worse, the
`git checkout -- Chapter17` used to undo the test also reverted the uncommitted edit for
those seven notebooks.

> **Lesson.** Commit one change before using git to inspect the next. An uncommitted
> tree makes `git diff` useless as a differential test and `git checkout` a destructive
> one.

---

## The setup cell

Rewritten along the way, from 38 lines of defensive clutter to 21. Two pieces of that
clutter were simply wrong: the seven-entry local `sys.path` list named a **`3rdparty/`
directory that does not exist**, and only one entry is needed — the directory
*containing* `jove/`. Verified by importing `jove.Def_RE2NFA` (the heaviest importer,
whose `yacc.py` does a bare `import lex`) with the root alone on the path.

It now also **says which Jove you got**, because guessing that cost two of the three
wrong answers above. Five outcomes, all exercised against a real clone:

```
Jove: CLONED  at 8dd18ea
Jove: PULLED  already current at 8dd18ea
Jove: PULLED  e102c1d -> 8dd18ea
8dd18ea Clean up the setup cell; confirm Chapter 4's toolbar fix
f08976b All 245 generated notebooks: clone-or-pull in the setup cell
Jove: WARNING ./Jove exists but is not a git checkout -- left as is
Jove: LOCAL   checkout at 8dd18ea
```

followed by, in the 81 notebooks that animate:

```
Jove loaded from /content/Jove/jove
animation toolbar: ready
```

If that last line ever says `STALE -- restart the runtime, then re-run`, the **loaded**
library is old and nothing downstream will behave.

The git work uses `subprocess`, not the `!` shell magic, so the cell is plain Python: it
parses, and the harness executes it instead of special-casing a line it cannot compile.

## Verification

| Check | Result |
|---|---|
| All four Animate modules parse and import | pass |
| `__init__`'s **first** `display()` call is the font-awesome `<link>` | pass |
| All four carry the loader, the hook, and both step icons | pass |
| `_ipython_display_` yields an empty mimebundle for all four | pass |
| Old 3-line and new 2-line cell forms both display the widget once | pass |
| Replayed the failing session: pre-fix clone, old module imported, then the setup cell — `False` → `PULLED` → `ready` → `True`, empty mimebundle | pass |
| All four Colab branches (clone / current / behind / not-a-repo) | pass |
| Each notebook's self-check names its own Animate class (DFA 51, NFA 14, PDA 8, TM 8) | pass |
| All 245 generated notebooks execute cleanly | pass |
| `metadata.widgets` invariant across 633 notebooks | 0 violations |
| **Confirmed working in Colab by hand** | pass |

## The tools

| Tool | Does |
|---|---|
| `tools/fix_animation_toolbar.py` | Patches the library: stylesheet loader into `__init__`, the display hook, class docstrings. Idempotent. |
| `tools/simplify_animation_cells.py` | Deletes the redundant line from notebooks. `--scope` limits the tree. |
| `tools/fix_animation_fontawesome.py` | **Superseded**, guarded so `--write` cannot undo the fix. |

Both active tools dry-run by default and need `--write`. Git is the revert path.

## Rollout status

| Tree | Animation cells | Carrying the line |
|---|---:|---:|
| `Chapter1–18/` | 78 | **0** |
| `Basics/` | 3 | **0** |
| `For_CS3100_Fall2024/` | 58 | 54 — **held back**, live Colab links |
| rest of the repo | — | 169 |

The library fix is **repo-wide and already in effect**: every animation cell in the
repo, including the untouched legacy trees, gets its stylesheet from
`Animate*.__init__`. The table only tracks deletion of the now-redundant text. Cells
that still carry the line work fine; they merely fetch the stylesheet twice.

The generated notebooks were brought over by **regenerating** them, not patching in
place, so they match their generators exactly. Regeneration left the setup cells
byte-identical — the diff is confined to the animation cells and the stale markdown note
that used to explain why the line had to come last.

## What is left

* **`For_CS3100_Fall2024/`** — 54 cells still carry the line, and those notebooks still
  have the **old clone-only setup guard**, which is what pinned a session to a stale
  library in the first place. That is the more valuable of the two fixes for that tree.
* **`jove/JoveEditor.py`** — a separate component with its own `icon=` button and its
  own font-awesome line. Untouched.

## Reverting

```sh
git revert <commit>
```

or by hand: delete the stylesheet block from each `__init__` and the four
`_ipython_display_` methods, and restore the per-cell line in notebooks.

## Environment tested

`ipywidgets 8.1.3`, `IPython 8.24.0`, Python 3.12, macOS arm64, plus Colab by hand.
Colab pins its own ipywidgets version — a further reason the fix must not depend on
frontend behaviour. Loading the stylesheet works whatever the frontend renders.

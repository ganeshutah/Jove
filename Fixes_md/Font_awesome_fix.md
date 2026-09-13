# Removing the font-awesome boilerplate from Jove animations

**Date:** 2026-09-13
**Touches:** `jove/AnimateDFA.py`, `AnimateNFA.py`, `AnimatePDA.py`, `AnimateTM.py`,
`tools/`, and the generated notebooks under `Chapter*/` and `Basics/`.

---

## The symptom

Every cell that animated a machine had to carry three lines, not two:

```python
from jove.AnimateDFA import *
AnimateDFA(has01, FuseEdges=True)
display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

Leave the third line out and one of two things went wrong:

* the toolbar's **buttons were invisible** — play, pause, stop, step-back and
  step-forward all rendered as blank space; or
* the cell printed **`<jove.AnimateDFA.AnimateDFA at 0x7853472c5e50>`** where the
  toolbar should have been.

It was also load-bearing in a way that felt arbitrary: the line had to come **after**
the `Animate*` call. Put it first and the animation broke again.

## Why the obvious fixes don't work

The natural reaction is "load the stylesheet once at the top of the notebook". That
fails, and the reason is the crux of the whole problem:

> **Colab renders each cell's output inside its own sandboxed iframe.**

A `<link>` injected into cell 3's output area is in a *different document* from cell
9's output area. So a setup-cell `display(HTML(...))`, a `%%html` cell, a `custom.css`,
an import-time hook — all of them fix the local Jupyter case and none of them fix
Colab. The stylesheet has to reach **the output area of the cell that draws the
toolbar**.

## Diagnosis: one line doing two unrelated jobs

The reason the line resisted tidying is that it was two fixes stapled together.

**Job 1 — load the CSS.** Font-awesome supplies the toolbar glyphs. Per the above, it
has to be loaded per cell.

**Job 2 — return `None`.** `Animate*.__init__` already calls `display()` on the widget
it builds. So a cell whose **last expression** is the constructor gets the widget *and*
Jupyter's echo of the returned object's `repr`. `display(...)` returns `None`, and a
cell ending in `None` echoes nothing — so the line was accidentally suppressing the
repr as well. That is the entire explanation for "it must come last".

## Which buttons need font-awesome, and why you cannot design it away

All of them — and not for the reason the Python source suggests.

| Button | Rendered by | Needs font-awesome |
|---|---|---|
| step-backward, step-forward | Jove, `Button(icon='step-…')` | yes — becomes `<i class="fa fa-step-forward">` |
| play, pause, stop | **the ipywidgets frontend, in JavaScript** | yes — it emits `fa-play`, `fa-pause`, `fa-stop` |
| "Animate" | Jove, `Button(description='Animate')` | no — plain text |

The `Play` widget is the decisive one. Its buttons are constructed by the ipywidgets
**frontend**, not by Jove's Python:

```
$ grep -l 'fa-play\|fa-pause\|fa-stop' $(python -c "…")/widgetsnbextension/static/extension.js
widgetsnbextension/static/extension.js
```

No Python-side change can reach them. `Play` does not even expose an `icon` trait:

```
>>> [t for t in widgets.Play(...).trait_names() if 'icon' in t]
[]
```

**So font-awesome cannot be removed. It has to be loaded.** The only question is *by
whom*.

## The fix

**Load it from inside `__init__`.**

`__init__` runs in the very cell that creates the widget, so a `display(HTML(...))`
there lands in **that cell's output area** — the same iframe the widget goes into, on
Colab and everywhere else. Every animation cell therefore gets the stylesheet
automatically, with nothing written by hand.

```python
def __init__(self, m_desc, FuseEdges=False, ...):
    # ---- toolbar stylesheet ----
    # ... runs in the cell that creates the widget, so the stylesheet lands
    # in that cell's output area -- which matters on Colab, where each cell's
    # output is a separate sandboxed iframe.
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

And a no-op display hook handles job 2:

```python
def _ipython_display_(self):
    return None
```

IPython honours `_ipython_display_` by handing display over to it entirely. Returning
nothing produces an **empty mimebundle**, so no `Out[n]` is emitted:

```
class                mimebundle keys
-------------------  ---------------
plain object         ['text/plain']   -> '<__main__.Plain at 0x1073aed20>'
__repr__ = ''        ['text/plain']   -> ''
_ipython_display_    []               -> nothing
```

Note the middle row. **`__repr__` returning the empty string does not work** — it still
emits a `text/plain` part, which leaves a blank output area under the toolbar. The
display hook is the only one of the two that suppresses the output entirely.

## What a cell looks like now

```python
from jove.AnimateDFA import *
AnimateDFA(has01, FuseEdges=True)
```

Every button appears: play, pause, stop, step-back, step-forward.

## Backward compatibility

No existing notebook needed changing, and none broke.

An existing cell ends with the font-awesome line, so:

* the widget is displayed by `__init__`, exactly as before;
* the constructor's value is **not** the cell's last expression, so it is never echoed,
  so the new `_ipython_display_` hook is never reached;
* the stylesheet is now loaded twice — once by `__init__`, once by the old line. A
  duplicate `<link>` is harmless.

Only cells that *end* with the constructor are affected, which is precisely the
simplified form the change enables.

## What I got wrong on the first attempt

Worth recording, because the wrong version was committed and pushed before it was
caught by actually running it.

**I concluded that `Play` did not need font-awesome.** The evidence I used was that
`Play` has no `icon` trait — from which I inferred it "draws its own controls". That
inference does not follow: a trait describes the Python-side API, and says nothing
about what the frontend renders. `Play`'s buttons are emitted as `fa-play` /
`fa-pause` / `fa-stop` by the ipywidgets JavaScript.

On that false premise I replaced Jove's two `Button(icon='step-…')` with Unicode
labels (`|◀`, `▶|`) and declared the dependency gone — "works offline, on a plane,
behind a firewall". **That was wrong.** It fixed exactly the two buttons Jove controls
and left play, pause and stop invisible, which is worse than before: the toolbar looked
half-broken rather than obviously broken.

The check I should have run was the one that eventually found it — open a notebook and
look at the toolbar. A widget-model assertion (`icon == ''`) confirmed only that my
edit had been applied, not that the toolbar worked. **Asserting that a change took
effect is not the same as asserting that it had the intended effect.**

The Unicode labels have been reverted; the icons are back as they were.

## The trap that hid the fix: a stale Colab clone

After the library fix was pushed and correct, the toolbar was **still** broken when
tested — and the giveaway was that the cell printed
`<jove.AnimateDFA.AnimateDFA at 0x...>`. That echo is impossible with the patched
library, because `_ipython_display_` suppresses it. So the running Jove was not the
patched one.

The cause was in the notebook setup cell, inherited from the older notebooks:

```sh
! if [ ! -d Jove ]; then git clone -q https://github.com/ganeshutah/Jove Jove; fi
```

**It never updates an existing clone.** A Colab session keeps `/content` across
notebooks, so once any Jove notebook has run, every later notebook in that session
silently uses whatever was cloned first — fixes included. Testing a fix repeatedly in
one session is exactly the workflow that guarantees you never see it.

Two changes:

```sh
! if [ ! -d Jove ]; then git clone -q ... Jove; else git -C Jove pull -q --ff-only ...; fi
```

and the setup cell now **self-reports**, so this is answerable from the cell output
rather than by guesswork:

```
Jove loaded from /content/Jove/jove
animation toolbar: ready
```

If that second line ever says `STALE`, the *loaded* library is old and nothing
downstream will behave — restart the runtime.

Note `jove` has no `__init__.py` — it is a **namespace package**, so `jove.__file__` is
`None` and the directory has to come from `jove.__path__`. The first version of the
self-check used `__file__`, which raised `TypeError` *outside* its own try block and
would have broken the setup cell outright. The whole check now sits inside the try: a
diagnostic must never be able to break the thing it is diagnosing.

## The trap that hid it a second time: a cached module

With the library fixed *and* the clone pulling correctly, the toolbar was **still**
broken — same `<jove.AnimateDFA.AnimateDFA at 0x...>` echo, same missing buttons — even
though the setup cell printed `Jove: PULLED`.

`PULLED` describes the **files on disk**. It says nothing about what is **loaded**.
Python caches imported modules in `sys.modules`, so in a session that had already
imported the old `jove.AnimateDFA`, the pull updated the files and the subsequent
`import` handed back the stale module object anyway:

```
1. imported OLD module. has _ipython_display_?  False
2. pulled. does the FILE on disk have the fix?  True
3. re-imported. has _ipython_display_?          False   <-- the bug
4. after purging sys.modules:                   True
```

One cause, both symptoms: the cached class neither suppresses the repr nor loads the
stylesheet.

The setup cell now drops them before importing:

```python
for _m in [k for k in list(sys.modules) if k == 'jove' or k.startswith('jove.')]:
    del sys.modules[_m]
```

and the self-check was moved off the **file** and onto the **loaded class**, which is
the distinction that matters:

```python
import jove.AnimateDFA as _a; print('animation toolbar:',
      'ready' if hasattr(_a.AnimateDFA, '_ipython_display_')
      else 'STALE -- restart the runtime, then re-run')
```

Checking the file was checking the wrong thing — it was green throughout the period
when the loaded module was stale. **Verify the object you are about to use, not the
bytes it was built from.**

## Verification

| Check | Result |
|---|---|
| All four Animate modules parse and import | pass |
| `__init__`'s **first** `display()` call is the font-awesome `<link>` | pass |
| The widget is displayed after it, in the same cell | pass |
| All four modules carry the loader, the hook, and both icons | pass |
| `_ipython_display_` yields an empty mimebundle | pass |
| Chapter 4 (22 notebooks) executes cleanly after simplification | pass |
| `metadata.widgets` invariant across 633 notebooks | 0 violations |

**Still not verified here:** whether the toolbar *looks* right in a browser. That needs
a human with the notebook open, which is how the first attempt's flaw surfaced.

## The tools

| Tool | Does |
|---|---|
| `tools/fix_animation_toolbar.py` | Patches the library: adds the stylesheet loader to `__init__`, adds the display hook, rewrites the class docstrings. Idempotent. |
| `tools/simplify_animation_cells.py` | Deletes the now-redundant line from notebooks. `--scope` limits the tree. Optional — leaving it is merely a duplicate `<link>`. |
| `tools/fix_animation_fontawesome.py` | **Superseded**, and guarded (below). |

Both active tools dry-run by default and need `--write`. Git is the revert path.

## Two traps found on the way

**The old checker became a foot-gun.** `fix_animation_fontawesome.py` existed to
enforce "the font-awesome line must come last in every animation cell". With the
library fixed, running it would **add the line back** into the cells it had just been
removed from. It is now guarded — and note that the guard has to key off **the loader
in `__init__`, not off the icons**, because the icons are still there:

```
$ python3 tools/fix_animation_fontawesome.py
Animate*.__init__ now loads the font-awesome stylesheet itself
(see tools/fix_animation_toolbar.py), so the per-cell line is
redundant and this check has nothing to enforce. Nothing to do.
```

**The remover missed 30 cells.** There are **two quoting variants** of the same line in
this repo. Generated notebooks store it as

```python
display(HTML('<link rel="stylesheet" ... />'))
```

while older hand-written ones store it with **literal backslash-escaped quotes**:

```python
display(HTML('<link rel=\"stylesheet\" ... />'))
```

The first version of `simplify_animation_cells.py` matched the exact inner markup and
so saw only the first variant, silently skipping 30 cells — 268 of 298 repo-wide, and
43 of 54 in `For_CS3100_Fall2024/`. It now matches the *shape* of the call (a lone
`display(HTML(...))` mentioning font-awesome) rather than its markup, covering all 298
while still rejecting unrelated `display(HTML(...))` calls and the `Animate*` call
itself.

## A third trap: `git diff` against an uncommitted change

While checking that the in-place setup-cell update matched what a full regeneration
would produce, I regenerated one chapter and read `git diff`. The diff showed the
setup cell changing — which looked like the in-place update had not worked.

It had. `git diff` compares against **HEAD**, and the in-place update was still
uncommitted, so the diff showed *both* pending changes at once and the comparison
proved nothing. Worse, the `git checkout -- Chapter17` used to undo the test also
reverted the uncommitted setup-cell update for those seven notebooks.

Lesson: **commit one change before using git to inspect the next.** An uncommitted
working tree makes `git diff` useless as a differential test, and `git checkout` a
destructive one.

## The setup cell, cleaned up and made to say what it did

The clone-or-pull fix left the cell at 38 lines of defensive clutter, and two pieces of
that clutter were simply wrong:

* the seven-entry local `sys.path` list named a **`3rdparty/` directory that does not
  exist** in this repo;
* only one entry is needed — the directory *containing* `jove/`. Verified by importing
  `jove.Def_RE2NFA` (the heaviest importer, and the one whose `yacc.py` does a bare
  `import lex`) with the root alone on the path.

It also now **reports which Jove you got**, because guessing that has cost real
debugging time. Four outcomes, all exercised:

```
Jove: CLONED  at 8dd18ea
Jove: PULLED  already current at 8dd18ea
Jove: PULLED  e102c1d -> 8dd18ea
8dd18ea Clean up the setup cell; confirm Chapter 4's toolbar fix
f08976b All 245 generated notebooks: clone-or-pull in the setup cell
Jove: WARNING ./Jove exists but is not a git checkout -- left as is
```

plus `Jove: LOCAL   checkout at <sha>` off Colab. When a pull brings something new, the
new commits are listed — so a changed library announces itself instead of being
inferred from behaviour.

The git work is done with `subprocess`, not the `!` shell magic. That is not cosmetic:
the cell is now **plain Python**, so it parses, and the test harness can execute it
instead of special-casing a line it cannot compile.

**The same trap, twice, in two different tools.** Both located the setup cell by a
string the rewrite removed:

* `update_setup_cells.py` keyed on `OWN_INSTALL`. It stopped recognising cells it had
  itself just rewritten, and silently reported all 245 as "skipped".
* the notebook-execution harness keyed on the `#~~~~` banner the cell used to open
  with. It then tried to `exec` the `!` shell line as Python, and **all 245 notebooks
  "failed"** with `SyntaxError` — a full-red test run caused entirely by the test rig.

Both now key on `import google.colab`, the one line the Colab detection cannot do
without. **A tool that rewrites something must not key on a string its own rewrite
removes** — and a sudden *uniform* failure across every target is far more likely to be
the harness than the subject.

## Rollout status

Two independent rollouts are in flight. Keep them apart:

**(a) The setup-cell fix** — clone-or-pull, plus the cleanup above. **Done for all 245
generated notebooks** (`Chapter1–18/`, `Basics/`). Applied in place by
`Concepts/tools-concept/nbgen/update_setup_cells.py` in the workbook repo, which
rebuilds *only* cell 2 using the same `nbuild.header_cell()` the generators use — so
it does not drag in the font-awesome change, which is still pending review.

`For_CS3100_Fall2024/` and the other legacy trees still have the clone-only guard.

**(b) Deleting the redundant font-awesome line** — pending verification of Chapter 4.

| Tree | Cells still carrying the line | Simplified |
|---|---:|---|
| `Chapter4/` | 0 | **yes** |
| `Chapter1–3, 5–18/` | 72 | not yet |
| `Basics/` | 3 | not yet |
| `For_CS3100_Fall2024/` | 54 | **no** — live Colab links, held back deliberately |
| rest of the repo | 169 | not yet |

72 + 3 + 54 + 169 = 298, the repo-wide total. (There are 319 animation cells in all;
the other 21 never had the line, including Chapter 4's 6.)

The library fix is repo-wide and already in effect — **every** animation cell in the
repo now gets its stylesheet from `__init__`, whether or not it still carries the old
line. The table is only about deleting the redundant text.

## Not covered

`jove/JoveEditor.py` is a separate component with its own `icon=` button and its own
font-awesome line. It was left alone.

## Reverting

```sh
git revert <commit>
```

or by hand: delete the stylesheet block from each `__init__` and the four
`_ipython_display_` methods, and restore the per-cell line in notebooks.

## Environment tested

`ipywidgets 8.1.3`, `IPython 8.24.0`, Python 3.12, macOS arm64. Colab pins its own
ipywidgets version, which is a further reason the fix must not depend on frontend
behaviour: loading the stylesheet works whatever the frontend renders.

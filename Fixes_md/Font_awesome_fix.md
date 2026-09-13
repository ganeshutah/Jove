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

* the toolbar's **step buttons were invisible** — the play/pause control appeared,
  but the two stepping buttons next to it were blank; or
* the cell printed **`<jove.AnimateDFA.AnimateDFA at 0x7853472c5e50>`** where the
  toolbar should have been.

It was also load-bearing in a way that felt arbitrary: the line had to come **after**
the `Animate*` call. Put it first and the animation broke again.

## Why the obvious fixes don't work

The natural reaction is "load the stylesheet once at the top of the notebook". That
fails, and the reason is worth knowing:

> **Colab renders each cell's output inside its own sandboxed iframe.**

A `<link>` injected into cell 3's output area is in a *different document* from cell
9's output area. The stylesheet genuinely has to be re-injected per cell — so long as
the toolbar depends on it at all.

That rules out every notebook-level workaround: a setup-cell `display(HTML(...))`, a
`%%html` cell, a custom.css, an `IPython.display` hook at import time. All of them fix
the local Jupyter case and none of them fix Colab.

Which points at the real answer: **stop depending on the stylesheet.**

## Diagnosis: one line doing two unrelated jobs

The reason the line resisted tidying is that it was two fixes stapled together.

**Job 1 — load the CSS.** `ipywidgets` renders `Button(icon='step-forward')` as
`<i class="fa fa-step-forward">`. That element is *empty* unless font-awesome is
loaded; hence invisible buttons. (Under ipywidgets 7 the classic notebook shipped
font-awesome itself, so this used to work by accident. JupyterLab and Colab do not.)

**Job 2 — return `None`.** `Animate*.__init__` already calls `display()` on the widget
it builds. So a cell whose **last expression** is the constructor gets the widget *and*
Jupyter's echo of the returned object's `repr`. `display(...)` returns `None`, and a
cell ending in `None` echoes nothing — so the line was accidentally suppressing the
repr as well. That is the whole explanation for "it must come last".

Each job needed its own fix.

## Fix 1 — the icons

The entire font-awesome dependency in Jove turned out to be **eight lines**: two
buttons in each of the four Animate classes.

```
jove/AnimateDFA.py:109   Button(icon='step-backward', ...)
jove/AnimateDFA.py:113   Button(icon='step-forward',  ...)
jove/AnimateNFA.py:105   ... and the same pair in NFA, PDA, TM
```

They are now Unicode labels:

```python
self.backward = widgets.Button(description='|◀', layout=Layout(width='45px'), ...)
self.forward  = widgets.Button(description='▶|', layout=Layout(width='45px'), ...)
```

`U+25C0` and `U+25B6` are BMP **geometric shapes**, present in essentially every system
font — deliberately not the `U+23EE`/`U+23ED` media glyphs, which need an emoji font
and box-render without one. The button width went from 40px to 45px to fit a
two-character label instead of an icon square.

The `Play` widget needed nothing. Under ipywidgets 8 it draws its own controls and has
no `icon` trait at all:

```
>>> [t for t in widgets.Play(...).trait_names() if 'icon' in t]
[]
```

So it was never the reason for the stylesheet.

**Result: no CDN dependency at all.** The toolbar now works offline, on a plane, and
behind a firewall that blocks `stackpath.bootstrapcdn.com`.

## Fix 2 — the echo

Each Animate class gained a no-op display hook:

```python
def _ipython_display_(self):
    return None
```

IPython honours `_ipython_display_` by handing the object's display over to it
entirely. Returning nothing produces an **empty mimebundle**, so no `Out[n]` is
emitted at all:

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

## Backward compatibility

No existing notebook needed changing, and none broke.

An existing cell ends with the font-awesome line, so:

* the widget is displayed by `__init__`, exactly as before;
* the constructor's value is **not** the cell's last expression, so it is never echoed,
  so the new `_ipython_display_` hook is never reached;
* the now-pointless `<link>` is still fetched — harmless, just wasted.

Only cells that *end* with the constructor are affected, which is precisely the
simplified form the change enables.

## Verification

| Check | Result |
|---|---|
| All four Animate modules parse and import | pass |
| `AnimateDFA` constructs against a real DFA; buttons carry `description`, `icon=''` | pass |
| No `icon=` remains in any Animate class | pass |
| `_ipython_display_` yields an empty mimebundle for all four classes | pass |
| Old 3-line form and new 2-line form both display the widget exactly once | pass |
| Chapter 4 (22 notebooks) executes cleanly after simplification | pass |
| Chapter 4 notebooks structurally valid | pass |
| `metadata.widgets` invariant across 633 notebooks | 0 violations |

**Not verified here:** the glyphs were not eyeballed in a browser. The widget model is
correct and carries no `fa-` class, but whether `|◀` / `▶|` *look* right at 45px is a
visual judgement that needs a human. `tools/drop_fontawesome_dependency.py --write
--ascii` swaps them for `<<` / `>>` if they do not.

## The tools

| Tool | Does |
|---|---|
| `tools/drop_fontawesome_dependency.py` | Patches the library: icons → Unicode labels, adds the display hook, rewrites the class docstrings. Idempotent. `--ascii` for ASCII labels. |
| `tools/simplify_animation_cells.py` | Deletes the redundant line from notebooks. `--scope` limits the tree. Optional — leaving the line in place is merely a wasted fetch. |
| `tools/fix_animation_fontawesome.py` | **Superseded.** Now guarded (see below). |

Both new tools dry-run by default and need `--write` to act. Git is the revert path.

## Two things that went wrong on the way

**The old tool became a foot-gun.** `fix_animation_fontawesome.py` existed to enforce
"the font-awesome line must come last in every animation cell". With the library fixed,
running it would have **added the line back** into the very cells it had just been
removed from. It now checks whether the library still uses font-awesome icons and, if
not, exits without proposing anything:

```
$ python3 tools/fix_animation_fontawesome.py
The Animate* classes no longer use font-awesome icons
(see tools/drop_fontawesome_dependency.py), so the font-awesome line
is obsolete and this check has nothing to enforce. Nothing to do.
```

**The remover missed 30 cells.** There are **two quoting variants** of the same line in
this repo. The generated notebooks store it as

```python
display(HTML('<link rel="stylesheet" ... />'))
```

while the older hand-written ones store it with **literal backslash-escaped quotes**:

```python
display(HTML('<link rel=\"stylesheet\" ... />'))
```

The first version of `simplify_animation_cells.py` matched the exact inner markup and
therefore only saw the first variant, silently skipping 30 cells — 268 of 298
repo-wide, and 43 of 54 in `For_CS3100_Fall2024/`. It now matches the *shape* of the
call (a lone `display(HTML(...))` mentioning font-awesome) rather than its markup, and
covers all 298 while still rejecting unrelated `display(HTML(...))` calls and the
`Animate*` call itself.

## Rollout status

| Tree | Animation cells | Simplified |
|---|---:|---|
| `Chapter4/` | 6 | **yes** (trial) |
| `Chapter1–3, 5–18/` | 72 | not yet |
| `Basics/` | 3 | not yet |
| `For_CS3100_Fall2024/` | 54 | **no** — live Colab links, held back deliberately |
| rest of the repo | 169 | not yet |

72 + 3 + 54 + 169 = 298, the repo-wide total of cells still carrying the line.
(There are 319 animation cells in all; the other 21 never had one, including the
6 in Chapter 4 that have now been simplified.)

The library fix is repo-wide and already in effect; the table is only about deleting
the redundant line from notebook sources. Everything keeps working either way.

## Not covered

`jove/JoveEditor.py` is a separate component with its own `icon=` button and its own
font-awesome line. It was left alone.

## Reverting

```sh
git revert <commit>          # the library patch, the Ch4 sweep, or both
```

or, to go back to font-awesome icons by hand, restore the eight `icon='step-…'`
arguments and delete the four `_ipython_display_` methods.

## Environment tested

`ipywidgets 8.1.3`, `IPython 8.24.0`, Python 3.12, macOS arm64.
The change should be safe under ipywidgets 7 as well — `description=` and
`_ipython_display_` both predate 8 — but that was not exercised here.

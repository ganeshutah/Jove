# tools

Maintenance scripts for this repo.

## `fix_widget_metadata.py`

Repairs notebooks that GitHub and nbviewer refuse to render with:

> **Invalid Notebook** — There was an error rendering your Notebook: the `'state'`
> key is missing from `'metadata.widgets'`. Add `'state'` to each, or remove
> `'metadata.widgets'`.

```sh
python3 tools/fix_widget_metadata.py           # report only, exits 1 if any are broken
python3 tools/fix_widget_metadata.py --write   # repair in place
```

### Why it happens

nbconvert's HTML exporter reads exactly this path
(`nbconvert/filters/widgetsdatatypefilter.py`):

```python
metadata["widgets"]["application/vnd.jupyter.widget-state+json"]["state"]
```

Two older layouts in this repo did not provide it, and **both** raised the error:

| | Layout | Fix |
|---|---|---|
| **A** | models stored directly under the mimetype key, with no `state` wrapper | **wrap** — models moved under `state`, version fields added. **Nothing is lost.** |
| **B** | the pre-mimetype layout, holding only view references such as `{"views": [{"cell_index": 20}]}` | **drop** — the block is removed. View references alone cannot reconstruct a widget, so there is nothing to preserve. This is the "or remove `metadata.widgets`" remedy the error itself suggests. |

Neither case touches a cell. Only notebook-level metadata changes.

### Note

`nbformat.validate()` does **not** catch this — it passed all 437 notebooks while
51 of them failed to render. The reliable check is an actual HTML export:

```sh
jupyter nbconvert --to html --stdout NOTEBOOK.ipynb > /dev/null
```

Worth running after any bulk notebook edit, and before publishing links students
will click.


## `compact_help_banners.py`

Collapses the multi-line "help commands" banners the modules print on import.

```sh
python3 tools/compact_help_banners.py           # dry run
python3 tools/compact_help_banners.py --write   # apply
```

Twelve modules each opened with

```python
print('''You may use any of these help commands:
help(mk_dfa)
help(totalize_dfa)
... one line per function ...
''')
```

— **125 printed lines across the library**, all saying the same thing: help exists.
A typical notebook's four imports produced **47 lines of banner before it did
anything**. Each block becomes one statement naming the same functions:

```
help(<fn>) is available for: mkp_dfa, mk_dfa, totalize_dfa,
    addtosigma_dfa, step_dfa, run_dfa, accepts_dfa, comp_dfa, ...
```

125 lines → 29; the sample notebook's 47 → 11. Wrapping is done at patch time and
baked in as a string literal, so the modules gain no runtime import and the output
never wraps mid-name.

`Def_md2mc` splits its list with `.. and if you want to dig more, then ..`,
separating the function you call from the internals; that becomes `; internals: ...`.

The `Animate*` and `JoveEditor` modules print a one-line help *sentence* rather than a
list. They are already short and are left alone.

### It found two bugs

The banners advertised two functions that **do not exist**, so `help()` on them would
fail:

| advertised | actual |
|---|---|
| `help(addtosigma_delta)` | `addtosigma_dfa` |
| `help(suvivor_id)` | `survivor_id` |

Both were pre-existing typos in Jove's own banners. Fixed, and the tool now warns if a
banner names something the module does not define.

---

## `fix_animation_toolbar.py`

Makes the animation toolbar work with no per-cell boilerplate.

```sh
python3 tools/fix_animation_toolbar.py           # dry run
python3 tools/fix_animation_toolbar.py --write   # apply
```

### What the old boilerplate was for

```python
from jove.AnimateDFA import *
AnimateDFA(myDFA, FuseEdges=True)
display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

Two unrelated jobs in one line:

1. **Loading font-awesome**, which the toolbar glyphs need. It could not be hoisted to
   the top of the notebook because **Colab renders each cell's output in its own
   sandboxed iframe** — a `<link>` from one cell never reaches another cell's output.
2. **Returning `None`.** `Animate*.__init__` already `display()`s the widget, so a cell
   *ending* in the constructor also echoed `<jove.AnimateDFA.AnimateDFA at 0x...>`.
   That is why the line had to come **last**.

### Which buttons need font-awesome

All of them, and font-awesome cannot be designed away:

| Button | Rendered by | Needs fa |
|---|---|---|
| step-backward, step-forward | Jove, `Button(icon='step-…')` | yes |
| play, pause, stop | **the ipywidgets frontend, in JS** (`fa-play`, `fa-pause`, `fa-stop`) | yes |
| "Animate" | Jove, `Button(description=...)` | no |

The `Play` buttons are built in JavaScript; no Python-side change reaches them, and
`Play` has no `icon` trait at all.

### The fix

**Load the stylesheet from inside `__init__`.** It runs in the cell that creates the
widget, so the `<link>` lands in that cell's output area — the same iframe as the
widget. Every animation cell gets it with nothing written by hand.

A no-op `_ipython_display_` handles the echo: IPython then emits an **empty
mimebundle**. (`__repr__` returning `''` does *not* work — it still emits a
`text/plain` of `''`, leaving a blank output area.)

### After

```python
from jove.AnimateDFA import *
AnimateDFA(myDFA, FuseEdges=True)
```

### Not covered

`jove/JoveEditor.py` is a separate component with its own `icon=` button and its own
font-awesome line. It is untouched.

See `Fixes_md/Font_awesome_fix.md` for the full write-up, including a first attempt
that was wrong and why.

---

## `simplify_animation_cells.py`

Deletes the now-redundant font-awesome line from animation cells. Run
`fix_animation_toolbar.py` first.

```sh
python3 tools/simplify_animation_cells.py --scope 'Chapter*/*/*.ipynb'
python3 tools/simplify_animation_cells.py --scope 'Chapter*/*/*.ipynb' --write
```

Removing the line is **safe but optional** — with the library patched, leaving it in
place merely loads the stylesheet twice, which is harmless. Only cells that actually call an
`Animate*` constructor are touched.

---

## `fix_animation_fontawesome.py`

Makes every `Animate*` cell actually show its toolbar instead of ending with

```
<jove.AnimateDFA.AnimateDFA at 0x7853472c5e50>
```

```sh
python3 tools/fix_animation_fontawesome.py           # report, exits 1 if any
python3 tools/fix_animation_fontawesome.py --write   # fix in place
```

> **Superseded by `fix_animation_toolbar.py`.** Once `Animate*.__init__` loads the
> stylesheet itself, the per-cell line is redundant and the ordering rule below has
> nothing left to enforce. The script is guarded so that `--write` cannot add the
> lines back; note the guard keys off **the loader in `__init__`, not off the icons**,
> because the icons are still there. It is kept because it documents the failure it
> was written for.

### The rule it enforces

An **active** font-awesome `display(HTML(...))` line must be the **last statement of
the cell**, i.e. it must *follow* the `Animate*` call:

```python
AnimateNFA(ThirdLastIs1NFAalt, FuseEdges=True)
display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

Position matters, not just presence. Two separate things go wrong otherwise:

* the toolbar glyphs **are** font-awesome icons, so no controls render; and
* `Animate*.__init__` already calls `display()` on the widget, so if the constructor
  is the cell's last expression Jupyter *additionally* echoes the object's repr.
  Putting the `display(HTML(...))` call last returns `None` and suppresses that.

### What it found

Of 231 animation cells in this repo, **38 were wrong** in three ways:

| | Count | Problem |
|---|---:|---|
| `appended` | 22 | no font-awesome line at all |
| `moved` | 10 | line present but **before** the call, so the repr still showed |
| `uncommented+moved` | 6 | line commented out **and** in the wrong place |

The `moved` category is the easy one to miss: those cells *look* right in a grep for
`font-awesome`, but the ordering defeats them.

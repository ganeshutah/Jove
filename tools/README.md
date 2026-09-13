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


## `drop_fontawesome_dependency.py`

Removes Jove's font-awesome dependency at the source, so animation cells no
longer need the per-cell stylesheet line at all.

```sh
python3 tools/drop_fontawesome_dependency.py           # dry run
python3 tools/drop_fontawesome_dependency.py --write   # apply
python3 tools/drop_fontawesome_dependency.py --write --ascii   # '<<' / '>>' labels
```

### What the old boilerplate was actually for

```python
from jove.AnimateDFA import *
AnimateDFA(myDFA, FuseEdges=True)
display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))
```

That one line did **two unrelated jobs**, which is why it could not simply be
hoisted to the top of the notebook:

1. **It loaded the stylesheet.** It had to repeat per cell because Colab renders
   each cell's output in its own sandboxed iframe, so a `<link>` injected by one
   cell does not reach another cell's output.
2. **It returned `None`.** `Animate*.__init__` already calls `display()` on the
   widget, so a cell *ending* in the constructor also printed
   `<jove.AnimateDFA.AnimateDFA at 0x...>` over the toolbar.

### What the script changes

**The icons.** The only font-awesome consumers in the whole library were two
buttons per Animate class — `Button(icon='step-backward')` and
`Button(icon='step-forward')`, eight lines in total. ipywidgets renders `icon=`
as `<i class="fa fa-step-forward">`, which is empty without the stylesheet.
They become Unicode `description=` labels (`|◀`, `▶|`), so there is no CDN
dependency left and the toolbar works offline.

The `Play` widget needed nothing — under ipywidgets 8 it draws its own
controls — so it was never the reason for the link.

**The echo.** A no-op `_ipython_display_` is added to each Animate class.
IPython then produces an **empty mimebundle** for the object and emits no
`Out[n]` at all. (`__repr__` returning `''` does *not* do this: it still emits a
`text/plain` of `''`, leaving a blank output area.)

This is **backward compatible**. Existing notebooks end the cell with the
font-awesome line, so the constructor's value is never echoed and the hook is
never reached; the widget still comes from `__init__` exactly as before.

### After

```python
from jove.AnimateDFA import *
AnimateDFA(myDFA, FuseEdges=True)
```

### Not covered

`jove/JoveEditor.py` is a separate component with its own `icon=` button and its
own font-awesome line. It is untouched.

---

## `simplify_animation_cells.py`

Deletes the now-redundant font-awesome line from animation cells. Run
`drop_fontawesome_dependency.py` first.

```sh
python3 tools/simplify_animation_cells.py --scope 'Chapter*/*/*.ipynb'
python3 tools/simplify_animation_cells.py --scope 'Chapter*/*/*.ipynb' --write
```

Removing the line is **safe but optional** — with the library patched, leaving it
in place is merely a redundant stylesheet fetch. Only cells that actually call an
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

> **Superseded by `drop_fontawesome_dependency.py`.** Once the library no longer
> uses font-awesome icons, the ordering rule below no longer has anything to
> enforce. The script is kept because it documents the failure it was written
> for, and because it still reports correctly on notebooks that retain the line.

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

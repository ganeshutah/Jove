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


## `fix_animation_fontawesome.py`

Makes every `Animate*` cell actually show its toolbar instead of ending with

```
<jove.AnimateDFA.AnimateDFA at 0x7853472c5e50>
```

```sh
python3 tools/fix_animation_fontawesome.py           # report, exits 1 if any
python3 tools/fix_animation_fontawesome.py --write   # fix in place
```

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

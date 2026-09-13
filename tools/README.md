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

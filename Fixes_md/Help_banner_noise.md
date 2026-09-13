# Shrinking the "help commands" banners printed on import

**Date:** 2026-09-13
**Touches:** twelve modules under `jove/`, plus `tools/compact_help_banners.py`.

---

## The symptom

A notebook's four setup imports printed **47 lines** before it did anything:

```
You may use any of these help commands:
help(md2mc)
.. and if you want to dig more, then ..
help(default_line_attr)
help(length_ok_input_items)
...
```

Twelve modules each opened with a block like that — **125 printed lines across the
library** — and every one of them conveys a single fact: help exists.

## The change

Each block becomes one statement naming the same functions:

```
help(<fn>) is available for: mkp_dfa, mk_dfa, totalize_dfa,
    addtosigma_dfa, step_dfa, run_dfa, accepts_dfa, comp_dfa, flTup,
    union_dfa, intersect_dfa, pruneUnreach, iso_dfa, langeq_dfa, ...
```

| | before | after |
|---|---:|---:|
| printed lines, whole library | 125 | 29 |
| a typical notebook's imports | 47 | 11 |

Wrapping is done at patch time and baked in as a string literal, so the modules gain
no runtime import and the text never wraps mid-name.

Two details kept:

* `Def_md2mc` and `Def_md2mc_chatty` split their list with
  `.. and if you want to dig more, then ..`, separating the one function you actually
  call from the internals. That becomes `; internals: ...`.
* `Animate*` and `JoveEditor` print a one-line help *sentence*, not a list. Already
  short, left alone.

## It exposed two real bugs

Checking the advertised names against what the modules actually define turned up two
that do not exist — so `help()` on them had always failed:

| advertised | actual |
|---|---|
| `help(addtosigma_delta)` | `addtosigma_dfa` |
| `help(suvivor_id)` | `survivor_id` |

Both were pre-existing typos in Jove's own banners, faithfully carried over by the
first pass of the rewrite. Fixed, and `compact_help_banners.py` now **warns when a
banner names something the module does not define** — a banner that promises help on a
name is worth checking against reality.

This is the same lesson as the font-awesome work (`Font_awesome_fix.md`): verifying
that a change was *applied* is not the same as verifying it is *correct*. The check
that mattered here was `hasattr(module, name)` for every advertised name, not "did the
text get replaced".

## Not changed

`jove/PcpJupyter.py` does not parse at all — `TabError: inconsistent use of tabs and
spaces`. That is pre-existing (the committed version fails identically) and unrelated
to this work, so it was left alone. Worth a separate look.

## Reverting

```sh
git revert <commit>
```

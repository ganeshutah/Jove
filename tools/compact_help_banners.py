#!/usr/bin/env python3
"""Collapse Jove's multi-line "help commands" banners into one line each.

Importing a handful of Jove modules printed 47 lines of banner before a
notebook did anything, because twelve modules each open with

    print('''You may use any of these help commands:
    help(mk_dfa)
    help(totalize_dfa)
    ... one line per function ...
    ''')

125 printed lines across the library, all of which say the same thing: help
exists.  This rewrites each block as a single statement naming the same
functions:

    help(<fn>) is available for: mk_dfa, totalize_dfa, step_dfa, run_dfa,
        accepts_dfa, comp_dfa, union_dfa, ...

Wrapping is done here, at patch time, and baked in as a string literal, so
the modules gain no runtime import and the output does not wrap mid-name.

Two details preserved:

  * Def_md2mc and Def_md2mc_chatty split their list with the line
    ".. and if you want to dig more, then ..", separating the one function
    you actually call from the internals.  That distinction is kept as
    "; internals: ...".
  * The Animate* and JoveEditor modules print a one-line help SENTENCE, not
    a list.  They are already short and are left alone.

Idempotent.  Dry run by default; --write to apply.  Git is the revert path.
"""
import argparse, glob, os, re, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
JOVE = os.path.abspath(os.path.join(HERE, '..', 'jove'))

BLOCK = re.compile(
    r"print\('''\s*You may use any of these help commands:\s*\n(.*?)'''\s*\)", re.S)
HELPLINE = re.compile(r'^\s*help\((\w+)\)\s*$')


def compact(body):
    """Turn the block body into (primary fns, internal fns)."""
    primary, internals, seen_split = [], [], False
    for line in body.split('\n'):
        if not line.strip():
            continue
        m = HELPLINE.match(line)
        if m:
            (internals if seen_split else primary).append(m.group(1))
        else:
            seen_split = True          # the "dig more" separator
    return primary, internals


def render(primary, internals):
    text = 'help(<fn>) is available for: ' + ', '.join(primary)
    if internals:
        text += '; internals: ' + ', '.join(internals)
    lines = textwrap.wrap(text, width=76, subsequent_indent='    ')
    if len(lines) == 1:
        return 'print("%s")' % lines[0]
    body = '\n      '.join('"%s\\n"' % l if i < len(lines) - 1 else '"%s"' % l
                           for i, l in enumerate(lines))
    return 'print(%s)' % body


def verify(mod_path, names):
    """Warn about advertised names the module does not actually define.

    Jove's original banners carried two such typos -- help(addtosigma_delta)
    for addtosigma_dfa, and help(suvivor_id) for survivor_id -- so a banner
    that promises help on a name is worth checking against reality.
    """
    src = open(mod_path, encoding='utf-8').read()
    defined = set(re.findall(r'^\s*(?:def|class)\s+(\w+)', src, re.M))
    defined |= set(re.findall(r'^(\w+)\s*=', src, re.M))
    return [n for n in names if n not in defined]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    a = ap.parse_args()

    total_before = total_after = touched = 0
    for f in sorted(glob.glob(os.path.join(JOVE, '*.py'))):
        src = open(f, encoding='utf-8').read()
        blocks = list(BLOCK.finditer(src))
        if not blocks:
            continue
        new = src
        for m in reversed(blocks):
            primary, internals = compact(m.group(1))
            before = len([l for l in m.group(1).split('\n') if l.strip()]) + 1
            repl = render(primary, internals)
            after = repl.count('\n') + 1
            total_before += before
            total_after += after
            new = new[:m.start()] + repl + new[m.end():]
        touched += 1
        unknown = verify(f, primary + internals)
        print("  %-24s %2d fns: %2d printed lines -> %d%s"
              % (os.path.basename(f), len(primary) + len(internals), before, after,
                 "   WARNING advertises undefined: %s" % unknown if unknown else ""))
        if a.write and new != src:
            open(f, 'w', encoding='utf-8').write(new)

    print()
    print("%s %d modules: %d printed lines -> %d"
          % ('patched' if a.write else 'would patch', touched,
             total_before, total_after))
    if not a.write:
        print("(dry run -- pass --write to apply)")


if __name__ == '__main__':
    main()

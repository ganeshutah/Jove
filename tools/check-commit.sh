#!/bin/sh
# Refuse to let a mechanical sweep ride along with feature work.
# See PLAN.md.  Run before committing; exits non-zero if the staged
# change looks like two different changes wearing one message.
#
#   ./tools/check-commit.sh
#
# The fingerprint of a sweep is a file whose ENTIRE change is one line
# replaced by one line.  A handful of those is normal.  Two hundred of
# them next to a dozen real files is a feature commit with a repo-wide
# renumbering hidden inside it.
#
# Renames are detected (-M) and excluded from the count: moving a tree
# and fixing the references the move broke is ONE change, and splitting
# it would leave a commit in between where nothing works.

set -e
all=$(git diff --cached --numstat -M)
[ -n "$all" ] || { echo "nothing staged"; exit 0; }

renamed=$(printf '%s\n' "$all" | grep -c ' => ' || true)
stat=$(printf '%s\n' "$all" | grep -v ' => ' || true)

if [ -z "$stat" ]; then
    printf 'staged: %d files, all of them renames -- one change\n' "$renamed"
    exit 0
fi

total=$(printf '%s\n' "$stat" | grep -c .)
sweep=$(printf '%s\n' "$stat" | awk '$1==1 && $2==1' | grep -c . || true)
real=$((total - sweep))

printf 'staged: %d renamed, %d other (%d one-line, %d substantive)\n' \
       "$renamed" "$total" "$sweep" "$real"

if [ "$sweep" -ge 20 ] && [ "$sweep" -gt "$real" ]; then
    echo
    echo "STOP -- this looks like two commits:"
    echo
    printf '  %d files changed by a single line each:\n' "$sweep"
    printf '%s\n' "$stat" | awk '$1==1 && $2==1 {print "      " $3}' | head -5
    [ "$sweep" -gt 5 ] && printf '      ... and %d more\n' "$((sweep - 5))"
    echo
    printf '  %d files with substantive changes:\n' "$real"
    printf '%s\n' "$stat" | awk '!($1==1 && $2==1) {print "      " $3}' | head -8
    echo
    echo "Commit the sweep separately, with a subject that names it."
    echo "  git restore --staged <the sweep files>   # then commit the real work"
    exit 1
fi
echo "ok -- one coherent change"

#!/bin/bash
# gorefuse616.sh - S15r2 (HPP-616), Red Team: go_s15.sh (disk copy, ROOT -> the scratch base) with a stub sc_s15.py whose
# --seal-path prints the given path; DRY=2 (the plan right after the lock check, before any lock or game).
# usage: gorefuse616.sh <scratch base> <go_s15.sh under test>
B=$1
GO=$2
rm -rf "$B"; mkdir -p "$B/s15" "$B/pred"
sed -e "s#^ROOT=C:/kyty/s288\$#ROOT=$B#" "$GO" > "$B/s15/go_s15.sh"
grep -n '^ROOT=' "$B/s15/go_s15.sh"
for SP in pred/14_s.md pred/14b_s.md pred/15_s.md pred/15b_s.md pred/16_s.md pred/16b_s.md pred/13_s.md; do
  printf 'import sys\na = sys.argv[1:]\nif a[:1] == ["--seal-path"]:\n    print("%s")\n    sys.exit(0)\nprint("s15 lvl T u 300 - 100 600 1 0 -")\nsys.exit(0)\n' "$SP" > "$B/s15/sc_s15.py"
  OUT=$(DRY=2 bash "$B/s15/go_s15.sh" u_01 2>&1); RC=$?
  echo "$SP -> rc $RC | $(echo "$OUT" | grep -v "could not find /tmp" | head -1 | cut -c1-120)"
done
[ -e C:/kyty/SEALED_RUN.lock ] && echo "lock exists after (foreign?)" || echo "no lock after"

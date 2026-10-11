#!/bin/bash
# F40b2 (HPP-786, Red Team): one mutant binary of KYTY_FIX_F24 for the F40c tags (ROADMAP s122 item 696(b)(5)).
# Worktree C:/kyty/f287/f40b2/wt back to the F40a2 tree 7c38e497 (detached, clean), mut_f40b.py apply <m>, a detached
# commit of the mutant (worktree only - no branch, main untouched; the version string then names the mutant commit),
# reconfigure (SDL_REVISION takes the describe at configure), incremental build under the watchdog (bstep.sh, 540 s steps), pinned copy bin/kyty_emulator_<sha8>.exe, version and
# string counts, the worktree back to 7c38e497 and git status = 0.
# Usage: mut_one_f40b2.sh <m>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f40b2 || exit 1
G="/c/Program Files/Git/cmd/git.exe"
M=$1
"$G" -C wt checkout -q --detach 7c38e497 || exit 9
[ "$("$G" -C wt status --short --ignore-submodules=all | wc -l)" = 0 ] || { echo "worktree not clean"; exit 9; }
python mut_f40b.py apply $M C:/kyty/f287/f40b2/wt || exit 9
"$G" -C wt diff > mut_$M.diff
"$G" -C wt diff --stat | tail -1
export GIT_AUTHOR_NAME="Red Team" GIT_AUTHOR_EMAIL="red-team@kyty.local" GIT_COMMITTER_NAME="Red Team" GIT_COMMITTER_EMAIL="red-team@kyty.local"
"$G" -C wt commit -q -a -m "MUTANT $M (F40b2, HPP-786): mutant of KYTY_FIX_F24 for the F40c tag f24_$M - worktree only, never in main (ROADMAP s122 item 696(b)(5))" || exit 9
C=$("$G" -C wt rev-parse HEAD)
echo "$(date -u +%FT%TZ) F40b2 mutant $M commit ${C:0:8} diff $(sha256sum mut_$M.diff | cut -c1-8)" >> times.txt
bash bstep.sh mut_${M}_cfg configure > /dev/null 2>&1 || { echo "configure failed"; exit 9; } # SDL_REVISION is set at configure (one version string, as F40a2)
RC=1
for i in 1 2 3 4 5 6; do
  [ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; break; }
  bash bstep.sh mut_${M}_$i > /dev/null 2>&1; RC=$?
  echo "build step $i rc=$RC"
  [ $RC = 6 ] || break
done
if [ $RC = 0 ]; then
  H=$(sha256sum build/install/kyty_emulator.exe | cut -c1-64)
  cp build/install/kyty_emulator.exe bin/kyty_emulator_${H:0:8}.exe
  python - "bin/kyty_emulator_${H:0:8}.exe" "$M" "$C" "$H" > bin_$M.out.txt <<'PYEOF'
import re, sys
p, m, c, h = sys.argv[1:5]
b = open(p, 'rb').read()
v = sorted(set(x.decode() for x in re.findall(rb'KytyPS5-2026-[0-9A-Za-z.\-]+', b)))
print('mutant', m, 'commit', c, 'sha256', h, 'size', len(b), 'version', v)
for s in [b'9177b4267de1fb8bac7d1113afd8733210addfac', b'FixF24: init_owner hid=', b'FixF24: mode=', b'flap_life_min_us=',
          b'jp_scan_gap_max_us=', b'FixF24: open failed index=', b'FixF24: open failed instance=']:
    print(s.decode(), b.count(s))
PYEOF
  cat bin_$M.out.txt
  echo "$(date -u +%FT%TZ) F40b2 mutant $M binary ${H:0:8} pinned bin/kyty_emulator_${H:0:8}.exe out $(sha256sum bin_$M.out.txt | cut -c1-8)" >> times.txt
fi
"$G" -C wt checkout -q --detach 7c38e497
echo "worktree HEAD $("$G" -C wt rev-parse --short HEAD) status lines $("$G" -C wt status --short --ignore-submodules=all | wc -l)"
exit $RC

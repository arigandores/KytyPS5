#!/bin/bash
# F35b (HPP-756): configure, unmutated build and run, then mutants m1a m1b m2 m3 m4 m5 (apply, build, run at
# KYTY_FIX_F19=0/1, revert). Guard (lock, STOP, series HPP-752) before every build. Output -> run_all.log.
cd C:/kyty/f287/f35b || exit 1
G() { bash C:/kyty/f287/f35b/guard.sh || { echo "GUARD HALT before $1"; exit 7; }; }
B() { cmd //c "C:\\kyty\\f287\\f35b\\build_f35b.cmd tests" > "build_$1.log" 2>&1; local rc=$?; echo "build $1 rc=$rc"; echo "$(date -u +%FT%TZ) build $1 rc=$rc $(sha256sum build/shader_cfg_tests.exe | cut -c1-8)" >> times.txt; return $rc; }
STAGE=${1:-all}
if [ "$STAGE" = all ] || [ "$STAGE" = base ]; then
  G configure
  [ -f build/build.ninja ] || { cmd //c "C:\\kyty\\f287\\f35b\\build_f35b.cmd configure" > cfg.log 2>&1; echo "configure rc=$?"; }
  G base; B base && python mut_f35b.py run base
  echo "$(date -u +%FT%TZ) run base" >> times.txt
fi
if [ "$STAGE" = all ] || [ "$STAGE" = mut ]; then
  for m in m1a m1b m2 m3 m4 m5; do
    G $m
    python mut_f35b.py apply $m || exit 2
    if B $m; then python mut_f35b.py run $m; else echo "$m BUILD FAILED"; fi
    echo "$(date -u +%FT%TZ) run $m" >> times.txt
    python mut_f35b.py revert || exit 3
  done
  G final; B final && python mut_f35b.py run final
  echo "$(date -u +%FT%TZ) run final (reverted)" >> times.txt
fi
echo RUN_ALL DONE

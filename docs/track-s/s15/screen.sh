#!/bin/bash
# S15a: a screen of named mutants (mutlib --only, NOT the counted run); one batch per call, < 60 s (general rule 30)
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 5; }
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/s288/s15 || exit 1
python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s288/s15/sc_s15.py \
  --test C:/kyty/s288/s15/test_sc_s15.py --mutants C:/kyty/s288/s15/mut_sc_s15.py --no-memo --workers 12 --only "$1" \
  --work-dir C:/kyty/s288/s15/mutwork_screen --cache-dir C:/kyty/s288/s15/mutcache_screen --out C:/kyty/s288/s15/screen_$2.txt \
  > screen_$2.log 2>&1
echo "rc $?"; grep -v "KILLED" screen_$2.txt | tail -8

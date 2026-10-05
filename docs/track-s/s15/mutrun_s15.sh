#!/bin/bash
# S15a (HPP-601, item 511 (z)): the COUNTED full mutant run of sc_s15.py on the final text; writes its times line and the file
# mutrun_s15.done when it ends (the caller waits in steps of at most 540 s).
export PATH=/usr/bin:/mingw64/bin:$PATH
export PYTHONIOENCODING=utf-8
cd C:/kyty/s288/s15 || exit 1
rm -f mutrun_s15.done
S=$(date +%s)
python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s288/s15/sc_s15.py \
  --test C:/kyty/s288/s15/test_sc_s15.py --mutants C:/kyty/s288/s15/mut_sc_s15.py --control --no-memo --workers 12 \
  --work-dir C:/kyty/s288/s15/mutwork --cache-dir C:/kyty/s288/s15/mutcache --out C:/kyty/s288/s15/mut_sc_s15.txt \
  > mut_sc_s15.log 2>&1
RC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) COUNTED full mutant run rc $RC wall $(( $(date +%s) - S )) s: $(tail -1 mut_sc_s15.log); mut_sc_s15.txt sha256 $(sha256sum mut_sc_s15.txt | cut -c1-64)" >> times.txt
echo "rc $RC" > mutrun_s15.done

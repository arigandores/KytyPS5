#!/bin/bash
# S13a4 (HPP-553, item 452 (d)(3)): the COUNTED full mutant run of sc_s13.py on the final text; writes its times line and the
# file mutrun4.done when it ends (the caller waits in steps of at most 540 s).
export PATH=/usr/bin:/mingw64/bin:$PATH
export PYTHONIOENCODING=utf-8
cd C:/kyty/s288/s13 || exit 1
rm -f mutrun4.done
S=$(date +%s)
python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s288/s13/sc_s13.py \
  --test C:/kyty/s288/s13/test_sc_s13.py --mutants C:/kyty/s288/s13/mut_sc_s13.py --control --no-memo --workers 12 \
  --work-dir C:/kyty/s288/s13/mutwork --cache-dir C:/kyty/s288/s13/mutcache --out C:/kyty/s288/s13/mut_sc_s13.txt \
  > mut_sc_s13.log 2>&1
RC=$?
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) COUNTED full mutant run rc $RC wall $(( $(date +%s) - S )) s: $(tail -1 mut_sc_s13.log); mut_sc_s13.txt sha256 $(sha256sum mut_sc_s13.txt | cut -c1-64)" >> times.txt
echo "rc $RC" > mutrun4.done

#!/bin/bash
# s146 step 0 (HPP-386; ROADMAP p.314): the ONE counted full mutant run of sc146.py, --workers 16, own work/cache dirs.
export PATH=/usr/bin:/mingw64/bin:$PATH
cd C:/kyty/s146
T=C:/kyty/s146/step0/times.txt
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) step0 counted full mutant run start (796 mutants + 3 controls, --workers 16, run 2 after p.314(g); forecast ~900 s (run 1 wall 896.8 s); sc146.py $(sha256sum sc146.py | cut -c1-16) test_sc146.py $(sha256sum test_sc146.py | cut -c1-16) mut_sc146.py $(sha256sum mut_sc146.py | cut -c1-16))" >> $T
python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s146/sc146.py --test C:/kyty/s146/test_sc146.py --mutants C:/kyty/s146/mut_sc146.py --control --no-memo --workers 16 --work-dir C:/kyty/s146/mutwork --cache-dir C:/kyty/s146/mutcache --out C:/kyty/s146/mut_sc146.txt > C:/kyty/s146/step0/mut_run.log 2>&1
RC=$?
echo "rc=$RC" >> C:/kyty/s146/step0/mut_run.log
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) step0 counted full mutant run end rc $RC mut_sc146.txt sha256 $(sha256sum mut_sc146.txt | cut -c1-64): $(grep '^wall\|SURVIVORS\|ALL KILLED' mut_sc146.txt | tr '\n' ' ' | cut -c1-240)" >> $T

#!/bin/bash
# Track F link F16f (HPP-523): the reading of a made tag outside the lock: f16f_read.py rows and json (runs/<tag>/read.txt, read.json).
# Refuses under any lock (general rule 27) and with the stop file.  ASCII only.   usage: bash C:/kyty/f287/f16f/post_f16f.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f16f; D=$G/runs/$T
case "$T" in f5_sg|f5_ef|f5_bh|f5_eb|f5_sg0) ;; *) echo "usage: post_f16f.sh <f5_sg|f5_ef|f5_bh|f5_eb|f5_sg0>"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
python f16f_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F16f post_f16f $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), $(grep -h '^  CONTROL ' $D/read.txt | tr '\n' ';')" >> C:/kyty/f287/times.txt
cat $D/read.txt

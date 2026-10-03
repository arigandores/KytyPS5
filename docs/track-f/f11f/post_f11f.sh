#!/bin/bash
# F11f (HPP-468): the reading of one made tag outside the lock: f11f_read.py rows and read.json (runs/<tag>/).  Refuses under any lock
# (general rule 27) and with the stop file.  ASCII only.   usage: bash C:/kyty/f287/f11f/post_f11f.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f11f; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
python f11f_read.py --check-seal > $D/seal_check.txt 2>&1 || { echo "seal check FAIL"; cat $D/seal_check.txt; exit 1; }
python f11f_read.py $T --out $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F11f post_f11f $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -h '^WORD376 ' $D/read.txt | head -1 | cut -c1-120)" >> C:/kyty/f287/times.txt
cat $D/seal_check.txt $D/read.txt

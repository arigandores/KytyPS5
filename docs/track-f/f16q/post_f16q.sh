#!/bin/bash
# Track F link F16q (HPP-597): the reading of a made tag outside the lock.  Video tags: s51_vidglitch.py <rec> 4 6, the whole-video sheet
# sheet142.py and the first scene frame f16q_luma.py, written BEFORE the reader (the reader reads them); then f16q_read.py rows and json
# (runs/<tag>/read.txt, read.json).  'cmu' / 'f26' (after both arms of the pair): f16q_pair.py rows and the event sheets by present number
# (runs/pair_<cmu|f26>/pair.txt, pair.json, sheets/).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f16q/post_f16q.sh <tag|cmu|f26>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f16q
case "$T" in f16q_w|f5cmu_0b|f5cmu_1b|f26_0|f26_1|cmu|f26) ;; *) echo "usage: post_f16q.sh <tag|cmu|f26>"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
if [ "$T" = "cmu" ] || [ "$T" = "f26" ]; then
  if [ "$T" = "cmu" ]; then A=f5cmu_0b; B=f5cmu_1b; else A=f26_0; B=f26_1; fi
  [ -f runs/$A/read.json ] && [ -f runs/$B/read.json ] || { echo "read both arms first"; exit 2; }
  D=$G/runs/pair_$T; mkdir -p $D
  python f16q_pair.py $T --sheets $D/sheets --json $D/pair.json > $D/pair.txt 2>&1 || { echo "pair failed"; tail -3 $D/pair.txt; exit 1; }
  echo "$(u) F16q post_f16q pair $T: pair.txt $(sha256sum $D/pair.txt | cut -c1-16), $(head -1 $D/pair.txt | cut -c1-160)" >> C:/kyty/f287/times.txt
  grep -v '^    \|^  CMASK ITEM\|^  DCC ITEM' $D/pair.txt | head -40
  exit 0
fi
D=$G/runs/$T
[ -d $D ] || { echo "no $D"; exit 2; }
if [ "$T" != "f16q_w" ]; then
  REC=$G/rec_$T.mp4
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  python f16q_luma.py $REC $REC.idx > $D/luma.txt 2>&1
fi
python f16q_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F16q post_f16q $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), $(grep -h '^  CONTROL ' $D/read.txt | tr '\n' ';')" >> C:/kyty/f287/times.txt
grep -v '^  EVENT ' $D/read.txt

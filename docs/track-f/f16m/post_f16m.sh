#!/bin/bash
# Track F link F16m (HPP-585): the reading of a made tag outside the lock.  Pair arms (f5cmu_*): s51_vidglitch.py <rec> 4 6 and the whole-video
# sheet sheet142.py, written BEFORE the reader (the reader reads them); then f16m_read.py rows and json (runs/<tag>/read.txt, read.json).
# 'pair' (after both arms): f16m_pair.py rows and the event sheets by present number (runs/pair/pair.txt, runs/pair/sheets/).  Refuses
# under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f16m/post_f16m.sh <tag|pair>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f16m; D=$G/runs/$T
case "$T" in f5cmu_0|f5cmu_1|f5id_sg|f5id_ef|f5id_bh|f5id_eb|pair) ;; *) echo "usage: post_f16m.sh <tag|pair>"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
if [ "$T" = "pair" ]; then
  [ -f runs/f5cmu_0/read.json ] && [ -f runs/f5cmu_1/read.json ] || { echo "read both arms first"; exit 2; }
  mkdir -p $D
  python f16m_pair.py --sheets $D/sheets --json $D/pair.json > $D/pair.txt 2>&1 || { echo "pair failed"; tail -3 $D/pair.txt; exit 1; }
  echo "$(u) F16m post_f16m pair: pair.txt $(sha256sum $D/pair.txt | cut -c1-16), $(head -1 $D/pair.txt | cut -c1-160)" >> C:/kyty/f287/times.txt
  cat $D/pair.txt
  exit 0
fi
[ -d $D ] || { echo "no $D"; exit 2; }
case "$T" in f5cmu_*)
  REC=$G/rec_$T.mp4
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1;;
esac
python f16m_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F16m post_f16m $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), $(grep -h '^  CONTROL ' $D/read.txt | tr '\n' ';')" >> C:/kyty/f287/times.txt
cat $D/read.txt

#!/bin/bash
# Track F link F14g (HPP-507): the reading of one made tag outside the lock (port of F12f post_f12f.sh): f14g_read.py rows and json; the
# video tags (f19_v1, f19_ef) also s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the
# reader (the reader reads them); f19_rd also the structured read WITHOUT REPLAY of every capture f19_rd_kNN.rdc by the F14c reader
# C:/kyty/f287/f14c/rd_cmp_f14c.py through C:/kyty/f287/f14c/rdrun_f14c.sh (watchdog RDW s, default 240; the lock or the stop file
# appearing kills qrenderdoc by its pid) into rdcmp_f19_rd_kNN.txt, one times.txt line per capture at the event (F14d item 409 (a):
# deviation of F14c parked to the next capture-reader link).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f14g/post_f14g.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f14g; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
case "$T" in
  f19_v1|f19_ef) REC=$G/rec_$T.mp4
    python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
    python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1;;
  f19_rd)
    for C in $G/f19_rd_k*.rdc; do
      [ -f "$C" ] || continue
      KK=$(basename $C .rdc | sed 's/^f19_rd_k//')
      [ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock appeared - stop reading"; exit 3; }
      [ -e C:/kyty/f287/STOP ] && { echo "$(u) F14g post_f14g STOP file seen before the read of k$KK: $(head -1 C:/kyty/f287/STOP)" >> C:/kyty/f287/times.txt; exit 4; }
      echo "$(u) F14g post_f14g read start k$KK (rd_cmp_f14c.py, no replay) $(basename $C)" >> C:/kyty/f287/times.txt
      bash C:/kyty/f287/f14c/rdrun_f14c.sh C:/kyty/f287/f14c/rd_cmp_f14c.py "C:/kyty/f287/f14g/f19_rd_k$KK.rdc" "$G/rdcmp_f19_rd_k$KK.txt" ${RDW:-240} > $D/rdrun_k$KK.out.txt 2>&1
      RR=$?
      echo "$(u) F14g post_f14g read end k$KK rc $RR: $(tail -1 $D/rdrun_k$KK.out.txt | cut -c1-120); $(grep '^SUMMARY' $G/rdcmp_f19_rd_k$KK.txt 2>/dev/null | cut -c1-200)" >> C:/kyty/f287/times.txt
    done;;
esac
python f14g_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F14g post_f14g $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3

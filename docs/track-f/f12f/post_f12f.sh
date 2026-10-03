#!/bin/bash
# Track F link F12f (HPP-480): the reading of one made tag outside the lock (form of FS4c post_fs4c.sh): f12f_read.py rows and json; the
# video tags (f12_v, f12_vw, f12_bh) also s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the
# reader (the reader reads them).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f12f/post_f12f.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f12f; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
case "$T" in
  f12_v|f12_vw|f12_bh) REC=$G/rec_$T.mp4
    python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
    python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1;;
esac
python f12f_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F12f post_f12f $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3

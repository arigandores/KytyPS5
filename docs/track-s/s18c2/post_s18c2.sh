#!/bin/bash
# Track S link S18c2 (HPP-654; derived from S18c post_s18c.sh; the tag s18_w2 has no video, reader s18c2_read.py): the reading of one made tag outside the lock (port of F20c post_f20c.sh): the video tags (form v: s17c_v0,
# s17c_c2, s17c_n0, s17c_e3) get s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader
# (the reader reads them); then s17c_read.py rows and json (runs/<tag>/read.json) and the member table s17c_read.py --table (table.txt).
# Tags are read in the order of go_s17c.sh (a later tag reads the read.json of s17c_c2, s17c_n0, s17c_r3).  Refuses under any lock
# (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/s288/s18c2/post_s18c2.sh s18_w2
export PATH=/usr/bin:/mingw64/bin:$PATH
export PYTHONIOENCODING=utf-8
T=$1; G=C:/kyty/s288/s18c2; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/s288/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
case "$T" in
  s18_e1|s18_e2|s18_v)
    REC=$G/rec_$T.mp4
    python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
    python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1;;
esac
python s18c2_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python s18c2_read.py --table > $G/table.txt 2>&1
echo "$(u) S18c2 post_s18c2 $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -h '^  READING' $D/read.txt | head -1), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> $G/times.txt
cat $D/read.txt

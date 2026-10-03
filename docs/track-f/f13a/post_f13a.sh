#!/bin/bash
# F13a (HPP-479): the reading of one made tag outside the lock (form of FS4c post_fs4c.sh): for f13_k first s51_vidglitch.py <rec> 4 6,
# the lead sheet sheet142.py of the whole video, then the reader f13a_read.py (it reads the glitch and sheet outputs) and the press
# sheet press_sheet.py; for f13_rd the reader only.  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f13a/post_f13a.sh <f13_rd|f13_k>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f13a; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
if [ "$T" = "f13_k" ]; then
  REC=$G/rec_$T.mp4
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
fi
python f13a_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
if [ "$T" = "f13_k" ]; then
  python press_sheet.py $D/read.json $G/rec_$T.mp4 $D/presses_$T.png > $D/press_sheet.txt 2>&1
fi
echo "$(u) F13a post_f13a $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(tail -1 $D/read.txt | cut -c1-400); glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/sheet.txt $D/press_sheet.txt 2>/dev/null

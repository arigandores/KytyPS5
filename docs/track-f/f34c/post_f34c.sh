#!/bin/bash
# Track F link F34c (HPP-740; port of FS11c post_fs11c.sh): the reading of a made tag outside the lock.  Tags with a video (b6_v, b6_v2,
# b6_vl and repeats): s51_vidglitch.py <rec> 4 6 and the sheets of the room (sheets_f34c.py from the reader timeline; F34a (V4), item 676
# (v)) are written BEFORE the reader reads them; the whole-video sheet sheet142.py - reference.  Then f34c_read.py rows and json, and the
# table.  No tempo member (the items do not name one for the cutscene).  Refuses under any lock (general rule 27) and with the stop file.
# ASCII only.
# usage: bash C:/kyty/f287/f34c/post_f34c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f34c; D=$G/runs/$T
case "$T" in
  b6_w0|b6_v|b6_v2|b6_vl|b6_w|b6_wl|b6_w0_r[1-4]|b6_v_r[1-4]|b6_v2_r[1-4]|b6_vl_r[1-4]|b6_w_r[1-4]|b6_wl_r[1-4]) ;;
  *) echo "usage: post_f34c.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_whole_$T.png > $D/sheet_whole.txt 2>&1
  python f34c_read.py --timeline $T > $D/timeline.json 2> $D/timeline.err
  python sheets_f34c.py $REC $D/timeline.json $D $T > $D/sheet.txt 2>&1
fi
python f34c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f34c_read.py --table > $G/table.txt 2>&1
echo "$(u) F34c post_f34c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|READING)' $D/read.txt | tr '\n' ';' | cut -c1-300), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1), sheets: $(tail -1 $D/sheet.txt 2>/dev/null)" >> C:/kyty/f287/times.txt
cat $D/read.txt; head -3 $D/glitch.txt 2>/dev/null; cat $D/sheet.txt 2>/dev/null | cut -c1-300
exit 0

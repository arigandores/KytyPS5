#!/bin/bash
# Track F link F15e (HPP-516): the reading of the made tag b4_v outside the lock (form of FS5c post_fs5c.sh): s51_vidglitch.py <rec> 4 6
# and the lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); the pair image
# pair_b4_v_fs5_v.png = the sheet of b4_v left of the sheet of fs5_v (FS5c, C:/kyty/f287/fs5/fs5c/runs/fs5_v/sheet_fs5_v.png; a variant of
# the executor for the lead's look, not a reader input); then f15e_read.py rows and json.  Refuses under any lock (general rule 27) and
# with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f15e/post_f15e.sh b4_v
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f15e; D=$G/runs/$T
[ "$T" = "b4_v" ] || { echo "usage: post_f15e.sh b4_v"; exit 2; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
if [ -f $D/sheet_$T.png ]; then
  ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/fs5/fs5c/runs/fs5_v/sheet_fs5_v.png \
    -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_b4_v_fs5_v.png > $D/pair.txt 2>&1 \
    && echo "pair: $D/pair_b4_v_fs5_v.png (left b4_v, right fs5_v)" >> $D/pair.txt
fi
python f15e_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F15e post_f15e $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null

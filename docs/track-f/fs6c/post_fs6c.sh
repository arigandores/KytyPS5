#!/bin/bash
# Track F link FS6c (HPP-557): the reading of a made tag outside the lock (form of F15e post_f15e.sh).  fs6_v: s51_vidglitch.py <rec> 4 6
# and the lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); the pair image pair_fs6_v_b4_v.png =
# the sheet of fs6_v left of the sheet of b4_v (F15e, C:/kyty/f287/f15e/runs/b4_v/sheet_b4_v.png; item 454 (g)(3) 'the lead sheet beside
# b4_v'); fs6_w: no video.  Then fs6c_read.py rows and json.  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/fs6c/post_fs6c.sh <fs6_v|fs6_w>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs6c; D=$G/runs/$T
case "$T" in fs6_v|fs6_w) ;; *) echo "usage: post_fs6c.sh <fs6_v|fs6_w>"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
if [ "$T" = "fs6_v" ]; then
  REC=$G/rec_$T.mp4
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  if [ -f $D/sheet_$T.png ]; then
    ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/f15e/runs/b4_v/sheet_b4_v.png \
      -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_fs6_v_b4_v.png > $D/pair.txt 2>&1 \
      && echo "pair: $D/pair_fs6_v_b4_v.png (left fs6_v, right b4_v)" >> $D/pair.txt
  fi
fi
python fs6c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) FS6c post_fs6c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null

#!/bin/bash
# Track F link FS9c (HPP-673; port of F24e post_f24e.sh: tags fs9_v / fs9_w, the pair image is the sheet of fs9_v left of the sheet of
# b13_v (F24e, item 604 (d)(3): the lead sheet beside b13_v); item 604 (g) debt: pair.txt is read only in the form v, the last command
# is exit 0).  Track F link F24e (HPP-664): the reading of a made tag outside the lock (form of F15e post_f15e.sh).  Form v (b13_v): s51_vidglitch.py
# <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); the pair image
# pair_b13_v_b4_v.png = the sheet of b13_v left of the sheet of b4_v (F15e, the same V form on S12; a variant of the executor for the lead's
# look, not a reader input).  Form w (b13_w): no video.  Then f24e_read.py rows and json.  Refuses under any lock (general rule 27) and with
# the stop file.  ASCII only.
# usage: bash C:/kyty/f287/fs9c/post_fs9c.sh fs9_v|fs9_w[_r1..3]
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs9c; D=$G/runs/$T
case "$T" in
  fs9_v|fs9_v_r[1-3]) FORM=v;;
  fs9_w|fs9_w_r[1-3]) FORM=w;;
  *) echo "usage: post_fs9c.sh fs9_v|fs9_w[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
if [ $FORM = v ]; then
  REC=$G/rec_$T.mp4
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  if [ -f $D/sheet_$T.png ]; then
    ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/f24e/runs/b13_v/sheet_b13_v.png \
      -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_${T}_b13_v.png > $D/pair.txt 2>&1 \
      && echo "pair: $D/pair_${T}_b13_v.png (left $T, right b13_v)" >> $D/pair.txt
  fi
fi
python fs9c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) FS9c post_fs9c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), ROWS NO/NOT_READ: $(grep -c ': NO$\|: NOT_READ$' $D/read.txt), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt
if [ $FORM = v ]; then head -3 $D/glitch.txt 2>/dev/null; cat $D/pair.txt 2>/dev/null; fi
exit 0

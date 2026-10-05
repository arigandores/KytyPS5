#!/bin/bash
# Track F link FS8c (HPP-573): the reading of one made tag outside the lock (port of F14g post_f14g.sh without the rd branch): the video tags
# (fs8_v, fs8_ef) get s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader
# reads them), and the pair sheet for the lead: the new sheet over the sheet of the same form of F14g (fs8_v over f19_v1, fs8_ef over f19_ef;
# item 471 (g)(3) 'sheet of the lead against f19_v1 / f19_ef'); then fs8c_read.py rows and json.  Refuses under any lock (general rule 27) and
# with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/fs8c/post_fs8c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs8c; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
case "$T" in
  fs8_v|fs8_ef)
    REC=$G/rec_$T.mp4
    case "$T" in fs8_v) REF=C:/kyty/f287/f14g/runs/f19_v1/sheet_f19_v1.png; RT=f19_v1;; fs8_ef) REF=C:/kyty/f287/f14g/runs/f19_ef/sheet_f19_ef.png; RT=f19_ef;; esac
    python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
    python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
    if [ -f $D/sheet_$T.png ] && [ -f $REF ]; then
      ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i $REF -filter_complex "[0:v][1:v]vstack" \
        -q:v 3 $D/pair_${T}_over_$RT.jpg > $D/pair.txt 2>&1
      echo "pair: $D/pair_${T}_over_$RT.jpg rc $? (top $T, bottom $RT)" >> $D/pair.txt
    else
      echo "pair: not made (sheet or reference missing)" >> $D/pair.txt
    fi;;
esac
python fs8c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) FS8c post_fs8c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -h '^  READING' $D/read.txt | head -1), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null

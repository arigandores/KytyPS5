#!/bin/bash
# FS3c (HPP-449): the reading of one made tag outside the lock (form of the F9g post-processing): fs3_read.py rows and json,
# s51_vidglitch.py <rec> 4 6 (video tags), sheets (u/u0/pu: sheets_f9d.py with the phases of F9g; v/hb: the lead sheet sheet142.py and
# 1 frame/s of the whole video), pairs u0 (left) / u (right) of the rotation phase and of the first 36 cells of the static phase when
# both videos exist.  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/fs3/fs3c/post_fs3.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs3/fs3c; D=$G/runs/$T
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
python fs3_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
case "$T" in
  fs3_u|fs3_u0|fs3_u0r|fs3_pu) REC=$D/rec.mp4; P=${T#fs3_}
    python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
    python sheets_f9d.py $REC $D/sheets $P 3840 5850 5950 > $D/sheets.txt 2>&1;;
  fs3_v|fs3_hb) REC=$G/rec_$T.mp4
    python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
    python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
    python sheets_f9d.py $REC $D/sheets ${T#fs3_} 99999999 99999999 99999999 > $D/sheets.txt 2>&1;;
  fs3_w) : ;;
esac
if [ "$T" = "fs3_u0" ] || [ "$T" = "fs3_u0r" ] || [ "$T" = "fs3_u" ]; then
  L=$G/runs/fs3_u0r/rec.mp4; [ -f $L ] || L=$G/runs/fs3_u0/rec.mp4; R=$G/runs/fs3_u/rec.mp4
  if [ -f $L ] && [ -f $R ]; then
    mkdir -p $G/runs/cmp
    python cmp_sheets.py $L $R $G/runs/cmp cmp_u0_u_rot 3840 5850 > $G/runs/cmp/cmp_rot.txt 2>&1
    python cmp_sheets.py $L $R $G/runs/cmp cmp_u0_u_static 5950 6490 > $G/runs/cmp/cmp_static.txt 2>&1
  fi
fi
echo "$(u) post_fs3 $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/fs3/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3

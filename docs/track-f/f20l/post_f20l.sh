#!/bin/bash
# Track F link F20l (HPP-631): the reading of a made tag outside the lock (form of F20e post_f20e.sh): s51_vidglitch.py <rec> 4 6 and the
# lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); then b32_read.py rows and json (no theta:
# HOST_LOAD is not issued in the controls, item 550 (d)(6)), then the table b32_read.py --table.  Refuses under any lock (general rule 27)
# and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f20l/post_f20l.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f20l; D=$G/runs/$T
case "$T" in
  b32_z0|b32_pp|b32_pc|b32_pd|b32_pd2|b32_z0_r[1-6]|b32_pp_r[1-6]|b32_pc_r[1-6]|b32_pd_r[1-6]|b32_pd2_r[1-6]) ;;
  *) echo "usage: post_f20l.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
python b32_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python b32_read.py --table > $G/table.txt 2>&1
echo "$(u) F20l post_f20l $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep '^  ADMISSION' $D/read.txt | head -1), $(grep '^  K_I' $D/read.txt | head -1 | cut -c1-120), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt | head -60; cat $D/glitch.txt 2>/dev/null | head -3

#!/bin/bash
# Track F link F20l2 (HPP-648): the reading of a made tag outside the lock (form of F20e post_f20e.sh): s51_vidglitch.py <rec> 4 6 and the
# lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); then b32_read.py rows and json (theta_load
# from the seal, item 574 (b)(6), (e)), then the table b32_read.py --table.  Refuses under any lock (general rule 27)
# and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f20l2/post_f20l2.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f20l2; D=$G/runs/$T
case "$T" in
  b32_z0b|b32_ppb|b32_pcb|b32_z0b_r[1-6]|b32_ppb_r[1-6]|b32_pcb_r[1-6]) ;;
  *) echo "usage: post_f20l2.sh <tag>"; exit 2;;
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
echo "$(u) F20l2 post_f20l2 $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep '^  ADMISSION' $D/read.txt | head -1), $(grep '^  K_I' $D/read.txt | head -1 | cut -c1-120), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt | head -60; cat $D/glitch.txt 2>/dev/null | head -3

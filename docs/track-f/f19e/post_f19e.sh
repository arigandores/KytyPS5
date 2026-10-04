#!/bin/bash
# Track F link F19e (HPP-549): the reading of a made tag outside the lock (form of F18e post_f18e.sh): s51_vidglitch.py <rec> 4 6 and the
# lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); then f19e_read.py rows and json.  Refuses
# under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f19e/post_f19e.sh b24_h0|b24_s0|b24_h1|b24_d0|b24_d1|b24_n1
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f19e; D=$G/runs/$T
case "$T" in b24_h0|b24_s0|b24_h1|b24_d0|b24_d1|b24_n1) ;; *) echo "usage: post_f19e.sh b24_h0|b24_s0|b24_h1|b24_d0|b24_d1|b24_n1"; exit 2;; esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
python f19e_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F19e post_f19e $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep '^  READING' $D/read.txt | head -1 | cut -c1-120), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3

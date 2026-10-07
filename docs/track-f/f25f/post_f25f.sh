#!/bin/bash
# Track F link F25f (HPP-669; port of F20l3 post_f20l3.sh): the reading of a made tag outside the lock - s51_vidglitch.py <rec> 4 6 and the
# lead sheet sheet142.py of the whole video, written BEFORE the reader; then f25_read.py rows and json (theta_load from the seal), the table
# (table.txt) and the series summary (series.txt: controls, levels, stop rule of item 596 (e), cold layer, U5, budget).  Refuses under any
# lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f25f/post_f25f.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f25f; D=$G/runs/$T
case "$T" in
  f25_c[12]|f25_z[12]|f25_p[bc]|f25_s0[1-9]|f25_s[1-3][0-9]|f25_s40|f25_k0[1-9]|f25_k10) ;;
  f25_c[12]_r[1-6]|f25_z[12]_r[1-6]|f25_p[bc]_r[1-6]|f25_s0[1-9]_r[1-6]|f25_s[1-3][0-9]_r[1-6]|f25_s40_r[1-6]|f25_k0[1-9]_r[1-6]|f25_k10_r[1-6]) ;;
  *) echo "usage: post_f25f.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
python f25_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f25_read.py --table > $G/table.txt 2>&1
python f25_read.py --series > $G/series.txt 2>&1
echo "$(u) F25f post_f25f $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep '^  ADMISSION' $D/read.txt | head -1), $(grep '^  K_I' $D/read.txt | head -1 | cut -c1-110), $(grep '^  CONTROL ' $D/read.txt | head -1), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1); $(grep '^LEVEL\|^CONTROLS\|^NEXT' $G/series.txt | tr '\n' ';' | cut -c1-300)" >> C:/kyty/f287/times.txt
head -40 $D/read.txt; grep -E '^    FRAME .*(IN COUNT|INSTR_MADE_K2|K2-ref)' $D/read.txt | head -10; grep -E '^  (CONTROL|    \[)' $D/read.txt | tail -12; cat $D/glitch.txt 2>/dev/null | head -3; grep -v '^  [pb][oa]' $G/series.txt

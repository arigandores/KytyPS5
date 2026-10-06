#!/bin/bash
# Track F link F20l3 (HPP-655): the reading of a made tag outside the lock (form of F20e post_f20e.sh): s51_vidglitch.py <rec> 4 6 and the
# lead sheet sheet142.py of the whole video, written BEFORE the reader (the reader reads them); then b32_read.py rows and json (theta_load
# from the seal, item 574 (b)(6)), the table b32_read.py --table, the PK-A summary --pka (pka.txt) and the series summary --series
# (series.txt; after the 10th admitted series tag also --series --upto 10 -> series10.txt, item 591 (g)(6)).  Refuses under any lock
# (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f20l3/post_f20l3.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f20l3; D=$G/runs/$T
case "$T" in
  b32_pa|b32_pa2|b32_s0[1-9]|b32_s[1-5][0-9]|b32_s60|b32_z0c[1-5]) ;;
  b32_pa_r[1-6]|b32_pa2_r[1-6]|b32_s0[1-9]_r[1-6]|b32_s[1-5][0-9]_r[1-6]|b32_s60_r[1-6]|b32_z0c[1-5]_r[1-6]) ;;
  *) echo "usage: post_f20l3.sh <tag>"; exit 2;;
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
python b32_read.py --pka > $G/pka.txt 2>&1
python b32_read.py --series > $G/series.txt 2>&1
NS=$(grep -c '^  b32_s' $G/series.txt)
if [ "$NS" -ge 10 ] && [ ! -f $G/series10.txt ]; then
  python b32_read.py --series --upto 10 > $G/series10.txt 2>&1
  echo "$(u) F20l3 post_f20l3 $T: 10 admitted series tags - series10.txt $(sha256sum $G/series10.txt | cut -c1-16): $(grep '^U5 ANY' $G/series10.txt)" >> C:/kyty/f287/times.txt
fi
echo "$(u) F20l3 post_f20l3 $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep '^  ADMISSION' $D/read.txt | head -1), $(grep '^  K_I' $D/read.txt | head -1 | cut -c1-120), $(grep '^  PK-A COLD' $D/read.txt | head -1 | cut -c1-90), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1); $(head -2 $G/pka.txt | tail -1 | cut -c1-80); $(grep '^HOLDS\|^STOP RULE' $G/series.txt | tr '\n' ';' | cut -c1-140)" >> C:/kyty/f287/times.txt
cat $D/read.txt | head -70; cat $D/glitch.txt 2>/dev/null | head -3; cat $G/pka.txt; grep -v '^  b32_s' $G/series.txt

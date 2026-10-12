#!/bin/bash
# Track F link F47i (HPP-826; ROADMAP s122 item 740 (v)(3), 742 (e), 744 (g)-(d)): the reading of the made tag OUTSIDE the lock (port of
# F47d post_f47d.sh).  s51_vidglitch.py <rec> 4 6 and the sheet sheet142.py of the whole video; the admission member of item 742 (e) /
# 744 (g)(1) - dt_f47g2.py flips <log> --window WIN -> runs/<tag>/flips.txt; the table of the reader of F47g2 without --block (no rule
# (6), no verdict) - dt_f47g2.py table <log> --files <_f47dt dir> --window WIN --out runs/<tag>/dt_table.txt; the control of the detector
# on fs13_v (read_f47i.py --control) -> runs/<tag>/control_fs13_v.txt; then read_f47i.py <tag> --video --json runs/<tag>/read.json.
# Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f47i/post_f47i.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f47i; D=$G/runs/$T
DT=C:/kyty/KytyPS5/docs/track-f/f47g2/dt_f47g2.py
case "$T" in
  f47_dt|f47_dt_r[1-3]) ;;
  *) echo "usage: post_f47i.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
if [ $T = f47_dt ]; then DTD=$G/_f47dt; else DTD=$G/_f47dt_$T; fi
WIN=$(cat $D/window.txt)
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
fi
python $DT flips $G/log_$T.txt --window $WIN > $D/flips.txt 2>&1
echo "flips rc $?" >> $D/flips_rc.txt
python $DT table $G/log_$T.txt --files $DTD --window $WIN --out $D/dt_table.txt > /dev/null 2> $D/dt_table.err
echo "table rc $?" >> $D/flips_rc.txt
[ -f $D/control_fs13_v.txt ] || python read_f47i.py --control C:/kyty/f287/fs13c/log_fs13_v.txt C:/kyty/f287/fs13c/rec_fs13_v.mp4 > $D/control_fs13_v.txt 2>&1
python read_f47i.py $T --video --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
echo "$(u) F47i post_f47i $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  STATUS' $D/read.txt | tr '\n' ';' | cut -c1-200), flips: $(head -1 $D/flips.txt | cut -c1-200), dt_table.txt $(sha256sum $D/dt_table.txt 2>/dev/null | cut -c1-16) lines $(wc -l < $D/dt_table.txt 2>/dev/null), control: $(tail -1 $D/control_fs13_v.txt | cut -c1-80), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; head -3 $D/glitch.txt 2>/dev/null; cat $D/flips_rc.txt
exit 0

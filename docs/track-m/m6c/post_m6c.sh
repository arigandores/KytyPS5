#!/bin/bash
# Track M link M6c (HPP-850; port of M3a post_m3a.sh): the reading of a made tag outside the lock.  The video tag: s51_vidglitch.py <rec>
# 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; then m6c_read.py rows and json, the table of the
# M5W2Stat fields (m6c_read.py --table); the admission member 'scene tempo' (item 620 (g)(2), 621; tempo_m6c.py = tempo_fs15c.py, form V).
# A tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).  Refuses under any lock (general rule 27) and with the
# stop file.  No pairs, no theme verdict (the reading is M6d).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/m657/m6c; D=$G/runs/$T
PLAN=$(M6C_DRYRUN=1 bash $G/go_m6c.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
[ "${M6C_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; exit 0; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/m657/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
fi
python m6c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python m6c_read.py --table > $G/table.txt 2>&1
python tempo_m6c.py $G/log_$T.txt $D/run.txt --plan-w no --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form no (item 621); plan: $PLAN" >> $D/tempo.txt
echo "$(u) M6c post_m6c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|M5W2|READING)' $D/read.txt | tr '\n' ';' | cut -c1-300), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> $G/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) M6c post_m6c $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> $G/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

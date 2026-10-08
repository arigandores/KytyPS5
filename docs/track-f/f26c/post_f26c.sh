#!/bin/bash
# Track F link F26c (HPP-692; port of FS10c post_fs10c.sh without video): the reading of a made tag b25_NN outside the lock - the admission
# member 'scene tempo' (tempo_f26c.py, item 620 (g)(2), (d); the form is never W) and the reader f26c_read.py with the display line after
# 'lock released' (item 620 (g)(1)) and the tempo exit code; then the table and the series line.  A series state other than GOING writes
# SERIES_STOP (DETECTOR_STOP: item 630 (d)(1) - the return of the caches follows; INTERFERENCE_STOP: (d)(2) - question to the lead;
# HARNESS_STOP / TEMPO_STOP - question to the lead; COMPLETE - 55 tags counted, the return follows).  Refuses under any lock (general
# rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f26c/post_f26c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f26c; D=$G/runs/$T
case "$T" in
  b25_0[1-9]|b25_[1-4][0-9]|b25_5[0-5]) ;;
  *) echo "usage: post_f26c.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
python tempo_f26c.py $G/log_$T.txt $D/run.txt --plan-w no --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
python f26c_read.py $T --json $D/read.json --disp-after $D/disp_after.txt --tempo-rc $TRC > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f26c_read.py --table > $G/table.txt 2>&1
SL=$(grep '^SERIES ' $G/table.txt | tail -1)
echo "$(u) F26c post_f26c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  CLASS' $D/read.txt | sed 's/^ *//'), reasons: $(grep -E '^  reasons' $D/read.txt | cut -c1-160 | sed 's/^ *//'), tempo: $(head -1 $D/tempo.txt | cut -c1-80), display before / after: $(cut -c1-24 $D/disp_before.txt 2>/dev/null) / $(cut -c1-24 $D/disp_after.txt 2>/dev/null); $SL" >> C:/kyty/f287/times.txt
case "$SL" in
  *"state GOING"*) ;;
  *) echo "$(u) $T series: $SL" > $G/SERIES_STOP
     echo "$(u) F26c post_f26c $T: series state is not GOING - SERIES_STOP (item 630 (d)): $SL" >> C:/kyty/f287/times.txt;;
esac
cat $D/read.txt; head -2 $D/tempo.txt; echo "$SL"
exit 0

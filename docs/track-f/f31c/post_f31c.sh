#!/bin/bash
# Track F link F31c (HPP-731; port of F26c post_f26c.sh): the reading of a made tag b25m_NN outside the lock - the admission member 'scene
# tempo' (tempo_f31c.py, item 620 (g)(2), (d); the form is never W) and the reader f31c_read.py with the display line after 'lock
# released' (item 620 (g)(1)) and the tempo exit code; then the table and the series line (with the lock budget of item 667 (e)(4)).
# A series state other than GOING writes SERIES_STOP (DETECTOR_STOP: item 667 (e)(1) - the return of the caches follows;
# INTERFERENCE_STOP: (e)(2) - lead item; LOCK_BUDGET_STOP: (e)(4) - lead item; HARNESS_STOP / TEMPO_STOP - question to the lead;
# COMPLETE - 36 tags counted, the return follows).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f31c/post_f31c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f31c; D=$G/runs/$T
case "$T" in
  b25m_0[1-9]|b25m_[12][0-9]|b25m_3[0-6]) ;;
  *) echo "usage: post_f31c.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
python tempo_f31c.py $G/log_$T.txt $D/run.txt --plan-w no --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
python f31c_read.py $T --json $D/read.json --disp-after $D/disp_after.txt --tempo-rc $TRC > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f31c_read.py --table > $G/table.txt 2>&1
SL=$(grep '^SERIES ' $G/table.txt | tail -1)
echo "$(u) F31c post_f31c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  CLASS' $D/read.txt | sed 's/^ *//'), reasons: $(grep -E '^  reasons' $D/read.txt | cut -c1-160 | sed 's/^ *//'), tempo: $(head -1 $D/tempo.txt | cut -c1-80), display before / after: $(cut -c1-24 $D/disp_before.txt 2>/dev/null) / $(cut -c1-24 $D/disp_after.txt 2>/dev/null); $SL" >> C:/kyty/f287/times.txt
case "$SL" in
  *"state GOING"*) ;;
  *) echo "$(u) $T series: $SL" > $G/SERIES_STOP
     echo "$(u) F31c post_f31c $T: series state is not GOING - SERIES_STOP (item 667 (e)): $SL" >> C:/kyty/f287/times.txt;;
esac
cat $D/read.txt; head -2 $D/tempo.txt; echo "$SL"
exit 0

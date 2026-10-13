#!/bin/bash
# Track M link M9f (HPP-871; ROADMAP s122 item 785 (v)(3), (v)(5); port of M6c post_m6c.sh): the reading of a made tag outside the lock.
# The video tag: s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; the reader
# m9f_read.py (pass 1: read.json with the first scene frame), the detector nmag_m9f.py (N_mag, top12 sheet, pair sheets =2 / M6c), the
# reader again (pass 2: rows with the detector), the series table (m9f_read.py --table); the admission member 'scene tempo' (item 620
# (g)(2), 621; tempo_m9f.py = tempo_fs15c.py, form V).  STOP: a tempo other than PASS, or T188_STOP of the reader (a T188 invariant or an
# identity I1-I9 violated - a code interference, design section 7 (1), item 785 (v)(5)) - a times.txt line and SERIES_STOP (question to
# the lead).  Refuses under any lock (general rule 27) and with the stop file.  No verdict on T188 / T109 (the reading is M9g).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/m657/m9f; D=$G/runs/$T
PLAN=$(M9F_DRYRUN=1 bash $G/go_m9f.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
[ "${M9F_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; exit 0; }
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
python m9f_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
if [ -f $REC ]; then
  python nmag_m9f.py $T $D > $D/nmag.txt 2>&1; NRC=$?
  [ $NRC = 0 ] || echo "$(u) M9f post_m9f $T: nmag_m9f.py rc $NRC: $(head -1 $D/nmag.txt | cut -c1-160)" >> $G/times.txt
  python m9f_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed (pass 2)"; tail -3 $D/read.txt; exit 1; }
fi
python m9f_read.py --table > $G/table.txt 2>&1
python tempo_m9f.py $G/log_$T.txt $D/run.txt --plan-w no --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form no (item 621); plan: $PLAN" >> $D/tempo.txt
STOP188=$(python -c "import json,sys; d=json.load(open(sys.argv[1])); print('YES' if d.get('t188_stop') else 'NO')" $D/read.json 2>/dev/null)
echo "$(u) M9f post_m9f $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|T188 STOP MEMBERS|T188_STOP|DETECTOR|CLASS CHOICE|READING)' $D/read.txt | tr '\n' ';' | cut -c1-500), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> $G/times.txt
if [ "$STOP188" != NO ]; then
  echo "$(u) $T T188_STOP ($STOP188): $(grep -E '^  T188_STOP' $D/read.txt | cut -c1-300)" > $G/SERIES_STOP
  echo "$(u) M9f post_m9f $T: T188 stop member violated or unread ($STOP188) - SERIES_STOP, code interference, question to the lead (design section 7 (1))" >> $G/times.txt
fi
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" >> $G/SERIES_STOP
  echo "$(u) M9f post_m9f $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> $G/times.txt
fi
cat $D/read.txt; cat $D/nmag.txt 2>/dev/null | head -4; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt
[ "$STOP188" = NO ] || echo "SERIES_STOP: T188 stop"
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

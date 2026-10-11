#!/bin/bash
# Track F link F46c (HPP-800; ROADMAP s122 item 702 (g); port of F44c post_f44c.sh): the reading of a made tag outside the lock.
# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; the per-frame M / brightness
# table of the video (f46c_vid.py --frames <tag>: runs/<tag>/frames.json, detector of item 702 (d)); then f46c_read.py rows and json, the
# table; after f26s_1 (or its repeat) the plan of next_f46c.py (the event rule of the tint tags); then the admission member 'scene tempo'
# (item 620 (g)(2), 621; tempo_f46c.py = tempo_fs12c.py, the W form from the dry-run plan of go_f46c.sh: the line starting 'dryrun ').  F46C_POST_PLANONLY=1 prints the plan line and
# the W form and exits (fixtures only; before any check, reads nothing).  A tempo other than PASS - a times.txt line and SERIES_STOP
# (question to the lead).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f46c/post_f46c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f46c; D=$G/runs/$T
case "$T" in
  f26s_0|f26s_1|f26s_1b|f26s_t[1-4]|f26s_c[1-4]|f26s_0_r[1-3]|f26s_1_r[1-3]|f26s_1b_r[1-3]|f26s_t[1-4]_r[1-3]|f26s_c[1-4]_r[1-3]) ;;
  *) echo "usage: post_f46c.sh <tag>"; exit 2;;
esac
PLAN=$(F46C_DRYRUN=1 F46C_DRYKEY=0x0 bash $G/go_f46c.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${F46C_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  python f46c_vid.py --frames $T > $D/frames.txt 2>&1
fi
python f46c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f46c_read.py --table > $G/table.txt 2>&1
case "$T" in f26s_1|f26s_1_r1) python next_f46c.py --plan > $D/plan.txt 2>&1; cat $D/plan.txt >> $D/read.txt;; esac
python tempo_f46c.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
echo "$(u) F46c post_f46c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|EVENT)' $D/read.txt | tr '\n' ';' | cut -c1-400), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) F46c post_f46c $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> C:/kyty/f287/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; tail -2 $D/frames.txt 2>/dev/null; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

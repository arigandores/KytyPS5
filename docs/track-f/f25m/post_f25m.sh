#!/bin/bash
# Track F link F25m (HPP-680; port of F25f post_f25f.sh): the reading of a made tag outside the lock - when the tag has a video:
# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; then f25m_read.py rows and json
# (theta_load from the seal), the table (table.txt) and the series summary (series.txt).  Refuses under any lock (general rule 27) and with
# the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f25m/post_f25m.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f25m; D=$G/runs/$T
case "$T" in
  b36_s[01]|b36_f[01]|b36_k0[1-9]|b36_k1[0-3]|b36_v|b36_w) ;;
  b36_s[01]_r[1-3]|b36_f[01]_r[1-3]|b36_k0[1-9]_r[1-3]|b36_k1[0-3]_r[1-3]|b36_v_r[1-3]|b36_w_r[1-3]) ;;
  *) echo "usage: post_f25m.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
fi
python f25m_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f25m_read.py --table > $G/table.txt 2>&1
python f25m_read.py --series > $G/series.txt 2>&1
echo "$(u) F25m post_f25m $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep '^  ADMISSION' $D/read.txt | head -1), $(grep -E '^  (STAND|NO HARM|K_I)' $D/read.txt | head -1 | cut -c1-140), S $(grep -o 'S (stall us >= 1 000 000) [0-9]*' $D/read.txt | head -1 | awk '{print $NF}'), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
# SEAL 2 (item 620 (g)(2)): the scene tempo member - tempo_f25m.py; anything but TEMPO PASS stops the series (SERIES_STOP, a question to
# the lead).  SEAL 2a (item 621): the W form - the seal plan (dry run of go_f25m.sh) launches the tag with --vulkan-validation true - has
# the limit mean dt < 200 ms; the form comes from the plan, not from the tag name, and the run json launch arguments must agree.
PLAN=$(F25M_DRYRUN=1 bash $G/go_f25m.sh $T 2>&1 | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
python tempo_f25m.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621)" >> $D/tempo.txt
echo "$(u) F25m post_f25m $T seal 2 member (g)(2): $(head -1 $D/tempo.txt | cut -c1-200); display before / after: $(cat $D/disp_before.txt 2>/dev/null | cut -c1-40) / $(cat $D/disp_after.txt 2>/dev/null | cut -c1-40); hold OFF events $(grep -c '^event .* OFF' $D/disp_hold.txt 2>/dev/null)" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T seal 2 member (g)(2): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) F25m post_f25m $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> C:/kyty/f287/times.txt
fi
grep -v '^    \[ok\]' $D/read.txt | head -60; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt; cat $G/series.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"

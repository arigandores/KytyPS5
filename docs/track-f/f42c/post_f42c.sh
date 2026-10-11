#!/bin/bash
# Track F link F42c (HPP-781; port of F44c post_f44c.sh): the reading of a made call outside the lock.  Tags with video (f20_v, f20_hb):
# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; the pair image = the sheet of the
# tag left of the sheet of the same form on FS13 / FS4 (f20_v - fs13_v of FS13c; f20_hb - fs4_hb of FS4c), a row for the lead.  Then
# f42c_read.py rows and json, the table; then the admission member 'scene tempo' (item 620 (g)(2), 621; tempo_f42c.py = tempo_fs12c.py,
# the W form from the dry-run plan of go_f42c.sh: the line starting 'dryrun ').  N1 (item 705 (v)): 'Event: quit' with no
# 'FixF20Stat: when=exit' line after it - SERIES_STOP and a times.txt line (a defect of the witness, item of the lead).  The series return
# f42c_ret: only its manifest cmp line and the series state.  F42C_POST_PLANONLY=1 prints the plan line and the W form and exits (fixtures
# only; before any check, reads nothing).  A tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).  Refuses under
# any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f42c/post_f42c.sh <name>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f42c; D=$G/runs/$T
case "$T" in
  f20_v|f20_hb|f20_w|f42c_ret|f20_v_r[1-3]|f20_hb_r[1-3]|f20_w_r[1-3]|f42c_ret_r[1-3]) ;;
  *) echo "usage: post_f42c.sh <name>"; exit 2;;
esac
PLAN=$(F42C_DRYRUN=1 bash $G/go_f42c.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${F42C_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
case "$T" in
  f42c_ret*)
    echo "$(u) F42c post_f42c $T: $(head -1 $D/manifest_cmp.txt 2>/dev/null); series dirs: $(ls -d $G/series* 2>/dev/null | tr '\n' ' ')" >> C:/kyty/f287/times.txt
    cat $D/manifest_cmp.txt 2>/dev/null; ls -d $G/series* 2>/dev/null
    exit 0;;
esac
REC=$G/rec_$T.mp4
case "$T" in
  f20_v*) REF=C:/kyty/f287/fs13c/runs/fs13_v/sheet_fs13_v.png; RN=fs13_v;;
  f20_hb*) REF=C:/kyty/f287/fs4c/runs/fs4_hb/sheet_fs4_hb.png; RN=fs4_hb;;
  *) REF=; RN=;;
esac
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  if [ -f $D/sheet_$T.png ] && [ -n "$REF" ] && [ -f "$REF" ]; then
    ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i $REF -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" \
      $D/pair_${T}_$RN.png > $D/pair.txt 2>&1 && echo "pair: $D/pair_${T}_$RN.png (left $T, right $RN)" >> $D/pair.txt
  fi
fi
python f42c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f42c_read.py --table > $G/table.txt 2>&1
python tempo_f42c.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
echo "$(u) F42c post_f42c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|ROW exit|ROW preparation|ROW driver|N1 STOP)' $D/read.txt | tr '\n' ';' | cut -c1-600), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) F42c post_f42c $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> C:/kyty/f287/times.txt
fi
if grep -q '^  N1 STOP:' $D/read.txt; then
  echo "$(u) $T N1 (item 705 (v)): Event: quit with no FixF20Stat: when=exit after it - a defect of the witness" >> $G/SERIES_STOP
  echo "$(u) F42c post_f42c $T: N1 - Event: quit with no FixF20Stat: when=exit line - SERIES_STOP, item of the lead (item 705 (v))" >> C:/kyty/f287/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
grep -q '^  N1 STOP:' $D/read.txt && echo "SERIES_STOP: N1"
exit 0

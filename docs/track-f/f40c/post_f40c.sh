#!/bin/bash
# Track F link F40c (HPP-772; port of F38c post_f38c.sh): the reading of a made tag outside the lock.  f24_n1 (the form fs12_v): the video
# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py, written BEFORE the reader, and the pair image pair_f24_n1_fs12_v.png (the sheet
# of the tag left of the sheet of fs12_v of FS12c).  Every tag: f40c_read.py rows and json (the partner of f24_u1 / f24_p1 - the admitted
# read of f24_u0 / f24_p0 - is found by the reader), the table, then the admission member 'scene tempo' (item 620 (g)(2), 621;
# tempo_f40c.py = tempo_f38c.py, the W form from the dry-run plan of go_f40c.sh: the line starting 'dryrun ').  SERIES_STOP (a times.txt
# line, question to the lead) on: tempo not PASS; the word DEAD_CONTROL (item 692 (g)(1): the dead positive control f24_u0 - stand edition
# 3); the word WITNESS_DEAD (item 696 (b)(1), 700 (b)(1)); the third NOT_ADMITTED:flap of one tag family without an admitted attempt between
# (item 696 (b)(2)).  F40C_POST_PLANONLY=1 prints the plan line and the W form and exits (fixtures only).  Refuses under any lock (general
# rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f40c/post_f40c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f40c; D=$G/runs/$T
case "$T" in
  f24_u0|f24_u1|f24_p0|f24_p1|f24_f0|f24_f1|f24_x1|f24_d1|f24_m1|f24_m2|f24_m4|f24_m5|f24_m6|f24_n1|f24_u0b|f24_u1b|f24_p0b|f24_p1b) ;;
  f24_*_r[1-2]) ;;
  *) echo "usage: post_f40c.sh <tag>"; exit 2;;
esac
B=${T%_r[1-2]}
PLAN=$(F40C_DRYRUN=1 bash $G/go_f40c.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${F40C_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  if [ -f $D/sheet_$T.png ]; then
    ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/fs12c/runs/fs12_v/sheet_fs12_v.png       -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_${T}_fs12_v.png > $D/pair.txt 2>&1       && echo "pair: $D/pair_${T}_fs12_v.png (left $T, right fs12_v)" >> $D/pair.txt
  fi
fi
python f40c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f40c_read.py --table > $G/table.txt 2>&1
python tempo_f40c.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
WORD=$(grep '^  WORD ' $D/read.txt | head -1 | awk '{print $2}')
echo "$(u) F40c post_f40c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), word $WORD, $(grep -E '^  (ADMISSION|MEMBERS)' $D/read.txt | tr '\n' ';' | cut -c1-200), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
STOPW=""
[ $TRC != 0 ] && STOPW="tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)"
case "$WORD" in
  DEAD_CONTROL) STOPW="dead positive control $T (item 692 (g)(1)): stand edition 3, item of the lead";;
  WITNESS_DEAD) STOPW="witness init_owner dead in $T (item 696 (b)(1), 700 (b)(1)): item of the lead";;
  NOT_ADMITTED:flap)
    NF=0; NA=0
    for d in $G/runs/$B $G/runs/${B}_r1 $G/runs/${B}_r2; do
      [ -f $d/read.json ] || continue
      grep -q '"status": "NOT_ADMITTED:flap"' $d/read.json && NF=$((NF + 1))
      grep -q '"admitted": true' $d/read.json && NA=$((NA + 1))
    done
    [ $NF -ge 3 ] && [ $NA = 0 ] && STOPW="third flap non-admission of $B (item 696 (b)(2)): stand edition 3, item of the lead";;
esac
if [ -n "$STOPW" ]; then
  echo "$(u) $T $STOPW" > $G/SERIES_STOP
  echo "$(u) F40c post_f40c $T: SERIES_STOP - $STOPW" >> C:/kyty/f287/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null; cat $D/tempo.txt
[ -n "$STOPW" ] && echo "SERIES_STOP: $STOPW"
exit 0

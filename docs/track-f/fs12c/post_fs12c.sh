#!/bin/bash
# Track F link FS12c (HPP-752; port of F33e post_f33e.sh): the reading of a made tag outside the lock.  Tags with video (fs12_v, fs12_z):
# s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; at fs12_v the pair image
# pair_fs12_v_f21_v.png = the sheet of the tag left of the sheet of f21_v (F33e, the path =1 of the F33c binary 2b393af8; item 683 (g)(3)
# "the lead sheet next to f21_v").  Then fs12c_read.py rows and json, the table; then the admission member 'scene tempo' (item 620 (g)(2),
# 621; tempo_fs12c.py = tempo_fs11c.py, the W form from the dry-run plan of go_fs12c.sh).  F33e DEBT (item 683 (d), (g)(3)): the plan is
# the line starting 'dryrun ' of the dry-run output (grep '^dryrun '), NOT its first line - the first line of go_fs12c.sh output is the
# form linter line 'ALL OK'.  FS12C_POST_PLANONLY=1 prints the plan line and the W form and exits (fixtures only; before any check, reads
# nothing).  A tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).  Refuses under any lock (general rule 27)
# and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/fs12c/post_fs12c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs12c; D=$G/runs/$T
case "$T" in
  fs12_v|fs12_w|fs12_z|fs12_v_r[1-3]|fs12_w_r[1-3]|fs12_z_r[1-3]) ;;
  *) echo "usage: post_fs12c.sh <tag>"; exit 2;;
esac
PLAN=$(FS12C_DRYRUN=1 bash $G/go_fs12c.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${FS12C_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
  python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
  case "$T" in
    fs12_v*)
      if [ -f $D/sheet_$T.png ]; then
        ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/f33e/runs/f21_v/sheet_f21_v.png \
          -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_${T}_f21_v.png > $D/pair.txt 2>&1 \
          && echo "pair: $D/pair_${T}_f21_v.png (left $T, right f21_v)" >> $D/pair.txt
      fi;;
  esac
fi
python fs12c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python fs12c_read.py --table > $G/table.txt 2>&1
python tempo_fs12c.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
echo "$(u) FS12c post_fs12c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|ROW exit)' $D/read.txt | tr '\n' ';' | cut -c1-300), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) FS12c post_fs12c $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> C:/kyty/f287/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

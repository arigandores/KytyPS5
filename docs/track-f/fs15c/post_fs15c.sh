#!/bin/bash
# Track F link FS15c (HPP-822; port of FS14c post_fs14c.sh by gen_fs15c.py): the reading of a made tag outside the lock.  Tags with
# video (fs15_v, fs15_z): s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; at
# fs15_v the pair image pair_fs15_v_fs14_v.png = the sheet of the tag left of the sheet of fs14_v (FS14c, the installed FS14 013e1974;
# item 730 (g)(3) "the sheet next to fs14_v").  Then fs15c_read.py rows and json, the table; then the admission member 'scene tempo'
# (item 620 (g)(2), 621; tempo_fs15c.py = tempo_fs14c.py, the W form from the dry-run plan of go_fs15c.sh: the line starting 'dryrun ').
# FS15C_POST_PLANONLY=1 prints the plan line and the W form and exits (fixtures only; before any check, reads nothing).  A tempo other than
# PASS - a times.txt line and SERIES_STOP (question to the lead).  Refuses under any lock (general rule 27) and with the stop file.  ASCII
# only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs15c; D=$G/runs/$T
case "$T" in
  fs15_v|fs15_w|fs15_z|fs15_v_r[1-3]|fs15_w_r[1-3]|fs15_z_r[1-3]) ;;
  *) echo "usage: post_fs15c.sh <tag>"; exit 2;;
esac
PLAN=$(FS15C_DRYRUN=1 bash $G/go_fs15c.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${FS15C_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
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
    fs15_v*)
      if [ -f $D/sheet_$T.png ]; then
        ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/fs14c/runs/fs14_v/sheet_fs14_v.png \
          -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_${T}_fs14_v.png > $D/pair.txt 2>&1 \
          && echo "pair: $D/pair_${T}_fs14_v.png (left $T, right fs14_v)" >> $D/pair.txt
      fi;;
  esac
fi
python fs15c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python fs15c_read.py --table > $G/table.txt 2>&1
python tempo_fs15c.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
echo "$(u) FS15c post_fs15c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|ROW exit)' $D/read.txt | tr '\n' ';' | cut -c1-300), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) FS15c post_fs15c $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> C:/kyty/f287/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

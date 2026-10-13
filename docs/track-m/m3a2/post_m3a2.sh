#!/bin/bash
# Track M link M3a2 (HPP-861; port of M3a post_m3a.sh, HPP-842): the reading of a made tag outside the lock.  Video tags: s51_vidglitch.py
# <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; then m3a2_read.py rows and json, the table; the
# admission member 'scene tempo' (item 620 (g)(2), 621; tempo_m3a2.py = tempo_fs15c.py, the W form from the dry-run plan of go_m3a2.sh);
# then the pairs of the seal section 6 (item 778 (d)(4)): pairs/pair_<L>.png = the sheet of m3w2_<L>_v (MS2, left) beside the sheet of
# the MS1 support V tag of M3a (right; sg m3_sg_v_r1, hb m3_hb_v, mg m3_mg_v - C:/kyty/m657/m3a/runs/<tag>/sheet_<tag>.png, its sha256
# checked against the seal) when both exist.  No banner (T231 is not a theme of wave 2).  A tempo other than PASS - a times.txt line and
# SERIES_STOP (question to the lead).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/m657/m3a2; D=$G/runs/$T; M3A=C:/kyty/m657/m3a
PLAN=$(M3A2_DRYRUN=1 bash $G/go_m3a2.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${M3A2_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
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
python m3a2_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python m3a2_read.py --table > $G/table.txt 2>&1
case "$PLAN" in *" kind p "*) TRC=0; echo "TEMPO not read (warm-up p)" > $D/tempo.txt;;
  *) python tempo_m3a2.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?;;
esac
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
mkdir -p $G/pairs
for L in sg hb mg; do
  case $L in sg) R=m3_sg_v_r1;; hb) R=m3_hb_v;; mg) R=m3_mg_v;; esac
  A=$G/runs/m3w2_${L}_v/sheet_m3w2_${L}_v.png; F=$M3A/runs/$R/sheet_$R.png
  RS=$(grep -m1 "^support sheet $R: " $G/pred.md | cut -d' ' -f4)
  if [ -f $A ] && [ -f $F ] && [ ! -f $G/pairs/pair_$L.png ]; then
    if [ "$(sha256sum $F | cut -c1-64)" != "$RS" ]; then
      echo "$(u) M3a2 post pair $L: the support sheet $F sha256 differs from the seal - pair not made, question to the lead" >> $G/times.txt
      continue
    fi
    ffmpeg -hide_banner -loglevel error -y -i $A -i $F -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $G/pairs/pair_$L.png \
      && echo "$(u) M3a2 post pair $L: pairs/pair_$L.png (left m3w2_${L}_v MS2, right $R MS1) sha256 $(sha256sum $G/pairs/pair_$L.png | cut -c1-16)" >> $G/times.txt
  fi
done
echo "$(u) M3a2 post_m3a2 $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|T125|FORM|READING)' $D/read.txt | tr '\n' ';' | cut -c1-300), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> $G/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) M3a2 post_m3a2 $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> $G/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

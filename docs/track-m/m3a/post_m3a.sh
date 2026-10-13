#!/bin/bash
# Track M link M3a (HPP-842; port of FS15c post_fs15c.sh): the reading of a made tag outside the lock.  Video tags: s51_vidglitch.py
# <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; then m3a_read.py rows and json, the table; the
# admission member 'scene tempo' (item 620 (g)(2), 621; tempo_m3a.py = tempo_fs15c.py, the W form from the dry-run plan of go_m3a.sh);
# then the pairs of the seal section 6: pairs/pair_<L>.png = the sheet of m3_<L>_v (MS1, left) beside the sheet of m3_<L>_f (FS15,
# right) when both exist; pairs/banner_t231.png = frames 19.5 .. 21.5 s of the videos of m3_sg_v (top, T231=1) and m3_sg_t2310 (bottom,
# T231=0) every 0.25 s (item 759 (b)(iii)).  A tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).  Refuses
# under any lock (general rule 27) and with the stop file.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/m657/m3a; D=$G/runs/$T
PLAN=$(M3A_DRYRUN=1 bash $G/go_m3a.sh $T 2>&1 | grep '^dryrun ' | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
[ "${M3A_POST_PLANONLY:-}" = 1 ] && { echo "plan $PLAN"; echo "plan-w $PW"; exit 0; }
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
python m3a_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python m3a_read.py --table > $G/table.txt 2>&1
case "$PLAN" in *" kind p "*) TRC=0; echo "TEMPO not read (warm-up arm p)" > $D/tempo.txt;;
  *) python tempo_m3a.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?;;
esac
echo "  row: seal plan W form $PW (item 621); plan: $PLAN" >> $D/tempo.txt
mkdir -p $G/pairs
for L in sg hb mg ac f1 f2; do
  A=$G/runs/m3_${L}_v/sheet_m3_${L}_v.png; F=$G/runs/m3_${L}_f/sheet_m3_${L}_f.png
  if [ -f $A ] && [ -f $F ] && [ ! -f $G/pairs/pair_$L.png ]; then
    ffmpeg -hide_banner -loglevel error -y -i $A -i $F -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $G/pairs/pair_$L.png \
      && echo "$(u) M3a post pair $L: pairs/pair_$L.png (left m3_${L}_v MS1, right m3_${L}_f FS15) sha256 $(sha256sum $G/pairs/pair_$L.png | cut -c1-16)" >> $G/times.txt
  fi
done
if [ -f $G/rec_m3_sg_v.mp4 ] && [ -f $G/rec_m3_sg_t2310.mp4 ] && [ ! -f $G/pairs/banner_t231.png ]; then
  for k in m3_sg_v m3_sg_t2310; do
    ffmpeg -hide_banner -loglevel error -y -ss 19.5 -t 2.1 -i $G/rec_$k.mp4 -vf "fps=4,scale=320:-1,tile=9x1" -frames:v 1 $G/pairs/banner_$k.png
  done
  ffmpeg -hide_banner -loglevel error -y -i $G/pairs/banner_m3_sg_v.png -i $G/pairs/banner_m3_sg_t2310.png -filter_complex vstack $G/pairs/banner_t231.png \
    && echo "$(u) M3a post banner T231: pairs/banner_t231.png (top m3_sg_v T231=1, bottom m3_sg_t2310 T231=0; 19.5-21.5 s every 0.25 s) sha256 $(sha256sum $G/pairs/banner_t231.png | cut -c1-16)" >> $G/times.txt
fi
echo "$(u) M3a post_m3a $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS|FORM|READING)' $D/read.txt | tr '\n' ';' | cut -c1-300), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> $G/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) M3a post_m3a $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> $G/times.txt
fi
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

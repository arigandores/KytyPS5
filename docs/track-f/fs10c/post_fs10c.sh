#!/bin/bash
# Track F link FS10c (HPP-686; port of FS9c post_fs9c.sh and F25m post_f25m.sh): the reading of a made tag outside the lock.  Tags with a
# video (fs10_f1, fs10_v): s51_vidglitch.py <rec> 4 6 and the lead sheet sheet142.py of the whole video, written BEFORE the reader; fs10_v -
# the pair image pair_fs10_v_b36_v.png = the sheet of fs10_v left of the sheet of b36_v (F25m, item 624 (e)(3): the lead sheet beside
# b36_v).  Then fs10c_read.py rows and json, the table; then the admission member 'scene tempo' (item 620 (g)(2), 621; tempo_fs10c.py,
# the W form from the dry-run plan of go_fs10c.sh); a tempo other than PASS - a times.txt line and SERIES_STOP (question to the lead).
# Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/fs10c/post_fs10c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/fs10c; D=$G/runs/$T
case "$T" in
  fs10_s[01]|fs10_f1|fs10_v|fs10_w|fs10_s[01]_r[1-3]|fs10_f1_r[1-3]|fs10_v_r[1-3]|fs10_w_r[1-3]) ;;
  *) echo "usage: post_fs10c.sh <tag>"; exit 2;;
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
  case "$T" in fs10_v*)
    if [ -f $D/sheet_$T.png ]; then
      ffmpeg -hide_banner -loglevel error -y -i $D/sheet_$T.png -i C:/kyty/f287/f25m/runs/b36_v/sheet_b36_v.png \
        -filter_complex "[0][1]scale2ref=iw:ih[a][b];[a][b]hstack" $D/pair_${T}_b36_v.png > $D/pair.txt 2>&1 \
        && echo "pair: $D/pair_${T}_b36_v.png (left $T, right b36_v)" >> $D/pair.txt
    fi;;
  esac
fi
python fs10c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python fs10c_read.py --table > $G/table.txt 2>&1
PLAN=$(FS10C_DRYRUN=1 bash $G/go_fs10c.sh $T 2>&1 | head -1)
case "$PLAN" in dryrun\ *) ;; *) echo "no dry-run plan for $T: $PLAN"; exit 1;; esac
case "$PLAN" in *"--emu-arg=--vulkan-validation --emu-arg=true"*) PW=yes;; *) PW=no;; esac
python tempo_fs10c.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
echo "  row: seal plan W form $PW (item 621)" >> $D/tempo.txt
echo "$(u) FS10c post_fs10c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (ADMISSION|MEMBERS)' $D/read.txt | tr '\n' ';' | cut -c1-160), tempo: $(head -1 $D/tempo.txt | cut -c1-120), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) FS10c post_fs10c $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> C:/kyty/f287/times.txt
fi
case "$T" in fs10_f1*)
  if ! grep -q '^  MEMBERS fs10_f1 ALL YES' $D/read.txt; then
    echo "$(u) $T members not ALL YES (item 626 (b): stop of the FS10 shipping, the lead's item): $(grep -E '^  (ADMISSION|MEMBERS|READING)' $D/read.txt | tr '\n' ';' | cut -c1-160)" > $G/SERIES_STOP
    echo "$(u) FS10c post_fs10c $T: members not ALL YES or not admitted - SERIES_STOP, fs10_v / fs10_w wait for the lead's item (seal section 8 (10))" >> C:/kyty/f287/times.txt
  fi;;
esac
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/pair.txt 2>/dev/null; cat $D/tempo.txt
[ $TRC = 0 ] || echo "SERIES_STOP: tempo member not PASS"
exit 0

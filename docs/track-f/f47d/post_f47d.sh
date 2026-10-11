#!/bin/bash
# Track F link F47d (HPP-809; ROADMAP s122 item 708 (g)): the reading of a made tag OUTSIDE the lock (port of F46c post_f46c.sh).
# rd tags: the sheet of the 12 thumbnails runs/<tag>/<tag>_thumbs.png (ffmpeg tile 4x3, k01..k12 left to right) for the lead (F47a
# section 3.2: K must be a block, not a darkening of the whole frame).  hi tags: s51_vidglitch.py <rec> 4 6 and the sheet sheet142.py of
# the whole video before the reader.  Then f47d_read.py <tag> --json runs/<tag>/read.json (--video for hi: the detector of F47a
# section 1.3 on the title window) and the table.  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f47d/post_f47d.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f47d; D=$G/runs/$T
case "$T" in
  f47_rd|f47_rd2|f47_hi|f47_rd_r[1-3]|f47_rd2_r[1-3]|f47_hi_r[1-3]) ;;
  *) echo "usage: post_f47d.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
case "$T" in
  f47_hi*)
    REC=$G/rec_$T.mp4
    if [ -f $REC ]; then
      python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
      python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
    fi
    python f47d_read.py $T --video --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; };;
  *)
    if ls $D/k[0-9][0-9].png > /dev/null 2>&1; then
      ffmpeg -loglevel error -y -framerate 1 -i $D/k%02d.png -vf "scale=480:270,tile=4x3" -frames:v 1 $D/${T}_thumbs.png > $D/thumbsheet.txt 2>&1
    fi
    python f47d_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; };;
esac
python f47d_read.py --table > $G/table.txt 2>&1
echo "$(u) F47d post_f47d $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  (STATUS|G |ROW n0)' $D/read.txt | tr '\n' ';' | cut -c1-400), display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null), glitch: $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> C:/kyty/f287/times.txt
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3
exit 0

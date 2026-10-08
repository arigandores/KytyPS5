#!/bin/bash
# Track F link F27c (HPP-694; port of F26c post_f26c.sh): the reading of a made tag outside the lock - f27c_read.py rows and json, the
# table, the tempo row (tempo_f27c.py, item 620 (g)(2): a tempo other than PASS -> SERIES_STOP, question to the lead), the series state
# (item 631 (v)(3), (d)(1)) and the stop member of item 631 (d)(3): a frame >= 100 ms on a write window in a v1 tag -> SERIES_STOP after
# the tag (log, json, video kept; U was returned per tag; the driver cache returns by 'go_f27c.sh return').  Refuses under any lock
# (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f27c/post_f27c.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f27c; D=$G/runs/$T
case "$T" in
  f27_v0|f27_v0b|f27_v1a|f27_v1b|f27_v1c|f27_v0_r[12]|f27_v0b_r[12]|f27_v1[abc]_r[12]) ;;
  *) echo "usage: post_f27c.sh <tag>"; exit 2;;
esac
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
python tempo_f27c.py $G/log_$T.txt $D/run.txt --plan-w no --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
python f27c_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
python f27c_read.py --table > $G/table.txt 2>&1
SER=$(grep '^SERIES ' $G/table.txt | tail -1)
echo "$(u) F27c post_f27c $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), $(grep -E '^  MEMBERS' $D/read.txt | cut -c1-200), frames on windows: $(grep -o 'frames >= 100 ms on windows (letter) [^;]*' $D/read.txt | cut -c1-120), tempo: $(head -1 $D/tempo.txt | cut -c1-100); $SER" >> C:/kyty/f287/times.txt
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" > $G/SERIES_STOP
  echo "$(u) F27c post_f27c $T: the tempo row is not PASS - SERIES_STOP, question to the lead" >> C:/kyty/f287/times.txt
fi
case "$T" in f27_v1*)
  if ! grep -q 'frames >= 100 ms on windows (letter) \[\];' $D/read.txt; then
    echo "$(u) $T a frame >= 100 ms on a write window in a v1 tag (item 631 (d)(3)) - stop of the series after the tag" > $G/SERIES_STOP
    echo "$(u) F27c post_f27c $T: frame >= 100 ms on a write window in a v1 tag - SERIES_STOP (item 631 (d)(3))" >> C:/kyty/f287/times.txt
  fi;;
esac
case "$SER" in *STOP*|*NO_POWER*|*UNDEFINED*|*WITHOUT\ POWER*)
  [ -e $G/SERIES_STOP ] || echo "$(u) $T $SER" > $G/SERIES_STOP;;
esac
cat $D/read.txt; cat $D/tempo.txt; echo "$SER"
exit 0

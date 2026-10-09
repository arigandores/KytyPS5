#!/bin/bash
# Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)): the F30m (HPP-723) file with the names moved (f30m -> f30q, HPP-723 -> HPP-727,
# F30M_ -> F30Q_) and the tag set of item 664 (z)(2)-(3): f30_s1_w6, f30_s<1..9>_c6 [_r1.._r3].
# Track F link F30q (HPP-727; port of F30m post_f30m.sh): the reading of a made tag outside the lock: f30q_read.py rows and json, the
# table, then the admission member 'scene tempo' (item 620 (g)(2), 621; tempo_f30q.py, --plan-w yes only at w6 - the W form).  STOP rows of
# the reader (item 664 (z)(2)-(3), 665 (v)) or a tempo other than PASS - SERIES_STOP with the reason and a times.txt line (the lead item); a
# w6 NOT_ADMITTED - SERIES_STOP (item 664 (z)(2)); a c6 NOT_ADMITTED without a STOP row - a times.txt line, question to the lead, no stop
# (executor variant B2, seal section 5).  No video in this series.  Refuses under any lock (general rule 27) and with the stop file.
# ASCII only.
# usage: bash C:/kyty/f287/f30q/post_f30q.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f30q; D=$G/runs/$T
case "$T" in
  f30_s1_w6|f30_s[1-9]_c6) ;;
  f30_s1_w6_r[1-3]|f30_s[1-9]_c6_r[1-3]) ;;
  *) echo "usage: post_f30q.sh <tag>"; exit 2;;
esac
[ -e ${F30Q_LOCK:-C:/kyty/SEALED_RUN.lock} ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
TM=${F30Q_TIMES:-C:/kyty/f287/times.txt}
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
B=${T%_r[1-3]}
SC=$(echo $B | cut -d_ -f2); KD=$(echo $B | cut -d_ -f3)
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
fi
python f30q_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
RE=""   # F30q: no re-read (no tag reads another tag)
PW=no; [ "$KD" = w6 ] && PW=yes   # tempo limit of the W form (item 621) only at w6
python f30q_read.py --table > $G/table.txt 2>&1
python tempo_f30q.py $G/log_$T.txt $D/run.txt --plan-w $PW --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
ST=$(python -c "import json;r=json.load(open('$D/read.json'));print(r['status'] + ' | ' + ('; '.join(r.get('stop') or []) or 'no stop'))")
echo "$(u) F30q post_f30q $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), status/stop: $(echo "$ST" | cut -c1-300); re-read c4:${RE:- none}; tempo: $(head -1 $D/tempo.txt | cut -c1-120); display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null); glitch (reference): $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> "$TM"
STOPS=$(python -c "import json;r=json.load(open('$D/read.json'));print('; '.join(r.get('stop') or []))")
if [ -n "$STOPS" ]; then
  echo "$(u) $T reader STOP (item 643 (d)(11)): $STOPS" > $G/SERIES_STOP
  echo "$(u) F30q post_f30q $T: STOP row - SERIES_STOP, question to the lead: $(echo "$STOPS" | cut -c1-300)" >> "$TM"
fi
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" >> $G/SERIES_STOP
  echo "$(u) F30q post_f30q $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> "$TM"
fi
case "$ST" in NOT_ADMITTED*)
  [ "$KD" = c6 ] && echo "$(u) F30q post_f30q $T: c6 NOT_ADMITTED without a STOP row - question to the lead, the series goes on (executor variant B2)" >> "$TM"
  [ "$KD" = w6 ] && { echo "$(u) $T W NOT_ADMITTED (item 664 (z)(2)): $(echo "$ST" | cut -c1-200)" >> $G/SERIES_STOP; echo "$(u) F30q post_f30q $T: W NOT_ADMITTED - SERIES_STOP, the lead item (item 664 (z)(2))" >> "$TM"; };;
esac
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt
[ -e $G/SERIES_STOP ] && echo "SERIES_STOP: $(head -2 $G/SERIES_STOP)"
exit 0

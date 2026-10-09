#!/bin/bash
# Track F link F30m (HPP-723; ROADMAP s122 item 655 (e)): the F30f (HPP-711) file with the names moved (f30f -> f30m, HPP-711 ->
# HPP-723, F30F_ -> F30M_) and the tag set of item 655 (e)(2)-(3): f30_s<1..9>_c5, f30_cy_v, f30_cy_c3, f30_cy_c4 [_r1.._r3].
# Track F link F30m (HPP-723; port of F29e post_f29e.sh): the reading of a made tag outside the lock.  The tag with a video (v / v2):
# s51_vidglitch.py <rec> 4 6 - a reference (item 643 (d)(2)), written BEFORE the reader.  Then f30m_read.py rows and json; after a v / v2 tag
# the c4 tag of the same scene is read again (its member RC2 (b) needs the v sums, item 644 (v)); the table; then the admission member
# 'scene tempo' (item 620 (g)(2), 621; tempo_f30m.py, no W form in this series).  STOP rows of the reader (item 643 (d)(11), (g) RC2, RC3)
# or a tempo other than PASS - SERIES_STOP with the reason and a times.txt line (question to the lead); a STOP of (V) at v / v2 (outcome
# 640 (e)(4)) also makes the lead sheet sheet142.py of the whole video.  A c4 NOT_ADMITTED - a times.txt line, question to the lead, no
# stop (executor variant B2, seal section 5).  Refuses under any lock (general rule 27) and with the stop file.  ASCII only.
# usage: bash C:/kyty/f287/f30m/post_f30m.sh <tag>
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1; G=C:/kyty/f287/f30m; D=$G/runs/$T
case "$T" in
  f30_s[1-9]_c5|f30_cy_v|f30_cy_c3|f30_cy_c4) ;;
  f30_s[1-9]_c5_r[1-3]|f30_cy_v_r[1-3]|f30_cy_c3_r[1-3]|f30_cy_c4_r[1-3]) ;;
  *) echo "usage: post_f30m.sh <tag>"; exit 2;;
esac
[ -e ${F30M_LOCK:-C:/kyty/SEALED_RUN.lock} ] && { echo "lock held - not reading"; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
[ -d $D ] || { echo "no $D"; exit 2; }
TM=${F30M_TIMES:-C:/kyty/f287/times.txt}
u() { date -u +%Y-%m-%dT%H:%M:%SZ; }
cd $G || exit 1
B=${T%_r[1-3]}
SC=$(echo $B | cut -d_ -f2); KD=$(echo $B | cut -d_ -f3)
REC=$G/rec_$T.mp4
if [ -f $REC ]; then
  python C:/kyty/scripts/s51_vidglitch.py $REC 4 6 $D/vidframes > $D/glitch.txt 2>&1
fi
python f30m_read.py $T --json $D/read.json > $D/read.txt 2>&1 || { echo "reader failed"; tail -3 $D/read.txt; exit 1; }
RE=""   # F30m: no re-read - f30_cy_c4 is made after f30_cy_v and reads its read.json itself (RC2 (b))
python f30m_read.py --table > $G/table.txt 2>&1
python tempo_f30m.py $G/log_$T.txt $D/run.txt --plan-w no --json $G/$T.json > $D/tempo.txt 2>&1; TRC=$?
ST=$(python -c "import json;r=json.load(open('$D/read.json'));print(r['status'] + ' | ' + ('; '.join(r.get('stop') or []) or 'no stop'))")
echo "$(u) F30m post_f30m $T: read.txt $(sha256sum $D/read.txt | cut -c1-16), status/stop: $(echo "$ST" | cut -c1-300); re-read c4:${RE:- none}; tempo: $(head -1 $D/tempo.txt | cut -c1-120); display before / after: $(cut -c1-30 $D/disp_before.txt 2>/dev/null) / $(cut -c1-30 $D/disp_after.txt 2>/dev/null); glitch (reference): $(grep -h 'one-frame glitches' $D/glitch.txt 2>/dev/null | head -1)" >> "$TM"
STOPS=$(python -c "import json;r=json.load(open('$D/read.json'));print('; '.join(r.get('stop') or []))")
if [ -n "$STOPS" ]; then
  echo "$(u) $T reader STOP (item 643 (d)(11)): $STOPS" > $G/SERIES_STOP
  echo "$(u) F30m post_f30m $T: STOP row - SERIES_STOP, question to the lead: $(echo "$STOPS" | cut -c1-300)" >> "$TM"
  case "$STOPS" in *"(V) != 0"*)
    [ -f $REC ] && python sheet142.py $REC $D/sheet_$T.png > $D/sheet.txt 2>&1
    echo "$(u) F30m post_f30m $T: outcome 640 (e)(4) - lead sheet $D/sheet_$T.png" >> "$TM";;
  esac
fi
if [ $TRC != 0 ]; then
  echo "$(u) $T tempo member (item 620 (g)(2)): $(head -1 $D/tempo.txt | cut -c1-160)" >> $G/SERIES_STOP
  echo "$(u) F30m post_f30m $T: the tempo member is not PASS - SERIES_STOP, question to the lead (item 620 (g)(2))" >> "$TM"
fi
case "$ST" in NOT_ADMITTED*)
  [ "$KD" = c4 ] && echo "$(u) F30m post_f30m $T: c4 NOT_ADMITTED - question to the lead, the series goes on (executor variant B2)" >> "$TM";;
esac
cat $D/read.txt; cat $D/glitch.txt 2>/dev/null | head -3; cat $D/tempo.txt
[ -e $G/SERIES_STOP ] && echo "SERIES_STOP: $(head -2 $G/SERIES_STOP)"
exit 0

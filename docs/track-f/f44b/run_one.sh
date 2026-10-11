#!/bin/bash
# F44b (HPP-792): one stand run (=0 then =1) of <exe> with seed <s>, R 20, into <dir>, under the watchdog, after the gate
# wait; retried from an empty dir while killed by the watchdog (rc 7/8/3), up to the budget. Then the F44a reader and own rc_f44b.py.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f44b
EXE=$1; SEED=$2; DIR=$3; BUD=${4:-560}
T0=$(date +%s)
while :; do
  [ -e C:/kyty/f287/STOP ] && exit 4
  LEFT=$(( BUD - ($(date +%s) - T0) ))
  [ $LEFT -lt 90 ] && { echo "budget spent"; exit 9; }
  python wait_f44b.py $(( LEFT - 80 )) > /dev/null || { echo "wait not clear"; exit 9; }
  rm -rf "$DIR"; mkdir -p "$DIR"
  bash api_chk.sh "stand $DIR" > /dev/null || exit $?
  python watch_f44b.py --limit 80 --tag "stand $DIR" -- python run_stand_f44a.py run "$EXE" $SEED 20 "$DIR" > "$DIR.run.txt" 2>&1
  RC=$?
  echo "stand $DIR rc=$RC $(date -u +%FT%TZ)"
  [ $RC -eq 7 ] || [ $RC -eq 8 ] || [ $RC -eq 3 ] || break
done
grep -E "PASS|FAIL|ALL OK|STAND|process" "$DIR.run.txt" > /dev/null; tail -3 "$DIR.run.txt"
python rc_f44b.py "$DIR" 20 > "$DIR.rc.txt" 2>&1; echo "own: $(tail -1 $DIR.rc.txt)"; grep FAIL "$DIR.rc.txt" | head
echo "$(date -u +%FT%TZ) F44b stand $DIR exe $(sha256sum $EXE | cut -c1-8) reader=$(tail -1 $DIR.run.txt) own=$(tail -1 $DIR.rc.txt)" >> times.txt

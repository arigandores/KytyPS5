#!/bin/bash
# F44b (HPP-792): the stand run of run_one.sh split in two watched steps - KYTY_FIX_F29=0, then =1 - each retried after
# the gate wait while killed by the watchdog; output names as run_stand_f44a.py run; then the F44a reader (read) and rc_f44b.py.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f44b
EXE=$1; SEED=$2; DIR=$3; BUD=${4:-570}
T0=$(date +%s)
mkdir -p "$DIR"
for k in 0 1; do
  [ -s "$DIR/f29_$k.done" ] && continue
  while :; do
    [ -e C:/kyty/f287/STOP ] && exit 4
    LEFT=$(( BUD - ($(date +%s) - T0) ))
    [ $LEFT -lt 50 ] && { echo "budget spent at $k"; exit 9; }
    python wait_f44b.py $(( LEFT - 45 )) > /dev/null || { echo "wait not clear at $k"; exit 9; }
    rm -f "$DIR/f29_$k.tsv" "$DIR/f29_$k.tsv.log" "$DIR/f29_$k.out"
    bash api_chk.sh "stand $DIR k=$k" > /dev/null || exit $?
    KYTY_FIX_F29=$k python watch_f44b.py --limit 45 --tag "stand $DIR k=$k" -- "$EXE" $SEED 20 "C:/kyty/f287/f44b/$DIR/f29_$k.tsv" > "$DIR/f29_$k.out" 2>&1
    RC=$?
    echo "stand $DIR k=$k rc=$RC $(date -u +%FT%TZ)"
    [ $RC -eq 0 ] && { echo ok > "$DIR/f29_$k.done"; break; }
    [ $RC -eq 7 ] || [ $RC -eq 8 ] || [ $RC -eq 3 ] || exit $RC
  done
done
python run_stand_f44a.py read $SEED 20 "$DIR" > "$DIR.run.txt" 2>&1; echo "reader: $(tail -1 $DIR.run.txt)"
python rc_f44b.py "$DIR" 20 > "$DIR.rc.txt" 2>&1; echo "own: $(tail -1 $DIR.rc.txt)"
echo "$(date -u +%FT%TZ) F44b stand(split) $DIR exe $(sha256sum $EXE | cut -c1-8) reader=$(tail -1 $DIR.run.txt) own=$(tail -1 $DIR.rc.txt)" >> times.txt

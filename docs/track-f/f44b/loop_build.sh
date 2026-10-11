#!/bin/bash
# F44b (HPP-792): alternate the gate wait (wait_f44b.py) and one watched build step (watch_f44b.py, killed on lock,
# STOP or a gate process - p.431(v)(1)) until the step ends rc=0 or the budget (s) is spent. Usage: loop_build.sh <name> <budget> [build_f44b.cmd args]
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f44b
N=$1; BUD=$2; shift 2
T0=$(date +%s)
i=0
while :; do
  [ -e C:/kyty/f287/STOP ] && exit 4
  LEFT=$(( BUD - ($(date +%s) - T0) ))
  [ $LEFT -lt 30 ] && { echo "budget spent"; exit 9; }
  if ! python wait_f44b.py $(( LEFT - 20 )) > /dev/null; then echo "wait not clear"; exit 9; fi
  LEFT=$(( BUD - ($(date +%s) - T0) ))
  [ $LEFT -lt 20 ] && { echo "budget spent"; exit 9; }
  i=$((i+1))
  bash api_chk.sh "build $N try $i" > /dev/null || exit $?
  python watch_f44b.py --limit $LEFT --tag "build $N $*" -- cmd //c "C:\kyty\f287\f44b\build_f44b.cmd" "$@" > "build_${N}_$i.log" 2>&1
  RC=$?
  echo "try $i rc=$RC $(grep -aoE '\[[0-9]+/[0-9]+\]' build_${N}_$i.log | tail -1)"
  [ $RC -eq 0 ] && { grep -a "BUILD OK" build_${N}_$i.log; exit 0; }
  [ $RC -eq 7 ] || [ $RC -eq 8 ] || [ $RC -eq 3 ] || { tail -5 build_${N}_$i.log; exit $RC; }
done

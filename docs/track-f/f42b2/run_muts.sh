#!/bin/bash
# F42b2 (HPP-780, Red Team): drive the mutants through the windows of foreign series - wait (20 s steps) while the lock or
# a gate process (procload.py, counted by api_chk.sh) exists, then run the next unfinished mutant (mut_one.sh, resumable).
# Stops after ~520 s of wall time (tool limit). Usage: run_muts.sh m4 m1a ...
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f42b2
T0=$(date +%s)
for M in "$@"; do
  while [ ! -e mut/$M/done_all ]; do
    [ $(( $(date +%s) - T0 )) -gt 400 ] && { echo "time up at $M $(date -u +%T)"; exit 0; }
    [ -e C:/kyty/f287/STOP ] && exit 4
    if [ -e C:/kyty/SEALED_RUN.lock ]; then sleep 20; continue; fi
    G=$(bash api_chk.sh "mutant $M window" | grep -o "procload.py) [0-9]*" | grep -o "[0-9]*$")
    if [ "$G" != "0" ]; then sleep 20; continue; fi
    bash mut_one.sh $M | tail -6
  done
done
echo "all done $(date -u +%T)"

#!/bin/bash
# Session 146 step 0 (HPP-386): the call wrapper of the install and warm-up (port of C:/kyty/f287/fsc/next_fs.sh): stop file and lock
# first, ONE detached verbatim seal call "PLWAIT=540 bash C:/kyty/s146/go146i.sh install" (pred/00_i146.md), its output into
# step0/go_i146.out.txt (a previous output is moved to step0/old/ first, D-9), the rc into the same file and step0/times.txt; then a
# foreground wait (wait_i146.sh, < 600 s per invocation).  A running call is waited for again with wait_i146.sh - never a second
# next_i146.sh (go146i.sh also refuses by the attempt file).  ASCII only.  usage: next_i146.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
TIMES=C:/kyty/s146/step0/times.txt
OUT=C:/kyty/s146/step0/go_i146.out.txt
[ -e C:/kyty/s146/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_i146 STOP file found" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
if [ -e $OUT ]; then
  grep -q '^rc=' $OUT || { echo "a call is running (no rc line) - wait with wait_i146.sh"; exit 1; }
  mkdir -p C:/kyty/s146/step0/old; mv $OUT C:/kyty/s146/step0/old/go_i146.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_i146 previous output moved to step0/old/" >> $TIMES
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_i146 STOP absent, no lock; call: PLWAIT=540 bash C:/kyty/s146/go146i.sh install" >> $TIMES
nohup bash -c 'cd C:/kyty/s146; PLWAIT=540 bash C:/kyty/s146/go146i.sh install > C:/kyty/s146/step0/go_i146.out.txt 2>&1; RC=$?; echo "rc=$RC" >> C:/kyty/s146/step0/go_i146.out.txt; echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) next_i146 go146i install call returned rc=$RC" >> C:/kyty/s146/step0/times.txt' > /dev/null 2>&1 & disown
sleep 3
bash C:/kyty/s146/step0/wait_i146.sh

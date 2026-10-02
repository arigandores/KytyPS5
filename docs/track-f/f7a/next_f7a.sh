#!/bin/bash
# F7a (HPP-397): launch wrapper (form of s146 next_one.sh after "Process" 2 of the s146 audit, item 324 (i)): checks the stop file and
# the lock, moves an old output (refuses while a call without its rc line runs), starts ONE detached call of go_f7a.sh and RETURNS.
# The wait is a separate command: bash C:/kyty/f287/f7a/wait_f7a.sh <k>.  ASCII only.  usage: next_f7a.sh <k> <N>
export PATH=/usr/bin:/mingw64/bin:$PATH
K=$1; N=$2
case "$K" in 1|2) ;; *) echo "usage: next_f7a.sh <1|2> <N>"; exit 2;; esac
TIMES=C:/kyty/f287/times.txt
[ -e C:/kyty/f287/STOP ] && { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F7a next_f7a STOP file found before f7a_$K" >> $TIMES; exit 4; }
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held: $(head -1 C:/kyty/SEALED_RUN.lock)"; exit 3; }
GO=C:/kyty/f287/f7a/go_f7a_$K.out.txt
if [ -e $GO ]; then
  grep -q '^rc=' $GO || { echo "the previous call of f7a_$K has no rc line (running) - wait with wait_f7a.sh"; exit 1; }
  mkdir -p C:/kyty/f287/f7a/old
  mv $GO C:/kyty/f287/f7a/old/go_f7a_$K.$(date -u +%Y%m%dT%H%M%SZ).out.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F7a next_f7a STOP absent, no lock; call: bash C:/kyty/f287/f7a/go_f7a.sh $K $N (detached)" >> $TIMES
nohup bash -c "bash C:/kyty/f287/f7a/go_f7a.sh $K $N > $GO 2>&1; RC=\$?; echo rc=\$RC >> $GO; echo \"\$(date -u +%Y-%m-%dT%H:%M:%SZ) F7a call go_f7a $K returned rc=\$RC\" >> $TIMES" > /dev/null 2>&1 & disown
sleep 2
echo "launched f7a_$K"

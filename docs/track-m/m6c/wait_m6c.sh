#!/bin/bash
# Track M link M6c (HPP-850; ROADMAP s122 item 767 (i)): copy of the M3a (HPP-842) file wait_m3a.sh with the names moved (m3a -> m6c, M3A -> M6C, M3a -> M6c, HPP-842 -> HPP-850); no change of meaning.
# Track M link M6c (HPP-850): port of FS15c wait_fs15c.sh - foreground wait for the detached call of launch_m6c.sh, at most 54 x 10 s =
# 540 s per invocation; prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/m657/m6c/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/m657/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null

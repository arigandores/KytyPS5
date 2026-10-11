#!/bin/bash
# Track F link F44c (HPP-793; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file wait_f38c.sh with the names moved (f38c -> f44c, F38C -> F44C, F38c -> F44c, HPP-765 -> HPP-793); no change of meaning.
# Track F link F44c (HPP-793; ROADMAP s122 item 691 (d)(4)): copy of the FS12c (HPP-752) file wait_fs12c.sh with the names moved (fs12c -> f44c, FS12C -> F44C, FS12c -> F44c, HPP-752 -> HPP-793); no change of meaning.
# Track F link F44c (HPP-793; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file wait_f33e.sh with the names moved (f33e -> f44c, F33E -> F44C, F33e -> F44c, HPP-746 -> HPP-793); no change of meaning.
# Track F link F44c (HPP-793; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file wait_f34c.sh with the names moved (f34c -> f44c, F34C -> F44C, F34c -> F44c, HPP-740 -> HPP-793); no change of meaning.
# Track F link F44c (HPP-793; port of F31c wait_f31c.sh): foreground wait for the detached call of launch_f44c.sh, at most 54 x 10 s =
# 540 s per invocation; prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/f287/f44c/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null

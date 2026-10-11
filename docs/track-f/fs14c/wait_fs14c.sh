#!/bin/bash
# Track F link FS14c (HPP-814; ROADMAP s122 item 710 (g)(3), 712 (g)(3)): copy of the FS13c (HPP-789) file wait_fs13c.sh with the names moved (fs13c -> fs14c, FS13C -> FS14C, FS13c -> FS14c, HPP-789 -> HPP-814); no change of meaning.
# Track F link FS14c (HPP-814; ROADMAP s122 item 697 (g)(3)): copy of the FS12c (HPP-752) file wait_fs12c.sh with the names moved (fs12c -> fs14c, FS12C -> FS14C, FS12c -> FS14c, HPP-752 -> HPP-814); no change of meaning.
# Track F link FS14c (HPP-814; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file wait_f33e.sh with the names moved (f33e -> fs14c, F33E -> FS14C, F33e -> FS14c, HPP-746 -> HPP-814); no change of meaning.
# Track F link FS14c (HPP-814; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file wait_f34c.sh with the names moved (f34c -> fs14c, F34C -> FS14C, F34c -> FS14c, HPP-740 -> HPP-814); no change of meaning.
# Track F link FS14c (HPP-814; port of F31c wait_f31c.sh): foreground wait for the detached call of launch_fs14c.sh, at most 54 x 10 s =
# 540 s per invocation; prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/f287/fs14c/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null

#!/bin/bash
# Track F link FS15c (HPP-822; ROADMAP s122 item 730 (g)(3)): copy of the FS14c (HPP-814) file wait_fs14c.sh with the names moved (fs14c -> fs15c, FS14C -> FS15C, FS14c -> FS15c, HPP-814 -> HPP-822); no change of meaning.
# Track F link FS15c (HPP-822; ROADMAP s122 item 710 (g)(3), 712 (g)(3)): copy of the FS13c (HPP-789) file wait_fs13c.sh with the names moved (fs13c -> fs15c, FS13C -> FS15C, FS13c -> FS15c, HPP-789 -> HPP-822); no change of meaning.
# Track F link FS15c (HPP-822; ROADMAP s122 item 697 (g)(3)): copy of the FS12c (HPP-752) file wait_fs12c.sh with the names moved (fs12c -> fs15c, FS12C -> FS15C, FS12c -> FS15c, HPP-752 -> HPP-822); no change of meaning.
# Track F link FS15c (HPP-822; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file wait_f33e.sh with the names moved (f33e -> fs15c, F33E -> FS15C, F33e -> FS15c, HPP-746 -> HPP-822); no change of meaning.
# Track F link FS15c (HPP-822; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file wait_f34c.sh with the names moved (f34c -> fs15c, F34C -> FS15C, F34c -> FS15c, HPP-740 -> HPP-822); no change of meaning.
# Track F link FS15c (HPP-822; port of F31c wait_f31c.sh): foreground wait for the detached call of launch_fs15c.sh, at most 54 x 10 s =
# 540 s per invocation; prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/f287/fs15c/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null

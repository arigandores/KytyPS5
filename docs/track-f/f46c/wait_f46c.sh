#!/bin/bash
# Track F link F46c (HPP-800; ROADMAP s122 item 702 (g)): copy of the F44c (HPP-793) file wait_f44c.sh with the names moved (f44c -> f46c, F44C -> F46C, F44c -> F46c, HPP-793 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 698 (d)(4)): copy of the F38c (HPP-765) file wait_f38c.sh with the names moved (f38c -> f46c, F38C -> F46C, F38c -> F46c, HPP-765 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 691 (d)(4)): copy of the FS12c (HPP-752) file wait_fs12c.sh with the names moved (fs12c -> f46c, FS12C -> F46C, FS12c -> F46c, HPP-752 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 683 (g)(3), 686 (v)): copy of the F33e (HPP-746) file wait_f33e.sh with the names moved (f33e -> f46c, F33E -> F46C, F33e -> F46c, HPP-746 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; ROADMAP s122 item 675 (d)(4), 682): copy of the F34c (HPP-740) file wait_f34c.sh with the names moved (f34c -> f46c, F34C -> F46C, F34c -> F46c, HPP-740 -> HPP-800); no change of meaning.
# Track F link F46c (HPP-800; port of F31c wait_f31c.sh): foreground wait for the detached call of launch_f46c.sh, at most 54 x 10 s =
# 540 s per invocation; prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/f287/f46c/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null

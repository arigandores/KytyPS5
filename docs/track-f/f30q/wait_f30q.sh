#!/bin/bash
# Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)): the F30m (HPP-723) file with the names moved (f30m -> f30q, HPP-723 -> HPP-727,
# F30M_ -> F30Q_) and the tag set of item 664 (z)(2)-(3): f30_s1_w6, f30_s<1..9>_c6 [_r1.._r3].
# Track F link F30q (HPP-727): the F29e file with the names and the tag set moved (f29e -> f30q, HPP-704 -> HPP-727); no change of meaning.
# Track F link F30q (HPP-727; port of F25m wait_f25m.sh): foreground wait for the detached call of launch_f30q.sh, at most 54 x 10 s =
# 540 s per invocation; prints DONE and the rc line, or RUNNING (call again); the stop file ends the wait (not the call).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
F=C:/kyty/f287/f30q/go_$T.out.txt
S=RUNNING
for i in $(seq 1 54); do
  if grep -q '^rc=' $F 2>/dev/null; then S=DONE; break; fi
  [ -e C:/kyty/f287/STOP ] && { S="STOP file seen $(date -u +%H:%M:%SZ)"; break; }
  sleep 10
done
echo "$S $T"
tail -5 $F 2>/dev/null

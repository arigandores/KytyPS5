#!/bin/bash
# F42a2 (HPP-805): copy of the F42a chain.sh, executable lines f42a -> f42a2 (paths, names). Was:
# F42a (HPP-779): build chain under the watchdog - bstep.sh steps (540 s limit each, rc 6 -> the step is repeated,
# ninja is incremental). Usage: chain.sh <name> <build_f42a.cmd args...>; up to 8 attempts of the step.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
cd C:/kyty/f287/f42a2
N=$1; shift
for k in 1 2 3 4 5 6 7 8; do
	bash bstep.sh "${N}_$k" "$@"
	RC=$?
	echo "chain $N attempt $k rc=$RC $(date -u +%FT%TZ)"
	[ $RC -eq 6 ] || exit $RC
done
exit 6

#!/bin/bash
# F19d2 (HPP-560): wait (sleep 5 steps, max $1 s, default 500) until there is neither the lock nor a gate process
# (argument ending with procload.py) nor STOP; exit 0 when free, 9 on time out, 4 on STOP. Only sleep and the checks.
export PATH=/usr/bin:/mingw64/bin:$PATH
cd C:/kyty/f287/f19d2
T0=$(date +%s); M=${1:-500}
while :; do
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ ! -e C:/kyty/SEALED_RUN.lock ] && python gate_free.py > /dev/null; then exit 0; fi
	[ $(( $(date +%s) - T0 )) -gt $M ] && exit 9
	sleep 5
done

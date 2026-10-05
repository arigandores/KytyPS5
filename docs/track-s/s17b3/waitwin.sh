#!/bin/bash
# S17b3: wait (bash builtins + sleep) for a new "lock released" line of the F20c series lock log, then run the given
# window script within 20 s of that line (general rule 30, amendment ROADMAP p. 535(g)). Gives up after $2 s.
L=C:/kyty/f287/f20c/runs/lock.log
last() { local l x; while IFS= read -r l; do x=$l; done < $L; printf '%s' "$x"; }
start=$(last)
echo "start line: $start"
t=0
while [ $t -lt $2 ]; do
	now=$(last)
	if [ "$now" != "$start" ] && [[ "$now" == "lock released"* ]] && [ ! -e C:/kyty/SEALED_RUN.lock ]; then
		echo "window: $now at $(date -u +%T)"
		bash "$1" "$now"
		exit $?
	fi
	sleep 2
	t=$((t + 2))
done
echo "no window in $2 s (last: $(last))"
exit 9

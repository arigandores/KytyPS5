#!/bin/bash
# S16d (HPP-608): form of C:/kyty/f287/f23f/wrun.sh - run one resumable command inside one tool call (<= 560 s): wait while
# the lock or a gate process is present (waitfree.py); when free - API line in times.txt, then the command under
# watch_s16d.py with the remaining time; killed (7 gate / 3 lock / 6 limit) -> loop again (the command resumes).
# Exit = the command's code, 1 - time up, 4 - STOP. Usage: wrun_s16d.sh <tag> <command> [args...]
[ -e C:/kyty/s288/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/s288/s16d
TAG=$1; shift
T0=$(date +%s)
K=0
while true; do
	EL=$(( $(date +%s) - T0 ))
	[ $EL -ge 520 ] && { echo "$(date -u +%FT%TZ) time up after $K attempts"; exit 1; }
	[ -e C:/kyty/s288/STOP ] && exit 4
	python waitfree.py $(( 530 - EL )) > /dev/null || { echo "$(date -u +%FT%TZ) busy, time up after $K attempts"; exit 1; }
	[ -e C:/kyty/SEALED_RUN.lock ] && continue
	EL=$(( $(date +%s) - T0 ))
	[ $EL -ge 520 ] && { echo "$(date -u +%FT%TZ) time up after $K attempts"; exit 1; }
	K=$((K + 1))
	echo "$(date -u +%FT%TZ) $TAG attempt $K start (lock and gate absent)${PREV}" >> times.txt
	PREV=""
	python watch_s16d.py --limit $(( 550 - EL )) --tag "$TAG" -- "$@" > "wrun_${TAG}_$K.log" 2>&1
	RC=$?
	case $RC in
		3) PREV="; attempt $K killed by the lock (line written after the release, rule 27)"; continue ;;
		7) echo "$(date -u +%FT%TZ) $TAG attempt $K killed rc 7 (gate)" >> times.txt; continue ;;
		*) echo "$(date -u +%FT%TZ) $TAG attempt $K rc $RC" >> times.txt; echo "rc=$RC attempts=$K"; exit $RC ;;
	esac
done

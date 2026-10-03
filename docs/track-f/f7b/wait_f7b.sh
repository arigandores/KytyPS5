#!/bin/bash
# F7b: wait for the replay phase to finish, at most $2 s (default 540).
PH=${1:-hist}; MAX=${2:-540}
D=C:/kyty/f287/f7b
S=0
while [ ! -e $D/rd/done_$PH.txt ] && [ $S -lt $MAX ]; do sleep 10; S=$((S+10)); done
if [ -e $D/rd/done_$PH.txt ]; then cat $D/rd/done_$PH.txt; else echo "still running after $S s"; fi

#!/bin/bash
# Track F link F27c (HPP-694; port of F26c launch_f26c.sh): ONLY launches one detached call of go_f27c.sh <arg> (process rule p.324(i):
# the launcher only launches, the wait is wait_f27c.sh <= 540 s per tool command, separate commands).  ITEM 634 (a)(3): no guard / hold
# check and no block here - the one guard check of the call runs inside go_f27c.sh right after the lock.  A previous output of a refused
# call is moved to old/ before the new call (rule p.309(i)).  The output go_<arg>.out.txt ends with the line rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f27c
TM=${F27C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  base|return|f27_v0|f27_v0b|f27_v1a|f27_v1b|f27_v1c|f27_v0_r[12]|f27_v0b_r[12]|f27_v1[abc]_r[12]) ;;
  *) echo "usage: launch_f27c.sh base|return|f27_v0|f27_v0b|f27_v1a|f27_v1b|f27_v1c[_r1|_r2]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f27c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F27c launch_f27c previous output of $T moved to f27c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F27c launch_f27c detached call: bash $G/go_f27c.sh $T" >> "$TM"
F27C_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f27c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched

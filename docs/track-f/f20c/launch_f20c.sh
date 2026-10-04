#!/bin/bash
# Track F link F20c (HPP-561): ONLY launches one detached call of go_f20c.sh <tag> (process rule p.324(i): the launcher only launches, the
# wait is wait_f20c.sh <= 540 s per tool command, separate commands).  Port of F18e launch_f18e.sh.  A previous output of a refused call
# (rc 3 / 5, or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  FS6b window (ROADMAP s122 item 473, HPP-556): the file C:/kyty/f287/FS6B_WINDOW present with mtime younger than
# 900 s => the tag is not launched, a times.txt line, exit 6 (interference, not an attempt, item 473(b)(5)); the caller repeats the check
# not more often than once per 60 s; older than 900 s => the window expired, a times.txt line, the tag goes (the file is not deleted).
# F20C_FS6B_WINDOW / F20C_TIMES override the paths and F20C_DRYRUN=1 stops before the launch (fixtures only).  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f20c
W=${F20C_FS6B_WINDOW:-C:/kyty/f287/FS6B_WINDOW}
TM=${F20C_TIMES:-C:/kyty/f287/times.txt}
case "$T" in f20_v0[1-9]|f20_v[12][0-9]|f20_v30) ;; *) echo "usage: launch_f20c.sh f20_v01..f20_v30"; exit 2;; esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ -e "$W" ]; then
  AGE=$(( $(date +%s) - $(stat -c %Y "$W") ))
  if [ "$AGE" -lt 900 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20c FS6b window active (FS6B_WINDOW age ${AGE} s < 900, p.473): $T not launched (interference, not an attempt); recheck >= 60 s" >> "$TM"
    echo "FS6b window active age ${AGE} s"; exit 6
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20c FS6b window expired (FS6B_WINDOW age ${AGE} s >= 900, p.473; file kept): series goes, $T" >> "$TM"
fi
[ "$F20C_DRYRUN" = 1 ] && { echo "dryrun"; exit 0; }
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f20c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20c launch_f20c previous output of $T moved to f20c/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F20c launch_f20c detached call: bash $G/go_f20c.sh $T" >> "$TM"
nohup bash -c "bash $G/go_f20c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched

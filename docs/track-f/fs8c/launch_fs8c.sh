#!/bin/bash
# Track F link FS8c (HPP-573): ONLY launches one detached call of go_fs8c.sh <tag> (process rule p.324(i): the launcher only launches, the wait
# is wait_fs8c.sh <= 540 s per tool command, separate commands).  Port of FS7c launch_fs7c.sh.  A previous output of a refused call (rc 3 / 5,
# or rc 1 before the emulator start) is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends with the line
# rc=<n>.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/fs8c
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
case "$T" in fs8_v|fs8_w|fs8_ef) ;; *) echo "usage: launch_fs8c.sh <fs8_v|fs8_w|fs8_ef>"; exit 2;; esac
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_fs8c.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS8c launch_fs8c previous output of $T moved to fs8c/old/" >> C:/kyty/f287/times.txt
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FS8c launch_fs8c detached call: bash $G/go_fs8c.sh $T" >> C:/kyty/f287/times.txt
nohup bash -c "bash $G/go_fs8c.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched

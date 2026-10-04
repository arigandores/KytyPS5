#!/bin/bash
# FS6b (HPP-556): run one stand slice (sstep.sh / sstepL.sh) in the gaps of a foreign series: under the lock or a procload.py
# process - only sleep; a slice killed by the watchdog (rc 3/5/7/8) is rerun into the same file name.
# Usage: sloop.sh <sstep.sh|sstepL.sh> <mode> <fix> <N> <first>
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs6b
S=$1; shift
for k in $(seq 1 100); do
	[ -e C:/kyty/f287/STOP ] && exit 4
	if [ -e C:/kyty/SEALED_RUN.lock ]; then sleep 5; continue; fi
	bash $S "$@"; RC=$?
	case $RC in 3|5|7|8) sleep 5; continue;; esac
	exit $RC
done
exit 9

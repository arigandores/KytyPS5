#!/bin/bash
# F47e (HPP-810): wait (poll 5 s, at most WAIT_S) until there is neither the lock, STOP nor a live gate process (argv ending with the gate
# script name, assembled at run time - item 698(e)), then run one replay step by rdw_f47e.sh (its watchdog kills the replay when the gate
# comes back, item 431(v)(1)).  usage: bash waitrun_f47e.sh <wait_s> <tag> <script.py> <limit_s>   (RD_* from the caller)
# EXIT: 9 still busy after wait_s; otherwise rdw_f47e.sh's code.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
W=${1:-300}; shift
G=C:/kyty/f287/f47e
t0=$(date +%s)
while :; do
  [ -e C:/kyty/SEALED_RUN.lock ] && exit 3
  [ -e C:/kyty/f287/STOP ] && exit 4
  N=$(python -c "
import psutil, os
nm = 'proc' + 'load.py'
print(len([p for p in psutil.process_iter(['pid', 'cmdline']) if p.info['pid'] != os.getpid() and any(a.replace(chr(92), '/').endswith('/' + nm) or a == nm for a in (p.info['cmdline'] or []))]))")
  [ "$N" = "0" ] && break
  [ $(( $(date +%s) - t0 )) -ge $W ] && { echo "$(date -u +%FT%TZ) waitrun: gate busy after $W s"; exit 9; }
  sleep 5
done
echo "$(date -u +%FT%TZ) waitrun: free after $(( $(date +%s) - t0 )) s"
bash $G/rdw_f47e.sh "$@"

#!/bin/bash
# Track F link F14c (HPP-489): run one qrenderdoc --python script (no replay) on one capture with a watchdog (form of rdsd_f12f.sh).
# usage: bash rdrun_f14c.sh <script.py> <capture.rdc> <out.txt> [watchdog_s]
# The watchdog is 50 s by default: while a run link of another track is in_progress no command of this link may exceed 60 s
# (ROADMAP p.371(e)(2), p.400(z)).  The lock or STOP appearing while qrenderdoc runs kills it (by its own pid, never by image name).
# EXIT: 0 'done' in the output; 1 no 'done'; 2 usage; 3 lock; 4 STOP.  ASCII only.
export PATH=/usr/bin:/mingw64/bin:$PATH
SCR=${1:-}; CAP=${2:-}; OUTF=${3:-}; WMAX=${4:-50}
[ -n "$SCR" ] && [ -n "$CAP" ] && [ -n "$OUTF" ] || { echo "usage: rdrun_f14c.sh <script.py> <capture.rdc> <out.txt> [watchdog_s]"; exit 2; }
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
RDHOME="/c/Program Files/RenderDoc"
rm -f "$OUTF"
RD_CAP="$CAP" RD_OUT="$OUTF" "$RDHOME/qrenderdoc.exe" --python "$SCR" > "$OUTF.qrd.txt" 2>&1 &
QP=$!
WP=$(cat /proc/$QP/winpid 2>/dev/null)
WS=0; WHY=''
while kill -0 $QP 2>/dev/null; do
  if grep -q '^done' "$OUTF" 2>/dev/null; then sleep 2; break; fi
  if [ -e C:/kyty/SEALED_RUN.lock ]; then WHY=lock; break; fi
  if [ -e C:/kyty/f287/STOP ]; then WHY=stop; break; fi
  if [ $WS -ge $WMAX ]; then WHY=watchdog; break; fi
  sleep 1; WS=$((WS+1))
done
if kill -0 $QP 2>/dev/null; then
  kill -9 $QP 2>/dev/null
  [ -n "$WP" ] && taskkill //F //PID "$WP" > /dev/null 2>&1
  echo "qrenderdoc pid $QP/$WP killed ($WHY)"
fi
wait $QP 2>/dev/null
echo "rdrun end after ~$WS s why=${WHY:-none} out=$(wc -l < "$OUTF" 2>/dev/null) lines"
[ "$WHY" = lock ] && exit 3
[ "$WHY" = stop ] && exit 4
grep -q '^done' "$OUTF" 2>/dev/null || exit 1
exit 0

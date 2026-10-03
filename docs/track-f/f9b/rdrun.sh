#!/bin/bash
# F9b: rdrun.sh <out-file> <watchdog-s> VAR=val ... ; runs qrenderdoc --python rd_f9b.py with the given env, kills on watchdog.
export PATH=/usr/bin:/mingw64/bin:$PATH
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCK; exit 3; }
[ -e C:/kyty/f287/f9/STOP ] && { echo STOP; exit 4; }
OUTF=$1; WD=$2; shift 2
for kv in "$@"; do export "$kv"; done
export RD_OUT=$OUTF
"/c/Program Files/RenderDoc/qrenderdoc.exe" --python C:/kyty/f287/f9/f9b/rd_f9b.py &
PID=$!
T=0
while kill -0 $PID 2>/dev/null; do
  sleep 2; T=$((T+2))
  if [ $T -ge $WD ]; then echo "watchdog $WD s"; taskkill //F //IM qrenderdoc.exe >/dev/null 2>&1; break; fi
done
wait $PID 2>/dev/null
echo "wall $T s"
tail -c 300 "$OUTF"

#!/bin/bash
# F11a2 (HPP-460): window check p.277(g)/p.372(b) and the RenderDoc replay of rd_f11a.py (read only) in ONE command,
# foreground; inner watchdog MAX s (default 540) kills qrenderdoc on timeout, on STOP or on the lock.
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH; export PYTHONIOENCODING=utf-8
MAX=${1:-540}
D=C:/kyty/f287/f11a2; T=C:/kyty/f287/times.txt
tl(){ echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F11a2 (HPP-460) $*" >> $T; }
python $D/winchk_f11a2.py; rc=$?
[ $rc -ne 0 ] && { echo "window rc $rc - replay not started"; exit 5; }
if tasklist //FI "IMAGENAME eq qrenderdoc.exe" 2>/dev/null | grep -qi qrenderdoc; then tl "qrenderdoc alive - not started"; exit 6; fi
mkdir -p $D/rd
tl "replay start (qrenderdoc --python C:/kyty/f287/f11a/rd_f11a.py, RD_OUT $D/rd, watchdog $MAX s); GLCache before: $(python C:/kyty/f287/f7b/glsha.py)"
RD_OUT=$D/rd "C:/Program Files/RenderDoc/qrenderdoc.exe" --python C:/kyty/f287/f11a/rd_f11a.py > $D/rd/qrd.txt 2>&1 &
P=$!; S=0; WHY=""
while kill -0 $P 2>/dev/null; do
  sleep 5; S=$((S+5))
  if [ $S -ge $MAX ]; then WHY="watchdog $MAX s"; break; fi
  if [ -e C:/kyty/f287/STOP ] || [ -e C:/kyty/SEALED_RUN.lock ]; then WHY="STOP or lock appeared"; break; fi
done
if [ -n "$WHY" ]; then tl "replay stopped: $WHY, taskkill"; taskkill //F //IM qrenderdoc.exe; fi
wait $P; R=$?
tl "replay end rc=$R after ~$S s; GLCache after: $(python C:/kyty/f287/f7b/glsha.py)"
echo "replay rc=$R after ~$S s"

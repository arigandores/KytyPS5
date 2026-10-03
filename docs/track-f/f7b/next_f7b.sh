#!/bin/bash
# F7b (HPP-398): only LAUNCHES the RenderDoc replay of rd_f7b.py (detached), waiting is wait_f7b.sh (<= 540 s per call).
# next_f7b.sh <phase hist|debug> [watchdog s]  ; RD_DBG passes through for the debug phase.
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH; export PYTHONIOENCODING=utf-8
PH=${1:-hist}; MAX=${2:-3000}
D=C:/kyty/f287/f7b; T=C:/kyty/f287/times.txt
tl(){ echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F7b (HPP-398) $*" >> $T; }
W=$(python $D/win_f7b.py); rc=$?
tl "window p.277(g) before replay $PH: $W (rc $rc)"
[ $rc -ne 0 ] && { echo "closed: $W"; exit 5; }
if tasklist //FI "IMAGENAME eq qrenderdoc.exe" 2>/dev/null | grep -qi qrenderdoc; then tl "qrenderdoc alive - not started"; exit 6; fi
if tasklist //FI "IMAGENAME eq kyty_emulator.exe" 2>/dev/null | grep -qi kyty_emulator; then tl "emulator alive - not started"; exit 6; fi
mkdir -p $D/rd
rm -f $D/rd/done_$PH.txt
tl "replay $PH start (qrenderdoc --python rd_f7b.py, watchdog $MAX s); GLCache before: $(python $D/glsha.py)"
nohup bash -c "RD_PHASE=$PH \"C:/Program Files/RenderDoc/qrenderdoc.exe\" --python $D/rd_f7b.py > $D/rd/qrd_$PH.txt 2>&1 & P=\$!; S=0; while kill -0 \$P 2>/dev/null; do sleep 5; S=\$((S+5)); if [ \$S -ge $MAX ]; then echo \"\$(date -u +%Y-%m-%dT%H:%M:%SZ) F7b (HPP-398) replay $PH watchdog $MAX s, taskkill\" >> $T; taskkill //F //IM qrenderdoc.exe; break; fi; if [ -e C:/kyty/f287/STOP ] || [ -e C:/kyty/SEALED_RUN.lock ]; then echo \"\$(date -u +%Y-%m-%dT%H:%M:%SZ) F7b (HPP-398) replay $PH stopped: STOP or lock appeared, taskkill\" >> $T; taskkill //F //IM qrenderdoc.exe; break; fi; done; wait \$P; R=\$?; echo \"\$(date -u +%Y-%m-%dT%H:%M:%SZ) F7b (HPP-398) replay $PH end rc=\$R after ~\$S s; GLCache after: \$(python $D/glsha.py)\" >> $T; echo rc=\$R > $D/rd/done_$PH.txt" > $D/rd/runner_$PH.txt 2>&1 &
echo launched

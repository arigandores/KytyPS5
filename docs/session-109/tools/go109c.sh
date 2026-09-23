#!/bin/bash
# Session 109: pred/04_frm109.md - frame-time ABBA cspfree=0|1 as a MEASUREMENT (nothing ships, no video).
# Installed build 2f593229.  Holds the sealed-run lock.
L=/c/kyty/s109/go109c.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s109
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go109c.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs109
log "frm109 start"
python C:/kyty/s109/enter_scene.py frm109 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s109/gates_base.txt \
  --pred C:/kyty/s109/pred/04_frm109.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 cspfree=0|dawalk=1 dawalklead=1 cspfree=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > frm109.stdout.txt 2>&1
log "frm109 rc=$? $(tail -1 frm109.stdout.txt)"
python C:/kyty/s109/frm109.py frm109 --out C:/kyty/s109/runs109/frm109_score.json > runs109/frm109_score.stdout.txt 2>&1
log "frm109 score $(grep -o 'VERDICT: .*' runs109/frm109_score.stdout.txt | head -1)"
log "done"

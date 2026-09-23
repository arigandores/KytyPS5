#!/bin/bash
# Session 106: pred/01_gwall.md run gw106 (installs d23094df), then the scorer.
L=/c/kyty/s106/go106.log
cd /c/kyty/s106
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "gw106 start"
python C:/kyty/s106/enter_scene.py gw106 --hold 600 --attempts 1 --gates-file C:/kyty/s106/gates_base.txt \
  --pred C:/kyty/s106/pred/01_gwall.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=0 dawalklead=1 plkstat=1|dawalk=1 dawalklead=1 plkstat=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 > gw106.stdout.txt 2>&1
log "gw106 rc=$? $(tail -1 gw106.stdout.txt) bin=$(python -c "import json;print(json.load(open('gw106.json'))['binary_sha256'][:8])")"
mkdir -p runs106
python C:/kyty/s106/gw106.py gw106 --out C:/kyty/s106/runs106/gw106_score.json > runs106/gw106_score.stdout.txt 2>&1
log "gw106 score rc=$? $(grep -o 'VERDICT: .*' runs106/gw106_score.stdout.txt | head -1)"
log "done"

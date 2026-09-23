#!/bin/bash
# Session 107: pred/01_obs107.md run obs107 (installs dd567a0f), then the scorer.
L=/c/kyty/s107/go107.log
cd /c/kyty/s107
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "obs107 start"
python C:/kyty/s107/enter_scene.py obs107 --hold 300 --attempts 1 --gates-file C:/kyty/s107/gates_obs.txt \
  --pred C:/kyty/s107/pred/01_obs107.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > obs107.stdout.txt 2>&1
log "obs107 rc=$? $(tail -1 obs107.stdout.txt) bin=$(python -c "import json;print(json.load(open('obs107.json'))['binary_sha256'][:8])")"
mkdir -p runs107
python C:/kyty/s107/obs107.py obs107 --out C:/kyty/s107/runs107/obs107_score.json > runs107/obs107_score.stdout.txt 2>&1
log "obs107 score rc=$? $(grep -o 'VERDICT: .*' runs107/obs107_score.stdout.txt | head -1)"
log "done"

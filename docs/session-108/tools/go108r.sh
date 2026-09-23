#!/bin/bash
# Session 108, ROADMAP §0.1 "СЕССИЯ 108" item 8: the new build 379777bb (cspfam default 0, rollback) - install, pinned video
# vid108r with gates_base.txt (cspfam absent => the default), glitch scan, check108r.py.  Holds the sealed-run lock.
L=/c/kyty/s108/go108r.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s108
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go108r.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
log "vid108r start"
python C:/kyty/s108/enter_scene.py vid108r --hold 120 --attempts 1 --rec --gates-file C:/kyty/s108/gates_base.txt \
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid108r.stdout.txt 2>&1
log "vid108r rc=$? $(tail -1 vid108r.stdout.txt)"
mkdir -p vidframes_vid108r runs108
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s108/rec_vid108r.mp4 4 6 C:/kyty/s108/vidframes_vid108r > vid108r_glitch.txt 2>&1
log "vidglitch $(tail -1 vid108r_glitch.txt)"
python C:/kyty/s108/check108r.py --out C:/kyty/s108/runs108/check108r.json > runs108/check108r.stdout.txt 2>&1
log "check108r $(grep -o '"verdict": "[A-Z]*"' runs108/check108r.stdout.txt)"
log "done"

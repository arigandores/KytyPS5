#!/bin/bash
# Session 108, ROADMAP §0.1 "СЕССИЯ 108" item 5: the new build fc78c564 (cspfam default 4) - install, pinned video
# vid108 with gates_base.txt (cspfam absent => the default), glitch scan, check108.py.  Holds the sealed-run lock.
L=/c/kyty/s108/go108v.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s108
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go108v.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
log "vid108 start"
python C:/kyty/s108/enter_scene.py vid108 --hold 120 --attempts 1 --rec --gates-file C:/kyty/s108/gates_base.txt \
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid108.stdout.txt 2>&1
log "vid108 rc=$? $(tail -1 vid108.stdout.txt)"
mkdir -p vidframes_vid108 runs108
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s108/rec_vid108.mp4 4 6 C:/kyty/s108/vidframes_vid108 > vid108_glitch.txt 2>&1
log "vidglitch $(tail -1 vid108_glitch.txt)"
python C:/kyty/s108/check108.py --out C:/kyty/s108/runs108/check108.json > runs108/check108.stdout.txt 2>&1
log "check108 $(grep -o '"verdict": "[A-Z]*"' runs108/check108.stdout.txt)"
log "done"

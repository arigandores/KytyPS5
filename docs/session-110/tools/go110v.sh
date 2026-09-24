#!/bin/bash
# Session 110, ROADMAP §0.1 "СЕССИЯ 110" item 6: the new build 072861c8 (cspfree default 1) - install, pinned video
# vid110 with gates_base.txt (cspfree absent => the default), glitch scan, check110.py.  Holds the sealed-run lock.
L=/c/kyty/s110/go110v.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s110
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go110v.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
log "vid110 start"
python C:/kyty/s110/enter_scene.py vid110 --hold 120 --attempts 1 --rec --gates-file C:/kyty/s110/gates_base.txt \
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid110.stdout.txt 2>&1
log "vid110 rc=$? $(tail -1 vid110.stdout.txt)"
mkdir -p vidframes_vid110 runs110
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s110/rec_vid110.mp4 4 6 C:/kyty/s110/vidframes_vid110 > vid110_glitch.txt 2>&1
log "vidglitch $(tail -1 vid110_glitch.txt)"
python C:/kyty/s110/check110.py --out C:/kyty/s110/runs110/check110.json > runs110/check110.stdout.txt 2>&1
log "check110 $(grep -o '"verdict": "[A-Z]*"' runs110/check110.stdout.txt)"
log "done"

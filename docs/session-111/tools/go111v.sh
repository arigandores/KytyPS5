#!/bin/bash
# Session 111, ROADMAP §0.1 "СЕССИЯ 111" item 5: the new build 0c8a13f2 (daslot default 1) - install, pinned video
# vid111 with gates_base.txt (daslot and cspfree absent => the defaults), glitch scan, check111.py.  Holds the lock.
L=/c/kyty/s111/go111v.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s111
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go111v.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
log "vid111 start"
python C:/kyty/s111/enter_scene.py vid111 --hold 120 --attempts 1 --rec --gates-file C:/kyty/s111/gates_base.txt \
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid111.stdout.txt 2>&1
log "vid111 rc=$? $(tail -1 vid111.stdout.txt)"
mkdir -p vidframes_vid111 runs111
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s111/rec_vid111.mp4 4 6 C:/kyty/s111/vidframes_vid111 > vid111_glitch.txt 2>&1
log "vidglitch $(tail -1 vid111_glitch.txt)"
python C:/kyty/s111/check111.py --out C:/kyty/s111/runs111/check111.json > runs111/check111.stdout.txt 2>&1
log "check111 $(grep -o '"verdict": "[A-Z]*"' runs111/check111.stdout.txt)"
log "done"

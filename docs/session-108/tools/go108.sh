#!/bin/bash
# Session 108: pred/01_cspfam.md - fam108 ABBA (installs build fd1d0bd7), score, and the pinned video only on
# SHIP_PENDING_VIDEO.  Holds C:/kyty/SEALED_RUN.lock for the whole chain: a heartbeat does nothing while it exists.
L=/c/kyty/s108/go108.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s108
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go108.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
log "fam108 start"
python C:/kyty/s108/enter_scene.py fam108 --hold 600 --attempts 1 --gates-file C:/kyty/s108/gates_base.txt \
  --pred C:/kyty/s108/pred/01_cspfam.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 cspfam=0|dawalk=1 dawalklead=1 cspfam=4" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > fam108.stdout.txt 2>&1
log "fam108 rc=$? $(tail -1 fam108.stdout.txt)"
mkdir -p runs108
python C:/kyty/s108/fam108.py fam108 --out C:/kyty/s108/runs108/fam108_score.json > runs108/fam108_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs108/fam108_score.stdout.txt | head -1)
log "fam108 score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    python C:/kyty/s108/enter_scene.py vfm108 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s108/gates_fam4.txt \
      --pred C:/kyty/s108/pred/01_cspfam.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vfm108.stdout.txt 2>&1
    log "vfm108 rc=$?"
    mkdir -p vidframes_vfm108
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s108/rec_vfm108.mp4 4 6 C:/kyty/s108/vidframes_vfm108 > vfm108_glitch.txt 2>&1
    log "vidglitch $(tail -1 vfm108_glitch.txt)"
    python C:/kyty/s108/fam108.py fam108 --out C:/kyty/s108/runs108/fam108_score_video.json \
      --video-meta C:/kyty/s108/vfm108.json --video-report C:/kyty/s108/vfm108_glitch.txt > runs108/fam108_score_video.stdout.txt 2>&1
    log "fam108 video score $(grep -o 'VERDICT: .*' runs108/fam108_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

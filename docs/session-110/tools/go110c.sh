#!/bin/bash
# Session 110: pred/03_shp110.md - the ship ABBA cspfree=0|1 (600 s, pinned; installed build b3f7a2c9), score, and
# the pinned video vsh110 only on SHIP_PENDING_VIDEO.  Holds the sealed-run lock.
L=/c/kyty/s110/go110c.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s110
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go110c.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs110
log "shp110 start"
python C:/kyty/s110/enter_scene.py shp110 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s110/gates_base.txt \
  --pred C:/kyty/s110/pred/03_shp110.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 cspfree=0|dawalk=1 dawalklead=1 cspfree=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > shp110.stdout.txt 2>&1
log "shp110 rc=$? $(tail -1 shp110.stdout.txt)"
python C:/kyty/s110/shp110.py shp110 --out C:/kyty/s110/runs110/shp110_score.json > runs110/shp110_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs110/shp110_score.stdout.txt | head -1)
log "shp110 score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    python C:/kyty/s110/enter_scene.py vsh110 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s110/gates_free1.txt \
      --pred C:/kyty/s110/pred/03_shp110.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vsh110.stdout.txt 2>&1
    log "vsh110 rc=$?"
    mkdir -p vidframes_vsh110
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s110/rec_vsh110.mp4 4 6 C:/kyty/s110/vidframes_vsh110 > vsh110_glitch.txt 2>&1
    log "vidglitch $(tail -1 vsh110_glitch.txt)"
    python C:/kyty/s110/shp110.py shp110 --out C:/kyty/s110/runs110/shp110_score_video.json \
      --video-meta C:/kyty/s110/vsh110.json --video-report C:/kyty/s110/vsh110_glitch.txt > runs110/shp110_score_video.stdout.txt 2>&1
    log "shp110 video score $(grep -o 'VERDICT: .*' runs110/shp110_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

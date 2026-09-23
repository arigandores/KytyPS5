#!/bin/bash
# Session 106: pred/02_dabatch.md - dab106 ABBA, score, and the pinned video only on SHIP_PENDING_VIDEO.
L=/c/kyty/s106/go106b.log
cd /c/kyty/s106
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "dab106 start"
python C:/kyty/s106/enter_scene.py dab106 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s106/gates_base.txt \
  --pred C:/kyty/s106/pred/02_dabatch.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 dabatch=64|dawalk=1 dawalklead=1 dabatch=8" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > dab106.stdout.txt 2>&1
log "dab106 rc=$? $(tail -1 dab106.stdout.txt)"
mkdir -p runs106
python C:/kyty/s106/dab106.py dab106 --out C:/kyty/s106/runs106/dab106_score.json > runs106/dab106_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs106/dab106_score.stdout.txt | head -1)
log "dab106 score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    python C:/kyty/s106/enter_scene.py vdb106 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s106/gates_dab8.txt \
      --pred C:/kyty/s106/pred/02_dabatch.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vdb106.stdout.txt 2>&1
    log "vdb106 rc=$?"
    mkdir -p vidframes_vdb106
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s106/rec_vdb106.mp4 4 6 C:/kyty/s106/vidframes_vdb106 > vdb106_glitch.txt 2>&1
    log "vidglitch $(tail -1 vdb106_glitch.txt)"
    python C:/kyty/s106/dab106.py dab106 --out C:/kyty/s106/runs106/dab106_score_video.json \
      --video-meta C:/kyty/s106/vdb106.json --video-report C:/kyty/s106/vdb106_glitch.txt > runs106/dab106_score_video.stdout.txt 2>&1
    log "dab106 video score $(grep -o 'VERDICT: .*' runs106/dab106_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

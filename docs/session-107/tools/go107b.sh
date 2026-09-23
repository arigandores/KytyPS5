#!/bin/bash
# Session 107: pred/02_dabatch2.md - dab107 ABBA, score, and the pinned video only on SHIP_PENDING_VIDEO.
L=/c/kyty/s107/go107b.log
cd /c/kyty/s107
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "dab107 start"
python C:/kyty/s107/enter_scene.py dab107 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s107/gates_base.txt \
  --pred C:/kyty/s107/pred/02_dabatch2.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 dabatch=8|dawalk=1 dawalklead=1 dabatch=2" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > dab107.stdout.txt 2>&1
log "dab107 rc=$? $(tail -1 dab107.stdout.txt)"
mkdir -p runs107
python C:/kyty/s107/dab107.py dab107 --out C:/kyty/s107/runs107/dab107_score.json > runs107/dab107_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs107/dab107_score.stdout.txt | head -1)
log "dab107 score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    python C:/kyty/s107/enter_scene.py vdb107 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s107/gates_dab2.txt \
      --pred C:/kyty/s107/pred/02_dabatch2.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vdb107.stdout.txt 2>&1
    log "vdb107 rc=$?"
    mkdir -p vidframes_vdb107
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s107/rec_vdb107.mp4 4 6 C:/kyty/s107/vidframes_vdb107 > vdb107_glitch.txt 2>&1
    log "vidglitch $(tail -1 vdb107_glitch.txt)"
    python C:/kyty/s107/dab107.py dab107 --out C:/kyty/s107/runs107/dab107_score_video.json \
      --video-meta C:/kyty/s107/vdb107.json --video-report C:/kyty/s107/vdb107_glitch.txt > runs107/dab107_score_video.stdout.txt 2>&1
    log "dab107 video score $(grep -o 'VERDICT: .*' runs107/dab107_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

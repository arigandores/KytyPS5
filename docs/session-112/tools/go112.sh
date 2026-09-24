#!/bin/bash
# Session 112: pred/01 vdg112 (installs b47b58a9; ABBA daslot=0 daguard=0 | daslot=1 daguard=1, smemocheck=1 in place)
# -> on GO pred/02 net112 (ABBA daslot=1 daguard=1 | daslot=0 daguard=0, 600 s)
# -> on REVERT_PENDING_VIDEO the pinned video vnet112 (gates_guard0.txt) and the re-score;
# -> on KEEP the pinned video vid112 of the build (defaults) and check112.py (ROADMAP "СЕССИЯ 112" item 4).
# Holds the sealed-run lock for the whole chain.
L=/c/kyty/s112/go112.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s112
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go112.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs112
log "vdg112 start"
python C:/kyty/s112/enter_scene.py vdg112 --hold 300 --attempts 1 --gates-file C:/kyty/s112/gates_chk.txt \
  --pred C:/kyty/s112/pred/01_vdg112.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 daslot=0 daguard=0|dawalk=1 dawalklead=1 daslot=1 daguard=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vdg112.stdout.txt 2>&1
log "vdg112 rc=$? $(tail -1 vdg112.stdout.txt)"
python C:/kyty/s112/vdg112.py --out C:/kyty/s112/runs112/vdg112_score.json > runs112/vdg112_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs112/vdg112_score.stdout.txt | head -1)
log "vdg112 score $V"
[ "$V" = "VERDICT: GO" ] || { log "stop after vdg112"; exit 0; }
log "net112 start"
python C:/kyty/s112/enter_scene.py net112 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s112/gates_base.txt \
  --pred C:/kyty/s112/pred/02_net112.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 daslot=1 daguard=1|dawalk=1 dawalklead=1 daslot=0 daguard=0" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > net112.stdout.txt 2>&1
log "net112 rc=$? $(tail -1 net112.stdout.txt)"
python C:/kyty/s112/net112.py net112 --out C:/kyty/s112/runs112/net112_score.json > runs112/net112_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs112/net112_score.stdout.txt | head -1)
log "net112 score $V"
case "$V" in
  *REVERT_PENDING_VIDEO*)
    python C:/kyty/s112/enter_scene.py vnet112 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s112/gates_guard0.txt \
      --pred C:/kyty/s112/pred/02_net112.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vnet112.stdout.txt 2>&1
    log "vnet112 rc=$?"
    mkdir -p vidframes_vnet112
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s112/rec_vnet112.mp4 4 6 C:/kyty/s112/vidframes_vnet112 > vnet112_glitch.txt 2>&1
    log "vidglitch $(tail -1 vnet112_glitch.txt)"
    python C:/kyty/s112/net112.py net112 --out C:/kyty/s112/runs112/net112_score_video.json \
      --video-meta C:/kyty/s112/vnet112.json --video-report C:/kyty/s112/vnet112_glitch.txt > runs112/net112_score_video.stdout.txt 2>&1
    log "net112 video score $(grep -o 'VERDICT: .*' runs112/net112_score_video.stdout.txt | head -1)"
    ;;
  *KEEP*)
    python C:/kyty/s112/enter_scene.py vid112 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s112/gates_base.txt \
      KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid112.stdout.txt 2>&1
    log "vid112 rc=$?"
    mkdir -p vidframes_vid112
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s112/rec_vid112.mp4 4 6 C:/kyty/s112/vidframes_vid112 > vid112_glitch.txt 2>&1
    log "vidglitch $(tail -1 vid112_glitch.txt)"
    python C:/kyty/s112/check112.py --out C:/kyty/s112/runs112/check112.json > runs112/check112.stdout.txt 2>&1
    log "check112 $(grep -o '"verdict": "[A-Z]*"' runs112/check112.stdout.txt)"
    ;;
esac
log "done"

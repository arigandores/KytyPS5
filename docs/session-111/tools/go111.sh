#!/bin/bash
# Session 111: pred/01 obs111 (installed 072861c8, plkstat=1) -> on BUILD_DASLOT pred/02 vds111 (installs c8235c90,
# daslot=2 smemocheck=1) -> on GO pred/03 shp111 (ABBA daslot=0|1, 600 s) -> on SHIP_PENDING_VIDEO the pinned video
# vss111.  Holds the sealed-run lock for the whole chain.
L=/c/kyty/s111/go111.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s111
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go111.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs111
log "obs111 start"
python C:/kyty/s111/enter_scene.py obs111 --hold 300 --attempts 1 --no-install --gates-file C:/kyty/s111/gates_obs111.txt \
  --pred C:/kyty/s111/pred/01_obs111.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > obs111.stdout.txt 2>&1
log "obs111 rc=$? $(tail -1 obs111.stdout.txt)"
python C:/kyty/s111/obs111.py --out C:/kyty/s111/runs111/obs111_score.json > runs111/obs111_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs111/obs111_score.stdout.txt | head -1)
log "obs111 score $V"
[ "$V" = "VERDICT: BUILD_DASLOT" ] || { log "stop after obs111"; exit 0; }
log "vds111 start"
python C:/kyty/s111/enter_scene.py vds111 --hold 300 --attempts 1 --gates-file C:/kyty/s111/gates_slot2.txt \
  --pred C:/kyty/s111/pred/02_vds111.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vds111.stdout.txt 2>&1
log "vds111 rc=$? $(tail -1 vds111.stdout.txt)"
python C:/kyty/s111/vds111.py --out C:/kyty/s111/runs111/vds111_score.json > runs111/vds111_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs111/vds111_score.stdout.txt | head -1)
log "vds111 score $V"
[ "$V" = "VERDICT: GO" ] || { log "stop after vds111"; exit 0; }
log "shp111 start"
python C:/kyty/s111/enter_scene.py shp111 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s111/gates_base.txt \
  --pred C:/kyty/s111/pred/03_shp111.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 daslot=0|dawalk=1 dawalklead=1 daslot=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > shp111.stdout.txt 2>&1
log "shp111 rc=$? $(tail -1 shp111.stdout.txt)"
python C:/kyty/s111/shp111.py shp111 --out C:/kyty/s111/runs111/shp111_score.json > runs111/shp111_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs111/shp111_score.stdout.txt | head -1)
log "shp111 score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    python C:/kyty/s111/enter_scene.py vss111 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s111/gates_slot1.txt \
      --pred C:/kyty/s111/pred/03_shp111.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vss111.stdout.txt 2>&1
    log "vss111 rc=$?"
    mkdir -p vidframes_vss111
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s111/rec_vss111.mp4 4 6 C:/kyty/s111/vidframes_vss111 > vss111_glitch.txt 2>&1
    log "vidglitch $(tail -1 vss111_glitch.txt)"
    python C:/kyty/s111/shp111.py shp111 --out C:/kyty/s111/runs111/shp111_score_video.json \
      --video-meta C:/kyty/s111/vss111.json --video-report C:/kyty/s111/vss111_glitch.txt > runs111/shp111_score_video.stdout.txt 2>&1
    log "shp111 video score $(grep -o 'VERDICT: .*' runs111/shp111_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

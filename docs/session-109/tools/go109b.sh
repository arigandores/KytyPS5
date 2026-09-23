#!/bin/bash
# Session 109: knob cspfree - pred/01b vfy109 (installs build 2f593229) -> on GO pred/02 ent109b (8 entries) ->
# on PASS pred/03 frf109 (ABBA 600 s) -> on SHIP_PENDING_VIDEO the pinned video vff109.  Holds the sealed-run lock.
L=/c/kyty/s109/go109b.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s109
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go109b.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs109
log "vfy109 start"
python C:/kyty/s109/enter_scene.py vfy109 --hold 300 --attempts 1 --gates-file C:/kyty/s109/gates_free2.txt \
  --pred C:/kyty/s109/pred/01b_vfy109.md KYTY_PIPELINE_PRECACHE=gfx KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
  > vfy109.stdout.txt 2>&1
log "vfy109 rc=$? $(tail -1 vfy109.stdout.txt)"
python C:/kyty/s109/vfy109.py --out C:/kyty/s109/runs109/vfy109_score.json > runs109/vfy109_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs109/vfy109_score.stdout.txt | head -1)
log "vfy109 score $V"
[ "$V" = "VERDICT: GO" ] || { log "stop after vfy109"; exit 0; }
ORDER=ABBAABBA
for i in 1 2 3 4 5 6 7 8; do
  arm=${ORDER:$((i-1)):1}
  if [ "$arm" = "A" ]; then G=gates_free0.txt; else G=gates_free1.txt; fi
  log "ent109b_$i start arm $arm ($G)"
  python C:/kyty/s109/enter_scene.py ent109b_$i --hold 150 --attempts 1 --no-install --gates-file C:/kyty/s109/$G \
    --pred C:/kyty/s109/pred/02_ent109b.md KYTY_PIPELINE_PRECACHE=gfx KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
    > ent109b_$i.stdout.txt 2>&1
  log "ent109b_$i rc=$? $(tail -1 ent109b_$i.stdout.txt)"
done
python C:/kyty/s109/ent109b.py --out C:/kyty/s109/runs109/ent109b_score.json > runs109/ent109b_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs109/ent109b_score.stdout.txt | head -1)
log "ent109b score $V"
[ "$V" = "VERDICT: PASS" ] || { log "stop after ent109b"; exit 0; }
log "frf109 start"
python C:/kyty/s109/enter_scene.py frf109 --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s109/gates_base.txt \
  --pred C:/kyty/s109/pred/03_frf109.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 cspfree=0|dawalk=1 dawalklead=1 cspfree=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > frf109.stdout.txt 2>&1
log "frf109 rc=$? $(tail -1 frf109.stdout.txt)"
python C:/kyty/s109/frf109.py frf109 --out C:/kyty/s109/runs109/frf109_score.json > runs109/frf109_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs109/frf109_score.stdout.txt | head -1)
log "frf109 score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    python C:/kyty/s109/enter_scene.py vff109 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s109/gates_free1.txt \
      --pred C:/kyty/s109/pred/03_frf109.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vff109.stdout.txt 2>&1
    log "vff109 rc=$?"
    mkdir -p vidframes_vff109
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s109/rec_vff109.mp4 4 6 C:/kyty/s109/vidframes_vff109 > vff109_glitch.txt 2>&1
    log "vidglitch $(tail -1 vff109_glitch.txt)"
    python C:/kyty/s109/frf109.py frf109 --out C:/kyty/s109/runs109/frf109_score_video.json \
      --video-meta C:/kyty/s109/vff109.json --video-report C:/kyty/s109/vff109_glitch.txt > runs109/frf109_score_video.stdout.txt 2>&1
    log "frf109 video score $(grep -o 'VERDICT: .*' runs109/frf109_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

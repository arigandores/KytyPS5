#!/bin/bash
# Session 110: pred/02_stl110b.md - eight entries A B B A A B B A (compute precache off, pinned), then stl110b.py.
# Every entry runs the installed build b3f7a2c9.  Holds the sealed-run lock.
L=/c/kyty/s110/go110b.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s110
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go110b.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
ORDER=ABBAABBA
for i in 1 2 3 4 5 6 7 8; do
  arm=${ORDER:$((i-1)):1}
  if [ "$arm" = "A" ]; then G=gates_free0.txt; else G=gates_free1.txt; fi
  INST="--no-install"
  log "stl110b_$i start arm $arm ($G) $INST"
  python C:/kyty/s110/enter_scene.py stl110b_$i --hold 150 --attempts 1 $INST --gates-file C:/kyty/s110/$G \
    --pred C:/kyty/s110/pred/02_stl110b.md KYTY_PIPELINE_PRECACHE=gfx KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
    > stl110b_$i.stdout.txt 2>&1
  log "stl110b_$i rc=$? $(tail -1 stl110b_$i.stdout.txt)"
done
mkdir -p runs110
python C:/kyty/s110/stl110b.py --out C:/kyty/s110/runs110/stl110b_score.json > runs110/stl110b_score.stdout.txt 2>&1
log "stl110b score $(grep -o "VERDICT: .*" runs110/stl110b_score.stdout.txt | head -1)"
log "done"

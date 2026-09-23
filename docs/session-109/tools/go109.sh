#!/bin/bash
# Session 109: pred/01_ent109.md - eight entries A B B A A B B A (compute precache off, pinned), then ent109.py.
# Entry 1 installs build e90f5543; the rest run the installed binary.  Holds the sealed-run lock.
L=/c/kyty/s109/go109.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s109
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go109.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
ORDER=ABBAABBA
for i in 1 2 3 4 5 6 7 8; do
  arm=${ORDER:$((i-1)):1}
  if [ "$arm" = "A" ]; then G=gates_fam0.txt; else G=gates_fam4.txt; fi
  if [ $i -eq 1 ]; then INST=""; else INST="--no-install"; fi
  log "ent109_$i start arm $arm ($G) $INST"
  python C:/kyty/s109/enter_scene.py ent109_$i --hold 150 --attempts 1 $INST --gates-file C:/kyty/s109/$G \
    --pred C:/kyty/s109/pred/01_ent109.md KYTY_PIPELINE_PRECACHE=gfx KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
    > ent109_$i.stdout.txt 2>&1
  log "ent109_$i rc=$? $(tail -1 ent109_$i.stdout.txt)"
done
mkdir -p runs109
python C:/kyty/s109/ent109.py --out C:/kyty/s109/runs109/ent109_score.json > runs109/ent109_score.stdout.txt 2>&1
log "ent109 score $(grep -o 'VERDICT: .*' runs109/ent109_score.stdout.txt | head -1)"
log "done"

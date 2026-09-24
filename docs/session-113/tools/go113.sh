#!/bin/bash
# Session 113: pred/01 vbn113 (installs 94362eae; bdanarrow=2, 300 s) - on NOT_EVALUABLE (NEW regime) one repeat vbn113b.
# Holds the sealed-run lock for the whole chain.
L=/c/kyty/s113/go113.log
LOCK=/c/kyty/SEALED_RUN.lock
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
echo "go113.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs113
for T in vbn113 vbn113b; do
  INST=""
  [ "$T" = "vbn113b" ] && INST="--no-install"
  log "$T start"
  python C:/kyty/s113/enter_scene.py $T --hold 300 --attempts 1 $INST --gates-file C:/kyty/s113/gates_narrow2.txt \
    --pred C:/kyty/s113/pred/01_vbn113.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
  python C:/kyty/s113/vbn113.py --tag $T --out C:/kyty/s113/runs113/${T}_score.json > runs113/${T}_score.stdout.txt 2>&1
  V=$(grep -o 'VERDICT: .*' runs113/${T}_score.stdout.txt | head -1)
  log "$T score $V"
  [ "$V" = "VERDICT: NOT_EVALUABLE" ] || break
done
log "done"

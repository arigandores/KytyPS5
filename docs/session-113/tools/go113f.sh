#!/bin/bash
# Session 113, pred/01f (ROADMAP item 18): installs the PINNED build 1678d3f4 (exact check, GC-trigger env, priority-stall instrument)
# after a hash check, then the verify run of bdanarrow=2 with KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 (a forced OLD regime),
# vbn113m then vbn113n; stops at the first verdict other than NOT_EVALUABLE.  Refuses a held lock.  Holds the sealed-run
# lock for the chain.
L=/c/kyty/s113/go113f.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373
PINNED=/c/kyty/s113/kyty_emulator_1678d3f4.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go113f.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$PINNED" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
cp "$PINNED" "$GAME"
mkdir -p runs113
for T in vbn113m vbn113n; do
  SHA=$(sha256sum "$GAME" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
  log "$T start"
  python C:/kyty/s113/enter_scene.py $T --hold 300 --attempts 1 --no-install --gates-file C:/kyty/s113/gates_narrow2.txt \
    --pred C:/kyty/s113/pred/01f_vbn113f.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 \
    > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
  python C:/kyty/s113/vbn113f.py --tag $T --out C:/kyty/s113/runs113/${T}_score.json > runs113/${T}_score.stdout.txt 2>&1
  V=$(grep -o 'VERDICT: .*' runs113/${T}_score.stdout.txt | head -1)
  log "$T score $V"
  [ "$V" = "VERDICT: NOT_EVALUABLE" ] || break
done
log "done"

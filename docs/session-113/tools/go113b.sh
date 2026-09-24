#!/bin/bash
# Session 113, pred/01b vbn113b (replaces pred/01 before any run - pre-run audit, ROADMAP item 5): installs the PINNED
# copy of build 7d9fa028 after checking its hash, then the verify run of bdanarrow=2 (300 s); on NOT_EVALUABLE (NEW
# regime) one repeat vbn113b.  Refuses to start if the sealed-run lock is already held.  Holds the lock for the chain.
L=/c/kyty/s113/go113b.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f
PINNED=/c/kyty/s113/kyty_emulator_7d9fa028.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go113b.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$PINNED" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
cp "$PINNED" "$GAME"
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
log "installed $SHA"
mkdir -p runs113
for T in vbn113 vbn113b; do
  log "$T start"
  python C:/kyty/s113/enter_scene.py $T --hold 300 --attempts 1 --no-install --gates-file C:/kyty/s113/gates_narrow2.txt \
    --pred C:/kyty/s113/pred/01b_vbn113b.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
  python C:/kyty/s113/vbn113b.py --tag $T --out C:/kyty/s113/runs113/${T}_score.json > runs113/${T}_score.stdout.txt 2>&1
  V=$(grep -o 'VERDICT: .*' runs113/${T}_score.stdout.txt | head -1)
  log "$T score $V"
  [ "$V" = "VERDICT: NOT_EVALUABLE" ] || break
done
log "done"

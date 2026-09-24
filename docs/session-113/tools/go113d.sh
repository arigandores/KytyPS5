#!/bin/bash
# Session 113, pred/01d (ROADMAP items 11, 14): installs the PINNED build 5ba0e188 (exact check) after a hash check, then
# the verify run of bdanarrow=2, relaunched until the entry starts OLD (vbn113g..vbn113j; stops at the first verdict other
# than NOT_EVALUABLE).  Refuses a held lock.  Holds the sealed-run lock for the chain.
L=/c/kyty/s113/go113d.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=5ba0e1881565dc922651cb15e3df0fb9ddec39a33d117428cb6faf27a4948ba3
PINNED=/c/kyty/s113/kyty_emulator_5ba0e188.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go113d.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$PINNED" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
cp "$PINNED" "$GAME"
mkdir -p runs113
for T in vbn113g vbn113h vbn113i vbn113j; do
  SHA=$(sha256sum "$GAME" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
  log "$T start"
  python C:/kyty/s113/enter_scene.py $T --hold 300 --attempts 1 --no-install --gates-file C:/kyty/s113/gates_narrow2.txt \
    --pred C:/kyty/s113/pred/01d_vbn113d.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
  python C:/kyty/s113/vbn113d.py --tag $T --out C:/kyty/s113/runs113/${T}_score.json > runs113/${T}_score.stdout.txt 2>&1
  V=$(grep -o 'VERDICT: .*' runs113/${T}_score.stdout.txt | head -1)
  log "$T score $V"
  [ "$V" = "VERDICT: NOT_EVALUABLE" ] || break
done
log "done"

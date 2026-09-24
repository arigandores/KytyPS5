#!/bin/bash
# Session 113, pred/01c (ROADMAP item 10): the verify run of bdanarrow=2 on the installed build 7d9fa028, relaunched until
# the entry starts in the OLD regime (vbn113c..vbn113f; stops at the first verdict other than NOT_EVALUABLE).  Refuses a
# held lock; checks the installed sha before each entry.  Holds the sealed-run lock for the chain.
L=/c/kyty/s113/go113c.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=7d9fa0288099204f16974292a0d474afee80e58df43770612e11b8d5db5d6e5f
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go113c.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
mkdir -p runs113
for T in vbn113c vbn113d vbn113e vbn113f; do
  SHA=$(sha256sum "$GAME" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
  log "$T start"
  python C:/kyty/s113/enter_scene.py $T --hold 300 --attempts 1 --no-install --gates-file C:/kyty/s113/gates_narrow2.txt \
    --pred C:/kyty/s113/pred/01c_vbn113c.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
  python C:/kyty/s113/vbn113c.py --tag $T --out C:/kyty/s113/runs113/${T}_score.json > runs113/${T}_score.stdout.txt 2>&1
  V=$(grep -o 'VERDICT: .*' runs113/${T}_score.stdout.txt | head -1)
  log "$T score $V"
  [ "$V" = "VERDICT: NOT_EVALUABLE" ] || break
done
log "done"

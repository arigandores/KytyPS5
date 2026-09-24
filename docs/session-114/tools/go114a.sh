#!/bin/bash
# Session 114, pred/01 (ROADMAP items 2-5): the positive control of titleasync - ctl114a (titleasync=0) and ctl114b
# (titleasync=1), each 180 s with KYTY_MAIN_STALL_TEST=3000:3000, on the pinned build 916f6489; scored by ctl114.py.
# NOT TO BE RUN before the user allows game runs (ROADMAP 114 item 3).  Refuses a held lock; holds it for the chain.
L=/c/kyty/s114/go114a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c
PINNED=/c/kyty/s114/kyty_emulator_916f6489.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
cd /c/kyty/s114
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go114a.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$PINNED" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
cp "$PINNED" "$GAME"
mkdir -p runs114
for T in ctl114a ctl114b; do
  V=0; [ "$T" = "ctl114b" ] && V=1
  SHA=$(sha256sum "$GAME" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
  log "$T start (titleasync=$V)"
  python C:/kyty/s114/enter_scene.py $T --hold 180 --attempts 1 --no-install --gates-file C:/kyty/s114/gates_title$V.txt \
    --pred C:/kyty/s114/pred/01_ctl114.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_MAIN_STALL_TEST=3000:3000 \
    > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
done
python C:/kyty/s114/ctl114.py --out C:/kyty/s114/runs114/ctl114_score.json > runs114/ctl114_score.stdout.txt 2>&1
log "ctl114 score $(grep -o 'VERDICT: .*' runs114/ctl114_score.stdout.txt | head -1)"
log "done"

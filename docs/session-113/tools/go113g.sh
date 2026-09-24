#!/bin/bash
# Session 113, pred/02 (ROADMAP items 3, 17, 19): the ABBA shn113 of bdanarrow=0|1 in a forced OLD regime
# (KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024) on the build 1678d3f4; one repeat shn113b if the run is not admitted as OLD;
# on SHIP_PENDING_VIDEO the pinned, shifted video vsn113 (gates_narrow1.txt) and the re-score.  Refuses a held lock.
# Holds the sealed-run lock for the chain.
L=/c/kyty/s113/go113g.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373
PINNED=/c/kyty/s113/kyty_emulator_1678d3f4.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
SCHED="KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 bdanarrow=0|dawalk=1 dawalklead=1 bdanarrow=1"
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go113g.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
if [ "$SHA" != "$EXPECT" ]; then
  SHA=$(sha256sum "$PINNED" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
  cp "$PINNED" "$GAME"
fi
mkdir -p runs113
V=""
for T in shn113 shn113b; do
  SHA=$(sha256sum "$GAME" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
  log "$T start"
  python C:/kyty/s113/enter_scene.py $T --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s113/gates_base.txt \
    --pred C:/kyty/s113/pred/02_shn113.md "$SCHED" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
    KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
  python C:/kyty/s113/shn113.py $T --out C:/kyty/s113/runs113/${T}_score.json > runs113/${T}_score.stdout.txt 2>&1
  V=$(grep -o 'VERDICT: .*' runs113/${T}_score.stdout.txt | head -1)
  log "$T score $V"
  NEWREG=$(python -c "import json,sys; d=json.load(open('C:/kyty/s113/runs113/${T}_score.json')); a=(d.get('arming') or {}).get('checks') or {}; print(1 if a.get('REGIME_OLD_ARM0') is False else 0)" 2>/dev/null)
  [ "$NEWREG" = "1" ] || break
  log "$T: REGIME_OLD_ARM0 false - one repeat"
done
case "$V" in
  *SHIP_PENDING_VIDEO*)
    log "vsn113 start"
    python C:/kyty/s113/enter_scene.py vsn113 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s113/gates_narrow1.txt \
      --pred C:/kyty/s113/pred/02_shn113.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_BUFFER_GC_TRIGGER_SHIFT_MB=1024 \
      > vsn113.stdout.txt 2>&1
    log "vsn113 rc=$?"
    mkdir -p vidframes_vsn113
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s113/rec_vsn113.mp4 4 6 C:/kyty/s113/vidframes_vsn113 > vsn113_glitch.txt 2>&1
    log "vidglitch $(tail -1 vsn113_glitch.txt)"
    python C:/kyty/s113/shn113.py $T --out C:/kyty/s113/runs113/${T}_score_video.json \
      --video-meta C:/kyty/s113/vsn113.json --video-report C:/kyty/s113/vsn113_glitch.txt > runs113/${T}_score_video.stdout.txt 2>&1
    log "$T video score $(grep -o 'VERDICT: .*' runs113/${T}_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

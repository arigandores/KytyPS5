#!/bin/bash
# Session 114, pred/02 (ROADMAP items 2, 4, 5, 7): the ABBA ttl114 of titleasync=0|1 (600 s, pinned) on the build
# 916f6489; on SHIP_PENDING_VIDEO the pinned video vtt114 (gates_title1.txt) and the re-score.  Refuses a held lock.
# Holds the sealed-run lock for the chain.
L=/c/kyty/s114/go114b.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=916f64898a5a31c697ad0d823f0795850acc160cf56271b566e8ae330c7c3b2c
PINNED=/c/kyty/s114/kyty_emulator_916f6489.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
SCHED="KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1 titleasync=0|dawalk=1 dawalklead=1 titleasync=1"
cd /c/kyty/s114
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go114b.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
if [ "$SHA" != "$EXPECT" ]; then
  SHA=$(sha256sum "$PINNED" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
  cp "$PINNED" "$GAME"
fi
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
mkdir -p runs114
T=ttl114
log "$T start"
python C:/kyty/s114/enter_scene.py $T --hold 600 --attempts 1 --no-install --gates-file C:/kyty/s114/gates_base.txt \
  --pred C:/kyty/s114/pred/02_ttl114.md "$SCHED" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 \
  > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
python C:/kyty/s114/ttl114.py $T --out C:/kyty/s114/runs114/${T}_score.json > runs114/${T}_score.stdout.txt 2>&1
V=$(grep -o 'VERDICT: .*' runs114/${T}_score.stdout.txt | head -1)
log "$T score $V"
case "$V" in
  *SHIP_PENDING_VIDEO*)
    log "vtt114 start"
    python C:/kyty/s114/enter_scene.py vtt114 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s114/gates_title1.txt \
      --pred C:/kyty/s114/pred/02_ttl114.md KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vtt114.stdout.txt 2>&1
    log "vtt114 rc=$?"
    mkdir -p vidframes_vtt114
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s114/rec_vtt114.mp4 4 6 C:/kyty/s114/vidframes_vtt114 > vtt114_glitch.txt 2>&1
    log "vidglitch $(tail -1 vtt114_glitch.txt)"
    python C:/kyty/s114/ttl114.py $T --out C:/kyty/s114/runs114/${T}_score_video.json \
      --video-meta C:/kyty/s114/vtt114.json --video-report C:/kyty/s114/vtt114_glitch.txt > runs114/${T}_score_video.stdout.txt 2>&1
    log "$T video score $(grep -o 'VERDICT: .*' runs114/${T}_score_video.stdout.txt | head -1)"
    ;;
esac
log "done"

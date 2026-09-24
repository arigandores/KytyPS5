#!/bin/bash
# Session 113, ROADMAP item 21: the video pass vid113 of the installed build 1678d3f4 with today's defaults (pinned,
# gates_base.txt, no GC-trigger shift), its glitch report and check113.py.  Refuses a held lock.  Holds the sealed-run
# lock for the chain.
L=/c/kyty/s113/go113h.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=1678d3f40ace01cd652d375dbfd8229b58341846b465cc4fd91817634cbe3373
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
cd /c/kyty/s113
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go113h.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
mkdir -p runs113 vidframes_vid113
log "vid113 start"
python C:/kyty/s113/enter_scene.py vid113 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s113/gates_base.txt \
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid113.stdout.txt 2>&1
log "vid113 rc=$? $(tail -1 vid113.stdout.txt)"
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s113/rec_vid113.mp4 4 6 C:/kyty/s113/vidframes_vid113 > vid113_glitch.txt 2>&1
log "vidglitch $(tail -1 vid113_glitch.txt)"
python C:/kyty/s113/check113.py --out C:/kyty/s113/runs113/check113.json > runs113/check113.stdout.txt 2>&1
log "check113 $(grep -o '"verdict": "[A-Z]*"' runs113/check113.stdout.txt)"
log "done"

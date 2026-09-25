#!/bin/bash
# Session 115, ROADMAP item 2, seal pred/01_chk115.md: the ring-fix build (titleasync default 1) - the video vid115
# (gates_base.txt, 120 s) and the boot runs boot115a (defaults), boot115b (KYTY_PREPARE_MAIN_PRESENT=1, the positive
# control), boot115c (KYTY_TITLE_ASYNC=1), all with KYTY_PREPARE_HOLD_MS=10000; scored by check115.py.
# Refuses a held lock or a busy machine; holds the sealed-run lock for the chain.
L=/c/kyty/s115/go115a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=d3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64
PINNED=/c/kyty/s115/kyty_emulator_d3a981a2.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s115/pred/01_chk115.md
cd /c/kyty/s115
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s115/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy - not starting"; exit 1; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go115a.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
if [ "$SHA" != "$EXPECT" ]; then
  SHA=$(sha256sum "$PINNED" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
  cp "$PINNED" "$GAME"
fi
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
python C:/kyty/s115/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy - not starting"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
mkdir -p runs115 vidframes_vid115
run() {
  local T=$1; shift
  log "$T start"
  python C:/kyty/s115/enter_scene.py $T --attempts 1 --no-install --gates-file C:/kyty/s115/gates_base.txt --pred $PRED "$@" \
    > $T.stdout.txt 2>&1
  log "$T rc=$? $(tail -1 $T.stdout.txt)"
}
run vid115 --hold 120 --rec KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s115/rec_vid115.mp4 4 6 C:/kyty/s115/vidframes_vid115 > vid115_glitch.txt 2>&1
log "vidglitch $(tail -1 vid115_glitch.txt)"
run boot115a --hold 60 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000
run boot115b --hold 60 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 KYTY_PREPARE_MAIN_PRESENT=1
run boot115c --hold 60 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 KYTY_TITLE_ASYNC=1
python C:/kyty/s115/check115.py --out C:/kyty/s115/runs115/check115.json > runs115/check115.stdout.txt 2>&1
log "check115 $(grep -o 'VERDICT: .*' runs115/check115.stdout.txt | head -1)"
log "done"

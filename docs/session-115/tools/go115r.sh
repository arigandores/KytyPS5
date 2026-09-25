#!/bin/bash
# Session 115, ROADMAP item 5 (3), seal pred/01_chk115.md: the one repeat after NOT_ADMITTED.  Usage: go115r.sh <tag>
# where <tag> is one of vid115 boot115a boot115b boot115c.  Runs <tag>r with the sealed arguments of go115a.sh, copies
# every sealed file of the four runs byte for byte into C:/kyty/s115/rep (the repeated run's files renamed from <tag>r to
# <tag>), and scores with check115.py --root C:/kyty/s115/rep.  Same lock, load gate and idle check as go115a.sh.
T=$1
case "$T" in vid115|boot115a|boot115b|boot115c) ;; *) echo "usage: go115r.sh vid115|boot115a|boot115b|boot115c"; exit 2;; esac
R=${T}r
L=/c/kyty/s115/go115r.log
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
echo "go115r.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
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
mkdir -p runs115 rep
run() {
  local TT=$1; shift
  log "$TT start"
  python C:/kyty/s115/enter_scene.py $TT --attempts 1 --no-install --gates-file C:/kyty/s115/gates_base.txt --pred $PRED "$@" \
    > $TT.stdout.txt 2>&1
  log "$TT rc=$? $(tail -1 $TT.stdout.txt)"
}
case "$T" in
  vid115)
    mkdir -p vidframes_vid115r
    run $R --hold 120 --rec KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0
    python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s115/rec_vid115r.mp4 4 6 C:/kyty/s115/vidframes_vid115r > vid115r_glitch.txt 2>&1
    ;;
  boot115a) run $R --hold 60 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 ;;
  boot115b) run $R --hold 60 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 KYTY_PREPARE_MAIN_PRESENT=1 ;;
  boot115c) run $R --hold 60 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 KYTY_TITLE_ASYNC=1 ;;
esac
for X in vid115 boot115a boot115b boot115c; do
  S=$X; [ "$X" = "$T" ] && S=$R
  for F in "$S.json" "log_$S.txt" "stdout_$S.txt"; do
    [ -f "$F" ] && cp -p "$F" "rep/${F/$S/$X}"
  done
done
S=vid115; [ "$T" = vid115 ] && S=$R
cp -p "${S}_glitch.txt" rep/vid115_glitch.txt
python C:/kyty/s115/check115.py --root C:/kyty/s115/rep --out C:/kyty/s115/runs115/check115_rep.json > runs115/check115_rep.stdout.txt 2>&1
log "check115 (repeat $T) $(grep -o 'VERDICT: .*' runs115/check115_rep.stdout.txt | head -1)"
log "done"

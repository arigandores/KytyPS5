#!/bin/bash
# Session 116, ROADMAP §0.1 "СЕССИЯ 116" items 2-3, DRAFT seal pred/01_obs116.md: obs116 - ONE sealed observation of
# the GuestGpu phase split on the installed build d3a981a2 (git 7c73f26): Sky Garden, one attempt, 300-s hold,
# pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, KYTY_GPU_WALL=1, no recording, gates_obs116.txt (= gates_base.txt
# with mutsite=0 -> mutsite=1 in place and pathlap=1 appended); scored by obs116.py (ADMITTED / NOT_ADMITTED + report).
# Refuses: the V41_GO gate of the mutlib v4.1 workflow (ROADMAP 116 item 1: no sealed chain while it exists), a held
# lock (taken atomically with noclobber, item 3 (5)), a busy machine (procload.py with the timing-seal defaults: no
# process above 0.5 CPU s/s; it also refuses while any process with mutlib.py in its command line lives), a non-idle
# CPU/GPU.  Before the run every existing artefact of the tag is moved to C:/kyty/s116/old/<timestamp>/ (item 3 (4)),
# so the scorer can only read this run's files.  Holds C:/kyty/SEALED_RUN.lock throughout.
#   usage: go116a.sh [obs116|obs116r]      (obs116r = the one repeat pred/01_obs116.md allows after NOT_ADMITTED)
T=${1:-obs116}
case "$T" in obs116|obs116r) ;; *) echo "usage: go116a.sh [obs116|obs116r]"; exit 2;; esac
L=/c/kyty/s116/go116a.log
LOCK=/c/kyty/SEALED_RUN.lock
V41=/c/kyty/s116/V41_GO
EXPECT=d3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64
PINNED=/c/kyty/s116/kyty_emulator_d3a981a2.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s116/pred/01_obs116.md
GATES=C:/kyty/s116/gates_obs116.txt
cd /c/kyty/s116
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "go116a.sh $T requested"
if [ -e $V41 ]; then log "V41_GO present (mutlib v4.1 heavy stage allowed) - not starting"; exit 1; fi
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s116/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy (or mutlib lives) - not starting"; exit 1; }
if [ -e $V41 ]; then log "V41_GO appeared - not starting"; exit 1; fi
set -o noclobber
if ! { echo "go116a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  log "lock taken by someone else: $(cat $LOCK 2>/dev/null) - not starting"; exit 1
fi
set +o noclobber
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
if [ "$SHA" != "$EXPECT" ]; then
  SHA=$(sha256sum "$PINNED" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
  cp "$PINNED" "$GAME"
fi
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
log "files: $(sha256sum obs116.py test_obs116.py mut_obs116.py gates_obs116.txt enter_scene.py procload.py pred/01_obs116.md | cut -c1-16,65- | tr '\n' ';')"
python C:/kyty/s116/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy (or mutlib lives) - not starting"; exit 1; }
if [ -e $V41 ]; then log "V41_GO appeared - not starting"; exit 1; fi
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" log_${T}_a*.txt \
         stdout_${T}_a*.txt "runs116/$T.score.json" "runs116/$T.score.txt"; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs116
log "$T start"
python C:/kyty/s116/enter_scene.py $T --attempts 1 --no-install --gates-file $GATES --pred $PRED --hold 300 \
  KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_GPU_WALL=1 > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
python C:/kyty/s116/obs116.py --tag $T --out C:/kyty/s116/runs116/$T.score.json > runs116/$T.score.txt 2>&1
log "obs116 $T $(grep -o 'VERDICT: .*' runs116/$T.score.txt | head -1)"
log "done"

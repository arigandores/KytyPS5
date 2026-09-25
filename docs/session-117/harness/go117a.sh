#!/bin/bash
# Session 117, ROADMAP §0.1 "СЕССИЯ 117" items 4-6, seal pred/01_spn117.md: spn117 - ONE sealed observation of the
# shadow spine (knob "spine", route A stage 4 part 1) on the build 3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9 (git 36c8350): Sky Garden, one attempt,
# 300-s hold, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, no recording, gates_base.txt, schedule
# KYTY_GATE_SCHEDULE="90+1800:spine=1|spine=2" with KYTY_GATE_SCHEDULE_ABBA=1; scored by spn117.py (ADMITTED /
# NOT_ADMITTED, K5, K1, consequence).  Installs the pinned copy of the build.
# Refuses: a held lock (taken atomically with noclobber), a busy machine (procload.py: no process above 0.5 CPU s/s;
# it also refuses while any process with mutlib.py in its command line lives), a non-idle CPU/GPU.  Before the run
# every existing artefact of the tag is moved to C:/kyty/s117/old/<timestamp>/.  Holds C:/kyty/SEALED_RUN.lock.
#   usage: go117a.sh [spn117|spn117r]      (spn117r = the one repeat pred/01_spn117.md allows)
T=${1:-spn117}
case "$T" in spn117|spn117r) ;; *) echo "usage: go117a.sh [spn117|spn117r]"; exit 2;; esac
L=/c/kyty/s117/go117a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9
PINNED=/c/kyty/s117/kyty_emulator_3cde1af8.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s117/pred/01_spn117.md
GATES=C:/kyty/s117/gates_base.txt
SCHED="KYTY_GATE_SCHEDULE=90+1800:spine=1|spine=2"
cd /c/kyty/s117
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "go117a.sh $T requested"
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s117/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy (or mutlib lives) - not starting"; exit 1; }
set -o noclobber
if ! { echo "go117a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
  set +o noclobber
  log "lock taken by someone else: $(cat $LOCK 2>/dev/null) - not starting"; exit 1
fi
set +o noclobber
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$PINNED" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
cp "$PINNED" "$GAME"
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
log "files: $(sha256sum spn117.py test_spn117.py mut_spn117.py gates_base.txt enter_scene.py procload.py pred/01_spn117.md | cut -c1-16,65- | tr '\n' ';')"
python C:/kyty/s117/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy (or mutlib lives) - not starting"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" log_${T}_a*.txt \
         stdout_${T}_a*.txt "runs117/$T.score.json" "runs117/$T.score.txt"; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs117
log "$T start"
python C:/kyty/s117/enter_scene.py $T --attempts 1 --no-install --gates-file $GATES --pred $PRED --hold 300 \
  "$SCHED" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
python C:/kyty/s117/spn117.py --tag $T --out C:/kyty/s117/runs117/$T.score.json > runs117/$T.score.txt 2>&1
log "spn117 $T $(grep -o 'VERDICT: .*' runs117/$T.score.txt | head -1)"
log "done"

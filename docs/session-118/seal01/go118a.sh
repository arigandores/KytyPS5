#!/bin/bash
# Session 118, ROADMAP §0.1 "СЕССИЯ 118" items 1-3, seal pred/01_spk118.md: spk118 - ONE sealed observation of route A
# stage 4 part 2 (the spine's carry and safe plan, the slice census K3/K4) and the micro-track re-measure arm on the build
# 321175ab43ebba1664b03d307cb09e61782505a4f9628196c2f089414babcf76 (git 7bc87cd): Sky Garden, one attempt, 300-s hold,
# pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, no recording, gates_base.txt, schedule KYTY_GATE_SCHEDULE=
# "90+1800:<P>|<M>" with KYTY_GATE_SCHEDULE_ABBA=1; scored by spk118.py (ADMITTED / NOT_ADMITTED, K5, C, K3, K4,
# consequence).  Installs the pinned copy of the build.
# Refuses: a held lock (taken atomically with noclobber), a busy machine (procload.py: no process above 0.5 CPU s/s;
# it also refuses while any process with mutlib.py in its command line lives), a non-idle CPU/GPU.  Before the run
# every existing artefact of the tag is moved to C:/kyty/s118/old/<timestamp>/.  Holds C:/kyty/SEALED_RUN.lock.
#   usage: go118a.sh [spk118|spk118r]      (spk118r = the one repeat pred/01_spk118.md allows)
T=${1:-spk118}
case "$T" in spk118|spk118r) ;; *) echo "usage: go118a.sh [spk118|spk118r]"; exit 2;; esac
L=/c/kyty/s118/go118a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=321175ab43ebba1664b03d307cb09e61782505a4f9628196c2f089414babcf76
PINNED=/c/kyty/s118/kyty_emulator_321175ab.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s118/pred/01_spk118.md
GATES=C:/kyty/s118/gates_base.txt
SCHED="KYTY_GATE_SCHEDULE=90+1800:spine=2 slicecen=1 takelap=0 bindlap=0 pathlap=0 mutsite=0|spine=0 slicecen=0 takelap=1 bindlap=1 pathlap=1 mutsite=1"
cd /c/kyty/s118
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "go118a.sh $T requested"
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s118/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy (or mutlib lives) - not starting"; exit 1; }
set -o noclobber
if ! { echo "go118a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
log "files: $(sha256sum spk118.py test_spk118.py mut_spk118.py gates_base.txt enter_scene.py procload.py pred/01_spk118.md | cut -c1-16,65- | tr '\n' ';')"
python C:/kyty/s118/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy (or mutlib lives) - not starting"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" log_${T}_a*.txt \
         stdout_${T}_a*.txt "runs118/$T.score.json" "runs118/$T.score.txt"; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs118
log "$T start"
python C:/kyty/s118/enter_scene.py $T --attempts 1 --no-install --gates-file $GATES --pred $PRED --hold 300 \
  "$SCHED" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
python C:/kyty/s118/spk118.py --tag $T --out C:/kyty/s118/runs118/$T.score.json > runs118/$T.score.txt 2>&1
log "spk118 $T $(grep -o 'VERDICT: .*' runs118/$T.score.txt | head -1)"
log "done"

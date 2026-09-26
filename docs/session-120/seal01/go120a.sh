#!/bin/bash
# Session 120, ROADMAP §0.1 "СЕССИЯ 120" items 1, 2, 4 (design docs/session-120/design120.md): the measurement build of
# r1cen / r2cen / spcen on the build EXPECT below (git 0310cbb).  Sky Garden, one attempt, pinned (KYTY_GPU_CLOCK_PIN=1),
# KYTY_GPU_MARKERS=0, no recording, gates_base.txt, schedule "90+1800:<P>|<M>" with KYTY_GATE_SCHEDULE_ABBA=1:
#   P = r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1
#   M = r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1
#   smk120            UNSEALED smoke, 180-s hold (disclosed; no pred, no scorer gate)
#   cen120 / cen120r  SEALED, 300-s hold (seal pred/01_cen120.md; cen120r only on NOT_ADMITTED)
# Installs the pinned copy of the build.  Refuses: a held lock (taken atomically with noclobber), a busy machine
# (procload.py: no process above 0.5 CPU s/s; it also refuses while any process with mutlib.py in its command line
# lives), a live mutant/fixture process of this session (by name), a pre-registration whose sha differs from the
# scorers' PRED_SHA (sealed tags), a non-idle CPU/GPU.  Stale artefacts of the tag move to C:/kyty/s120/old/<ts>/.
#   usage: go120a.sh smk120|cen120|cen120r
T=${1:-}
case "$T" in
  smk120) HOLD=180; SEALED=0;;
  cen120|cen120r) HOLD=300; SEALED=1;;
  *) echo "usage: go120a.sh smk120|cen120|cen120r"; exit 2;;
esac
SCHED="KYTY_GATE_SCHEDULE=90+1800:r1cen=2 r2cen=2 spcen=1 bindlap=1 pathlap=1 mutsite=1|r1cen=0 r2cen=1 spcen=0 bindlap=1 pathlap=1 mutsite=1"
L=/c/kyty/s120/go120a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=15cdbfc6e2c9d19a9aa803beaa1dff670d3403b54b74b56f4911c456de4ca661
PINNED=/c/kyty/s120/kyty_emulator_15cdbfc6.exe
GAME="$HOME/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s120/pred/01_cen120.md
GATES=C:/kyty/s120/gates_base.txt
cd /c/kyty/s120
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "go120a.sh $T requested"
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s120/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy (or mutlib lives) - not starting"; exit 1; }
BUSY=$(powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'mut_rpk120|mut_spc120|test_rpk120|test_spc120|mutlib' -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r')
if [ -z "$BUSY" ] || [ "$BUSY" != "0" ]; then log "a mutant/fixture process lives ($BUSY) - not starting"; exit 1; fi
PREDARG=""
if [ "$SEALED" = "1" ]; then
  NSHA=$(sha256sum pred/01_cen120.md | cut -c1-64)
  for S in rpk120.py spc120.py; do
    PSHA=$(grep -o "^PRED_SHA = '[0-9a-f]*'" $S | cut -d"'" -f2)
    if [ -z "$PSHA" ] || [ "$PSHA" != "$NSHA" ]; then log "pred sha $NSHA != $S PRED_SHA '$PSHA' - not starting"; exit 1; fi
  done
  PREDARG="--pred $PRED"
fi
set -o noclobber
if ! { echo "go120a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
if [ "$SEALED" = "1" ]; then
  log "files: $(sha256sum rpk120.py test_rpk120.py mut_rpk120.py spc120.py test_spc120.py mut_spc120.py gates_base.txt enter_scene.py procload.py pred/01_cen120.md | cut -c1-16,65- | tr '\n' ';')"
fi
python C:/kyty/s120/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy (or mutlib lives) - not starting"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" log_${T}_a*.txt \
         stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs120
log "$T start (hold $HOLD, sealed $SEALED)"
python C:/kyty/s120/enter_scene.py $T --attempts 1 --no-install --gates-file $GATES $PREDARG --hold $HOLD \
  "$SCHED" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
log "done"

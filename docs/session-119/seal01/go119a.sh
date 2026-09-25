#!/bin/bash
# Session 119, ROADMAP 118 items 5-6 and 119 item 1, seal pred/01_g2_119.md: ONE sealed run of the G2 re-measure of route
# A at W = 2 on the installed build d3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64 (git 7c73f26):
# Sky Garden, one attempt, 300-s hold, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, no recording, gates_base.txt,
# schedule "90+1800:<arm0>|<arm1>" with KYTY_GATE_SCHEDULE_ABBA=1:
#   sh119 / sh119b    shadowresolve=0 shadowmask=3 | shadowresolve=1 shadowmask=3
#   mut119 / mut119b  mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1 | mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1
# Scored by g2_119.py once both runs exist (python g2_119.py --mut <m> --sh <s> --out runs119/g2_119_<s>_<m>.json).
# Installs the pinned copy of the build.  Refuses: a held lock (taken atomically with noclobber), a busy machine
# (procload.py: no process above 0.5 CPU s/s; it also refuses while any process with mutlib.py in its command line
# lives), a non-idle CPU/GPU.  Before the run every existing artefact of the tag is moved to C:/kyty/s119/old/<ts>/.
#   usage: go119a.sh sh119|sh119b|mut119|mut119b
T=${1:-}
case "$T" in
  sh119|sh119b) SCHED="KYTY_GATE_SCHEDULE=90+1800:shadowresolve=0 shadowmask=3|shadowresolve=1 shadowmask=3";;
  mut119|mut119b) SCHED="KYTY_GATE_SCHEDULE=90+1800:mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1|mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1";;
  *) echo "usage: go119a.sh sh119|sh119b|mut119|mut119b"; exit 2;;
esac
L=/c/kyty/s119/go119a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=d3a981a23fc1c5df651eef2a93ff1f02a8bffd04416adea2fd5cd2218e290f64
PINNED=/c/kyty/s119/kyty_emulator_d3a981a2.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s119/pred/01_g2_119.md
GATES=C:/kyty/s119/gates_base.txt
cd /c/kyty/s119
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "go119a.sh $T requested"
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s119/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy (or mutlib lives) - not starting"; exit 1; }
# ROADMAP 119 item 3: procload sees mutlib only by name - also refuse while a draft mutant loop or a fixture suite lives
BUSY=$(powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'mut_g2_119|test_g2_119|mutlib' -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r')
if [ -z "$BUSY" ] || [ "$BUSY" != "0" ]; then log "a mutant/fixture process lives ($BUSY) - not starting"; exit 1; fi
# ROADMAP 119 item 3: the pre-registration must be the one the scorer is sealed to
PSHA=$(grep -o "^PRED_SHA = '[0-9a-f]*'" g2_119.py | cut -d"'" -f2)
NSHA=$(sha256sum pred/01_g2_119.md | cut -c1-64)
if [ -z "$PSHA" ] || [ "$PSHA" != "$NSHA" ]; then log "pred sha $NSHA != scorer PRED_SHA '$PSHA' - not starting"; exit 1; fi
set -o noclobber
if ! { echo "go119a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
log "files: $(sha256sum g2_119.py test_g2_119.py mut_g2_119.py gates_base.txt enter_scene.py procload.py pred/01_g2_119.md | cut -c1-16,65- | tr '\n' ';')"
python C:/kyty/s119/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy (or mutlib lives) - not starting"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" log_${T}_a*.txt \
         stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs119
log "$T start"
python C:/kyty/s119/enter_scene.py $T --attempts 1 --no-install --gates-file $GATES --pred $PRED --hold 300 \
  "$SCHED" KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
log "done"

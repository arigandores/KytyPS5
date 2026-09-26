#!/bin/bash
# Session 121, ROADMAP §0.1 "СЕССИЯ 121" items 1-4 (design docs/session-121/design121.md): the R1 prototype, knob
# texmemo8, on the build EXPECT below (git 5e8e1d2).  Sky Garden, one attempt, pinned (KYTY_GPU_CLOCK_PIN=1),
# KYTY_GPU_MARKERS=0, gates_base.txt:
#   vfy121 / vfy121r  SEALED 01 (pred/01_vfy121.md, scorer vfy121.py): the verify run, 240-s hold, 4 arms in turn
#                     (no ABBA), video (enter_scene --rec):
#                     texmemo8=2 texfastcheck=1 | texmemo8=1 texfastcheck=1 | texmemo8=0 texfastcheck=1 | texmemo8=3 texfastcheck=1
#   shp121 / shp121r  SEALED 02 (pred/02_shp121.md, scorer shp121.py): 300-s hold, ABBA texmemo8=1 | texmemo8=0, no video
#   (the *r repeat only on NOT_ADMITTED)
# Installs the pinned copy of the build.  Refuses: a held lock (noclobber), a busy machine (procload.py; also while any
# mutlib.py lives), a live mutant/fixture process of this session (by name), a pre-registration whose sha differs from
# the scorer's PRED_SHA, a non-idle CPU/GPU, and for shp121|shp121r a missing sealed vfy121 PASS (ROADMAP s121 item 4:
# shp121 runs only after seal 01 PASSes; chk_vfy121.py: VFY_SCORER_SHA filled and = sha256(vfy121.py), and
# runs121/vfy121.score.json PASS, or vfy121 NOT_ADMITTED and runs121/vfy121r.score.json PASS, each written by
#   python C:/kyty/s121/vfy121.py --tag <vfy tag> --out C:/kyty/s121/runs121/<vfy tag>.score.json   (no --draft)
# with draft False, this build, that scorer).  The passing vfy tag goes to runs121/<tag>.vfytag: score the ABBA with
#   python C:/kyty/s121/shp121.py --tag <tag> --vfy $(cat runs121/<tag>.vfytag) --out runs121/<tag>.score.json
# Stale artefacts of the tag move to C:/kyty/s121/old/<ts>/.
#   usage: go121a.sh vfy121|vfy121r|shp121|shp121r
T=${1:-}
case "$T" in
  vfy121|vfy121r) HOLD=240; SC=vfy121.py; PRED=pred/01_vfy121.md
          SCHED="KYTY_GATE_SCHEDULE=90+1800:texmemo8=2 texfastcheck=1|texmemo8=1 texfastcheck=1|texmemo8=0 texfastcheck=1|texmemo8=3 texfastcheck=1"
          EXTRA=""; RECARG="--rec";;
  shp121|shp121r) HOLD=300; SC=shp121.py; PRED=pred/02_shp121.md
          SCHED="KYTY_GATE_SCHEDULE=90+1800:texmemo8=1|texmemo8=0"
          EXTRA="KYTY_GATE_SCHEDULE_ABBA=1"; RECARG="";;
  *) echo "usage: go121a.sh vfy121|vfy121r|shp121|shp121r"; exit 2;;
esac
L=/c/kyty/s121/go121a.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=0bd21ec24e546fbbb9b923c148fb76b57f45389ac166a71bad7410a3add738c7
PINNED=/c/kyty/s121/kyty_emulator_0bd21ec2.exe
GAME="$HOME/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
GATES=C:/kyty/s121/gates_base.txt
cd /c/kyty/s121
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "go121a.sh $T requested"
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
python C:/kyty/s121/procload.py --wait-s 1800 >> $L 2>&1 || { log "a process stays busy (or mutlib lives) - not starting"; exit 1; }
BUSY=$(powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'mut_shp121|test_shp121|mut_vfy121|test_vfy121|mutlib' -and \$_.ProcessId -ne \$PID }).Count" | tr -d '\r')
if [ -z "$BUSY" ] || [ "$BUSY" != "0" ]; then log "a mutant/fixture process lives ($BUSY) - not starting"; exit 1; fi
NSHA=$(sha256sum $PRED | cut -c1-64)
PSHA=$(grep -o "^PRED_SHA = '[0-9a-f]*'" $SC | cut -d"'" -f2)
if [ -z "$PSHA" ] || [ "$PSHA" != "$NSHA" ]; then log "pred sha $NSHA != $SC PRED_SHA '$PSHA' - not starting"; exit 1; fi
VT=""
if [ "$SC" = "shp121.py" ]; then
  VT=$(python C:/kyty/s121/chk_vfy121.py 2>> $L) || { log "no sealed vfy121 PASS (chk_vfy121.py refused) - not starting"; exit 1; }
  if [ "$VT" != "vfy121" ] && [ "$VT" != "vfy121r" ]; then log "chk_vfy121.py printed '$VT' - not starting"; exit 1; fi
  log "sealed verify PASS: $VT ($(sha256sum vfy121.py chk_vfy121.py runs121/$VT.score.json | cut -c1-16,65- | tr '\n' ';'))"
fi
set -o noclobber
if ! { echo "go121a.sh $T pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK; } 2>/dev/null; then
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
log "files: $(sha256sum $SC test_${SC} mut_${SC} gates_base.txt enter_scene.py procload.py $PRED | cut -c1-16,65- | tr '\n' ';')"
python C:/kyty/s121/procload.py --wait-s 0 >> $L 2>&1 || { log "a process became busy (or mutlib lives) - not starting"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
OLD=old/$(date +%Y%m%d_%H%M%S)_$T
for F in "$T.json" "log_$T.txt" "stdout_$T.txt" "$T.stdout.txt" "gpuclk_$T.csv" "cpuclk_$T.csv" "rec_$T.mp4" "rec_$T.mp4.idx" \
         log_${T}_a*.txt stdout_${T}_a*.txt; do
  if [ -f "$F" ]; then mkdir -p "$OLD"; mv "$F" "$OLD/" && log "moved stale $F to $OLD/"; fi
done
mkdir -p runs121
if [ -n "$VT" ]; then echo "$VT" > runs121/$T.vfytag; log "vfy tag $VT written to runs121/$T.vfytag (score with --vfy $VT)"; fi
log "$T start (hold $HOLD)"
python C:/kyty/s121/enter_scene.py $T --attempts 1 --no-install --gates-file $GATES --pred C:/kyty/s121/$PRED $RECARG --hold $HOLD \
  "$SCHED" $EXTRA KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > $T.stdout.txt 2>&1
log "$T rc=$? $(tail -1 $T.stdout.txt)"
log "done"

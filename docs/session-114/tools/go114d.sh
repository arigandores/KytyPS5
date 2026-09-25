#!/bin/bash
# Session 114, ROADMAP items 9-11: the checks of the default titleasync=1 on the build 8d7ba8f4 - the pinned video
# vid114 (gates_base.txt, 120 s) and the boot run boot114 (KYTY_PREPARE_HOLD_MS=10000, 120 s), scored by check114.py
# (pred/03_vid114.md).  Refuses a held lock; holds the sealed-run lock for the chain.
L=/c/kyty/s114/go114d.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec
PINNED=/c/kyty/s114/kyty_emulator_8d7ba8f4.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s114/pred/03_vid114.md
cd /c/kyty/s114
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go114d.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
if [ "$SHA" != "$EXPECT" ]; then
  SHA=$(sha256sum "$PINNED" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
  cp "$PINNED" "$GAME"
fi
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
# ROADMAP item 12 (m3): refuse to start unless the machine is idle - CPU < 15 % (3 samples) and GPU < 10 %.
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
mkdir -p runs114 vidframes_vid114
log "vid114 start"
python C:/kyty/s114/enter_scene.py vid114 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s114/gates_base.txt \
  --pred $PRED KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > vid114.stdout.txt 2>&1
log "vid114 rc=$? $(tail -1 vid114.stdout.txt)"
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s114/rec_vid114.mp4 4 6 C:/kyty/s114/vidframes_vid114 > vid114_glitch.txt 2>&1
log "vidglitch $(tail -1 vid114_glitch.txt)"
log "boot114 start"
python C:/kyty/s114/enter_scene.py boot114 --hold 120 --attempts 1 --no-install --gates-file C:/kyty/s114/gates_base.txt \
  --pred $PRED KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 > boot114.stdout.txt 2>&1
log "boot114 rc=$? $(tail -1 boot114.stdout.txt)"
python C:/kyty/s114/check114.py --out C:/kyty/s114/runs114/check114.json > runs114/check114.stdout.txt 2>&1
log "check114 $(grep -o 'VERDICT: .*' runs114/check114.stdout.txt | head -1)"
log "done"

#!/bin/bash
# Session 114, ROADMAP item 13, seal pred/03b_bootctl114.md: the two control boots boot114b (default titleasync=1) and
# boot114c (KYTY_TITLE_ASYNC=0 + gates_title0.txt), both with KYTY_PREPARE_HOLD_MS=10000 on the build 8d7ba8f4, scored by
# bootctl114.py.  Refuses a held lock or a busy machine; holds the sealed-run lock for the chain.
L=/c/kyty/s114/go114e.log
LOCK=/c/kyty/SEALED_RUN.lock
EXPECT=8d7ba8f4ae995a3da10670a095670acf0c46450675f7b61137714eb7975956ec
PINNED=/c/kyty/s114/kyty_emulator_8d7ba8f4.exe
GAME="/c/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe"
PRED=C:/kyty/s114/pred/03b_bootctl114.md
cd /c/kyty/s114
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
if [ -e $LOCK ]; then log "lock held: $(cat $LOCK) - not starting"; exit 1; fi
echo "go114e.sh pid $$ started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK
trap 'rm -f $LOCK' EXIT
SHA=$(sha256sum "$GAME" | cut -c1-64)
if [ "$SHA" != "$EXPECT" ]; then
  SHA=$(sha256sum "$PINNED" | cut -c1-64)
  [ "$SHA" = "$EXPECT" ] || { log "pinned copy sha $SHA != $EXPECT - stop"; exit 1; }
  cp "$PINNED" "$GAME"
fi
SHA=$(sha256sum "$GAME" | cut -c1-64)
[ "$SHA" = "$EXPECT" ] || { log "installed sha $SHA != $EXPECT - stop"; exit 1; }
CPU=$(powershell -NoProfile -Command "\$a=@(); 1..3 | % { \$a += (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 }; [int](\$a | Measure-Object -Average).Average" | tr -d '\r')
GPU=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1 | tr -d ' \r')
log "idle check cpu=$CPU gpu=$GPU"
if [ -z "$CPU" ] || [ -z "$GPU" ] || [ "$CPU" -ge 15 ] || [ "$GPU" -ge 10 ]; then log "machine not idle - not starting"; exit 1; fi
mkdir -p runs114
log "boot114b start"
python C:/kyty/s114/enter_scene.py boot114b --hold 60 --attempts 1 --no-install --gates-file C:/kyty/s114/gates_base.txt \
  --pred $PRED KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 > boot114b.stdout.txt 2>&1
log "boot114b rc=$? $(tail -1 boot114b.stdout.txt)"
log "boot114c start"
python C:/kyty/s114/enter_scene.py boot114c --hold 60 --attempts 1 --no-install --gates-file C:/kyty/s114/gates_title0.txt \
  --pred $PRED KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_PREPARE_HOLD_MS=10000 KYTY_TITLE_ASYNC=0 > boot114c.stdout.txt 2>&1
log "boot114c rc=$? $(tail -1 boot114c.stdout.txt)"
python C:/kyty/s114/bootctl114.py --out C:/kyty/s114/runs114/bootctl114.json > runs114/bootctl114.stdout.txt 2>&1
log "bootctl114 $(grep -o 'VERDICT: .*' runs114/bootctl114.stdout.txt | head -1)"
log "done"

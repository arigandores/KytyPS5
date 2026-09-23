#!/bin/bash
# Session 105: pred/02_m31.md runs, in the sealed order, then the scorers.
L=/c/kyty/s105/go105b.log
cd /c/kyty/s105
E="python C:/kyty/s105/enter_scene.py"
P="--pred C:/kyty/s105/pred/02_m31.md"
C="KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0"
log() { echo "[$(date +%H:%M:%S)] $*" >> $L; }
log "reg105a start (61ae7347, no install)"
$E reg105a --hold 180 --attempts 1 --no-install --gates-file C:/kyty/s105/gates_base.txt $P $C > reg105a.stdout.txt 2>&1
log "reg105a rc=$? $(tail -1 reg105a.stdout.txt) bin=$(python -c "import json;print(json.load(open('reg105a.json'))['binary_sha256'][:8])")"
$E reg105b --hold 180 --attempts 1 --gates-file C:/kyty/s105/gates_base.txt $P $C > reg105b.stdout.txt 2>&1
log "reg105b rc=$? $(tail -1 reg105b.stdout.txt) bin=$(python -c "import json;print(json.load(open('reg105b.json'))['binary_sha256'][:8])")"
$E ctx105 --hold 300 --attempts 1 --no-install --gates-file C:/kyty/s105/gates_ctx2.txt $P $C > ctx105.stdout.txt 2>&1
log "ctx105 rc=$? $(tail -1 ctx105.stdout.txt)"
$E abb105 --hold 900 --attempts 1 --no-install --gates-file C:/kyty/s105/gates_base.txt $P \
  "KYTY_GATE_SCHEDULE=90+1800:ctxtick=0|ctxtick=1" KYTY_GATE_SCHEDULE_ABBA=1 $C > abb105.stdout.txt 2>&1
log "abb105 rc=$? $(tail -1 abb105.stdout.txt)"
$E vct105 --hold 120 --attempts 1 --no-install --rec --gates-file C:/kyty/s105/gates_ctx1.txt $P KYTY_GPU_MARKERS=0 > vct105.stdout.txt 2>&1
log "vct105 rc=$?"
mkdir -p vidframes_vct105
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s105/rec_vct105.mp4 4 6 C:/kyty/s105/vidframes_vct105 > vct105_glitch.txt 2>&1
log "vidglitch $(tail -1 vct105_glitch.txt)"
for i in 01 02 03 04 05 06 07 08 09 10; do
  $E ect105_$i --hold 20 --attempts 1 --no-install --gates-file C:/kyty/s105/gates_ctx2.txt $P $C > ect105_$i.stdout.txt 2>&1
  log "ect105_$i rc=$? $(tail -1 ect105_$i.stdout.txt)"
done
mkdir -p runs105
python C:/kyty/s105/ctx105.py abb105 --out C:/kyty/s105/runs105/ctx105_score.json > runs105/ctx105_score.stdout.txt 2>&1
log "ctx105 score $(grep -o 'VERDICT: .*' runs105/ctx105_score.stdout.txt | head -1)"
python C:/kyty/s105/check105.py --out C:/kyty/s105/runs105/check105.json > runs105/check105.stdout.txt 2>&1
log "check105 rc=$?"
log "done"

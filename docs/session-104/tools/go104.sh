#!/bin/bash
# Session 104: Stage 1 (sh104, mut104) and Stage 2 (dwk104), exactly the RUNS104.md commands, one pass.
L=/c/kyty/s104/go104.log
cd /c/kyty/s104
echo "[$(date +%H:%M:%S)] sh104 start" >> $L
python C:/kyty/s104/enter_scene.py sh104 --hold 300 --attempts 1 --no-install \
  --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/02_a_stage1.md \
  "KYTY_GATE_SCHEDULE=90+1800:shadowresolve=0 shadowmask=3|shadowresolve=4 shadowmask=3" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > sh104.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] sh104 rc=$? $(tail -1 sh104.stdout.txt)" >> $L
python C:/kyty/s104/enter_scene.py mut104 --hold 300 --attempts 1 --no-install \
  --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/02_a_stage1.md \
  "KYTY_GATE_SCHEDULE=90+1800:mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1|mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > mut104.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] mut104 rc=$? $(tail -1 mut104.stdout.txt)" >> $L
python C:/kyty/s104/enter_scene.py dwk104 --hold 600 --attempts 1 --no-install \
  --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/03_dawalk.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=0 dawalklead=1|dawalk=1 dawalklead=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > dwk104.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] dwk104 rc=$? $(tail -1 dwk104.stdout.txt)" >> $L
mkdir -p C:/kyty/s104/runs104
python C:/kyty/s104/a104.py --mut mut104 --sh sh104 --out C:/kyty/s104/runs104/a104_score.json > runs104/a104_score.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] a104 rc=$?" >> $L
python C:/kyty/s104/dwk104.py dwk104 --out C:/kyty/s104/runs104/dwk104_score.json > runs104/dwk104_score.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] dwk104 score rc=$?" >> $L

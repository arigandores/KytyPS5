#!/bin/bash
# Session 104: the one repeat of mut104 allowed by pred/02 (INVALID on NO_FATAL_MARKER), then the dawalk video pass.
L=/c/kyty/s104/go104.log
cd /c/kyty/s104
echo "[$(date +%H:%M:%S)] mut104b start" >> $L
python C:/kyty/s104/enter_scene.py mut104b --hold 300 --attempts 1 --no-install \
  --gates-file C:/kyty/s104/gates_base.txt --pred C:/kyty/s104/pred/02_a_stage1.md \
  "KYTY_GATE_SCHEDULE=90+1800:mutwide=0 mutsite=1 amut=1 plkstat=1 pathlap=1|mutwide=15 mutsite=1 amut=1 plkstat=1 pathlap=1" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > mut104b.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] mut104b rc=$? $(tail -1 mut104b.stdout.txt)" >> $L
python C:/kyty/s104/gen_gates.py --with dawalk=1 --out C:/kyty/s104/gates_dawalk1.txt >> $L 2>&1
python C:/kyty/s104/enter_scene.py vwk104 --hold 120 --attempts 1 --no-install --rec \
  --gates-file C:/kyty/s104/gates_dawalk1.txt --pred C:/kyty/s104/pred/03_dawalk.md \
  KYTY_GPU_MARKERS=0 > vwk104.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] vwk104 rc=$? $(tail -1 vwk104.stdout.txt)" >> $L
python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s104/rec_vwk104.mp4 4 6 C:/kyty/s104/vidframes_vwk104 \
  > C:/kyty/s104/vwk104_glitch.txt 2>&1
echo "[$(date +%H:%M:%S)] vidglitch rc=$? $(tail -1 vwk104_glitch.txt)" >> $L
python C:/kyty/s104/a104.py --mut mut104b --sh sh104 --out C:/kyty/s104/runs104/a104_score_b.json > runs104/a104_score_b.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] a104b rc=$?" >> $L
python C:/kyty/s104/dwk104.py dwk104 --out C:/kyty/s104/runs104/dwk104_score_video.json \
  --video-meta C:/kyty/s104/vwk104.json --video-report C:/kyty/s104/vwk104_glitch.txt > runs104/dwk104_score_video.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] dwk104 video score rc=$?" >> $L

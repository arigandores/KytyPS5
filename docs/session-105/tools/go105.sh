#!/bin/bash
# Session 105: candidate 1 (pred/01_dawalklead.md) - the ABBA run, then its score; the video only on SHIP_PENDING_VIDEO.
L=/c/kyty/s105/go105.log
cd /c/kyty/s105
mkdir -p runs105
echo "[$(date +%H:%M:%S)] lead105 start" >> $L
python C:/kyty/s105/enter_scene.py lead105 --hold 600 --attempts 1 --no-install \
  --gates-file C:/kyty/s105/gates_base.txt --pred C:/kyty/s105/pred/01_dawalklead.md \
  "KYTY_GATE_SCHEDULE=90+1800:dawalk=1 dawalklead=1|dawalk=1 dawalklead=2" \
  KYTY_GATE_SCHEDULE_ABBA=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 > lead105.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] lead105 rc=$? $(tail -1 lead105.stdout.txt)" >> $L
python C:/kyty/s105/lead105.py lead105 --out C:/kyty/s105/runs105/lead105_score.json > runs105/lead105_score.stdout.txt 2>&1
V=$(grep -o "VERDICT: [A-Z_]*" runs105/lead105_score.stdout.txt | head -1)
echo "[$(date +%H:%M:%S)] lead105 score $V" >> $L
if [ "$V" = "VERDICT: SHIP_PENDING_VIDEO" ]; then
  python C:/kyty/s105/gen_gates.py --with dawalklead=2 --out C:/kyty/s105/gates_lead2.txt >> $L 2>&1
  python C:/kyty/s105/enter_scene.py vld105 --hold 120 --attempts 1 --no-install --rec \
    --gates-file C:/kyty/s105/gates_lead2.txt --pred C:/kyty/s105/pred/01_dawalklead.md \
    KYTY_GPU_MARKERS=0 > vld105.stdout.txt 2>&1
  echo "[$(date +%H:%M:%S)] vld105 rc=$?" >> $L
  mkdir -p vidframes_vld105
  python C:/kyty/scripts/s51_vidglitch.py C:/kyty/s105/rec_vld105.mp4 4 6 C:/kyty/s105/vidframes_vld105 > vld105_glitch.txt 2>&1
  python C:/kyty/s105/lead105.py lead105 --out C:/kyty/s105/runs105/lead105_score_video.json \
    --video-meta C:/kyty/s105/vld105.json --video-report C:/kyty/s105/vld105_glitch.txt > runs105/lead105_score_video.stdout.txt 2>&1
  echo "[$(date +%H:%M:%S)] video score $(grep -o 'VERDICT: .*' runs105/lead105_score_video.stdout.txt | head -1)" >> $L
fi
echo "[$(date +%H:%M:%S)] done" >> $L

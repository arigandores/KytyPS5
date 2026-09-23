#!/bin/bash
# Session 103: M5' equal -> bench -> score, exactly the M5P_RUNBOOK commands, one pass.
CAP="C:/Users/<user>/OneDrive/Desktop/ps5 em/_RenderDoc/kyty_1790110985179586_capture.rdc"
LOG=C:/kyty/s102/log_m5cap102b.txt
OUT=C:/kyty/s103/m5p/real
cd /c/kyty/s103
echo "[$(date +%H:%M:%S)] equal start" >> $OUT/go.log
python C:/kyty/s103/m5p_run.py equal --cap "$CAP" --plan $OUT/plan_m5p103.json \
    --out $OUT/equal_m5p103.json --timeout 7200 > $OUT/equal_m5p103.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] equal rc=$?" >> $OUT/go.log
python C:/kyty/s103/m5p_run.py bench --cap "$CAP" --plan $OUT/plan_m5p103.json \
    --out $OUT/bench_m5p103.json \
    --env RD_AUTO_EXTEND=1 --env RD_EQUAL=$OUT/equal_m5p103.json --timeout 21600 \
    > $OUT/bench_m5p103.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] bench rc=$?" >> $OUT/go.log
python C:/kyty/s103/m5p_103.py --plan $OUT/plan_m5p103.json --bench $OUT/bench_m5p103.json \
    --equal $OUT/equal_m5p103.json --capture-log $LOG --out $OUT/m5p_103_result.json \
    > $OUT/m5p_103_result.stdout.txt 2>&1
echo "[$(date +%H:%M:%S)] score rc=$?" >> $OUT/go.log

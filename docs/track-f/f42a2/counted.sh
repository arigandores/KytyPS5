#!/bin/bash
# F42a2 (HPP-805, ROADMAP s122 item 705(b)(3)): the counted stand - =0 and =1 as separate processes of one build
# (shader_recompiler_compute_tests of the worktree 5ccb1d31), R 200, seed 42051 (constants comment e6497623), then the
# recount sum_stand_f42a2.py. A run killed by the watchdog leaves rc != 0 and no summary.
[ -e C:/kyty/SEALED_RUN.lock ] && exit 3
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/f42a2
D=stand/c42051
bash api_chk.sh "counted stand c42051" | cut -c1-160
echo "$(date -u +%FT%TZ) counted stand start (R 200, seed 42051; constants comment e6497623 10:09:05Z; build 5ccb1d31)" >> times.txt
bash run_stand.sh $D m0 0 200 42051 || exit $?
bash run_stand.sh $D m1 1 200 42051 || exit $?
echo "$(date -u +%FT%TZ) counted stand end (rc 0 both)" >> times.txt
python sum_stand_f42a2.py $D 42051 200 > $D/sum_stand_f42a2.txt
RC=$?
echo "$(date -u +%FT%TZ) sum_stand_f42a2.py rc $RC" >> times.txt
tail -20 $D/sum_stand_f42a2.txt
exit $RC

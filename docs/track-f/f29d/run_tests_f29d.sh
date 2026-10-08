#!/bin/bash
# F29d (HPP-703, Red Team, item 639(e)(2) re-run by the reviewer): memory_tracker_tests and shader_cfg_tests of build dir $1
# under label $2, KYTY_FIX_B12 unset / 0 / 1; outputs C:/kyty/f287/f29d/tests/<label>_<test>_<knob>.txt, one "rc=" line each.
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCK; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
BD=$1; LB=$2; OUT=C:/kyty/f287/f29d/tests; mkdir -p $OUT
for v in $(env | grep -o '^KYTY_[A-Z0-9_]*'); do unset $v; done
cd $BD
for K in none 0 1; do
  if [ $K = none ]; then unset KYTY_FIX_B12; else export KYTY_FIX_B12=$K; fi
  ./memory_tracker_tests.exe > $OUT/${LB}_mt_$K.txt 2>&1; echo "rc=$?" >> $OUT/${LB}_mt_$K.txt
  KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 ./shader_cfg_tests.exe > $OUT/${LB}_cfg_$K.txt 2>&1; echo "rc=$?" >> $OUT/${LB}_cfg_$K.txt
  echo "$LB $K mt: $(tail -1 $OUT/${LB}_mt_$K.txt) cfg: $(tail -1 $OUT/${LB}_cfg_$K.txt) tests=$(grep -c '^\[test\]' $OUT/${LB}_cfg_$K.txt) fail_lines=$(grep -ci fail $OUT/${LB}_cfg_$K.txt)"
done

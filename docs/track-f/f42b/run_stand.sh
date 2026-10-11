# F42b (HPP-780, Red Team): copy of the F42a run_stand.sh with f42a->f42b in ALL lines.
#!/bin/bash
# F42b (HPP-779, ROADMAP s122 item 694(g)(1)): one stand process under the watchdog, every KYTY_* variable of the shell
# removed, then KYTY_FIX_F20=<mode>. Usage: run_stand.sh <dir> <name> <mode 0|1> <R> <seed> [exe]
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
cd C:/kyty/f287/f42b
D=$1; N=$2; M=$3; R=$4; S=$5; EXE=${6:-C:/kyty/f287/f42b/build/shader_recompiler_compute_tests.exe}
mkdir -p "$D"
UNSET=$(env | grep -o '^KYTY_[A-Za-z0-9_]*' | sed 's/^/-u /')
env $UNSET KYTY_FIX_F20=$M KYTY_TEST_F20STAND_OUT="$D/$N.tsv" KYTY_TEST_F20STAND_R=$R KYTY_TEST_F20STAND_SEED=$S \
  python watch_f42b.py --limit 540 --tag "stand $N" -- "$EXE" --f20-stand > "$D/$N.out.txt" 2>&1
RC=$?
echo "$N mode=$M R=$R seed=$S rc=$RC"
exit $RC

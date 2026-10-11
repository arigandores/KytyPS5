# FS15b (HPP-821, Red Team, ROADMAP s122 items 730(g)(2), 732): copy of the FS14b file with fs14b->fs15b, FS14b->FS15b, HPP-813->HPP-821 in ALL lines.
# FS15b (HPP-821, Red Team, ROADMAP s122 items 710(g)(2), 712(g)(2), 717): copy of the FS13b file with fs13b->fs15b, FS13b->FS15b in ALL lines.
#!/bin/bash
# FS13a (HPP-787): copy of the FS11a sstep.sh (fs11a -> fs15b, FS11a -> FS13a, HPP-714 -> HPP-787). Was:
# FS11a (HPP-714): copy of the FS10a sstep.sh (fs10a -> fs11a, FS10a -> FS11a, HPP-684 -> HPP-714). Was:
# FS10a (HPP-684): copy of the FS9a sstep.sh (fs9a -> fs10a, FS9a -> FS10a, HPP-671 -> HPP-684). Was:
# FS9a (HPP-671): copy of the FS8a sstep.sh, paths and names changed. Was:
# FS8a (HPP-571): copy of the FS7a sstep.sh, paths and names changed. Was:
# FS8a (HPP-571, ROADMAP s122 items 467(g)(1), 487(g)(1)): one step (stand driver or tests) under the watchdog
# watch_fs10a.py (540 s limit; killed at the lock, STOP or a procload.py process - item 431(v)(1)); an API check line in
# times.txt before. Form of the FS6a sstep.sh with the command given as arguments.
# Usage: sstep.sh <log name> <command...>   -> runs/log_<log name>.txt
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs15b
mkdir -p runs
N=$1; shift
bash api_chk.sh "step $N" > /dev/null || exit $?
python watch_fs15b.py --limit 540 --tag "step $N" -- "$@" > runs/log_$N.txt 2>&1
RC=$?
echo "rc=$RC"
tail -4 runs/log_$N.txt
exit $RC

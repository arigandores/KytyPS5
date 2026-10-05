#!/bin/bash
# FS7b (HPP-566, Red Team, ROADMAP s122 items 467(g)(2), 487(g)(2)): one stand step of my own build under the watchdog
# watch_fs7b.py (limit 300 s; lock / STOP / gate process -> killed, rc 3/4/7; the step is rerun into a fresh dir), an API
# check line (api_chk.sh) in times.txt before. Exes - fix/f8_audio_stand.exe, fix/b24_pad_stand.exe (sha in sha_fs7b.txt).
# Drivers: the FS7a ports (members, read as accepted by the lead in item 514(v)) and the originals of F18c/F19c
# (reference: on FS7 they must fail exactly on their "unset (= 0)" cases and pass every explicit =0 / =1 case).
# Usage: sstep_fs7b.sh <f8|f8orig|b24|b24orig|trig|lval>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
cd C:/kyty/f287/fs7b
D=C:/kyty/KytyPS5/docs/track-f
F8=C:/kyty/f287/fs7b/fix/f8_audio_stand.exe
B24=C:/kyty/f287/fs7b/fix/b24_pad_stand.exe
mkdir -p runs
O=runs/$1
rm -rf $O
case $1 in
	f8) CMD="python $D/fs7a/run_stand_fs7a_f8.py $F8 $O" ;;
	f8orig) CMD="python $D/f18c/run_stand_f18c.py $F8 $O" ;;
	b24) CMD="python $D/fs7a/run_stand_fs7a_b24.py $B24 $O" ;;
	b24orig) CMD="python $D/f19c/run_stand_f19c.py $B24 $O" ;;
	trig) CMD="python $D/fs7a/run_stand_fs7a_b24dd.py trig $B24 $O" ;;
	lval) CMD="python C:/kyty/f287/fs7b/lval_fs7b.py $F8 $B24 $O" ;;
	*) echo "usage"; exit 2 ;;
esac
bash api_chk.sh "stand $1" > /dev/null || exit $?
python watch_fs7b.py --limit 300 --tag "stand $1" -- $CMD > runs/log_$1.txt 2>&1
RC=$?
echo "rc=$RC $1: $(tail -1 runs/log_$1.txt)"
exit $RC

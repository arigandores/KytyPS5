#!/bin/bash
# Track F link F30q (HPP-727; ROADMAP s122 item 664 (z)): the F30m (HPP-723) file with the names moved (f30m -> f30q, HPP-723 -> HPP-727,
# F30M_ -> F30Q_) and the tag set of item 664 (z)(2)-(3): f30_s1_w6, f30_s<1..9>_c6 [_r1.._r3].
# Track F link F30q (HPP-727): the F29e file with the names and the tag set moved (f29e -> f30q, HPP-704 -> HPP-727); no change of meaning.
# Track F link F30q (HPP-727; port of F25m launch_f25m.sh, names moved, no level argument): ONLY launches one detached call of
# go_f30q.sh <tag> (process rule p.324(i): the launcher only launches, the wait is wait_f30q.sh <= 540 s per tool command, separate
# commands).  A previous output of a refused call is moved to old/ before the new call (rule p.309(i)).  The output go_<tag>.out.txt ends
# with the line rc=<n>.  Item 623 (v)(1): a display OFF is woken (dispstate.py --wake) and checked again; still OFF => exit 6 and a
# times.txt line (not an attempt).  ITEM 660 (d)(1) (form of item 634): no guard, no hold check, no block in the launcher - only the
# display, the lock queue (queue_f30q.py, item 322 (g): P > F > S; QUEUE BUSY => exit 9) and the launch; the one guard scan + hold check
# of a tag is in go_f30q.sh right after the lock.  ITEM 661 (b)(1): the first executable line is the form linter form634_check.py
# --series (FORM634 FAILED => exit 10: no lock, no files, not an attempt).  F30Q_DRYRUN=2 stops after the checks;
# F30Q_TIMES / F30Q_QUEUE_SKIP=1 / F30Q_DISP_SKIP=1 (fixtures only).  ASCII only.
python "C:/kyty/KytyPS5/ps5 em/docs/form634_check.py" --series C:/kyty/f287/f30q || exit 10
export PATH=/usr/bin:/mingw64/bin:$PATH
T=$1
G=C:/kyty/f287/f30q
TM=${F30Q_TIMES:-C:/kyty/f287/times.txt}
case "$T" in
  f30_s1_w6|f30_s[1-9]_c6) ;;
  f30_s1_w6_r[1-3]|f30_s[1-9]_c6_r[1-3]) ;;
  *) echo "usage: launch_f30q.sh <f30_s1_w6 | f30_s<1..9>_c6>[_r1..3]"; exit 2;;
esac
[ -e C:/kyty/f287/STOP ] && exit 4
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
if [ "${F30Q_DISP_SKIP:-}" != 1 ]; then
  DS=$(python $G/dispstate.py)
  if [ $? != 0 ]; then
    WS=$(python $G/dispstate.py --wake | tr '\n' ';')
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q launch_f30q display was $DS - wake (item 623 (v)(1)): $(echo "$WS" | cut -c1-300)" >> "$TM"
    DS=$(python $G/dispstate.py)
  fi
  if [ $? != 0 ]; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q launch_f30q display not ON after the wake (item 623 (v)(1)): $DS - $T not launched (not an attempt)" >> "$TM"
    echo "display not ON: $DS"; exit 6
  fi
fi
if [ "${F30Q_QUEUE_SKIP:-}" != 1 ]; then
  QS=$(python $G/queue_f30q.py 2>&1 | tr '\n' ';')
  if ! echo "$QS" | grep -q 'QUEUE FREE'; then
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q queue (item 322 (g)): $(echo "$QS" | cut -c1-220) - $T not launched" >> "$TM"
    echo "queue busy: $QS"; exit 9
  fi
fi
[ "${F30Q_DRYRUN:-}" = 2 ] && { echo "dryrun2"; exit 0; }
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q launch_f30q form 634 (item 660): no guard before the lock; queue: $(echo "$QS" | grep -o 'QUEUE [A-Z]*'); tag $T" >> "$TM"
if [ -e $G/go_$T.out.txt ]; then
  grep -q '^rc=' $G/go_$T.out.txt || { echo "go_$T.out.txt has no rc line - wait with wait_f30q.sh"; exit 1; }
  mkdir -p $G/old; mv $G/go_$T.out.txt $G/old/go_$T.$(date -u +%Y%m%dT%H%M%SZ).out.txt
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q launch_f30q previous output of $T moved to f30q/old/" >> "$TM"
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F30q launch_f30q detached call: bash $G/go_f30q.sh $T" >> "$TM"
F30Q_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f30q.sh $T > $G/go_$T.out.txt 2>&1; echo rc=\$? >> $G/go_$T.out.txt" > /dev/null 2>&1 & disown
echo launched

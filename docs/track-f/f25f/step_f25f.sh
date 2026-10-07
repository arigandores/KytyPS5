#!/bin/bash
# F25f (HPP-669): process helper (not a seal member; form of F20l3 step_f20l3.sh) - reads a made tag (post_f25f.sh, short summary), then,
# when <next> is given and the series rule lets it, the check before the call (chk_f25f.sh) and the launch only (launch_f25f.sh); the wait
# is a separate tool command (wait_f25f.sh), item 324 (i).  The launch is refused (exit 20) when NEXT of series.txt is a STOP, when the
# controls are not PASS, or when the level of <next> is not CONTINUE.  exit: post rc / chk rc / launch rc; 20 - the rule asks to stop.
# usage: bash C:/kyty/f287/f25f/step_f25f.sh <made tag> [<next tag> <pot|bonus>]
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f25f; P=$1; N=${2:-}; L=${3:-}
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo "STOP file"; exit 4; }
bash $G/post_f25f.sh $P > $G/runs/$P/post.out.txt 2>&1 || { echo "post rc $?"; tail -5 $G/runs/$P/post.out.txt; exit 1; }
grep -E "ADMISSION|STATUS|scene:|warm:|  K_I|M6:|IN COUNT|INSTR_MADE_K2 \||K2-ref|U5 windows|REFERENCE| \[NO\]" $G/runs/$P/read.txt | cut -c1-260
grep -E "^BUDGET|^CONTROLS|^LEVEL|^  CLASSES|^U5|^COLD|^NEXT" $G/series.txt | cut -c1-300
[ -z "$N" ] && exit 0
grep -q '^CONTROLS PASS' $G/series.txt || { echo "CONTROLS not PASS - no launch"; exit 20; }
grep -q '^NEXT see the levels' $G/series.txt || { echo "NEXT is a STOP - no launch"; exit 20; }
case "$L" in pot) LV=pot_treasure_cave;; bonus) LV=bonus_path_maker_mix;; *) echo "level pot|bonus"; exit 2;; esac
case "$N" in f25_s*) grep -q "^LEVEL $LV .*STOP RULE CONTINUE" $G/series.txt || { echo "level $LV is not CONTINUE - no launch"; exit 20; };; esac
python $G/guard_f25f.py status > /dev/null || { echo "guard block not open: $(python $G/guard_f25f.py status)"; exit 8; }
bash $G/chk_f25f.sh $N || exit $?
bash $G/launch_f25f.sh $N $L

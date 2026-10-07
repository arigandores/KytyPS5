#!/bin/bash
# F20l3 (HPP-655): process helper (not a seal member) - reads a made tag (post_f20l3.sh, short summary), then, when <next> is given and
# the series has not stopped, the check before the call (chk_f20l3.sh) and the launch only (launch_f20l3.sh); the wait is a separate
# tool command (wait_f20l3.sh), item 324 (i).  exit: post rc / chk rc / launch rc; 20 - the stop rule or U5 asks to stop (no launch).
# usage: bash C:/kyty/f287/f20l3/step_f20l3.sh <made tag> [<next tag>]
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f20l3; P=$1; N=${2:-}
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
[ -e C:/kyty/f287/STOP ] && { echo "STOP file"; exit 4; }
bash $G/post_f20l3.sh $P > $G/runs/$P/post.out.txt 2>&1 || { echo "post rc $?"; tail -5 $G/runs/$P/post.out.txt; exit 1; }
grep -E "ADMISSION|^  K_I|IN COUNT|PK-A COLD|U5\(1\) median|glitches:| \[NO\]" $G/runs/$P/post.out.txt | cut -c1-240
grep -E "^HOLDS|^STOP RULE|^U5|^CLASSES" $G/series.txt | cut -c1-300
[ -f $G/series10.txt ] && grep -E "^U5 ANY" $G/series10.txt | sed 's/^/series10: /'
[ -z "$N" ] && exit 0
grep -q '^STOP RULE CONTINUE' $G/series.txt || { echo "STOP RULE is not CONTINUE - no launch"; exit 20; }
grep -q '^U5 ANY FIRES' $G/series10.txt 2>/dev/null && [ ! -f $G/U5_10_HANDLED ] && { echo "U5 after the 10th tag FIRES - no launch (item 591 (d)(2))"; exit 20; }
bash $G/chk_f20l3.sh $N || exit $?
bash $G/launch_f20l3.sh $N

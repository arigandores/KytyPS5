#!/bin/bash
# F25f (HPP-669; ROADMAP s122 item 534 (v)(3), item 606 (v)(1)): one check of the guard block - hold_f25f.py check (a user VM or a process
# holding GLCache files = a user session -> the block closes, 'close user_session'), else guard_f25f.py open-block (two clean checks
# >= 600 s apart open it).  Prints the line of each script; exit = that of the last one (0 open, 9 pending / session).  ASCII only.
# usage: bash C:/kyty/f287/f25f/block_f25f.sh
export PATH=/usr/bin:/mingw64/bin:$PATH
G=C:/kyty/f287/f25f
[ -e C:/kyty/SEALED_RUN.lock ] && { echo "lock held"; exit 3; }
HS=$(python $G/hold_f25f.py check)
if [ $? != 0 ]; then
  python $G/guard_f25f.py close user_session > /dev/null
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) F25f block check (item 606 (v)(1)): $HS - block closed" >> C:/kyty/f287/times.txt
  echo "$HS - block closed"; exit 9
fi
echo "$HS"
python $G/guard_f25f.py open-block

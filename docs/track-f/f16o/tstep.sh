#!/bin/bash
# F16o (HPP-595; copy of f16k2/tstep.sh). Was: F16k2 (HPP-590): one test step (any command) under the watchdog watch_f16o.py, 540 s limit, after wait_free.sh and an
# API check line; survivors after a kill are looked up by the backslash path of the build tree (WD_MARK) - never by a
# bare 'f16k' (that matched this link's own shells at 20:39:32Z). Usage: tstep.sh <tag> <command...>
[ -e C:/kyty/SEALED_RUN.lock ] && { echo LOCKED; exit 3; }
[ -e C:/kyty/f287/STOP ] && exit 4
export PATH=/usr/bin:/mingw64/bin:$PATH PYTHONIOENCODING=utf-8
export WD_MARK='f16k\build'
cd C:/kyty/f287/f16o
T=$1; shift
bash wait_free.sh || exit 9
bash api_chk.sh "$T" > /dev/null || exit $?
python watch_f16o.py --limit 540 --tag "$T" -- "$@"

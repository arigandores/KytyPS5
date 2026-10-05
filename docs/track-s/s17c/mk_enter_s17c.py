"""S17c: enter_scene.py of S17c = the F20c file (seal 2, item 534 kill by pid) with the root moved to C:/kyty/s288/s17c, the pid file variable
S17C_PIDFILE and one new mode --until-prep (rebuild tags of item 524 (z) K4 / K6): the attempt ends at the first log line
'ShaderPreparation: startup wait finished' (outcome 'prep', then WM_CLOSE at once) or when the process exits by itself (outcome 'exited').
Writes LF; every anchor must match exactly once."""
import sys

SRC = 'C:/kyty/f287/f20c/enter_scene.py'
DST = sys.argv[1]
s = open(SRC, 'rb').read().decode('utf-8').replace('\r\n', '\n')
HEAD = ('# Track S link S17c (HPP-613): the F20c file of this role (seal 2, item 534: kill by pid only) with the root moved to\n'
        '# C:/kyty/s288/s17c, the pid file variable S17C_PIDFILE and the mode --until-prep (rebuild tags, item 524 (z) K4 / K6).\n')
EDITS = [
    ("ROOT = pathlib.Path('C:/kyty/f287/f18e')\n", "ROOT = pathlib.Path('C:/kyty/s288/s17c')\n"),
    ("    if os.environ.get('F20C_PIDFILE'):   # F20c item 534: the own emulator pid for guard_f20c.py (kill by pid, not by name)\n"
     "        with open(os.environ['F20C_PIDFILE'], 'w') as pidfile:\n",
     "    if os.environ.get('S17C_PIDFILE'):   # S17c (item 534): the own emulator pid for guard_s17c.py (kill by pid, not by name)\n"
     "        with open(os.environ['S17C_PIDFILE'], 'w') as pidfile:\n"),
    ("    marker_started = ('GuestOut: Level has started: %s' % options.level).encode()\n",
     "    marker_started = ('GuestOut: Level has started: %s' % options.level).encode()\n"
     "    marker_prep = b'ShaderPreparation: startup wait finished'   # S17c --until-prep\n"),
    ("            if b'GpuWaitSlow:' in line:  # session 58: read acopy= here before anything else\n",
     "            if options.until_prep and marker_prep in line:   # S17c: the preparation screen ended - close at once\n"
     "                stable = time.monotonic() - started\n"
     "                result.update(stable_s=round(stable, 1), outcome='prep')\n"
     "                print('%.1f s  preparation screen ended (--until-prep): %s' % (stable, line[:200].decode('utf8', 'replace')),\n"
     "                      flush=True)\n"
     "                return\n"
     "            if b'GpuWaitSlow:' in line:  # session 58: read acopy= here before anything else\n"),
    ("        if result['outcome'] == 'ok':\n            if options.hold > 0:\n",
     "        if result['outcome'] == 'prep':   # S17c --until-prep: no hold, WM_CLOSE at once\n"
     "            result.update(close_game(game))\n"
     "        elif result['outcome'] == 'ok':\n            if options.hold > 0:\n"),
    ("    parser.add_argument('--no-install', action='store_true')\n",
     "    parser.add_argument('--no-install', action='store_true')\n"
     "    parser.add_argument('--until-prep', action='store_true',\n"
     "                        help='S17c: end at the line ShaderPreparation: startup wait finished (WM_CLOSE) or at the exit')\n"),
    ("            if result['outcome'] == 'ok':\n                success = result\n                break\n",
     "            if result['outcome'] == 'ok' or (options.until_prep and result['outcome'] == 'prep'):\n"
     "                success = result\n                break\n"),
    ("    if success is None:\n        print('VERDICT: no attempt reached %s' % options.level, flush=True)\n        raise SystemExit(1)\n",
     "    if success is None:\n        print('VERDICT: no attempt reached %s' % options.level, flush=True)\n        raise SystemExit(1)\n"
     "    if options.until_prep:\n"
     "        print('VERDICT: preparation screen ended in %.1f s (--until-prep)' % success['stable_s'], flush=True)\n"
     "        return\n"),
]
for old, new in EDITS:
    n = s.count(old)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, old[:80]))
    s = s.replace(old, new)
s = HEAD + s
for ch in s:
    if ord(ch) > 127:
        raise SystemExit('non-ASCII character in the output')
open(DST, 'wb').write(s.encode('ascii'))
print('written', DST, len(s))

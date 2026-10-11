"""F40c (HPP-772): build C:/kyty/f287/f40c from the F38c tools (names moved) and the drafts of this link (go / launch / post, the reader and
its fixtures, beside this file).  enter_scene.py: the F38c file with ROOT moved and one option --mark-quit (the exit time of the tags
f24_x1 / f24_m2, item 692 (g)(1): 'exit no longer than HOLD_UPD_MS + 5 s'); off by default, the old forms are unchanged.  LF output.
ASCII only.
usage: python mk_f40c.py <draft dir>"""
import os
import sys

SRC = 'C:/kyty/f287/f38c'
DST = 'C:/kyty/f287/f40c'
DRAFT = sys.argv[1]
if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
    print('lock or STOP - nothing written')
    sys.exit(3)
for d in ('runs', 'pred', 'base', 'old'):
    os.makedirs(DST + '/' + d, exist_ok=True)


def moved(b):
    for a, z in ((b'f38c', b'f40c'), (b'F38C', b'F40C'), (b'F38c', b'F40c'), (b'HPP-765', b'HPP-772')):
        b = b.replace(a, z)
    return b


HDR = b'# Track F link F40c (HPP-772; ROADMAP s122 item 692 (g)(1), (g)(4)): copy of the F38c (HPP-765) file %s with the names moved (f38c -> f40c, F38C -> F40C, F38c -> F40c, HPP-765 -> HPP-772); no change of meaning.\n'
ROWS = []
for name, new in (('dispstate.py', 'dispstate.py'), ('guard_f38c.py', 'guard_f40c.py'), ('hold_f38c.py', 'hold_f40c.py'),
                  ('hostload_f38c.py', 'hostload_f40c.py'), ('idle142.py', 'idle142.py'), ('launch_run.py', 'launch_run.py'),
                  ('manifest_fs4c.py', 'manifest_fs4c.py'), ('mfsub_f38c.py', 'mfsub_f40c.py'), ('procload.py', 'procload.py'),
                  ('queue_f38c.py', 'queue_f40c.py'), ('run_safety99.py', 'run_safety99.py'), ('runchk_f38c.py', 'runchk_f40c.py'),
                  ('sheet142.py', 'sheet142.py'), ('snap_f38c.py', 'snap_f40c.py'), ('wait_f38c.sh', 'wait_f40c.sh'),
                  ('chk_f38c.sh', 'chk_f40c.sh'), ('gates.req', 'gates.req'), ('sample.req', 'sample.req'),
                  ('gates_default.txt', 'gates_default.txt'), ('tempo_f38c.py', 'tempo_f40c.py')):
    b = open(os.path.join(SRC, name), 'rb').read().replace(b'\r\n', b'\n')
    nb = moved(b)
    if nb != b:
        h = HDR % name.encode()
        if nb.startswith(b'#!'):
            i = nb.index(b'\n') + 1
            nb = nb[:i] + h + nb[i:]
        else:
            nb = h + nb
    open(os.path.join(DST, new), 'wb').write(nb)
    ROWS.append('%s -> %s changed %s' % (name, new, nb != b))

# enter_scene.py: ROOT moved + --mark-quit
b = open(os.path.join(SRC, 'enter_scene.py'), 'rb').read().replace(b'\r\n', b'\n')


def sub1(b, old, new):
    assert b.count(old) == 1, old[:80]
    return b.replace(old, new)


b = sub1(b, b"ROOT = pathlib.Path('C:/kyty/f287/f38c')", b"ROOT = pathlib.Path('C:/kyty/f287/f40c')")
b = sub1(b, b"def ft_tail_from_samples(samples, window=FT_TAIL_WINDOW_S):\n",
         b"M_QUIT_POSTED = b'TestHidLoss: quit posted'   # F40c: the stand line of the modes exit (KYTY_TEST_HIDLOSS edition 2)\n"
         b"\n"
         b"\n"
         b"class QuitMark:\n"
         b"    \"\"\"F40c (HPP-772, item 692 (g)(1) f24_x1: 'exit no longer than HOLD_UPD_MS + 5 s from quit posted'): during the hold, every\n"
         b"    FT_SAMPLE_S, its own Tail reads the log from the beginning; 'before' - the last sample that had NOT seen the line\n"
         b"    'TestHidLoss: quit posted', 'seen' - the first that had; 'dead_first' - the first sample that found the process ended,\n"
         b"    'alive_last' - the last that found it alive.  exit_upper_s = dead_first - before (an upper bound of quit posted -> process\n"
         b"    end, up to the log write delay), exit_lower_s = alive_last - seen.  Times relative to the process start.\"\"\"\n"
         b"\n"
         b"    def __init__(self, path, t0, clock=time.monotonic):\n"
         b"        self.tail = Tail(path)\n"
         b"        self.t0 = t0\n"
         b"        self.clock = clock\n"
         b"        self.seen = self.before = self.alive_last = self.dead_first = None\n"
         b"\n"
         b"    def sample(self, alive):\n"
         b"        now = self.clock()\n"
         b"        if self.seen is None:\n"
         b"            if any(M_QUIT_POSTED in line for line in self.tail.lines()):\n"
         b"                self.seen = now\n"
         b"            else:\n"
         b"                self.before = now\n"
         b"        if alive:\n"
         b"            self.alive_last = now\n"
         b"        elif self.dead_first is None:\n"
         b"            self.dead_first = now\n"
         b"\n"
         b"    def result(self):\n"
         b"        rel = (lambda t: None if t is None else round(t - self.t0, 3))\n"
         b"        up = None if None in (self.before, self.dead_first, self.seen) else round(self.dead_first - self.before, 3)\n"
         b"        lo = None if None in (self.seen, self.alive_last) else round(self.alive_last - self.seen, 3)\n"
         b"        return dict(seen_s=rel(self.seen), before_s=rel(self.before), alive_last_s=rel(self.alive_last),\n"
         b"                    dead_first_s=rel(self.dead_first), exit_upper_s=up, exit_lower_s=lo, step_s=FT_SAMPLE_S)\n"
         b"\n"
         b"\n"
         b"def ft_tail_from_samples(samples, window=FT_TAIL_WINDOW_S):\n")
b = sub1(b, b"                sub = SubTracker(EMU / '_kyty.txt', options.until_sublevel) if options.until_sublevel > 0 else None\n",
         b"                sub = SubTracker(EMU / '_kyty.txt', options.until_sublevel) if options.until_sublevel > 0 else None\n"
         b"                qm = QuitMark(EMU / '_kyty.txt', started) if options.mark_quit else None   # F40c\n"
         b"                if qm is not None:\n"
         b"                    qm.sample(game.poll() is None)\n")
b = sub1(b, b"                    ft.sample()\n                    if sub is not None and sub.done():\n",
         b"                    ft.sample()\n"
         b"                    if qm is not None:\n"
         b"                        qm.sample(game.poll() is None)\n"
         b"                    if sub is not None and sub.done():\n")
b = sub1(b, b"                result['hold_exit'] = game.poll()\n",
         b"                if qm is not None:   # F40c: one more sample after the loop (the process end or the hold end)\n"
         b"                    qm.sample(game.poll() is None)\n"
         b"                    result['quit_mark'] = qm.result()\n"
         b"                    print('quit mark: %s' % result['quit_mark'], flush=True)\n"
         b"                result['hold_exit'] = game.poll()\n")
b = sub1(b, b"    parser.add_argument('--require-idle', action='store_true',\n",
         b"    parser.add_argument('--mark-quit', action='store_true',\n"
         b"                        help='F40c: during the hold, time the line TestHidLoss: quit posted and the process end (quit_mark)')\n"
         b"    parser.add_argument('--require-idle', action='store_true',\n")
b = (b'# Track F link F40c (HPP-772; ROADMAP s122 item 692 (g)(1), (g)(4)): the F38c file of this role with ROOT moved (f287/f38c to f287/f40c)\n'
     b'# and one option --mark-quit (class QuitMark: the exit time of the exit tags), off by default; nothing else changed.\n') + b
assert all(c < 128 for c in b)
open(os.path.join(DST, 'enter_scene.py'), 'wb').write(b)
ROWS.append('enter_scene.py ROOT moved, --mark-quit added')
for name in ('go_f40c.sh', 'launch_f40c.sh', 'post_f40c.sh', 'f40c_read.py', 'test_f40c_read.py', 'test_tools_f40c.py', 'mk_f40c.py'):
    p = os.path.join(DRAFT, name)
    if not os.path.exists(p):
        ROWS.append('draft %s ABSENT' % name)
        continue
    b = open(p, 'rb').read().replace(b'\r\n', b'\n')
    assert all(c < 128 for c in b), name
    open(os.path.join(DST, name), 'wb').write(b)
    ROWS.append('draft %s' % name)
for r in ROWS:
    print(r)
print('ALL OK')

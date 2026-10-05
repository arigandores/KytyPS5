"""hmut_s15.py - S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)(4)-(5)): the hand mutants of s15/enter_scene_s15.py (the U hold)
and s15/go_s15.sh (the hold-rule field of the plan).  Each mutant is applied to a copy of its target; the suite runs on the copy
(argv[1]); a mutant must make the suite FAIL (rc != 0 and no "ALL OK").  enter mutants run in parallel, each with its own fixture
directory (FX_ENTER_BASE); go mutants run one by one (fixed fixture directories).  Outputs: s15/hmut/hmut_<id>.txt and a summary.
Refuses when the lock or the stop file exists.  ASCII.
    python hmut_s15.py enter|go [<id>,<id>...]
"""
import concurrent.futures
import hashlib
import os
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/s288/STOP'
D = 'C:/kyty/s288/s15'
OUT = D + '/hmut'
ENTER = [
    ('e01_cap_gt', "        if self.shown() >= self.cap_us:", "        if self.shown() > self.cap_us:"),
    ('e02_min_gt', "self.shown() >= self.min_us and self.video >= self.frames", "self.shown() > self.min_us and self.video >= self.frames"),
    ('e03_vid_gt', "self.shown() >= self.min_us and self.video >= self.frames", "self.shown() >= self.min_us and self.video > self.frames"),
    ('e04_and_or', "self.shown() >= self.min_us and self.video >= self.frames", "self.shown() >= self.min_us or self.video >= self.frames"),
    ('e05_closed_fi', "            elif not self.closed and (d if d is not None else -1) >= SCENE_DRAWS_U:",
     "            elif (d if d is not None else -1) >= SCENE_DRAWS_U:"),
    ('e06_no_close', "            else:\n                self.closed = True", "            else:\n                pass"),
    ('e07_name_in', "                if name == self.level:", "                if self.level in name:"),
    ('e08_no_strip', "            name = line[len(M_START_U):].strip().decode('latin1')", "            name = line[len(M_START_U):].decode('latin1')"),
    ('e09_fi_row', "                self.fi = i\n", "                self.fi = i\n                self.after_fi_us += dt\n"),
    ('e10_entry_0', "(self.after_entry_us if a == 'entry' else 0)", "(0 if a == 'entry' else 0)"),
    ('e11_draws', "SCENE_DRAWS_U = 100 ", "SCENE_DRAWS_U = 101 "),
    ('e12_video_eq', "            self.video += len(self.idx.lines())", "            self.video = len(self.idx.lines())"),
    ('e13_no_break', "                        if ucause is not None:\n                            break", "                        if ucause is not None:\n                            pass"),
    ('e14_wall', "                    deadline = hold_t0 + rule[2] / 1000000.0 + U_WALL_EXTRA_S", "                    deadline = hold_t0 + options.hold"),
    ('e15_json', "            guest_args=guest_args, hold_s=options.hold, hold_rule=hold_rule,", "            guest_args=guest_args, hold_s=options.hold, hold_rule=None,"),
    ('e16_no_idx', "(ROOT / ('rec_%s.mp4.idx' % tag)) if options.rec else None", "None"),
    ('e17_entry_rows', "            self.after_entry_us += dt\n", ""),
    ('e18_parse_order', "    if mn > cap or cap <= 0:", "    if cap <= 0:"),
]
GO = [
    ('g01_dash', 'if [ "$HU" = "-" ]; then HUX=""', 'if [ "$HU" = "-" ]; then HUX="--hold-u -"'),
    ('g02_unanchored', '[[ "$HU" =~ ^[0-9]+:[0-9]+:[0-9]+$ ]]', '[[ "$HU" =~ [0-9]+:[0-9]+:[0-9]+ ]]'),
    ('g03_rc', 'echo "bad hold rule"; exit 2', 'echo "bad hold rule"; exit 0'),
    ('g04_no_hux', '--hold $HOLD $HUX $VALX', '--hold $HOLD $VALX'),
    ('g05_enter_s9', 'ENTERPY=$ROOT/s15/enter_scene_s15.py', 'ENTERPY=$ROOT/s9/enter_scene_s9.py'),
    ('g06_field10', 'HU=${11:-}', 'HU=${10:-}'),
]


def run_one(kind, mid, old, new):
    tgt = D + ('/enter_scene_s15.py' if kind == 'enter' else '/go_s15.sh')
    suite = D + ('/test_enter_scene_s15.py' if kind == 'enter' else '/test_go_s15.py')
    t = open(tgt, 'rb').read().decode('ascii')
    if t.count(old) != 1:
        return mid, 'NOT APPLIED (anchor %d times)' % t.count(old), ''
    mdir = OUT + '/' + mid
    os.makedirs(mdir, exist_ok=True)
    mp = mdir + ('/enter_scene_s15.py' if kind == 'enter' else '/go_s15.sh')
    open(mp, 'wb').write(t.replace(old, new).encode('ascii'))
    env = dict(os.environ, PYTHONIOENCODING='utf-8', FX_ENTER_BASE=mdir + '/fx', FX_FAST='1',
               PATH='/usr/bin:/mingw64/bin:' + os.environ.get('PATH', ''))
    if kind == 'enter':
        # the generated file check U15 compares with mk_enter_s15.py: a mutant always fails it - run the suite without U15 credit
        pass
    p = subprocess.run([sys.executable, suite, mp], capture_output=True, text=True, env=env, timeout=900, cwd=D)
    out = p.stdout + p.stderr
    open(OUT + '/hmut_%s.txt' % mid, 'w', encoding='utf-8').write(out)
    fails = [x for x in out.splitlines() if x.startswith('FAIL ')]
    real = [x for x in fails if not x.startswith('FAIL U15 ')]
    killed = p.returncode != 0 and 'ALL OK' not in out and bool(real)
    return mid, 'KILLED by %s' % (real[0][:110] if real else '-') if killed else 'SURVIVED (rc %d, fails %s)' % (
        p.returncode, [x[:60] for x in fails][:3]), hashlib.sha256(out.encode('utf-8')).hexdigest()


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCKED or STOP - nothing run')
        return 5
    kind = sys.argv[1]
    only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None
    muts = [m for m in (ENTER if kind == 'enter' else GO) if only is None or m[0] in only]
    os.makedirs(OUT, exist_ok=True)
    res = []
    if kind == 'enter':
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(os.environ.get('HMUT_WORKERS', '6'))) as ex:
            res = list(ex.map(lambda m: run_one(kind, *m), muts))
    else:
        res = [run_one(kind, *m) for m in muts]
    for mid, word, sh in res:
        print('%-16s %s  (output sha256 %s)' % (mid, word, sh[:16]))
    k = sum(1 for _, w, _ in res if w.startswith('KILLED'))
    print('HMUT %s: %d of %d killed' % (kind, k, len(res)))
    return 0 if k == len(res) else 1


if __name__ == '__main__':
    sys.exit(main())

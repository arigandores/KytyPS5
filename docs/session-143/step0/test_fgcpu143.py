"""Fixtures of fgcpu143.py (the foreign-CPU row of go143a.sh; session 143 step 0, HPP-297; ROADMAP s122 item 231 (i)(4), (l)
debt D-4).  The snapshot, the clock and the sleep are injected (no process is sampled); one case per term: processes alive
at both ends only, the game apart, Idle / System and the sampler itself out, a negative delta clamped to 0, the top order,
the % of the logical CPUs, the run part without its --save file ("n/a"), a failing snapshot ("unavailable"), the save
file, the usage, and the output in strict cp1250 WITHOUT PYTHONIOENCODING (a child process, item 175 (v)).
The first output line names this suite and the target by sha256; the output ends with ALL OK.
    python C:/kyty/s143/test_fgcpu143.py [<fgcpu143.py under test>]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fgcpu143.py')
print('suite test_fgcpu143.py sha256 %s target fgcpu143.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('fgcpu143_under_test', SRC)
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
FX = Path('C:/kyty/s143/fx_fgcpu143')
shutil.rmtree(FX, ignore_errors=True)
FX.mkdir(parents=True)
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def run(argv, snaps, times, me=99, ncpu=32):
    it = iter(snaps)
    ti = iter(times)
    slept = []

    def snap():
        x = next(it)
        if isinstance(x, Exception):
            raise x
        return dict(x)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = F.main(argv, snapshot=snap, clock=lambda: next(ti), sleep=slept.append, me=me, ncpu=ncpu)
    return rc, buf.getvalue().strip(), slept


A = {(1, 'chrome'): 10.0, (2, 'node'): 5.0, (4, 'Idle'): 100.0, (5, 'System'): 50.0, (6, 'gone'): 1.0, (99, 'python'): 0.0,
     (7, 'kyty_emulator'): 3.0, (8, 'drift'): 9.0}
B = {(1, 'chrome'): 30.0, (2, 'node'): 6.0, (3, 'newcomer'): 50.0, (4, 'Idle'): 900.0, (5, 'System'): 60.0,
     (99, 'python'): 40.0, (7, 'kyty_emulator'): 23.0, (8, 'drift'): 8.0}
C = {(1, 'chrome'): 31.0, (2, 'node'): 6.0, (3, 'newcomer'): 60.0}
ok = True
sp = FX / 'a.json'
rc, out, _ = run(['--save', str(sp)], [A], [1000.0])
saved = json.loads(sp.read_text(encoding='ascii'))
ok &= case('f1 --save writes the time and every process (pid, name, cpu)', rc == 0 and saved['t'] == 1000.0 and
           len(saved['procs']) == len(A) and 'saved 8 processes' in out)
rc, out, slept = run(['--since', str(sp)], [B, C], [1020.0, 1030.0])
print('  line: %s' % out)
ok &= case('f2 run part: wall 20 s; chrome (30-10)/20 = 1.000, node 0.050; drift clamped to 0; foreign 1.050 CPU s/s',
           'run 20.0 s: foreign 1.050 CPU s/s' in out)
ok &= case('f3 the newcomer (not alive at --save), gone, Idle, System and the sampler pid are out of the run part; '
           'processes alive at both ends counted 4 (chrome, node, drift, the game)',
           'newcomer' not in out.split('|')[0] and 'Idle' not in out and 'System' not in out and 'python' not in out
           and 'over 4 processes alive at both ends' in out.split('|')[0])
ok &= case('f4 the game is apart (23-3)/20 = 1.000 and not foreign', 'game 1.000' in out.split('|')[0])
ok &= case('f5 top order by rate: chrome before node before drift', out.split('|')[0].find('chrome:1:1.000') <
           out.split('|')[0].find('node:2:0.050') < out.split('|')[0].find('drift:8:0.000'))
ok &= case('f6 % of 32 logical CPUs: 1.050 / 32 = 3.3 %', '= 3.3 % of 32 logical CPUs' in out)
ok &= case('f7 the now part samples --span (default 10 s) between two snapshots: newcomer 1.000, chrome 0.100',
           slept == [10.0] and 'now 10.0 s: foreign 1.100 CPU s/s' in out and 'newcomer:3:1.000' in out.split('|')[1])
rc, out, slept = run(['--since', str(FX / 'none.json'), '--span', '2'], [B, C], [1020.0, 1022.0])
ok &= case('f8 without the --save file the run part is n/a and the now part still prints (span 2)',
           rc == 0 and 'run n/a (no snapshot at the lock' in out and 'now 2.0 s:' in out and slept == [2.0])
rc, out, _ = run(['--since', str(sp)], [RuntimeError('powershell failed')], [1020.0])
ok &= case('f9 a failing snapshot prints one unavailable line, rc 0 (a row, not a guard)',
           rc == 0 and out.startswith('fgcpu143: unavailable (RuntimeError'))
rc, out, _ = run(['--since', str(sp)], [B, RuntimeError('x')], [1020.0, 1030.0])
ok &= case('f9b the run part survives a failing second snapshot', 'run 20.0 s' in out and 'now unavailable' in out)
bad = FX / 'bad.json'
bad.write_text('{"t": 1}', encoding='ascii')
rc, out, _ = run(['--since', str(bad)], [B, C], [1020.0, 1030.0])
ok &= case('f10 a broken --save file reads n/a', 'run n/a' in out)
rc, out, _ = run(['--save', str(FX / 'nodir' / 'x.json')], [A], [1000.0])
ok &= case('f11 a --save that cannot write prints save unavailable, rc 0', rc == 0 and 'save unavailable' in out)
rc, out, _ = run([], [], [])
ok &= case('f12 no mode -> usage rc 2', rc == 2 and out.startswith('usage'))
ok &= case('f13 the constants: span 10 s, top 5, the game name, the ignore set of procload',
           F.SPAN == 10.0 and F.TOP == 5 and F.GAME == 'kyty_emulator' and F.IGNORE == {'idle', 'system', 'system idle process'})
U = {(1, 'proc\u00e9x'): 0.0}
U2 = {(1, 'proc\u00e9x'): 5.0}
rc, out, _ = run(['--since', str(FX / 'none.json')], [U, U2], [1.0, 11.0])
ok &= case('f14 a non-ASCII process name is printed as ASCII', all(ord(c) < 128 for c in out) and 'proc?x:1:0.500' in out)
drv = FX / 'drv.py'
drv.write_text('import sys\nsys.path.insert(0, %r)\nimport importlib.util\n'
               's = importlib.util.spec_from_file_location("f", %r)\nm = importlib.util.module_from_spec(s)\n'
               's.loader.exec_module(m)\n'
               'sys.exit(m.main(["--since", "none.json", "--span", "0"], snapshot=lambda: {(1, "proc\\u00e9x"): 1.0}, '
               'clock=lambda: 5.0, sleep=lambda s: None))\n' % (HERE, SRC), encoding='utf-8')
env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env['PYTHONIOENCODING'] = ''
env.pop('PYTHONIOENCODING')
env['PYTHONUTF8'] = '0'
p = subprocess.run([sys.executable, str(drv)], capture_output=True, env=env, cwd=str(FX), timeout=60)
try:
    p.stdout.decode('cp1250', errors='strict')
    enc = p.returncode == 0 and b'fgcpu143:' in p.stdout and not p.stderr
except UnicodeError:
    enc = False
ok &= case('f15 a child without PYTHONIOENCODING (console cp1250) prints its line, rc 0, no error', enc)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)

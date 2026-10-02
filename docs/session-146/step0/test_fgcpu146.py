"""Fixtures of fgcpu146.py (the foreign-CPU row of go146a.sh; session 143 (ported to s144 by HPP-330, to s145 by HPP-350, to s146 by HPP-386, names 143 -> 144 -> 145 -> 146; session 146: every process of a TOP list prints as <app>:<pid>:<rate>) step 0, HPP-297, link 1b HPP-321; ROADMAP s122
item 231 (i)(4), (l) debt D-4, item 242 (a), (g)).  The snapshot, the system times, the clock and the sleep are injected
(no process is sampled) except in k1 - the real kernel32 snapshot on this machine (read only, nothing is printed of it but
counts).  One case per term of item 242 (a): (1) processes alive at both ends, (2) processes new at the end with ALL their
CPU, (3) the system member delta(kernel + user - idle) / wall, the game and the chain (the chain pid and its descendants)
out of (1) and (2), (4) the residual (a negative one printed as is), (5) the blind zone; Idle / System out; a negative delta
clamped to 0; the top order; the % of the logical CPUs; the run part without its --save file ("n/a"), without the system
times ("unavailable"), a failing snapshot, the save file, the usage, and the output in strict cp1250 WITHOUT
PYTHONIOENCODING (a child process, item 175 (v)).  Process names are neutral (appA, appB, ...; item 242 (g)).
The first output line names this suite and the target by sha256; the output ends with ALL OK.
    python C:/kyty/s146/test_fgcpu146.py [<fgcpu146.py under test>]
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'fgcpu146.py')
print('suite test_fgcpu146.py sha256 %s target fgcpu146.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('fgcpu146_under_test', SRC)
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)
FX = Path('C:/kyty/s146/fx_fgcpu146')
shutil.rmtree(FX, ignore_errors=True)
FX.mkdir(parents=True)
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def run(argv, snaps, times, systs=None, me=99, ncpu=32):
    it = iter(snaps)
    ti = iter(times)
    si = iter(systs or [])
    slept = []

    def snap():
        x = next(it)
        if isinstance(x, Exception):
            raise x
        cpu, par = x
        return dict(cpu), dict(par)

    def syst():
        x = next(si)
        if isinstance(x, Exception):
            raise x
        return x
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = F.main(argv, snapshot=snap, systimes=syst, clock=lambda: next(ti), sleep=slept.append, me=me, ncpu=ncpu)
    return rc, buf.getvalue().strip(), slept


def term(out, k, part=0):
    """The text of term k ('(1)', '(2)', '(3)', '(4)', 'game', 'blind') of the run (0) or now (1) part."""
    p = out.split(' || ')[part]
    for x in p.split(' | '):
        if (k in ('game', 'blind') and x.startswith(k)) or (k not in ('game', 'blind') and x.lstrip().startswith(k)) or \
                (k == '(1)' and '(1) alive' in x):
            return x
    return ''


# the window: --save at t 1000, the end at t 1020 (20 s), the now sample to t 1030
A = {(1, 'appA'): 10.0, (2, 'appB'): 5.0, (4, 'Idle'): 100.0, (5, 'System'): 50.0, (6, 'gone'): 1.0, (8, 'appD'): 9.0,
     (70, 'bash'): 2.0, (7, 'kyty_emulator'): 3.0}
PA = {1: 900, 2: 900, 4: 0, 5: 0, 6: 900, 8: 900, 70: 900, 7: 70}
B = {(1, 'appA'): 30.0, (2, 'appB'): 6.0, (3, 'appC'): 50.0, (4, 'Idle'): 900.0, (5, 'System'): 60.0, (8, 'appD'): 8.0,
     (70, 'bash'): 4.0, (71, 'bash'): 1.0, (99, 'python'): 0.4, (72, 'tail'): 0.0, (7, 'kyty_emulator'): 23.0,
     (9, 'kyty_emulator'): 4.0}
PB = {1: 900, 2: 900, 3: 900, 4: 0, 5: 0, 8: 900, 70: 900, 71: 70, 99: 71, 72: 71, 7: 70, 9: 900}
C = {(1, 'appA'): 31.0, (2, 'appB'): 6.0, (3, 'appC'): 60.0, (70, 'bash'): 4.0, (99, 'python'): 0.5}
PC = {1: 900, 2: 900, 3: 900, 70: 900, 99: 70}
S0 = (1000.0, 1300.0, 200.0)     # idle, kernel (incl. idle), user - seconds over all CPUs
S1 = (1500.0, 1900.0, 300.0)     # busy delta = (600 - 500) + 100 = 200 CPU s over 20 s = 10.000 CPU s/s
S2 = (1800.0, 2100.0, 320.0)     # busy delta = (200 - 300) + 20 = -80 over 10 s = -8.000 (a broken counter: printed as is)
ok = True
sp = FX / 'a.json'
rc, out, _ = run(['--save', str(sp)], [(A, PA)], [1000.0], [S0])
saved = json.loads(sp.read_text(encoding='ascii'))
ok &= case('f1 --save writes the time, every process (pid, name, cpu) and the system times', rc == 0 and saved['t'] == 1000.0
           and len(saved['procs']) == len(A) and saved['sys'] == list(S0) and 'saved 8 processes' in out
           and '(system times yes)' in out)
rc, out, slept = run(['--since', str(sp), '--chain-pid', '70'], [(B, PB), (C, PC)], [1020.0, 1030.0], [S1, S2])
print('  line: %s' % out)
ok &= case('f2 (1) alive at both ends: appA (30-10)/20 = 1.000, appB 0.050, appD clamped to 0 -> foreign 1.050 over 3',
           '(1) alive at both ends: foreign 1.050 CPU s/s = 3.3 % of 32 logical CPUs over 3 processes' in term(out, '(1)'))
ok &= case('f3 (2) new at the end: appC with ALL its CPU 50/20 = 2.500, named; a newcomer kyty_emulator is the game, not (2)',
           '(2) new at the end: foreign 2.500 CPU s/s = 7.8 % over 1 processes; top <app>:3:2.500' in term(out, '(2)'))
ok &= case('f3b Idle, System, the gone process are out of (1) and (2)', 'Idle' not in out and 'System:' not in out
           and 'gone' not in out)
ok &= case('f4b the chain = the chain pid 70 and its descendants alive at the end: bash 70 (4-2)/20 = 0.100, bash 71 0.050, '
           'python 99 (the sampler) 0.020, tail 72 0, kyty_emulator 7 (a child of 70) 1.000 -> chain 1.170 over 5; '
           'the other kyty_emulator 9 is the game 0.200',
           'game 0.200, chain (pid 70 and its descendants alive at the end) 1.170 over 5' in out.split(' || ')[0])
ok &= case('f5 top order by rate in (1): appA before appB before appD', term(out, '(1)').find('<app>:1:1.000') <
           term(out, '(1)').find('<app>:2:0.050') < term(out, '(1)').find('<app>:8:0.000') and
           term(out, '(1)').find('<app>:1:1.000') > 0)
ok &= case('f6 (3) system: ((1900-1300) + (300-200) - (1500-1000)) / 20 = 10.000 CPU s/s = 31.2 % of 32',
           '(3) system (GetSystemTimes) 10.000 CPU s/s = 31.2 %' in out.split(' || ')[0])
ok &= case('f7 (4) residual = 10.000 - 1.050 - 2.500 - 0.200 - 1.170 = 5.080',
           '(4) residual = (3) - (1) - (2) - game - chain = 5.080 CPU s/s (the game and the chain\'s processes dead at the '
           'end are in it)' in out.split(' || ')[0])
ok &= case('f8 (5) the blind zone is written in the run part and in the now part',
           out.split(' || ')[0].endswith(F.BLIND) and out.split(' || ')[1].endswith(F.BLIND) and
           F.BLIND == 'blind zone: processes born and dead inside the run: only in the system member')
ok &= case('f9 the now part samples --span (default 10 s): appA 0.100, appC 1.000 alive at both ends of the sample; python 99 '
           'is the sampler (me) -> chain', slept == [10.0] and out.split(' || ')[1].startswith('now 10.0 s: (1) alive at '
                                                                                               'both ends: foreign 1.100')
           and 'chain (pid 70 and its descendants alive at the end) 0.010 over 2' in out.split(' || ')[1])
ok &= case('f10 a negative residual is printed as it is, not clipped: (3) -8.000 - 1.100 - 0 - 0 - 0.010 = -9.110',
           '(3) system (GetSystemTimes) -8.000 CPU s/s' in out.split(' || ')[1] and
           'game - chain = -9.110 CPU s/s' in out.split(' || ')[1])
rc, out, _ = run(['--since', str(sp)], [(B, PB), (C, PC)], [1020.0, 1030.0], [S1, S2])
ok &= case('f11 without --chain-pid the chain is the sampler and its descendants only: python 99 0.020 over 1; bash 70/71 '
           'and tail are (1)/(2); kyty_emulator 7 and 9 are the game 1.200',
           'game 1.200, chain (pid None and its descendants alive at the end) 0.020 over 1' in out.split(' || ')[0] and
           '<app>:70:0.100' in term(out, '(1)') and '<app>:71:0.050' in term(out, '(2)'))
rc, out, _ = run(['--since', str(sp), '--chain-pid', 'x'], [(B, PB), (C, PC)], [1020.0, 1030.0], [S1, S2])
ok &= case('f11b a --chain-pid that is not a number reads as none', 'chain (pid None and' in out)
rc, out, slept = run(['--since', str(FX / 'none.json'), '--span', '2'], [(B, PB), (C, PC)], [1020.0, 1022.0], [S1, S2])
ok &= case('f12 without the --save file the run part is n/a and the now part still prints (span 2)',
           rc == 0 and 'run n/a (no snapshot at the lock' in out and ' || now 2.0 s:' in out and slept == [2.0])
rc, out, _ = run(['--since', str(sp)], [RuntimeError('kernel32 failed')], [1020.0], [S1])
ok &= case('f13 a failing snapshot prints one unavailable line, rc 0 (a row, not a guard)',
           rc == 0 and out.startswith('fgcpu146: unavailable (RuntimeError'))
rc, out, _ = run(['--since', str(sp)], [(B, PB), RuntimeError('x')], [1020.0, 1030.0], [S1, S2])
ok &= case('f13b the run part survives a failing second snapshot', 'run 20.0 s' in out and 'now unavailable' in out)
rc, out, _ = run(['--since', str(sp), '--chain-pid', '70'], [(B, PB), (C, PC)], [1020.0, 1030.0], [OSError('no'), S2])
ok &= case('f14 the system times unavailable at the end: (3) unavailable, (4) n/a; (1) and (2) still print',
           '(3) system unavailable' in out.split(' || ')[0] and '(4) residual n/a' in out.split(' || ')[0]
           and 'foreign 1.050' in out.split(' || ')[0])
sp2 = FX / 'nosys.json'
run(['--save', str(sp2)], [(A, PA)], [1000.0], [OSError('no')])
rc, out, _ = run(['--since', str(sp2)], [(B, PB), (C, PC)], [1020.0, 1030.0], [S1, S2])
ok &= case('f14b a --save without system times: the save says so, the run part prints (3) unavailable',
           json.loads(sp2.read_text())['sys'] is None and '(3) system unavailable' in out.split(' || ')[0])
bad = FX / 'bad.json'
bad.write_text('{"t": 1}', encoding='ascii')
rc, out, _ = run(['--since', str(bad)], [(B, PB), (C, PC)], [1020.0, 1030.0], [S1, S2])
ok &= case('f15 a broken --save file reads n/a', 'run n/a' in out)
rc, out, _ = run(['--save', str(FX / 'nodir' / 'x.json')], [(A, PA)], [1000.0], [S0])
ok &= case('f16 a --save that cannot write prints save unavailable, rc 0', rc == 0 and 'save unavailable' in out)
rc, out, _ = run([], [], [])
ok &= case('f17 no mode -> usage rc 2', rc == 2 and out.startswith('usage'))
ok &= case('f18 the constants: span 10 s, top 5, the game name, the ignore set of procload',
           F.SPAN == 10.0 and F.TOP == 5 and F.GAME == 'kyty_emulator' and F.IGNORE == {'idle', 'system', 'system idle process'})
ok &= case('f19 descendants: roots and every descendant; a cycle and a self-parent do not loop; None roots are ignored',
           F.descendants({1: 0, 2: 1, 3: 2, 4: 9, 5: 5, 6: 7, 7: 6}, [1, None]) == {1, 2, 3} and
           F.descendants({6: 7, 7: 6}, [6]) == {6, 7} and F.descendants({}, [None]) == set())
ok &= case('f20 sysrate: None when a reading is missing or the wall is 0', F.sysrate(None, S1, 1) is None and
           F.sysrate(S0, None, 1) is None and F.sysrate(S0, S1, 0) is None and F.sysrate(S0, S1, 20) == 10.0)
U = {(1, 'proc\u00e9x'): 0.0}
U2 = {(1, 'proc\u00e9x'): 5.0}
rc, out, _ = run(['--since', str(FX / 'none.json')], [(U, {1: 0}), (U2, {1: 0})], [1.0, 11.0], [S0, S1])
ok &= case('f21 a non-ASCII process name is printed as ASCII', all(ord(c) < 128 for c in out) and '<app>:1:0.500' in out)
k1 = True
try:
    cpu, par = F._win_snapshot()
    st = F._win_systimes()
    me = os.getpid()
    k1 = (any(p == me for p, _ in cpu) and par.get(me) == os.getppid() and len(cpu) > 20 and
          all(isinstance(v, float) and v >= 0 for v in cpu.values()) and len(st) == 3 and st[1] >= st[0] >= 0)
except Exception as e:      # noqa: BLE001
    print('  k1 error %s' % type(e).__name__)
    k1 = False
ok &= case('k1 the real kernel32 snapshot (read only): this process with its parent pid, > 20 processes, CPU >= 0; '
           'GetSystemTimes: 3 values, kernel >= idle', k1)
drv = FX / 'drv.py'
drv.write_text('import sys\nsys.path.insert(0, %r)\nimport importlib.util\n'
               's = importlib.util.spec_from_file_location("f", %r)\nm = importlib.util.module_from_spec(s)\n'
               's.loader.exec_module(m)\n'
               'sys.exit(m.main(["--since", "none.json", "--span", "0"], snapshot=lambda: ({(1, "proc\\u00e9x"): 1.0}, {1: 0}), '
               'systimes=lambda: (1.0, 2.0, 1.0), clock=lambda: 5.0, sleep=lambda s: None))\n' % (HERE, SRC), encoding='utf-8')
env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env['PYTHONUTF8'] = '0'
p = subprocess.run([sys.executable, str(drv)], capture_output=True, env=env, cwd=str(FX), timeout=60)
try:
    p.stdout.decode('cp1250', errors='strict')
    enc = p.returncode == 0 and b'fgcpu146:' in p.stdout and not p.stderr
except UnicodeError:
    enc = False
ok &= case('f22 a child without PYTHONIOENCODING (console cp1250) prints its line, rc 0, no error', enc)
ok &= case('f146 session 146 ("Process" 5 of s145): no input process name reaches the output - every TOP entry is '
           '<app>:<pid>:<rate>', all(('app%s:' % c) not in out for c in 'ABCDEFGH') and '<app>:' in out)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)

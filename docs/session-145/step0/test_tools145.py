"""Fixtures of cachemf145.py (the cache manifest, ROADMAP s122 item 242 (b)) and lockcheck145.py (the dangling-lock rule,
item 242 (d)) - session 143 (ported to s144 by HPP-330, to s145 by HPP-350, names 143 -> 144 -> 145) link 1b, HPP-321.  Fixture directories only: the caches of the emulator and of the driver and the
real lock are never written (t9 lists the real roots read only and prints counts only).  One case per term: every file of
every root with its relative path, size, mtime and sha256, nested directories, an absent root, the json and its sha in the
line, the round trip into sc145.cache_manifest / cache_diff / continuity (same, a changed file, a new file), an unknown root,
the usage; the lock verdicts NO LOCK / HELD (process alive, emulator alive) / UNKNOWN OWNER (old line, another tag) /
DANGLING, --remove only with the tag of the lock, its two lines with both times, the real process checks of kernel32, and
the output of both tools in strict cp1250 WITHOUT PYTHONIOENCODING.  The first output line names this suite and both
targets by sha256; the output ends with ALL OK.
    python C:/kyty/s145/test_tools145.py
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
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name + '_under_test', os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


print('suite test_tools145.py sha256 %s target cachemf145.py sha256 %s target lockcheck145.py sha256 %s' % (
    sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'cachemf145.py')), sha(os.path.join(HERE, 'lockcheck145.py'))))
M = load('cachemf145')
L = load('lockcheck145')
S = load('sc145')
FX = Path('C:/kyty/s145/fx_tools145')
shutil.rmtree(FX, ignore_errors=True)
FX.mkdir(parents=True)
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*a, **k)
    return rc, buf.getvalue().strip()


ok = True
SH, PI, GL = FX / 'shader', FX / 'pipeline', FX / 'glc'
SH.mkdir()
GL.mkdir()
(SH / 'a.bin').write_bytes(b'aaaa')
(SH / 'b.bin').write_bytes(b'bb')
(GL / 'd1' / 'd2').mkdir(parents=True)
(GL / 'd1' / 'd2' / 'x.toc').write_bytes(b'toc')
ROOTS = ['--root', 'shader=%s' % SH.as_posix(), '--root', 'pipeline=%s' % PI.as_posix(), '--root', 'glcache=%s' % GL.as_posix()]
RUNS = FX / 'runs145'
RUNS.mkdir()
o1 = RUNS / 'cache_w145_00.after.json'
rc, out = quiet(M.main, [str(o1)] + ROOTS)
js = json.loads(o1.read_text(encoding='ascii'))
ok &= case('t1 every file of every root: relative path with "/", size, mtime ns, sha256; the absent root is listed absent',
           rc == 0 and js['roots'] == [['shader', SH.as_posix(), True], ['pipeline', PI.as_posix(), False],
                                       ['glcache', GL.as_posix(), True]] and
           [f[:3] for f in js['files']] == [['shader', 'a.bin', 4], ['shader', 'b.bin', 2], ['glcache', 'd1/d2/x.toc', 3]]
           and js['files'][0][3] == os.stat(SH / 'a.bin').st_mtime_ns and js['files'][0][4] == hashlib.sha256(b'aaaa').hexdigest())
ok &= case('t2 the line: counts and bytes per root, "absent", the sha256 of the json; no directory printed',
           out == 'cachemf145: shader 2 files 6 bytes; pipeline absent; glcache 1 files 3 bytes; cache_w145_00.after.json '
                  'sha256 %s' % sha(o1) and str(FX) not in out and FX.as_posix() not in out)
o2 = RUNS / 'cache_w145_01.before.json'
quiet(M.main, [str(o2)] + ROOTS)
a, b = S.cache_manifest(str(FX), 'w145_00', 'after'), S.cache_manifest(str(FX), 'w145_01', 'before')
ok &= case('t3 the round trip into sc145: two manifests of the same caches are equal (continuity "same")',
           a is not None and S.cache_diff(a, b) == dict(shader=(0, 0, 0, False), pipeline=(0, 0, 0, False),
                                                       glcache=(0, 0, 0, False)) and
           S.continuity(str(FX), ['w145_00', 'w145_01'])[1] is None)
time.sleep(0.05)
(SH / 'b.bin').write_bytes(b'bc')
(GL / 'd1' / 'n.bin').write_bytes(b'n')
quiet(M.main, [str(o2)] + ROOTS)
b = S.cache_manifest(str(FX), 'w145_01', 'before')
lines, brk = S.continuity(str(FX), ['w145_00', 'w145_01'])
ok &= case('t4 a rewritten file (same size, new content) and a new driver file -> changed between tags, the break at w145_01',
           S.cache_diff(a, b) == dict(shader=(0, 0, 1, False), pipeline=(0, 0, 0, False), glcache=(1, 0, 0, False)) and
           brk == 'w145_01' and '  w145_00 -> w145_01: cache changed between tags (shader +0 -0 ~1; pipeline +0 -0 ~0; '
                                 'glcache +1 -0 ~0)' in lines)
PI.mkdir()
quiet(M.main, [str(o2)] + ROOTS)
ok &= case('t5 a root that appears (an empty pipeline cache) is a presence change',
           S.cache_diff(a, S.cache_manifest(str(FX), 'w145_01', 'before'))['pipeline'] == (0, 0, 0, True))
rc, out = quiet(M.main, [str(FX / 'x.json'), '--root', 'other=C:/x'])
rc2, out2 = quiet(M.main, [])
rc3, out3 = quiet(M.main, [str(FX / 'x.json'), '--root'])
ok &= case('t6 an unknown root, no output path, a --root without a value -> usage rc 2', rc == 2 and rc2 == 2 and rc3 == 2
           and out.startswith('usage') and out2.startswith('usage'))
rc, out = quiet(M.main, [str(FX / 'nodir' / 'x.json')] + ROOTS)
ok &= case('t7 a json that cannot be written -> rc 1 with one line', rc == 1 and out.startswith('cachemf145: manifest not written'))
ok &= case('t8 the default roots: the emulator caches and LOCALAPPDATA/NVIDIA/GLCache (USERPROFILE/AppData/Local without it)',
           M.default_roots(dict(LOCALAPPDATA='C:/L')) == dict(shader='C:/kyty/KytyPS5/ps5 em/_ShaderCache/PPSA21564',
                                                              pipeline='C:/kyty/KytyPS5/ps5 em/_PipelineCache',
                                                              glcache='C:/L/NVIDIA/GLCache') and
           M.default_roots(dict(USERPROFILE='C:/U'))['glcache'] == 'C:/U/AppData/Local/NVIDIA/GLCache' and
           M.ORDER == S.CACHE_ROOTS)
rr, ff = M.manifest(M.default_roots())
ok &= case('t9 the real roots read only: the translation cache is present and listed with sha256 (counts only printed)',
           rr[0][0] == 'shader' and rr[0][2] is True and sum(1 for f in ff if f[0] == 'shader') > 0 and
           all(len(f[4]) == 64 or f[4] == 'unreadable' for f in ff))
print('  real roots: %s' % ', '.join('%s %s' % (n, sum(1 for f in ff if f[0] == n) if p else 'absent') for n, _, p in rr))
# ---------------- lockcheck145
LK = FX / 'lock'
LR = FX / 'lroot'
GM = FX / 'game.exe'
GM.write_bytes(b'not the build')


def lc(argv, alive=False, game=False):
    return quiet(L.main, argv, lock=str(LK), root=str(LR), game=str(GM), alive=lambda pid: alive,
                 game_alive=lambda: game, now='2026-10-01T12:00:00Z')


rc, out = lc([])
ok &= case('l1 no lock -> NO LOCK rc 0, with the installed sha against the pinned build',
           rc == 0 and out.startswith('lockcheck145: NO LOCK; installed emulator sha256 ') and '(!= the pinned 9235a7ac)' in out)
LK.write_text('go145a.sh v145_09 pid 1234 winpid 5678 started 2026-10-01T03:00:00\n', encoding='ascii')
os.utime(LK, (1759288000, 1759288000))
rc, out = lc([], alive=True)
rc2, out2 = lc(['--remove', '--tag', 'v145_09'], game=True)
ok &= case('l2 the holder pid alive or a kyty_emulator.exe alive -> HELD rc 1, never removed (even with --remove)',
           rc == 1 and 'HELD by v145_09 (winpid 5678 alive yes' in out and rc2 == 1 and 'kyty_emulator.exe alive yes' in out2
           and LK.exists())
rc, out = lc([])
ok &= case('l3 no holder and no emulator -> DANGLING rc 2, read only without --remove; the lock mtime in UTC',
           rc == 2 and 'DANGLING lock of v145_09 (winpid 5678 not alive, no kyty_emulator.exe; lock mtime '
                       '2025-10-01T03:06:40Z)' in out and LK.exists())
rc, out = lc(['--remove', '--tag', 'w145_09'])
rc2, out2 = lc(['--remove'])
ok &= case('l4 --remove with another tag -> UNKNOWN OWNER rc 1; --remove without --tag -> rc 2; the lock stays',
           rc == 1 and 'UNKNOWN OWNER' in out and rc2 == 2 and LK.exists())
rc, out = lc(['--remove', '--tag', 'v145_09'])
tl = (LR / 'step2' / 'times.txt').read_text(encoding='ascii')
ll = (LR / 'runs145' / 'lock.log').read_text(encoding='ascii')
ok &= case('l5 --remove --tag of the lock: the lock is removed, rc 0; times.txt carries both times (noticed, lock mtime) with '
           'the source and the lock line; lock.log the release line',
           rc == 0 and not LK.exists() and tl == '2026-10-01T12:00:00Z lockcheck145 v145_09 dangling lock removed by the '
           'Harness Engineer: noticed 2026-10-01T12:00:00Z, lock mtime 2025-10-01T03:06:40Z (source: mtime of the lock '
           'file); lock line: go145a.sh v145_09 pid 1234 winpid 5678 started 2026-10-01T03:00:00\n' and
           ll == 'lock released v145_09 2026-10-01T12:00:00Z (dangling, removed by lockcheck145)\n')
LK.write_text('go145a.sh v145_09 pid 1234 started 2026-10-01T03:00:00\n', encoding='ascii')
rc, out = lc(['--remove', '--tag', 'v145_09'])
LK.write_text('go_s.sh s4 pid 1\n', encoding='ascii')
rc2, out2 = lc([])
ok &= case('l6 a lock line without winpid (the old form) or of another chain -> UNKNOWN OWNER rc 1, never removed',
           rc == 1 and rc2 == 1 and 'UNKNOWN OWNER' in out2 and LK.exists())
LK.unlink()
GM.write_bytes(b'')
ok &= case('l7 the constants: the real lock, the s145 root, the installed emulator, the pinned build',
           L.LOCK == 'C:/kyty/SEALED_RUN.lock' and L.ROOT == 'C:/kyty/s145' and
           L.GAME == 'C:/kyty/KytyPS5/ps5 em/kyty_emulator.exe' and
           L.BUILD == '9235a7ac61f1affb684c6c4440fce2bdbc99d6131a91c50eefaccd8a32fc72b7')
dead = subprocess.Popen([sys.executable, '-c', 'pass'])
dead.wait()
ok &= case('l8 the real kernel32 checks: this process is alive, a finished process is not; the emulator check is a bool',
           L._alive(os.getpid()) is True and L._alive(dead.pid) is False and isinstance(L._game_alive(), bool))
env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env['PYTHONUTF8'] = '0'
drv = FX / 'drv.py'
drv.write_text('import sys, importlib.util\n'
               'def ld(n):\n    s = importlib.util.spec_from_file_location(n, %r + "/" + n + ".py")\n'
               '    m = importlib.util.module_from_spec(s)\n    s.loader.exec_module(m)\n    return m\n'
               'M = ld("cachemf145")\nL = ld("lockcheck145")\n'
               'r1 = M.main([%r, "--root", "shader=" + %r])\n'
               'r2 = L.main([], lock="nolock", root=".", game="none")\n'
               'sys.exit(r1 + r2)\n' % (HERE, (FX / 'drv.json').as_posix(), (FX / 'd\u00e9').as_posix()), encoding='utf-8')
(FX / 'd\u00e9').mkdir()
(FX / 'd\u00e9' / 'f\u00e9.bin').write_bytes(b'x')
p = subprocess.run([sys.executable, str(drv)], capture_output=True, env=env, cwd=str(FX), timeout=120)
try:
    p.stdout.decode('cp1250', errors='strict')
    enc = p.returncode == 0 and b'cachemf145:' in p.stdout and b'lockcheck145: NO LOCK' in p.stdout and not p.stderr
except UnicodeError:
    enc = False
ok &= case('t10 both tools in a child without PYTHONIOENCODING (console cp1250): their lines, rc 0, no error (a non-ASCII '
           'file name under a root is kept in the json, not in the line)', enc)
ok &= case('t11 the json of a non-ASCII file name is ASCII (escaped)', all(b < 128 for b in (FX / 'drv.json').read_bytes()))
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)

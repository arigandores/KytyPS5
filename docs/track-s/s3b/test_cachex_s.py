"""Offline fixtures of cachex_s.py (track S, link S3, HPP-313; ROADMAP "SESSION 122" item 241 (g)(1)-(3), S1 RC1, RC12):
the app manifest reproduces d8ca8c8e... on C:/kyty/s288/snap0 and the GLCache manifest reproduces 1767ca0a... on
C:/kyty/s288/snap0_drv (read only); copy / restore / note on fixture directories only (CACHEX_EMU, CACHEX_GLC, CACHEX_LOCK):
the mirror removes extra files and copies missing / changed ones, keeps mtime, refuses a wrong expected sha, a source
without MANIFEST.txt, a write without the lock of this tag, an existing copy without --replace; DXCache is not a set.
The first output line names this suite and the tool by sha256; the output ends with ALL OK.
    python C:/kyty/s288/test_cachex_s.py
"""
import hashlib
import importlib.util
import io
import contextlib
import json
import os
import shutil
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'cachex_s.py')
print('suite test_cachex_s.py sha256 %s target cachex_s.py sha256 %s' % (
    hashlib.sha256(Path(os.path.abspath(__file__)).read_bytes()).hexdigest(), hashlib.sha256(Path(SRC).read_bytes()).hexdigest()))
BASE = Path('C:/kyty/s288/s3/fx_cachex')
shutil.rmtree(BASE, ignore_errors=True)
EMU = BASE / 'emu'
GLC = BASE / 'glc'
LOCKF = BASE / 'lock'
os.environ['CACHEX_EMU'] = str(EMU)
os.environ['CACHEX_GLC'] = str(GLC)
os.environ['CACHEX_LOCK'] = str(LOCKF)
LAD = BASE / 'lad'
os.environ['CACHEX_KNOWN_LAD'] = str(LAD)       # S3b RC9: the known folder stands here; %LOCALAPPDATA% must equal it
os.environ['LOCALAPPDATA'] = str(LAD)
_spec = importlib.util.spec_from_file_location('cachex_under_test', SRC)
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
N = [0]


def case(name, cond):
    N[0] += 1
    print('%s %s' % ('PASS' if cond else 'FAIL', name))
    return bool(cond)


def put(p, data, mtime=1700000000):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    os.utime(p, (mtime, mtime))


def run(*args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = C.main(list(args))
    return rc, buf.getvalue().strip()


ok = True
ok &= case('X1 paths come from the fixture environment', C.EMU == str(EMU) and C.GLC == str(GLC) and C.LOCK == str(LOCKF))
ok &= case('X2 the path map of RC12', C.APP_MAP == (('PipelineCache/', '_PipelineCache'),
                                                    ('ShaderCache_PPSA21564/', '_ShaderCache/PPSA21564')))
_, s_app = C.app_manifest('C:/kyty/s288/snap0')
_, s_drv = C.glc_manifest('C:/kyty/s288/snap0_drv')
ok &= case('X3 the app manifest of snap0 = d8ca8c8e... (S0 3.1, S1 RC12)',
           s_app == 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4')
ok &= case('X4 the GLCache manifest of snap0_drv (its MANIFEST.txt excluded) = 1767ca0a... (item 238 (b))',
           s_drv == '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028')
put(EMU / '_PipelineCache' / 'PPSA21564.bin', b'drv')
put(EMU / '_ShaderCache' / 'PPSA21564' / 'vs_1_2.bin', b'vs')
put(EMU / '_ShaderCache' / 'OTHER' / 'x.bin', b'other title')
put(GLC / 'a' / 'b.bin', b'glc1')
put(GLC / 'a' / 'b.toc', b'glc2', 1700000100)
t, s1 = C.app_manifest(None)
ok &= case('X5 app manifest lines: mapped path, size, sha256; sorted; another title is not in the set',
           t == 'PipelineCache/PPSA21564.bin 3 %s\nShaderCache_PPSA21564/vs_1_2.bin 2 %s\n' % (
               hashlib.sha256(b'drv').hexdigest(), hashlib.sha256(b'vs').hexdigest()))
tg, g1 = C.glc_manifest(str(GLC))
ok &= case('X6 GLCache manifest lines: rel, size, mtime UTC, sha256 (tab separated)',
           tg.splitlines()[0] == 'a/b.bin\t4\t2023-11-14T22:13:20Z\t%s' % hashlib.sha256(b'glc1').hexdigest())
rc, o = run('man', 'app')
ok &= case('X7 man app prints the sha without the lock', rc == 0 and o == 'man app sha %s' % s1)
rc, o = run('--tag', 't1', 'copy', 'app', str(BASE / 'cp'))
ok &= case('X8 copy without the lock -> rc 3, nothing written', rc == 3 and not (BASE / 'cp').exists())
LOCKF.write_text('go_s.sh other pid 1 started x\n')
rc, o = run('--tag', 't1', 'copy', 'app', str(BASE / 'cp'))
ok &= case('X9 copy under the lock of another tag -> rc 3', rc == 3)
LOCKF.write_text('go_s.sh t1 pid 1 started x\n')
rc, o = run('--tag', 't1', 'copy', 'app', str(BASE / 'cp'))
ok &= case('X10 copy app under its lock: the snapshot layout, MANIFEST.txt with the same sha', rc == 0 and
           (BASE / 'cp' / 'PipelineCache' / 'PPSA21564.bin').read_bytes() == b'drv' and
           hashlib.sha256((BASE / 'cp' / 'MANIFEST.txt').read_bytes()).hexdigest() == s1 and o.endswith('sha %s' % s1))
rc, o = run('--tag', 't1', 'copy', 'app', str(BASE / 'cp'))
ok &= case('X11 a second copy into an existing directory without --replace -> rc 1', rc == 1)
rc, o = run('--tag', 't1', 'copy', 'glc', str(BASE / 'gp'), '--replace')
ok &= case('X12 copy glc keeps mtime; its MANIFEST.txt sha = the live GLCache sha', rc == 0 and
           hashlib.sha256((BASE / 'gp' / 'MANIFEST.txt').read_bytes()).hexdigest() == g1 and
           int(os.stat(BASE / 'gp' / 'a' / 'b.toc').st_mtime) == 1700000100)
# change the live sets, then restore from the copies
put(EMU / '_PipelineCache' / 'PPSA21564.salt.bin', b'salted')
put(EMU / '_ShaderCache' / 'PPSA21564' / 'vs_1_2.bin', b'vs changed')
(EMU / '_PipelineCache' / 'PPSA21564.bin').unlink()
put(GLC / 'a' / 'new.bin', b'new')
put(GLC / 'a' / 'b.bin', b'glc1', 1700000500)
rc, o = run('--tag', 't1', 'restore', 'app', str(BASE / 'cp'), '00' * 32)
ok &= case('X13 restore with an expected sha that is not the copy manifest -> rc 1, nothing changed', rc == 1 and
           (EMU / '_PipelineCache' / 'PPSA21564.salt.bin').exists())
rc, o = run('--tag', 't1', 'restore', 'app', str(BASE / 'cp'), s1)
ok &= case('X14 restore app mirrors: the salted file removed, the changed file back, the deleted file back; live sha = '
           'expected; another title untouched', rc == 0 and C.app_manifest(None)[1] == s1 and
           not (EMU / '_PipelineCache' / 'PPSA21564.salt.bin').exists() and
           (EMU / '_ShaderCache' / 'OTHER' / 'x.bin').exists() and o.endswith('sha %s' % s1))
rc, o = run('--tag', 't1', 'restore', 'glc', str(BASE / 'gp'), g1)
ok &= case('X15 restore glc mirrors (an extra file removed, mtime restored): live sha = expected', rc == 0 and
           C.glc_manifest(str(GLC))[1] == g1 and not (GLC / 'a' / 'new.bin').exists())
rc, o = run('--tag', 't1', 'restore', 'glc', str(BASE / 'none'), g1)
ok &= case('X16 restore from a directory without MANIFEST.txt -> rc 1', rc == 1)
(BASE / 'gp' / 'a' / 'b.bin').write_bytes(b'corrupt')
rc, o = run('--tag', 't1', 'restore', 'glc', str(BASE / 'gp'), g1)
ok &= case('X17 a corrupt copy: the live sha after the mirror differs from the expected -> rc 1', rc == 1 and 'live sha' in o)
LOCKF.unlink()
rc, o = run('--tag', 't1', 'restore', 'glc', str(BASE / 'gp'), g1)
ok &= case('X18 restore without the lock -> rc 3', rc == 3)
LOCKF.write_text('go_s.sh t1 pid 1 started x\n')
cj = BASE / 'runs' / 't1.cache.json'
rc, o = run('--tag', 't1', 'note', str(cj), 'restore_app', 'expected=%s' % s1, 'got=%s' % s1)
rc2, o2 = run('--tag', 't1', 'note', str(cj), 'installed_after', 'sha=ab')
d = json.loads(cj.read_text())
ok &= case('X19 note writes and merges keys of the arm cache json', rc == 0 and rc2 == 0 and
           d == {'restore_app': {'expected': s1, 'got': s1}, 'installed_after': {'sha': 'ab'}})
rc, o = run('--tag', 't1', 'note', str(cj), 'k', 'bad')
ok &= case('X20 note with a pair without "=" -> rc 2', rc == 2)
put(EMU / '_Shaders' / 'gcn' / 'vs_0001.bin', b'gcn')
rc, o = run('--tag', 't1', 'copy', 'gcn', str(BASE / 'gcn'), '--replace')
_, sg = C.gcn_manifest(str(EMU / '_Shaders' / 'gcn'))
ok &= case('X21 copy gcn: the GCN dumps with a manifest of the same sha', rc == 0 and
           (BASE / 'gcn' / 'vs_0001.bin').read_bytes() == b'gcn' and
           hashlib.sha256((BASE / 'gcn' / 'MANIFEST.txt').read_bytes()).hexdigest() == sg)
rc, o = run('--tag', 't1', 'restore', 'gcn', str(BASE / 'gcn'), sg)
ok &= case('X22 gcn is never restored -> rc 2', rc == 2)
rc, o = run('--tag', 't1', 'restore', 'dx', str(BASE / 'gcn'), sg)
ok &= case('X23 no other set (DXCache is never touched) -> rc 2', rc == 2)
rc, o = run('man', 'glc')
ok &= case('X24 man glc prints the live GLCache sha', rc == 0 and o == 'man glc sha %s' % C.glc_manifest(str(GLC))[1])
try:
    o.encode('cp1250', errors='strict')
    enc = True
except UnicodeError:
    enc = False
ok &= case('X25 ASCII output', enc)
# S3b RC9 (item 250 (zh)): the GLCache path of the known folder FOLDERID_LocalAppData
rc, o = run('where', 'glc')
ok &= case('X26 where glc: %%LOCALAPPDATA%% = the known folder -> rc 0, the line names the path and "ok"', rc == 0 and
           o == 'where glc path %s known %s env LOCALAPPDATA %s ok' % (GLC, LAD, LAD))
os.environ['LOCALAPPDATA'] = str(LAD).replace('\\', '/').upper() + '/'
rc, o = run('where', 'glc')
ok &= case('X27 the same folder with other slashes, case and a trailing slash -> rc 0 (normalised)', rc == 0)
os.environ['LOCALAPPDATA'] = str(BASE / 'elsewhere')
snap = C.glc_manifest(str(GLC))[1]
rc1, o1 = run('where', 'glc')
rc2, o2 = run('man', 'glc')
rc3, o3 = run('--tag', 't1', 'copy', 'glc', str(BASE / 'gx'), '--replace')
rc4, o4 = run('--tag', 't1', 'restore', 'glc', str(BASE / 'gp'), g1)
ok &= case('X28 %%LOCALAPPDATA%% != the known folder -> where / man / copy / restore glc rc 1, nothing written, the live '
           'GLCache unchanged', (rc1, rc2, rc3, rc4) == (1, 1, 1, 1) and 'MISMATCH' in o1 and 'refused' in o2 and
           not (BASE / 'gx').exists() and C.glc_manifest(str(GLC))[1] == snap)
rc, o = run('man', 'app')
ok &= case('X29 the app set does not depend on the GLCache path check', rc == 0)
del os.environ['LOCALAPPDATA']
rc, o = run('where', 'glc')
ok &= case('X30 no %%LOCALAPPDATA%% in the environment -> rc 1', rc == 1 and 'env LOCALAPPDATA None MISMATCH' in o)
os.environ['LOCALAPPDATA'] = str(LAD)
del os.environ['CACHEX_KNOWN_LAD']
real = C.known_lad()
os.environ['CACHEX_KNOWN_LAD'] = str(LAD)
ok &= case('X31 the known folder without the fixture override is the real FOLDERID_LocalAppData (...\\AppData\\Local)',
           real is not None and real.replace('/', '\\').lower().endswith('\\appdata\\local') and os.path.isdir(real)
           and C.known_lad() == str(LAD) and C.known_lad(False) == real)
shutil.rmtree(GLC)
rc, o = run('--tag', 't1', 'restore', 'glc', str(BASE / 'gp'), g1)
ok &= case('X32 restore glc when the live root does not exist -> rc 1, the root is not created', rc == 1 and
           'does not exist' in o and not GLC.exists())
rc, o = run('--tag', 't1', 'copy', 'glc', str(BASE / 'gy'), '--replace')
ok &= case('X33 copy glc of a missing live root -> rc 1, no copy directory left', rc == 1 and not (BASE / 'gy').exists())
put(GLC / 'a' / 'b.bin', b'glc1')
LOCKF.unlink()
rc, o = run('--tag', 't1', 'man', 'glc', '--save', str(BASE / 'm.txt'))
ok &= case('X34 man --save without the lock of the tag -> rc 3, no file', rc == 3 and not (BASE / 'm.txt').exists())
LOCKF.write_text('go_s.sh t1 pid 1 started x\n')
rc, o = run('--tag', 't1', 'man', 'glc', '--save', str(BASE / 'm.txt'))
ok &= case('X35 man glc --save under its lock writes the manifest text whose sha is printed', rc == 0 and
           hashlib.sha256((BASE / 'm.txt').read_bytes()).hexdigest() == o.split()[-1] and
           (BASE / 'm.txt').read_bytes().startswith(b'a/b.bin\t4\t'))
rc, o = run('--tag', 't1', 'man', 'glc', '--save')
ok &= case('X36 --save without a file -> rc 2', rc == 2)
print('checks: %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)

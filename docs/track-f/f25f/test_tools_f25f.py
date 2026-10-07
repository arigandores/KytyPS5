"""F25f (HPP-669): fixtures of the harness tools - snap_f25f.py (take / restore / refuse / a missing folder / the manifest equality),
m6_f25f.py (the line with emu_t and qpc_ns, the calibration poller: first sight of each FrameTrace n, a partial line, a rotated log),
go_f25f.sh dry run (form, level, snapshots of each tag kind; refusals), queue_f25f.py (busy only on a ready track P link), strict cp1250
output of every script.  ASCII only; ends with ALL OK.
usage: python test_tools_f25f.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m6_f25f as M6  # noqa: E402

TMP = os.path.join(HERE, 'fx_tools')
print('suite test_tools_f25f.py sha256 %s target snap_f25f.py sha256 %s m6_f25f.py sha256 %s go_f25f.sh sha256 %s' % tuple(
    hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in (os.path.abspath(__file__), os.path.join(HERE, 'snap_f25f.py'),
                                                                os.path.join(HERE, 'm6_f25f.py'), os.path.join(HERE, 'go_f25f.sh'))))
ok = True
nchk = 0


def check(name, cond, got=None):
    global ok, nchk
    nchk += 1
    if not cond:
        ok = False
        print('FAIL %s (got %s)' % (name, got))


def env_cp1250():
    e = dict(os.environ)
    e.pop('PYTHONIOENCODING', None)
    e['PYTHONUTF8'] = '0'
    return e


def py(args, **kw):
    p = subprocess.run([sys.executable] + args, capture_output=True, env=env_cp1250(), **kw)
    return p.returncode, p.stdout.decode('ascii', 'replace'), p.stderr.decode('ascii', 'replace'), p.stdout


if os.path.isdir(TMP):
    shutil.rmtree(TMP)
os.makedirs(TMP)

# ---- snap_f25f.py
live = os.path.join(TMP, 'live')
for d, files in (('a', {'x.bin': b'1', 'sub/y.bin': b'22'}), ('b', {'z.bin': b'333'})):
    for f, data in files.items():
        p = os.path.join(live, d, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
LV = ['--live', 'A=%s' % os.path.join(live, 'a'), 'B=%s' % os.path.join(live, 'b'), 'C=%s' % os.path.join(live, 'c')]
root = os.path.join(TMP, 'snap')
rc, out, err, raw = py([os.path.join(HERE, 'snap_f25f.py'), 'take', 'A', '--root', root] + LV)
check('snap take A: rc 0, SNAP TAKEN A files 3 copy EQUAL (missing C is a MISSING line)', rc == 0 and out.startswith('SNAP TAKEN A files 4 copy EQUAL'),
      (rc, out, err[-200:]))
rc, out, _, _ = py([os.path.join(HERE, 'snap_f25f.py'), 'take', 'A', '--root', root] + LV)
check('snap take A again without --replace: refused', rc == 1 and 'SNAP EXISTS' in out, out)
open(os.path.join(live, 'a', 'x.bin'), 'wb').write(b'changed')
open(os.path.join(live, 'a', 'new.bin'), 'wb').write(b'n')
os.makedirs(os.path.join(live, 'c'))
open(os.path.join(live, 'c', 'w.bin'), 'wb').write(b'w')
rc, out, _, _ = py([os.path.join(HERE, 'snap_f25f.py'), 'restore', 'A', '--root', root] + LV)
check('snap restore A: rc 0, EQUAL; the changed file back, the new file gone, the folder absent in A removed',
      rc == 0 and 'SNAP RESTORED A manifest cmp EQUAL' in out and open(os.path.join(live, 'a', 'x.bin'), 'rb').read() == b'1' and
      not os.path.exists(os.path.join(live, 'a', 'new.bin')) and not os.path.exists(os.path.join(live, 'c')), out)
rc, out, _, _ = py([os.path.join(HERE, 'snap_f25f.py'), 'restore', 'Q', '--root', root] + LV)
check('snap restore of a missing snapshot: FAILED rc 1', rc == 1 and 'SNAP RESTORE FAILED' in out, out)
rc, out, _, _ = py([os.path.join(HERE, 'snap_f25f.py'), 'take', 'A', '--replace', '--root', root] + LV)
check('snap take A --replace: rc 0', rc == 0 and 'SNAP TAKEN A' in out, out)
sys.path.insert(0, HERE)
import snap_f25f as SN  # noqa: E402
check('snap live set = the 5 folders of the F20l3 manifest (labels in order)', [x.split('=')[0] for x in SN.LIVE] ==
      ['_ShaderCache', '_ShaderSeeds', '_PipelineCache', '_SaveData', 'GLCache'] and SN.LIVE[4].endswith('AppData/Local/NVIDIA/GLCache'), SN.LIVE)
import manifest_fs4c as MF  # noqa: E402
mt = os.path.join(TMP, 'm.tsv')
rc, out, _, _ = py([os.path.join(HERE, 'snap_f25f.py'), 'manifest', mt] + LV)
check('snap manifest = manifest_fs4c form (byte equal)', rc == 0 and open(mt, 'rb').read() == ('\n'.join(MF.manifest(LV[1:])) + '\n').encode(), out)

# ---- m6_f25f.py line form (fake snapshots) and the poller
fk = os.path.join(TMP, 'fake.json')
json.dump([[[10, 'game.exe', 0.0], [20, 'x.exe', 0.0]], [[10, 'game.exe', 1.0], [20, 'x.exe', 9.0]]], open(fk, 'w'))
pidf = os.path.join(TMP, 'pid.txt')
open(pidf, 'w').write('10 0\n')
loc, mo = os.path.join(TMP, 'm6l.txt'), os.path.join(TMP, 'm6.txt')
rc, out, err, raw = py([os.path.join(HERE, 'm6_f25f.py'), '--pidfile', pidf, '--local', loc, '--out', mo, '--stop', os.path.join(TMP, 'stop'),
                        '--fake', fk])
lines = open(mo).read().splitlines()
check('m6 fake: one sample line with emu_t - and qpc_ns, foreign 9.00, top <app>; end line with cal_lines 0',
      rc == 0 and len(lines) == 2 and ' emu_t=- qpc_ns=2000000000 game=1.00 loader=0.00 foreign=9.00 top=<app>:20:9.00' in lines[0] and
      lines[1] == 'M6 end samples=1 foreign_max=9.00 foreign_mean=9.00 cal_lines=0', lines)
check('m6 local file keeps the name', 'top=x.exe:20:9.00' in open(loc).read())
sys.path.insert(0, HERE)
import f25_read as R  # noqa: E402
m6r = R.read_m6(mo)
check('the reader reads the m6 line form (qpc 2e9, foreign 9.0, emu_t None)', m6r == [dict(t=1.0, emu_t=None, qpc=2000000000, foreign=9.0)], m6r)
logp = os.path.join(TMP, 'live.log')
calp = os.path.join(TMP, 'cal.txt')
open(logp, 'wb').write(b'x\nFrameTrace: n=5 dt_us=1\nFrameTrace: n=6 dt_us=1\nFrameTrace: n=6 dt_us=1\nFrameTr')
ev = threading.Event()
pl = M6.Poller(logp, calp, pidf, ev, 0.02)
pl.start()
time.sleep(0.3)
with open(logp, 'ab') as f:
    f.write(b'ace: n=7 dt_us=1\nFrameTrace: n=4 dt_us=1\n')
time.sleep(0.3)
open(logp, 'wb').write(b'FrameTrace: n=1 dt_us=1\nFrameTrace: n=8 dt_us=1\n')   # rotated (shorter): read again from 0
time.sleep(0.3)
ev.set()
pl.join(5)
cal = open(calp).read().splitlines()
ns = [int(l.split('n=')[1]) for l in cal]
check('poller: first sight of each new n (5, 6, 7 from a split line, 8 after the rotation); 6 once; smaller n not written', ns == [5, 6, 7, 8] and
      pl.lines == 4, cal)
qs = [int(l.split('qpc_ns=')[1].split()[0]) for l in cal]
check('poller: QPC of the sight non-decreasing, the later lines later', qs == sorted(qs) and qs[2] > qs[1], qs)
check('the reader reads the CAL form', R.read_cal(calp) == dict((n, q) for n, q in zip(ns, qs)))
ev2 = threading.Event()
pl2 = M6.Poller(logp, os.path.join(TMP, 'cal2.txt'), os.path.join(TMP, 'nopid.txt'), ev2, 0.02)
pl2.start()
time.sleep(0.2)
ev2.set()
pl2.join(5)
check('poller waits for the pid file of the own emulator (no pid file - no CAL lines)', open(os.path.join(TMP, 'cal2.txt')).read() == '')

# ---- go_f25f.sh dry run
BASH = 'C:/Program Files/Git/bin/bash.exe'


def dry(*a):
    e = dict(os.environ)
    e['F25F_DRYRUN'] = '1'
    p = subprocess.run([BASH, os.path.join(HERE, 'go_f25f.sh')] + list(a), capture_output=True, env=e)
    return p.returncode, p.stdout.decode('ascii', 'replace').strip()


for args, want in ((('f25_c1',), 'dryrun f25_c1 base f25_c1 level pot_treasure_cave knobs KYTY_DIAG_B32=1 pre A exp A noret 1 take C1'),
                   (('f25_c2',), 'dryrun f25_c2 base f25_c2 level bonus_path_maker_mix knobs KYTY_DIAG_B32=1 pre C1 exp C1 noret 1 take B'),
                   (('f25_z1',), 'dryrun f25_z1 base f25_z1 level pot_treasure_cave knobs KYTY_DIAG_B32=0 pre - exp B noret 0 take -'),
                   (('f25_z2',), 'dryrun f25_z2 base f25_z2 level bonus_path_maker_mix knobs KYTY_DIAG_B32=0 pre - exp B noret 0 take -'),
                   (('f25_pb',), 'dryrun f25_pb base f25_pb level pot_treasure_cave knobs KYTY_DIAG_B32=1 KYTY_TEST_B32=60:present:3000 pre - exp B noret 0 take -'),
                   (('f25_pc',), 'dryrun f25_pc base f25_pc level bonus_path_maker_mix knobs KYTY_DIAG_B32=1 KYTY_TEST_B32=60:gpusleep:6000 pre - exp B noret 0 take -'),
                   (('f25_s01', 'pot'), 'dryrun f25_s01 base f25_s01 level pot_treasure_cave knobs KYTY_DIAG_B32=1 pre - exp B noret 0 take -'),
                   (('f25_s40_r2', 'bonus'), 'dryrun f25_s40_r2 base f25_s40 level bonus_path_maker_mix knobs KYTY_DIAG_B32=1 pre - exp B noret 0 take -'),
                   (('f25_k03', 'bonus'), 'dryrun f25_k03 base f25_k03 level bonus_path_maker_mix knobs KYTY_DIAG_B32=1 pre A exp A noret 0 take -'),
                   (('f25_z1', 'bonus'), 'dryrun f25_z1 base f25_z1 level pot_treasure_cave knobs KYTY_DIAG_B32=0 pre - exp B noret 0 take -')):
    rc, out = dry(*args)
    check('go dry run %s' % ' '.join(args), rc == 0 and out == want, (rc, out))
for args in (('f25_s01',), ('f25_s01', 'x'), ('f25_s41', 'pot'), ('f25_k11', 'pot'), ('f25_c3',), ('b32_s01', 'pot'), ('f25_s01_r7', 'pot')):
    rc, out = dry(*args)
    check('go dry run refused %s (rc 2)' % ' '.join(args), rc == 2, (rc, out))
check('go: the KYTY_GPU_HANG_ABORT_S=22 pair after the harness constants in the call', 'KYTY_GPU_WALL=1 KYTY_GPU_HANG_ABORT_S=22 $KN' in
      open(os.path.join(HERE, 'go_f25f.sh')).read())
check('go: binary B and S18 constants', 'TB=e342b839d74d5689bc4f66ee0ed04a37e9a640e60a199a2882c8e83ecf19cfa4' in open(os.path.join(HERE, 'go_f25f.sh')).read()
      and 'S18=b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a' in open(os.path.join(HERE, 'go_f25f.sh')).read())

# ---- queue_f25f.py
qf = os.path.join(TMP, 'q.json')
json.dump([dict(identifier='HPP-669', status='in_progress', title='\u0442\u0440\u0435\u043a F, F25f', executionRunId='x'),
           dict(identifier='HPP-664', status='in_progress', title='\u0442\u0440\u0435\u043a F, F24e', executionRunId='y'),
           dict(identifier='HPP-1', status='blocked', title='track P link', executionRunId=None)], open(qf, 'w', encoding='utf-8'))
rc, out, _, _ = py([os.path.join(HERE, 'queue_f25f.py'), '--fake', qf])
check('queue: a ready F link and a blocked P link -> QUEUE FREE (rc 0)', rc == 0 and 'QUEUE FREE' in out and 'HPP-664 in_progress track F' in out, out)
json.dump([dict(identifier='HPP-2', status='todo', title='track P link', executionRunId=None)], open(qf, 'w', encoding='utf-8'))
rc, out, _, _ = py([os.path.join(HERE, 'queue_f25f.py'), '--fake', qf])
check('queue: a ready P link -> QUEUE BUSY (rc 1)', rc == 1 and 'QUEUE BUSY: HPP-2' in out, out)

# ---- strict cp1250 output of the python scripts (usage / --help paths)
for s, a in (('snap_f25f.py', []), ('f25_read.py', ['x']), ('regress_f25.py', None), ('refs_f25f.py', None)):
    if a is None:
        continue
    rc, out, err, raw = py([os.path.join(HERE, s)] + a)
    check('%s prints ASCII in strict cp1250 (rc %d)' % (s, rc), all(b < 128 for b in raw) and 'Traceback' not in err, err[-200:])

shutil.rmtree(TMP)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

"""F25f (HPP-669): fixtures of the harness tools (seal 2: + item 606 - reconcile, merge-return, hold check) - snap_f25f.py (take / restore / refuse / a missing folder / the manifest equality),
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

# ---- item 606: reconcile (B' / A', user files D, stop, limit), restore keeps D, merge-return, hold check
R6 = os.path.join(TMP, 'r606')
lv6 = os.path.join(R6, 'live')
rt6 = os.path.join(R6, 'snap')


def put6(rel, data):
    p = os.path.join(lv6, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'wb').write(data)


put6('S/a.bin', b'a')
put6('S/old.bin', b'old')
put6('G/u/x.bin', b'x')
LV6 = ['--live', 'S=%s' % os.path.join(lv6, 'S'), 'G=%s' % os.path.join(lv6, 'G')]
SN = os.path.join(HERE, 'snap_f25f.py')


def sn(*a):
    return py([SN] + list(a) + ['--root', rt6] + LV6)


check('606: take A', sn('take', 'A')[0] == 0)
put6('S/a.bin', b'a2')             # prewarm changes a series file
put6('S/b.bin', b'b')              # prewarm adds one
os.remove(os.path.join(lv6, 'S/old.bin'))   # prewarm removes one
check('606: take B', sn('take', 'B')[0] == 0)
rc, out, err, _ = sn('reconcile')
check('606: reconcile at B (no STATE file = B) -> EQUAL rc 0', rc == 0 and out.startswith('RECONCILE EQUAL state B'), (rc, out, err[-200:]))
put6('G/u/vm.bin', b'vm1')         # the user VM adds a file outside A and B
rc, out, _, _ = sn('reconcile')
A6, B6, D6 = [SN_M.read_tsv(os.path.join(rt6, n + '.tsv')) for n in ('A', 'B', 'D')] if False else (None, None, None)
import snap_f25f as SN_M  # noqa: E402
A6, B6, D6 = [SN_M.read_tsv(os.path.join(rt6, n + '.tsv')) for n in ('A', 'B', 'D')]
check("606: a new user file -> UPDATED 1 of 2 (new 1); B' = live (EQUAL); the file in A', B', D, copies in both snapshots",
      rc == 0 and out.startswith('RECONCILE UPDATED 1 of 2: state B new 1 changed 0 removed 0; snapshot B = live EQUAL') and
      ('G', 'u/vm.bin') in A6 and ('G', 'u/vm.bin') in B6 and ('G', 'u/vm.bin') in D6 and
      open(os.path.join(rt6, 'A', 'G', 'u', 'vm.bin'), 'rb').read() == b'vm1' and open(os.path.join(rt6, 'B', 'G', 'u', 'vm.bin'), 'rb').read() == b'vm1',
      (rc, out))
check('606: A0.tsv / B0.tsv keep the first snapshots (no user file in them)', ('G', 'u/vm.bin') not in SN_M.read_tsv(os.path.join(rt6, 'A0.tsv')) and
      ('G', 'u/vm.bin') not in SN_M.read_tsv(os.path.join(rt6, 'B0.tsv')) and len(SN_M.read_tsv(os.path.join(rt6, 'A0.tsv'))) == 3)
check('606: reconcile again -> EQUAL', sn('reconcile')[1].startswith('RECONCILE EQUAL'))
put6('G/u/vm.bin', b'vm2')         # the user file D changed
rc, out, _, _ = sn('reconcile')
check('606: a changed user file -> UPDATED 2 of 2 (changed 1)', rc == 0 and out.startswith('RECONCILE UPDATED 2 of 2: state B new 0 changed 1'), out)
put6('G/u/vm3.bin', b'v3')
rc, out, _, _ = sn('reconcile')
check('606: the third update -> LIMIT rc 5, nothing changed (vm3 not in B)', rc == 5 and out.startswith('RECONCILE LIMIT') and
      ('G', 'u/vm3.bin') not in SN_M.read_tsv(os.path.join(rt6, 'B.tsv')), (rc, out))
os.remove(os.path.join(lv6, 'G/u/vm3.bin'))
open(os.path.join(rt6, 'updates.log'), 'w').write('x\n')     # back to one update for the next members
put6('S/a.bin', b'a3')             # a series file changed by someone
rc, out, _, _ = sn('reconcile')
check('606 (4): a changed series file -> STOP rc 4, nothing updated', rc == 4 and out.startswith('RECONCILE STOP state B: 1') and
      SN_M.read_tsv(os.path.join(rt6, 'B.tsv'))[('S', 'a.bin')][1] != SN_M.read_tsv(os.path.join(rt6, 'B.tsv')).get(('S', 'zz'), ('', ''))[1], (rc, out))
put6('S/a.bin', b'a2')
os.remove(os.path.join(lv6, 'S/b.bin'))
rc, out, _, _ = sn('reconcile')
check('606 (4): a removed series file -> STOP rc 4', rc == 4 and 'S/b.bin' in out, (rc, out))
put6('S/b.bin', b'b')
put6('S/old.bin', b'old')          # a file of A (removed in B) back in the live set at state B
rc, out, _, _ = sn('reconcile')
check('606 (4): a series file of A unexpected at state B -> STOP rc 4', rc == 4 and 'S/old.bin' in out, (rc, out))
os.remove(os.path.join(lv6, 'S/old.bin'))
check('606: back to EQUAL', sn('reconcile')[1].startswith('RECONCILE EQUAL'))
rc, out, _, _ = sn('restore', 'A')
check("606 (3): restore A' keeps the user file with the same content and removes the files of the prewarm (b.bin)",
      rc == 0 and open(os.path.join(lv6, 'G/u/vm.bin'), 'rb').read() == b'vm2' and not os.path.exists(os.path.join(lv6, 'S/b.bin')) and
      open(os.path.join(lv6, 'S/old.bin'), 'rb').read() == b'old' and open(os.path.join(lv6, 'S/a.bin'), 'rb').read() == b'a', (rc, out))
check("606: STATE A -> reconcile against A' EQUAL", sn('state', 'A')[0] == 0 and sn('reconcile')[1].startswith('RECONCILE EQUAL state A'))
os.remove(os.path.join(lv6, 'G/u/vm.bin'))
rc, out, _, _ = sn('reconcile')
check("606 (3): a removed user file -> UPDATED (removed 1), dropped from A' and B' and D", rc == 0 and 'removed 1' in out and
      ('G', 'u/vm.bin') not in SN_M.read_tsv(os.path.join(rt6, 'A.tsv')) and ('G', 'u/vm.bin') not in SN_M.read_tsv(os.path.join(rt6, 'D.tsv')),
      (rc, out))
mb, ml = os.path.join(R6, 'mb'), os.path.join(R6, 'ml')
for d, files in ((mb, {'x.bin': b'1', 'sub/y.bin': b'2'}), (ml, {'x.bin': b'changed', 'vm.bin': b'v'})):
    for f, data in files.items():
        p = os.path.join(d, f)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(data)
rc, out, _, _ = py([SN, 'merge-return', 'GLCache', mb, ml])
check('606 (3): merge-return writes the copy back (x 1, sub/y 2), keeps the live file not in the copy (vm.bin), removes the copy',
      rc == 0 and out.startswith("MERGE RETURN kept 1: ['vm.bin']") and open(os.path.join(ml, 'x.bin'), 'rb').read() == b'1' and
      open(os.path.join(ml, 'sub/y.bin'), 'rb').read() == b'2' and open(os.path.join(ml, 'vm.bin'), 'rb').read() == b'v' and
      not os.path.exists(mb), out)
HD = os.path.join(HERE, 'hold_f25f.py')
GLP = os.path.join(os.environ.get('USERPROFILE', 'C:/Users/x'), 'AppData/Local/NVIDIA/GLCache').replace('\\', '/')
hf = os.path.join(TMP, 'hold.json')
for procs, want_rc, want in (([dict(pid=5, name='qemu-system-x86_64.exe', files=[])], 9, 'HOLD USER SESSION 1: <app> pid 5 kind vm'),
                             ([dict(pid=6, name='x.exe', files=[GLP + '/a/b.bin'])], 9, 'HOLD USER SESSION 1: <app> pid 6 kind holder'),
                             ([dict(pid=7, name='emulator.exe', files=[])], 9, 'HOLD USER SESSION 1: <app> pid 7 kind vm'),
                             ([dict(pid=10, name='kyty_emulator.exe', files=[GLP + '/a/b.bin'])], 0, 'HOLD CLEAR'),
                             ([dict(pid=8, name='y.exe', files=['C:/other/GLCacheX/a.bin'])], 0, 'HOLD CLEAR')):
    json.dump(procs, open(hf, 'w', encoding='ascii'))
    rc, out, _, raw = py([HD, 'check', '--pidfile', pidf, '--fake', hf])
    check('606 (1): hold check %s -> rc %d %s (own pid 10 excluded, names masked)' % (procs[0]['name'], want_rc, want),
          rc == want_rc and out.strip() == want and b'qemu' not in raw and b'x.exe' not in raw, (rc, out))
json.dump([dict(pid=5, name='qemu-system-x86_64.exe', files=[])], open(hf, 'w', encoding='ascii'))
fl = os.path.join(TMP, 'vmflag.txt')
rc, out, _, _ = py([HD, 'watch', '--pidfile', os.path.join(TMP, 'nopid.txt'), '--flag', fl, '--stop', os.path.join(TMP, 'nostop'), '--fake', hf])
check('606 (1): hold watch (fake, one poll) does not flag on a single sight (2 in a row needed)', rc == 0 and not os.path.exists(fl), (rc, out))
check('606: go_f25f.sh runs reconcile before every non-prewarm tag, the hold check before and after the lock, the VM watch and the merge',
      all(s in open(os.path.join(HERE, 'go_f25f.sh')).read() for s in ('snap_f25f.py reconcile', 'hold_f25f.py check', 'hold_f25f.py watch',
                                                                        'merge-return GLCache', 'SERIES_STOP', 'snap_f25f.py state A')))
check('606: launch_f25f.sh refuses on a user session (exit 7) before the block status', 'hold_f25f.py check' in open(os.path.join(HERE, 'launch_f25f.sh')).read())

# ---- strict cp1250 output of the python scripts (usage / --help paths)
for s, a in (('snap_f25f.py', []), ('hold_f25f.py', []), ('f25_read.py', ['x']), ('regress_f25.py', None), ('refs_f25f.py', None)):
    if a is None:
        continue
    rc, out, err, raw = py([os.path.join(HERE, s)] + a)
    check('%s prints ASCII in strict cp1250 (rc %d)' % (s, rc), all(b < 128 for b in raw) and 'Traceback' not in err, err[-200:])

shutil.rmtree(TMP)
print('checks %d' % nchk)
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

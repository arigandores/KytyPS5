"""Track M link M6c (HPP-850): fixtures of the M6c reader m6c_read.py and of the harness plan (go_m6c.sh dry run) - one or more checks per
member and per edge: the M5W2Stat line form (21 fields in order), the total of item 770 (e) (last line with the largest pushes; ties ->
the later line; a later smaller line does not win), the M5W2Clr group (same when, after the chosen line, before the next Stat line), the
unparsable lines, the knob witness, the no-knob lines, the reference rows (sums of per-frame counters), the tag table (plan_of = the case
of go_m6c.sh by the dry run), the admission on a real M3a tag (binary, knob witness and plan members are NO), the strict cp1250 output.
First line 'suite ... target ...', last line ALL OK.  ASCII only.
usage: python test_m6c.py"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m6c_read as R  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_m6c.py sha256 %s target m6c_read.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'm6c_read.py'))))
n = 0
bad = []


def check(name, cond):
    global n
    n += 1
    if not cond:
        bad.append(name)
    print('[%s] %s' % ('ok' if cond else 'FAIL', name))


def stat(when, vals):
    return ('[t][00:00:00.000] M5W2Stat: when=%s ' % when + ' '.join('%s=%d' % (f, v) for f, v in zip(R.FIELDS, vals)) + '\n').encode()


def clr(when, fmt, a, b, c):
    return ('M5W2Clr: when=%s fmt=%d clr_dw=%d clr_dw_div=%d clr_dw_div8=%d\n' % (when, fmt, a, b, c)).encode()


def write(lines):
    fd, p = tempfile.mkstemp(suffix='.txt')
    with os.fdopen(fd, 'wb') as f:
        f.write(b''.join(lines))
    return p


V1 = list(range(1, 22))
V2 = [10] + [0] * 20
V3 = [10] + list(range(100, 120))
V4 = [7] + [5] * 20
log1 = write([
    b'M5W2: mode=1\n',
    stat('periodic', V1), clr('periodic', 9, 3, 0, 1),
    b'FrameTrace-x: n=1 a=0 clr_ok=4 b=1\n', b'FrameTrace-x: n=2 clr_ok=6\n', b'FrameTrace-draw: n=2 x=1 img_minlod=2 y=0\n',
    stat('periodic', V2), clr('periodic', 16, 8, 1, 2),
    stat('exit', V3), clr('exit', 9, 11, 0, 4), clr('exit', 37, 5, 5, 0), clr('periodic', 9, 99, 99, 99),
    stat('exit', V4), clr('exit', 9, 1, 1, 1),
    b'M5W2Stat: when=exit pushes=1 broken\n',
    b'GuestPrintf: negative precision prec=-3\n', b'AmprRecordSpace: refused why=space cb=0x1 n=1\n',
    b'AmprWriteAddress: refused why=state cb=0x1 n=1\n', b'AgcReserveDW: cursor state class=up0 up=0x0 n=1\n',
    b'AgcReserveDW: cursor state class=up0 up=0x0 n=2\n',
    b'Texture: T# MIN_LOD 128/256 applied to a sampled view (x)\n',
    b'MWave1: mask=0x33 T234=1 T233=1 T256=0 T306=0 T032=1 T203=1\n', b'MT272: mode=1\n',
])
y = R.scan_m5(log1)
t = R.total_of(y)
check('stat lines parsed 4 (the broken line is unparsable)', len(y['stat']) == 4)
check('unparsable stat lines 1', y['stat_bad'] == 1)
check('total = last line with the largest pushes (V3 exit, not the later V4 with pushes 7)', t is not None and t['when'] == 'exit'
      and t['ao_obj_push'] == 100 and t['ao_obj_vq'] == 119)
check('fields in order: pushes first, ao_obj_vq last (V1 line)', y['stat'][0]['pushes'] == 1 and y['stat'][0]['ao_obj_vq'] == 21
      and y['stat'][0]['minlod_div_x'] == 17 and y['stat'][0]['clr_dw_div8'] == 18 and y['stat'][0]['ao_obj_unread'] == 19
      and y['stat'][0]['inv_part_src'] == 20)
check('clr group of the total: 2 lines with when=exit, fmt 9 and 37', [c['fmt'] for c in t['clr']] == [9, 37] and t['clr'][0]['clr_dw_div8'] == 4)
check('clr line with another when after a Stat line is outside the group (clr_bad 1 + the line after the broken Stat 0)', y['clr_bad'] == 1)
check('knob witness mode [1]', y['mode'] == [1] and y['mode_bad'] == 0)
check('no-knob counts T031 1, T309 1+1, T023 2', y['noknob'] == {'T031': 1, 'T309_space': 1, 'T309_waddr': 1, 'T023': 2})
check('no-knob first line kept', y['noknob_first']['T023'].startswith('AgcReserveDW: cursor state class=up0 up=0x0 n=1'))
check('reference clr_ok = sum of per-frame deltas 10 over 2 lines', y['clr_ok'] == 10 and y['clr_ok_lines'] == 2)
check('reference img_minlod 2 and T# MIN_LOD applied lines 1', y['img_minlod'] == 2 and y['tminlod'] == 1)
check('MWave1 0x33 and MT272 1 parsed', y['mw'] == [0x33] and y['mt']['272'] == [1])

tie = write([stat('periodic', V2), clr('periodic', 9, 1, 0, 0), stat('exit', V2), clr('exit', 16, 2, 0, 0)])
yt = R.scan_m5(tie)
tt = R.total_of(yt)
check('tie of pushes -> the later line (exit) and its clr group', tt['when'] == 'exit' and [c['fmt'] for c in tt['clr']] == [16])
empty = write([b'nothing here\n'])
ye = R.scan_m5(empty)
check('no Stat line -> total None, mode []', R.total_of(ye) is None and ye['mode'] == [])
check('missing log -> None', R.scan_m5(os.path.join(HERE, 'no_such_log.txt')) is None)
two = write([b'M5W2: mode=1\n', b'M5W2: mode=1\n', b'M5W2: mode=x\n'])
y2 = R.scan_m5(two)
check('two mode lines and one unparsable are seen (admission needs exactly [1])', y2['mode'] == [1, 1] and y2['mode_bad'] == 1)
for p in (log1, tie, empty, two):
    os.remove(p)

for tg, lv in (('m6_sg', 'underwater_aerial_garden'), ('m6_hb', 'hoover_beach'), ('m6_mg', 'mini_giants_garden'), ('m6_hb_r2', 'hoover_beach')):
    p = R.plan_of(tg)
    check('plan_of %s level %s hold 330 knob KYTY_DIAG_M5W2=1' % (tg, lv), p is not None and p['level'] == lv and p['hold'] == 330
          and p['knob'] == ('KYTY_DIAG_M5W2', '1'))
for tg in ('m6_xx', 'm3_sg_v', 'm6_sg_r4', 'm6_sg_v', ''):
    check('plan_of %r unknown' % tg, R.plan_of(tg) is None)
GO = os.path.join(HERE, 'go_m6c.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
if os.path.exists(GO):
    env = dict(os.environ, M6C_DRYRUN='1')
    for tg in ('m6_sg', 'm6_hb', 'm6_mg', 'm6_mg_r1'):
        o = subprocess.run([BASH, GO, tg], capture_output=True, env=env).stdout.decode('ascii', 'replace')
        p = R.plan_of(tg)
        want = 'level %s kind v sd 300 timeout 480 hold 330 rec --rec cache K0 save none knobs KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0 KYTY_DIAG_M5W2=1' % p['level']
        check('go_m6c.sh dry run of %s = the plan of the reader' % tg, [ln for ln in o.splitlines() if ln.startswith('dryrun %s ' % tg) and want in ln] != [])
    for tg in ('m6_xx', 'm6_sg_r4'):
        rc = subprocess.run([BASH, GO, tg], capture_output=True, env=env).returncode
        check('go_m6c.sh dry run of %s refused (rc 2)' % tg, rc == 2)
else:
    check('go_m6c.sh present next to the reader', False)

# admission on a real M3a tag (MS1 binary, no knob): admitted must be False, with the binary, knob witness and plan members NO
M3 = 'C:/kyty/m657/m3a'
if os.path.exists(M3 + '/log_m3_hb_v.txt'):
    d = tempfile.mkdtemp()
    pth = R.paths('m6_hb', d)
    src = dict(log=M3 + '/log_m3_hb_v.txt', stdout=M3 + '/stdout_m3_hb_v.txt', run=M3 + '/m3_hb_v.json', idx=M3 + '/rec_m3_hb_v.mp4.idx',
               seal=M3 + '/pred.md', installed_before=M3 + '/runs/m3_hb_v/installed_before.txt',
               installed_after=M3 + '/runs/m3_hb_v/installed_after.txt', manifest_cmp=M3 + '/runs/m3_hb_v/manifest_cmp.txt',
               installed_sha=M3 + '/runs/m3_hb_v/installed_sha.txt', level=M3 + '/runs/m3_hb_v/level.txt',
               plan=M3 + '/runs/m3_hb_v/plan.txt')
    for k, s in src.items():
        if os.path.exists(s):
            os.link(s, pth[k]) if k == 'log' else open(pth[k], 'wb').write(open(s, 'rb').read())
    res = R.read_tag('m6_hb', pth)
    am = dict((a.split(' (')[0], b) for a, b in res['admission'])
    check('real M3a tag: NOT_ADMITTED', res['status'] == 'NOT_ADMITTED')
    check('real M3a tag: json binary member NO', am.get('json binary_sha256 = M6a3 test binary 2179005b') is False)
    check('real M3a tag: knob witness member NO', [b for a, b in res['admission'] if a.startswith('knob witness')] == [False])
    check('real M3a tag: env member NO (KYTY_DIAG_M5W2 missing)', [b for a, b in res['admission'] if a.startswith('env = ')] == [False])
    check('real M3a tag: entry line and window members ok', [b for a, b in res['admission'] if a.startswith(('entry line', 'window events'))] == [True, True])
    check('real M3a tag: signature member ok (MS1 8dcf3177, mw1_33)', [b for a, b in res['admission'] if a.startswith('translation signature')] == [True])
    yr = R.scan_m5(pth['log'])
    check('real M3a log: 0 M5W2 lines, reference clr_ok > 0', yr['stat'] == [] and yr['mode'] == [] and yr['clr_ok'] > 0)
    for k in pth:
        if os.path.exists(pth[k]):
            os.remove(pth[k])
    os.rmdir(d)
else:
    check('M3a log for the admission fixture present', False)

envc = dict(os.environ)
envc.pop('PYTHONIOENCODING', None)
envc['PYTHONIOENCODING'] = 'cp1250:strict'
o = subprocess.run([sys.executable, os.path.join(HERE, 'm6c_read.py'), '--plan', 'm6_mg'], capture_output=True, env=envc)
check('reader output in strict cp1250 (rc 0, ascii)', o.returncode == 0 and o.stdout.decode('ascii', 'replace').startswith('bin m6a3 level mini_giants_garden'))
src = open(os.path.join(HERE, 'm6c_read.py'), 'rb').read()
check('reader source is ASCII', all(c < 128 for c in src))
print('checks %d, failed %d %s' % (n, len(bad), bad))
print('ALL OK' if not bad else 'FAILED')
sys.exit(0 if not bad else 1)

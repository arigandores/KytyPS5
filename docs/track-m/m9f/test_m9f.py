"""Track M link M9f (HPP-871): fixtures of the T188 rules t188_rules.py, the reader m9f_read.py, the detector nmag_m9f.py, the queue
queue_m9f.py and the harness plan (go_m9f.sh dry run) - one or more checks per member and per edge: the line forms (70 / 27 / 10 fields
in order, a log prefix, unparsable lines, key=other), the mode witness, E (exit lines), Z (invariants on every line), N (I7 cls=all),
I1, I2a-d, I3 (every class field, tint_skip = sum of the five skips, key=other in the sum), I4, I5 (when=exit, the conditional part_off
member), I6 (each equation and each bound at its edge, the K x classes bound with key=other), I8, I9 (each chain at its edge), the class
choice of item 785 (v)(2) (share edge 0.8, at most 2, key=other never chosen, ties, scene sum 0), the class rows (readback alive needs
the global zeros, coverage edge 0.5), the field open of item 788 (g) N2, the T109 rule of item 791 (v) (one line, first at exit, a later
periodic line with 0, two periodic lines) and 789 (g)(3), the detector on a synthetic video (threshold edge, top12 ties, pairs at the same
offset from the first scene frame, pairs beyond the M6c window), the queue (M3a2 ahead), the plan of go_m9f.sh, the admission on a real
M6c tag (binary, T188 witness and env members NO) and the strict cp1250 output.  First line 'suite ... target ...', last line ALL OK.
ASCII only.
usage: python test_m9f.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import t188_rules as T  # noqa: E402
import m9f_read as R  # noqa: E402
import nmag_m9f as NM  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('suite test_m9f.py sha256 %s target m9f_read.py sha256 %s t188_rules.py sha256 %s nmag_m9f.py sha256 %s queue_m9f.py sha256 %s '
      'test_t188.py sha256 %s' % (sha(os.path.abspath(__file__)), sha(os.path.join(HERE, 'm9f_read.py')), sha(os.path.join(HERE, 't188_rules.py')),
                                  sha(os.path.join(HERE, 'nmag_m9f.py')), sha(os.path.join(HERE, 'queue_m9f.py')),
                                  sha(os.path.join(HERE, 'test_t188.py'))))
n = 0
bad = []


def check(name, cond):
    global n
    n += 1
    if not cond:
        bad.append(name)
    print('[%s] %s' % ('ok' if cond else 'FAIL', name))


# ---- part 1: the rules suite test_t188.py (the mutlib suite) - run here, must end with ALL OK ----------------------------------------
o = subprocess.run([sys.executable, os.path.join(HERE, 'test_t188.py')], capture_output=True)
tt = o.stdout.decode('ascii', 'replace').splitlines()
check('rules suite test_t188.py: rc 0, last line ALL OK, 0 FAIL lines (%s; %s)' % (tt[-2] if len(tt) > 1 else '-', tt[0][:90] if tt else '-'),
      o.returncode == 0 and tt and tt[-1] == 'ALL OK' and not [x for x in tt if x.startswith('FAIL')])


def mem_of(ch, prefix):
    return [b for a, b in ch if a.startswith(prefix)]


def base_stat():
    e = dict((k, 0) for k in T.STAT)
    e.update(part=1, part_st=1, w_mipal=1, ep_new=1, open=1)
    return e


e = base_stat()
sl = ('T188Stat: when=exit ' + ' '.join('%s=%d' % (k, e[k]) for k in T.STAT) + '\n').encode()
im0 = dict((k, 0) for k in T.CLS)
im0.update(ev=1, ev_st=1, ep_new=1)
il = ('T188Img: when=exit key=00000000000000aa ' + ' '.join('%s=%d' % (k, 1) for k in T.HEAD) + ' ' +
      ' '.join('%s=%d' % (k, im0[k]) for k in T.CLS) + '\n').encode()
ol = ('T188Img: when=exit key=other ' + ' '.join('%s=0' % k for k in T.CLS) + '\n').encode()
tl = ('T109Stat: when=exit ' + ' '.join('%s=%d' % (k, v) for k, v in zip(T.T109, (5, 2, 1, 1, 0, 0, 0, 0, 0, 0))) + '\n').encode()

# ---- detector on a synthetic video -------------------------------------------------------------------------------------------------
check('select: top12 ties -> the earlier record; sorted by record', NM.select([5, 9, 9, 1] + [0] * 20, list(range(24)))[:3] == [0, 1, 2])
check('even: 12 offsets over a window of 100', len(NM.even(list(range(100)))) == 12 and NM.even(list(range(100)))[0] == 0
      and NM.even(list(range(100)))[-1] == 99)
check('even: a window of 5 -> all 5', NM.even(list(range(5))) == list(range(5)))
fx = tempfile.mkdtemp()
NF = 40
FSN = 11


def mkvid(path, sq):
    p = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '960x540',
                          '-r', '60', '-i', '-', '-c:v', 'libx264', '-qp', '0', '-pix_fmt', 'yuv444p', path], stdin=subprocess.PIPE)
    for i in range(NF):
        a = np.full((540, 960, 3), 60, dtype=np.uint8)
        if i in sq:
            s = sq[i]
            a[100:100 + s, 100:100 + s] = (255, 0, 255)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    p.wait()


# tag: records 0..39, presents 1..40; first scene present 11 -> w0 = record 10.  Squares: 18x18 = 324 at record 15 (below 338),
# 19x19 = 361 at 20 (> 338), 30x30 at 25, 30x30 at 30; record 5 has a big square before the window (not counted).
mkvid(os.path.join(fx, 'rec.mp4'), {5: 40, 15: 18, 20: 19, 25: 30, 30: 30})
mkvid(os.path.join(fx, 'm6c.mp4'), {})
open(os.path.join(fx, 'rec.idx'), 'w').write(''.join('%d %d %.3f\n' % (i, i + 1, i / 60) for i in range(NF)))
open(os.path.join(fx, 'm6c.idx'), 'w').write(''.join('%d %d %.3f\n' % (i, i + 3, i / 60) for i in range(30)))
json.dump(dict(info=dict(first_scene_n=FSN)), open(os.path.join(fx, 'read.json'), 'w'))
json.dump(dict(info=dict(first_scene_n=FSN)), open(os.path.join(fx, 'm6c.json'), 'w'))
od = os.path.join(fx, 'out')
os.environ['M9F_NMAG_NOLOCK'] = '1'
rc = NM.main(['--dir', fx, 't188_sg2', od])
nj = json.load(open(os.path.join(od, 'nmag.json')))
check('detector: rc 0, window from present 11 = record 10, 30 records', rc == 0 and nj['w0'] == 10 and nj['window_records'] == 30)
check('detector: 324 px (18x18) not marked, 361 px (19x19) marked (threshold 338 edge), the square before the window not counted',
      nj['marked'] == 3 and nj['marked_ge3'] and nj['threshold'] == 338)
check('detector: top12 led by records 20/25/30 with N_mag 361/900/900', [t['record'] for t in nj['top'] if t['nmag'] > 0] == [15, 20, 25, 30]
      and [t['nmag'] for t in nj['top'] if t['record'] in (20, 25)] == [361, 900])
check('detector: pair of record 20 (offset 10) = M6c w0 8 + 10 = record 18', [t['m6c_record'] for t in nj['top'] if t['record'] == 20] == [18])
check('detector: offsets beyond the M6c window -> none (M6c window records 8..29)', [t['m6c_record'] for t in nj['even'] if t['record'] == 39] == [None])
check('detector: sheet_top.png and 4 pair sheets written', all(os.path.exists(os.path.join(od, s)) for s in nj['sheets']) and len(nj['sheets']) == 5)
os.environ.pop('M9F_NMAG_NOLOCK', None)
check('detector: unknown tag refused (rc 9)', NM.main(['--dir', fx, 'm6_sg', od]) == 9)
shutil.rmtree(fx)

# ---- queue -----------------------------------------------------------------------------------------------------------------------------
Q = os.path.join(HERE, 'queue_m9f.py')


def qrun(issues, extra=None):
    fd, p = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w') as f:
        json.dump(dict(issues=issues, extra=extra or []), f)
    o = subprocess.run([sys.executable, Q, '--fake', p], capture_output=True)
    os.remove(p)
    return o.returncode, o.stdout.decode('ascii', 'replace')


I861 = dict(identifier='HPP-861', status='in_progress', title='M3a2 (track M)', executionRunId=None)
I862 = dict(identifier='HPP-862', status='blocked', title='M3b2 (track M)', executionRunId=None)
rc, o = qrun([I861, I862])
check('queue: M3a2 in_progress -> QUEUE BUSY (item 785 (v)(5))', rc == 1 and 'QUEUE BUSY: HPP-861' in o)
rc, o = qrun([dict(I861, status='blocked'), I862])
check('queue: M3a2 blocked without a run -> QUEUE FREE', rc == 0 and 'QUEUE FREE' in o)
rc, o = qrun([dict(I861, status='blocked', executionRunId='r1'), I862])
check('queue: M3a2 blocked with a going run -> BUSY', rc == 1)
rc, o = qrun([], [dict(I861, status='done'), I862])
check('queue: M3a2 done (fetched by id) -> FREE', rc == 0)
rc, o = qrun([dict(identifier='HPP-900', status='todo', title='x (track P)'), dict(I861, status='done')])
check('queue: a ready track P link -> BUSY', rc == 1 and 'HPP-900' in o)
rc, o = qrun([dict(identifier='HPP-871', status='in_progress', title='M9f (track M)'), dict(I861, status='done')])
check('queue: own issue does not hold the queue', rc == 0)
rc, o = qrun([I862])
check('queue: M3a2 not fetched -> BUSY by rule', rc == 1)
rc, o = qrun([dict(I861, status='done'), dict(I862, status='in_progress')])
check('queue: M3b2 in_progress (the lead, no lock) -> reference row, FREE', rc == 0 and 'reference row' in o)

# ---- plan / dry run ------------------------------------------------------------------------------------------------------------------
for tg, lv in (('t188_sg2', 'underwater_aerial_garden'), ('t188_hb2', 'hoover_beach'), ('t188_mg2', 'mini_giants_garden'),
               ('t188_mg2_r3', 'mini_giants_garden')):
    p = R.plan_of(tg)
    check('plan_of %s level %s hold 330 knobs M5W2=1 T188=2' % (tg, lv), p is not None and p['level'] == lv and p['hold'] == 330
          and p['knob'] == ('KYTY_DIAG_M5W2', '1') and p['knob2'] == ('KYTY_DIAG_T188', '2'))
for tg in ('t188_sg3', 't188_sg2_r4', 'm6_sg', 't188_sg2c_1', ''):
    check('plan_of %r unknown' % tg, R.plan_of(tg) is None)
check('expected env: KYTY_DIAG_T188=2 required, KYTY_DIAG_T188_CLS absent (extra -> admission NO)',
      R.expected_env(R.plan_of('t188_sg2'))['KYTY_DIAG_T188'] == '2' and 'KYTY_DIAG_T188_CLS' not in R.expected_env(R.plan_of('t188_sg2')))
GO = os.path.join(HERE, 'go_m9f.sh')
BASH = 'C:/Program Files/Git/bin/bash.exe'
if os.path.exists(GO):
    env = dict(os.environ, M9F_DRYRUN='1')
    for tg in ('t188_sg2', 't188_hb2', 't188_mg2', 't188_sg2_r1'):
        o = subprocess.run([BASH, GO, tg], capture_output=True, env=env).stdout.decode('ascii', 'replace')
        p = R.plan_of(tg)
        want = ('bin m9d3 level %s kind v sd 300 timeout 480 hold 330 rec --rec cache K0 save none knobs KYTY_GPU_CLOCK_PIN=1 '
                'KYTY_GPU_MARKERS=0 KYTY_DIAG_M5W2=1 KYTY_DIAG_T188=2' % p['level'])
        check('go_m9f.sh dry run of %s = the plan of the reader' % tg, [ln for ln in o.splitlines() if ln.startswith('dryrun %s ' % tg)
                                                                       and ln.endswith(want)] != [])
    for tg in ('t188_xx2', 't188_sg2_r4'):
        rc = subprocess.run([BASH, GO, tg], capture_output=True, env=env).returncode
        check('go_m9f.sh dry run of %s refused (rc 2)' % tg, rc == 2)
    src = open(GO, 'rb').read().decode('ascii')
    check('go_m9f.sh: binary feb55b54 full sha = reader TB, seal seal.md, no KYTY_DIAG_T188_CLS set',
          'TB=%s' % R.TB in src and 'SEAL=$G/seal.md' in src and 'KYTY_DIAG_T188_CLS=' not in src)
else:
    check('go_m9f.sh present next to the reader', False)

# ---- admission on a real M6c tag (binary 2179005b, no T188 knob) -------------------------------------------------------------------
M6 = 'C:/kyty/m657/m6c'
if os.path.exists(M6 + '/log_m6_hb.txt'):
    d = tempfile.mkdtemp()
    pth = R.paths('t188_hb2', d)
    src = dict(log=M6 + '/log_m6_hb.txt', stdout=M6 + '/stdout_m6_hb.txt', run=M6 + '/m6_hb.json', idx=M6 + '/rec_m6_hb.mp4.idx',
               seal=M6 + '/pred.md', installed_before=M6 + '/runs/m6_hb/installed_before.txt',
               installed_after=M6 + '/runs/m6_hb/installed_after.txt', manifest_cmp=M6 + '/runs/m6_hb/manifest_cmp.txt',
               installed_sha=M6 + '/runs/m6_hb/installed_sha.txt', level=M6 + '/runs/m6_hb/level.txt', plan=M6 + '/runs/m6_hb/plan.txt')
    for k, s in src.items():
        if os.path.exists(s):
            os.link(s, pth[k]) if k == 'log' else open(pth[k], 'wb').write(open(s, 'rb').read())
    res = R.read_tag('t188_hb2', pth)
    ad = res['admission']
    check('real M6c tag: NOT_ADMITTED', res['status'] == 'NOT_ADMITTED')
    check('real M6c tag: json binary member NO (2179005b is not feb55b54)', [b for a, b in ad if a.startswith('json binary_sha256')] == [False])
    check('real M6c tag: T188 knob witness NO, M5W2 witness ok', [b for a, b in ad if a.startswith('knob witness')] == [True, False])
    check('real M6c tag: env member NO (KYTY_DIAG_T188 missing)', [b for a, b in ad if a.startswith('env = ')] == [False])
    check('real M6c tag: entry, window and signature members ok', [b for a, b in ad if a.startswith(('entry line', 'window events',
                                                                                                       'translation signature'))] == [True] * 3)
    check('real M6c tag: no T188 lines -> E members violated, no Z violation, no T188 stop (not admitted)',
          res['t188'] is not None and mem_of(res['t188']['checks'], 'E: exactly') == [False] and mem_of(res['t188']['checks'], 'Z:') == [True]
          and res['t188_stop'] is False)
    for k in pth:
        if os.path.exists(pth[k]):
            os.remove(pth[k])
    os.rmdir(d)
else:
    check('M6c log for the admission fixture present', False)

# ---- output encoding --------------------------------------------------------------------------------------------------------------
fd, lp = tempfile.mkstemp(suffix='.txt')
with os.fdopen(fd, 'wb') as f:
    f.write(b'M5W2: mode=1\nT188: mode=2 cls=all k=4\n' + sl + il + ol + tl)
envc = dict(os.environ)
envc['PYTHONIOENCODING'] = 'cp1250:strict'
o = subprocess.run([sys.executable, os.path.join(HERE, 'm9f_read.py'), '--scan-t188', lp], capture_output=True, env=envc)
txt = o.stdout.decode('ascii', 'replace')
check('reader --scan-t188 output in strict cp1250 (rc 0, ascii, stop members printed)', o.returncode == 0 and 'T188 STOP MEMBERS' in txt
      and 'CLASS CHOICE' in txt)
o = subprocess.run([sys.executable, os.path.join(HERE, 'm9f_read.py'), '--plan', 't188_mg2'], capture_output=True, env=envc)
check('reader --plan in strict cp1250', o.returncode == 0 and o.stdout.decode('ascii').startswith('bin m9d3 level mini_giants_garden'))
os.remove(lp)
for f in ('m9f_read.py', 't188_rules.py', 'nmag_m9f.py', 'queue_m9f.py', 'test_m9f.py'):
    check('%s source is ASCII' % f, all(c < 128 for c in open(os.path.join(HERE, f), 'rb').read()))
print('checks %d, failed %d %s' % (n, len(bad), bad))
print('ALL OK' if not bad else 'FAILED')
sys.exit(0 if not bad else 1)

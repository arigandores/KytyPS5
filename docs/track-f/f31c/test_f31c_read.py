"""F31c (HPP-731): fixtures of f31c_read.py (port of F26c test_f26c_read.py) - every class member and every edge of item 667 (d)(3),
(d)(5), (e); the series line of the table with the lock budget (e)(4); the positive control of the detector on the three real B25 logs
(item 667 (d)(5): log_f30_s3_c5 and the two logs of item 630 (g)(5)); a regression of sum_dt against F26a sweep_f26a.walk on a course log
of mini_giants_garden; output in strict cp1250.  The first line names the suite and the target with sha256; the last line is ALL OK.
ASCII only."""
import hashlib, json, lzma, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
sys.path.insert(0, HERE)
import f31c_read as R  # noqa: E402
import sweep_f26a as S  # noqa: E402

NL = chr(10)
W = HERE + '/fxread'
shutil.rmtree(W, ignore_errors=True)
os.makedirs(W)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()  # noqa: E731
print('suite test_f31c_read.py sha256 %s target f31c_read.py sha256 %s' % (sha(HERE + '/test_f31c_read.py'), sha(HERE + '/f31c_read.py')))
bad = []
F300 = (16667,) * 18000   # 300.006 s


def check(name, cond):
    print('%s %s' % ('ok  ' if cond else 'FAIL', name))
    if not cond:
        bad.append(name)


def mklog(name, frames=F300, pre=(), post=(), entry=True, before_frames=(50000,), extra_after=(), xz=False):
    L = ['[1][00:00:01.000] libkernel::x()', 'LevelDocument Loaded: mini_giants_garden [x]']
    L += ['FrameTrace: n=%d dt_us=%d lat_us=0' % (i, d) for i, d in enumerate(before_frames)]
    L += list(pre)
    if entry:
        L.append('GuestOut: Level has started: mini_giants_garden')
    L += ['FrameTrace: n=%d dt_us=%d lat_us=0 draws=755' % (100 + i, d) for i, d in enumerate(frames)]
    L += list(extra_after)
    L += list(post)
    body = (NL.join(L) + NL).encode()
    p = '%s/log_%s.txt' % (W, name) + ('.xz' if xz else '')
    if xz:
        with lzma.open(p, 'wb') as f:
            f.write(body)
    else:
        open(p, 'wb').write(body)
    return p


def mkjson(name, started_s=12.3, binary=R.TB, env=None, cmd=None, drop=()):
    e = dict(R.FORM)
    e.update({'KYTY_GATE_FILE': 'x', 'KYTY_SAMPLE_GATE': 'y', 'KYTY_QUEUE_TRACE': '1'})
    for k in drop:
        e.pop(k, None)
    e.update(env or {})
    j = dict(binary_sha256=binary, env=e, cmdline=cmd or ['kyty_emulator.exe', '--vulkan-validation', 'false', '--game', 'g'],
             attempts=[dict(started_s=started_s, hold_s=300.2, hold_exit=None, outcome='ok')], launched='t0', finished='t1')
    p = '%s/%s.json' % (W, name)
    json.dump(j, open(p, 'w'))
    return p


def mkout(name, lines=()):
    p = '%s/stdout_%s.txt' % (W, name)
    open(p, 'wb').write((NL.join(['start'] + list(lines)) + NL).encode())
    return p


def cls(name, **kw):
    js = kw.pop('json_kw', {})
    so = kw.pop('stdout_lines', ())
    r = R.read(name, mklog(name, **kw), mkout(name, so), mkjson(name, **js))
    return r


ASSERT = ['ASSERT: D:\\asobi\\6.0\\source\\engine\\js\\src\\framework\\js\\gpu\\command\\_IMPL\\_PPR\\command_buffer_writer.ppr.cpp:31', '',
          'There are too many objects/batches in this scene.',
          'Unhandled host exception: type=1 code=3221225477 pc=0x00000009004a020e access=1 address=0xffffffffffffffff']

# constants of item 667
check('constants: FS11 ea51ae80, level mini_giants_garden, 290 s, entry 60 s, 5 interferences, 36 tags, 5 inventory, N 41, budget 14400 s',
      R.TB.startswith('ea51ae80') and R.E == b'Level has started: mini_giants_garden' and R.SUM_MIN_US == 290000000 and R.ENTRY_MAX_S == 60.0
      and R.INTERF_STOP == 5 and R.TAGS == 36 and R.INVENTORY == 5 and R.N_RULE == 41 and R.LOCK_BUDGET_S == 14400)
# class members
r = cls('counted'); check('counted: class COUNTED', r['cls'] == 'COUNTED')
check('counted: frames 18000 sum 300.0 s', r['frames'] == 18000 and r['sum_dt_s'] == 300.0)
check('counted: frames before the entry not summed', r['max_dt_us'] == 16667)
r = cls('det', post=ASSERT); check('detector in the log: DETECTOR, strings 1/1/1', r['cls'] == 'DETECTOR' and r['detector'] == [1, 1, 1])
for k, s in enumerate(ASSERT):
    if k == 1:
        continue
    r = cls('det1_%d' % k, post=[s]); check('detector single string %d: DETECTOR' % k, r['cls'] == 'DETECTOR')
r = cls('detso', stdout_lines=['There are too many objects/batches in this scene.']); check('detector in the stdout only: DETECTOR', r['cls'] == 'DETECTOR')
r = cls('detbefore', pre=['There are too many objects/batches in this scene.']); check('detector before the entry: DETECTOR', r['cls'] == 'DETECTOR')
r = cls('detnoentry', entry=False, post=ASSERT); check('detector without an entry: DETECTOR', r['cls'] == 'DETECTOR')
r = cls('detharness', post=ASSERT, json_kw=dict(binary='0' * 64)); check('detector beats a harness problem: DETECTOR', r['cls'] == 'DETECTOR')
r = cls('detshort', frames=(16667,) * 100, post=ASSERT); check('detector with a short hold: DETECTOR', r['cls'] == 'DETECTOR')
r = cls('err', post=['--- Error ---']); check('--- Error --- without the detector: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['error_lines'] == 1)
r = cls('hexc', post=['Unhandled host exception: type=1 code=1 pc=0x0000000900000000']); check('Unhandled host exception without the detector: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['host_exc'] == 1)
for m in ('Unhandled exception: x', '--- Fatal Error ---', 'GpuHangAbort: 8 s', 'ErrorDeviceLost'):
    r = cls('d_' + m[:5].strip('-: '), post=[m]); check('death %r in the log: INTERFERENCE' % m, r['cls'] == 'INTERFERENCE')
r = cls('dso', stdout_lines=['GpuHangAbort: 8 s']); check('death in the stdout: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('noentry', entry=False); check('no entry line: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['entry_line'] is None)
r = cls('otherlvl', entry=False, extra_after=['GuestOut: Level has started: intro_next']); check('entry of another level only: INTERFERENCE', r['cls'] == 'INTERFERENCE')
# edges
r = cls('f1s', frames=(16667,) * 17999 + (1000000,)); check('frame 1 000 000 us after the entry: COUNTED (item 667 (e)(3)), row long 1', r['cls'] == 'COUNTED' and r['long_frames'] == 1)
r = cls('f3s', frames=(16667,) * 17990 + (3700000,)); check('frame 3.7 s after the entry (as s18_c13): COUNTED, row long 1, max 3700000', r['cls'] == 'COUNTED' and r['long_frames'] == 1 and r['max_dt_us'] == 3700000)
r = cls('f1sm', frames=(16667,) * 17999 + (999999,)); check('frame 999 999 us: COUNTED, row long 0', r['cls'] == 'COUNTED' and r['long_frames'] == 0)
r = cls('f1sbefore', before_frames=(3000000,)); check('frame >= 1 s before the entry: COUNTED, row pre max 3000000 count 1', r['cls'] == 'COUNTED' and r['pre_entry_max_dt_us'] == 3000000 and r['pre_entry_long_frames'] == 1)
r = cls('s290', frames=(1000000,) * 290); check('sum exactly 290 000 000 us: COUNTED', r['cls'] == 'COUNTED' and r['sum_dt_us'] == 290000000)
r = cls('s290m', frames=(1000000,) * 289 + (999999,)); check('sum 289 999 999 us: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['sum_dt_us'] == 289999999)
r = cls('s120', frames=(16667,) * 7200); check('the F26c hold of 120 s: INTERFERENCE (sum < 290 s)', r['cls'] == 'INTERFERENCE')
r = cls('e60', json_kw=dict(started_s=60.0)); check('entry_s 60.0: COUNTED', r['cls'] == 'COUNTED')
r = cls('e601', json_kw=dict(started_s=60.1)); check('entry_s 60.1: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('enone', json_kw=dict(started_s=None)); check('entry_s None: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('nextlvl', extra_after=['GuestOut: Level has started: worldmap'] + ['FrameTrace: n=9 dt_us=5000000 lat_us=0'] * 3)
check('frames after the next level are not summed: COUNTED, max 16667', r['cls'] == 'COUNTED' and r['max_dt_us'] == 16667 and r['next_level_line'] is not None)
r = cls('twoentry', extra_after=['GuestOut: Level has started: mini_giants_garden', 'FrameTrace: n=9 dt_us=5000000 lat_us=0'])
check('a second mini_giants_garden entry closes the sum: entries 2, max 16667', r['entries'] == 2 and r['max_dt_us'] == 16667)
# harness form
for nm, kw in (('bin', dict(binary='1' * 64)), ('binfs10', dict(binary='abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe')),
               ('rec', dict(env={'KYTY_REC': 'x.mp4'})), ('patch', dict(env={'KYTY_GAME_PATCH': 'p'})),
               ('fix', dict(env={'KYTY_FIX_B12': '0'})), ('stand', dict(env={'KYTY_TEST_LOGSTALL': '60:3000:3'})),
               ('val', dict(cmd=['k', '--vulkan-validation', 'true'])), ('args', dict(env={'KYTY_GUEST_ARGS': '-lvl intro_next'})),
               ('lite', dict(drop=('KYTY_FRAME_TRACE',))), ('hang', dict(env={'KYTY_GPU_HANG_ABORT_S': '22'})),
               ('pin', dict(drop=('KYTY_GPU_CLOCK_PIN',))), ('mark', dict(env={'KYTY_GPU_MARKERS': '1'}))):
    r = cls('h_' + nm, json_kw=kw); check('form %s: HARNESS' % nm, r['cls'] == 'HARNESS')
r = R.read('nojson', mklog('nojson'), mkout('nojson'), W + '/absent.json'); check('no json: HARNESS', r['cls'] == 'HARNESS')
# members of item 620 (g)(1)-(2)
r = R.read('dispoff', mklog('dispoff'), mkout('dispoff'), mkjson('dispoff'), disp_after='dispstate OFF idle_s 3 utc x'); check('display OFF after a clean tag: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = R.read('dispon', mklog('dispon'), mkout('dispon'), mkjson('dispon'), disp_after='dispstate ON idle_s 3 utc x', tempo_rc=0); check('display ON, tempo 0: COUNTED', r['cls'] == 'COUNTED')
r = R.read('dispdet', mklog('dispdet', post=ASSERT), mkout('dispdet'), mkjson('dispdet'), disp_after='dispstate OFF'); check('display OFF with the detector: DETECTOR', r['cls'] == 'DETECTOR')
for rc in (1, 2, 3):
    r = R.read('tempo%d' % rc, mklog('tempo%d' % rc), mkout('t'), mkjson('tempo%d' % rc), disp_after='dispstate ON', tempo_rc=rc); check('tempo rc %d on a counted tag: TEMPO' % rc, r['cls'] == 'TEMPO')
r = R.read('tempoi', mklog('tempoi', post=['--- Error ---']), mkout('t'), mkjson('tempoi'), disp_after='dispstate ON', tempo_rc=2); check('tempo rc 2 on an interference tag: INTERFERENCE (a row)', r['cls'] == 'INTERFERENCE')
# host load layer (row)
LD = W + '/load'


def mkrun(name, files):
    d = '%s/%s' % (LD, name)
    os.makedirs(d, exist_ok=True)
    for k, v in files.items():
        open('%s/%s' % (d, k), 'w').write(v + NL)
    return d


H0 = 'hostload: over05 0 max 0.000 total 0.312 procs []'
H1 = "hostload: over05 1 max 0.744 total 1.020 procs [('<app>', 44272, 0.744)]"
check('layer: before 0, after 0 -> CLEAN', R.layer_of(mkrun('c', {'hostload_before.txt': H0, 'hostload_after.txt': H0}))[0] == 'CLEAN')
check('layer: before 1 -> HOST_LOAD', R.layer_of(mkrun('d', {'hostload_before.txt': H1, 'hostload_after.txt': H0}))[0] == 'HOST_LOAD')
check('layer: after 1 -> HOST_LOAD', R.layer_of(mkrun('e', {'hostload_before.txt': H0, 'hostload_after.txt': H1}))[0] == 'HOST_LOAD')
check('layer: only before 0 -> UNKNOWN', R.layer_of(mkrun('e2', {'hostload_before.txt': H0}))[0] == 'UNKNOWN')
check('layer: a broken line -> UNKNOWN', R.layer_of(mkrun('f', {'hostload_before.txt': 'Traceback', 'hostload_after.txt': H0}))[0] == 'UNKNOWN')
check('layer: no files -> UNKNOWN', R.layer_of(mkrun('g', {}))[0] == 'UNKNOWN')
jp = mkjson('setload')
R.set_load(jp, mkrun('h', {'hostload_before.txt': H1, 'hostload_after.txt': H0}))
jj = json.load(open(jp))
check('set-load writes host_load {layer HOST_LOAD, before, after} and keeps binary_sha256', jj['host_load']['layer'] == 'HOST_LOAD' and jj['host_load']['before'] == H1 and jj['binary_sha256'] == R.TB)
r = R.read('lay', mklog('lay'), mkout('lay'), mkjson('lay'), rundir=mkrun('i', {'hostload_before.txt': H1, 'hostload_after.txt': H0}))
check('a HOST_LOAD tag stays COUNTED (layer is a row)', r['cls'] == 'COUNTED' and r['layer'] == 'HOST_LOAD')
# xz log
p = mklog('xzc', xz=True); r = R.read('xzc', p, None, mkjson('xzc')); check('xz log: COUNTED, sum 300.0', r['cls'] == 'COUNTED' and r['sum_dt_s'] == 300.0)
p = mklog('xzd', xz=True, post=ASSERT); r = R.read('xzd', p, None, mkjson('xzd')); check('xz log with the assert: DETECTOR', r['cls'] == 'DETECTOR')

# lock budget (item 667 (e)(4))
def mklock(d, pairs):
    os.makedirs(d + '/runs', exist_ok=True)
    with open(d + '/runs/lock.log', 'w') as f:
        for tag, a, b in pairs:
            f.write('lock taken %s %s\n' % (tag, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(a))))
            if b is not None:
                f.write('lock released %s %s\n' % (tag, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(b))))


T0 = 1790000000
d = W + '/lk1'; mklock(d, [('base', T0, T0 + 60), ('b25m_01', T0 + 100, T0 + 470)])
check('lock seconds: base 60 + tag 370 = 430', R.lock_seconds(d + '/runs/lock.log') == 430)
d = W + '/lk2'; mklock(d, [('b25m_01', T0, T0 + 100), ('b25m_02', T0 + 200, None)])
check('lock seconds: an open taken counts to now (> 100)', R.lock_seconds(d + '/runs/lock.log') > 100 + 3600)
check('lock seconds: no file -> 0', R.lock_seconds(W + '/none/lock.log') == 0)

# the series line of the table
SER = [0]


def series(classes, lock=None):
    SER[0] += 1
    d = W + '/ser_%d' % SER[0]
    shutil.rmtree(d, ignore_errors=True)
    for i, c in enumerate(classes):
        os.makedirs('%s/runs/b25m_%02d' % (d, i + 1))
        json.dump(dict(tag='b25m_%02d' % (i + 1), cls=c, binary=R.TB, hold_s=300, frames=1, sum_dt_s=300.0, max_dt_us=1, long_frames=0,
                       detector=[0, 0, 0], reasons=[]), open('%s/runs/b25m_%02d/read.json' % (d, i + 1), 'w'))
    os.makedirs('%s/runs/b25m_99.user_1' % d)
    json.dump(dict(tag='x', cls='DETECTOR'), open('%s/runs/b25m_99.user_1/read.json' % d, 'w'))
    if lock is not None:
        mklock(d, [('b25m_01', T0, T0 + lock)])
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        st = R.table(d)
    return st, buf.getvalue()


st, out = series(['COUNTED'] * 35); check('35 counted: GOING (N 40 of 41)', st == 'GOING' and 'N = 5 inventory + 35 = 40 of 41' in out)
st, out = series(['COUNTED'] * 36); check('36 counted: COMPLETE (N 41)', st == 'COMPLETE' and '= 41 of 41' in out)
st, out = series(['COUNTED'] * 3 + ['INTERFERENCE'] * 4); check('4 interference: GOING', st == 'GOING')
st, out = series(['COUNTED'] * 3 + ['INTERFERENCE'] * 5); check('5 interference: INTERFERENCE_STOP', st == 'INTERFERENCE_STOP')
st, out = series(['COUNTED'] * 3 + ['DETECTOR']); check('a detector tag: DETECTOR_STOP', st == 'DETECTOR_STOP')
st, out = series(['COUNTED', 'HARNESS']); check('a harness tag: HARNESS_STOP', st == 'HARNESS_STOP')
st, out = series(['COUNTED', 'TEMPO']); check('a tempo tag: TEMPO_STOP', st == 'TEMPO_STOP')
check('moved run folders (b25m_NN.<suffix>) are not read', 'b25m_99' not in out)
st, out = series(['COUNTED'] * 30, lock=14399); check('lock 14 399 s, 30 counted: GOING', st == 'GOING' and 'lock 14399 s of 14400' in out)
st, out = series(['COUNTED'] * 30, lock=14400); check('lock 14 400 s, 30 counted: LOCK_BUDGET_STOP', st == 'LOCK_BUDGET_STOP')
st, out = series(['COUNTED'] * 36, lock=15000); check('lock 15 000 s, 36 counted: COMPLETE (budget not read)', st == 'COMPLETE')
st, out = series(['COUNTED'] * 3 + ['DETECTOR'], lock=15000); check('lock over budget with a detector: DETECTOR_STOP', st == 'DETECTOR_STOP')

# positive control of the detector on the three real logs (item 667 (d)(5))
for nm, p, ln in (('s59', 'C:/kyty/s59/log_sig1.txt.xz', 627192), ('s42', 'C:/kyty/log_s14_s42_merged_cold.txt.xz', 4407364),
                  ('f30_s3_c5', 'C:/kyty/f287/f30m/log_f30_s3_c5.txt', None)):
    r = R.read(nm, p, None, None, require_form=False)
    check('positive control %s: DETECTOR, strings %s, first line %s (F26a: %s)' % (nm, r['detector'], r['detector_first_line'], ln),
          r['cls'] == 'DETECTOR' and r['detector'][0] >= 1 and r['detector'][2] >= 1 and (ln is None or abs((r['detector_first_line'] or 0) - ln) <= 3))
# regression: a course log of mini_giants_garden (no assert), the reader = F31a ft31.py (docs/track-f/f31a/ft_mgg.out.txt: 'log_s18_e2.txt
# frames 19929 hold 332.6 s'); sweep_f26a.walk sums only intro_next, so it is not the reference here
p = 'C:/kyty/s288/s18c/log_s18_e2.txt'
r = R.read('s18_e2', p, None, None, require_form=False)
check('regression s18_e2: class COUNTED, frames %d = F31a 19929, sum %.1f s = F31a 332.6 s' % (r['frames'], r['sum_dt_s']),
      r['cls'] == 'COUNTED' and r['frames'] == 19929 and abs(r['sum_dt_s'] - 332.6) < 0.05)
check('sweep_f26a.walk still imports and SIGS = the reader strings', tuple(S.SIGS) == tuple(R.SIGS) if hasattr(S, 'SIGS') else False)
r2 = R.read('s18_e2j', p, None, 'C:/kyty/s288/s18c/s18_e2.json')
check('s18_e2 with its json is not the form of 667 (d): HARNESS (%s)' % r2['form'][:2], r2['cls'] == 'HARNESS')
# cp1250 strict output, usage
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
c = subprocess.run([sys.executable, HERE + '/f31c_read.py', '--log', mklog('cp'), '--name', 'cp'], capture_output=True, env=env)
check('cp1250 strict output: rc 0, CLASS line', c.returncode == 0 and b'CLASS COUNTED' in c.stdout)
c = subprocess.run([sys.executable, HERE + '/f31c_read.py'], capture_output=True, env=env)
check('no arguments: usage, rc 2', c.returncode == 2)
c = subprocess.run([sys.executable, HERE + '/f31c_read.py', '--table', '--dir', W + '/ser_1'], capture_output=True, env=env)
check('table rc 0 on GOING (ser_1: 35 counted)', c.returncode == 0 and b'state GOING' in c.stdout)
c = subprocess.run([sys.executable, HERE + '/f31c_read.py', '--table', '--dir', W + '/ser_5'], capture_output=True, env=env)
check('table rc 1 on DETECTOR_STOP (ser_5)', c.returncode == 1 and b'state DETECTOR_STOP' in c.stdout)
print('ALL OK' if not bad else 'FAILED %d: %s' % (len(bad), bad))
sys.exit(0 if not bad else 1)

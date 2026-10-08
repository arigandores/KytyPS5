"""F26c (HPP-692): fixtures of f26c_read.py - every class member and every edge of item 630 (g)(3), (g)(5), (d); the series line of the
table; the positive control of the detector on the two real B25 logs; a regression of sum_dt against F26a sweep_f26a.walk on the course
log s18_c02; output in strict cp1250.  The first line names the suite and the target with sha256; the last line is ALL OK.  ASCII only."""
import hashlib, json, lzma, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, '/')
sys.path.insert(0, HERE)
import f26c_read as R  # noqa: E402
import sweep_f26a as S  # noqa: E402

NL = chr(10)
W = HERE + '/fxread'
shutil.rmtree(W, ignore_errors=True)
os.makedirs(W)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()  # noqa: E731
print('suite test_f26c_read.py sha256 %s target f26c_read.py sha256 %s' % (sha(HERE + '/test_f26c_read.py'), sha(HERE + '/f26c_read.py')))
bad = []


def check(name, cond):
    print('%s %s' % ('ok  ' if cond else 'FAIL', name))
    if not cond:
        bad.append(name)


def mklog(name, frames=(16667,) * 7200, pre=(), post=(), entry=True, before_frames=(50000,), extra_after=(), xz=False):
    L = ['[1][00:00:01.000] libkernel::x()', 'LevelDocument Loaded: intro_next [intro]']
    L += ['FrameTrace: n=%d dt_us=%d lat_us=0' % (i, d) for i, d in enumerate(before_frames)]
    L += list(pre)
    if entry:
        L.append('GuestOut: Level has started: intro_next')
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
             attempts=[dict(started_s=started_s, hold_s=120.2, hold_exit=None, outcome='ok')], launched='t0', finished='t1')
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

# class members
r = cls('counted'); check('counted: class COUNTED', r['cls'] == 'COUNTED')
check('counted: frames 7200 sum 120.0 s', r['frames'] == 7200 and r['sum_dt_s'] == 120.0)
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
r = cls('err', post=['--- Error ---']); check('--- Error --- without the detector: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['error_lines'] == 1)
r = cls('hexc', post=['Unhandled host exception: type=1 code=1 pc=0x0000000900000000']); check('Unhandled host exception without the detector: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['host_exc'] == 1)
for m in ('Unhandled exception: x', '--- Fatal Error ---', 'GpuHangAbort: 8 s', 'ErrorDeviceLost'):
    r = cls('d_' + m[:5].strip('-: '), post=[m]); check('death %r in the log: INTERFERENCE' % m, r['cls'] == 'INTERFERENCE')
r = cls('dso', stdout_lines=['GpuHangAbort: 8 s']); check('death in the stdout: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('noentry', entry=False); check('no entry line: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['entry_line'] is None)
# edges
r = cls('f1s', frames=(16667,) * 7199 + (1000000,)); check('frame 1 000 000 us after the entry: INTERFERENCE', r['cls'] == 'INTERFERENCE' and r['long_frames'] == 1)
r = cls('f1sm', frames=(16667,) * 7199 + (999999,)); check('frame 999 999 us: COUNTED', r['cls'] == 'COUNTED')
r = cls('f1sbefore', before_frames=(3000000,)); check('frame >= 1 s before the entry: COUNTED (not after the entry), row pre max 3000000 count 1', r['cls'] == 'COUNTED' and r['pre_entry_max_dt_us'] == 3000000 and r['pre_entry_long_frames'] == 1)
r = cls('s90', frames=(15000000,) * 0 + (900000,) * 100); check('sum exactly 90 000 000 us: COUNTED', r['cls'] == 'COUNTED' and r['sum_dt_s'] == 90.0)
r = cls('s90m', frames=(900000,) * 99 + (899999,)); check('sum 89 999 999 us: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('e60', json_kw=dict(started_s=60.0)); check('entry_s 60.0: COUNTED', r['cls'] == 'COUNTED')
r = cls('e601', json_kw=dict(started_s=60.1)); check('entry_s 60.1: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('enone', json_kw=dict(started_s=None)); check('entry_s None: INTERFERENCE', r['cls'] == 'INTERFERENCE')
r = cls('nextlvl', extra_after=['GuestOut: Level has started: worldmap'] + ['FrameTrace: n=9 dt_us=5000000 lat_us=0'] * 3)
check('frames after the next level are not summed: COUNTED, max 16667', r['cls'] == 'COUNTED' and r['max_dt_us'] == 16667 and r['next_level_line'] is not None)
r = cls('twoentry', extra_after=['GuestOut: Level has started: intro_next', 'FrameTrace: n=9 dt_us=5000000 lat_us=0'])
check('a second intro_next entry closes the sum: entries 2, max 16667', r['entries'] == 2 and r['max_dt_us'] == 16667)
# harness form
for nm, kw in (('bin', dict(binary='1' * 64)), ('rec', dict(env={'KYTY_REC': 'x.mp4'})), ('patch', dict(env={'KYTY_GAME_PATCH': 'p'})),
               ('fix', dict(env={'KYTY_FIX_B36': '0'})), ('stand', dict(env={'KYTY_TEST_LOGSTALL': '60:3000:3'})),
               ('val', dict(cmd=['k', '--vulkan-validation', 'true'])), ('args', dict(env={'KYTY_GUEST_ARGS': '-lvl worldmap'})),
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
# xz log
p = mklog('xzc', xz=True); r = R.read('xzc', p, None, mkjson('xzc')); check('xz log: COUNTED, sum 120.0', r['cls'] == 'COUNTED' and r['sum_dt_s'] == 120.0)
p = mklog('xzd', xz=True, post=ASSERT); r = R.read('xzd', p, None, mkjson('xzd')); check('xz log with the assert: DETECTOR', r['cls'] == 'DETECTOR')


# the series line of the table
SER = [0]


def series(classes):
    SER[0] += 1
    d = W + '/ser_%d' % SER[0]
    shutil.rmtree(d, ignore_errors=True)
    for i, c in enumerate(classes):
        os.makedirs('%s/runs/b25_%02d' % (d, i + 1))
        json.dump(dict(tag='b25_%02d' % (i + 1), cls=c, binary=R.TB, hold_s=120, frames=1, sum_dt_s=120.0, max_dt_us=1, detector=[0, 0, 0],
                       reasons=[]), open('%s/runs/b25_%02d/read.json' % (d, i + 1), 'w'))
    os.makedirs('%s/runs/b25_99.user_1' % d)
    json.dump(dict(tag='x', cls='DETECTOR'), open('%s/runs/b25_99.user_1/read.json' % d, 'w'))
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        st = R.table(d)
    return st, buf.getvalue()


st, out = series(['COUNTED'] * 54); check('54 counted: GOING (N 59 of 60)', st == 'GOING' and 'N = 5 inventory + 54 = 59 of 60' in out)
st, out = series(['COUNTED'] * 55); check('55 counted: COMPLETE (N 60)', st == 'COMPLETE')
st, out = series(['COUNTED'] * 3 + ['INTERFERENCE'] * 4); check('4 interference: GOING', st == 'GOING')
st, out = series(['COUNTED'] * 3 + ['INTERFERENCE'] * 5); check('5 interference: INTERFERENCE_STOP', st == 'INTERFERENCE_STOP')
st, out = series(['COUNTED'] * 3 + ['DETECTOR']); check('a detector tag: DETECTOR_STOP', st == 'DETECTOR_STOP')
st, out = series(['COUNTED', 'HARNESS']); check('a harness tag: HARNESS_STOP', st == 'HARNESS_STOP')
st, out = series(['COUNTED', 'TEMPO']); check('a tempo tag: TEMPO_STOP', st == 'TEMPO_STOP')
check('moved run folders (b25_NN.<suffix>) are not read', 'b25_99' not in out)

# positive control of the detector on the two real logs (item 630 (g)(5))
for nm, p, ln in (('s59', 'C:/kyty/s59/log_sig1.txt.xz', 627192), ('s42', 'C:/kyty/log_s14_s42_merged_cold.txt.xz', 4407364)):
    r = R.read(nm, p, None, None, require_form=False)
    check('positive control %s: DETECTOR, strings %s, first line %s (F26a: %d)' % (nm, r['detector'], r['detector_first_line'], ln),
          r['cls'] == 'DETECTOR' and r['detector'][0] >= 1 and r['detector'][2] == 1 and abs((r['detector_first_line'] or 0) - ln) <= 3)
# regression: the course log s18_c02 (no assert, F26a section 3: 333.7 s)
p = 'C:/kyty/s288/s18c/log_s18_c02.txt'
r = R.read('s18_c02', p, 'C:/kyty/s288/s18c/stdout_s18_c02.txt', None, require_form=False)
w = S.walk(p)
ws = [L for L in w['levels'] if L['name'] == 'intro_next'][0]
check('regression s18_c02: class COUNTED, frames %d = sweep %d, sum %.1f s = sweep %.1f s' % (r['frames'], ws['frames'], r['sum_dt_s'], ws['sum_us'] / 1e6),
      r['cls'] == 'COUNTED' and r['frames'] == ws['frames'] and abs(r['sum_dt_s'] - ws['sum_us'] / 1e6) < 0.05 and abs(r['sum_dt_s'] - 333.7) < 0.15)
r2 = R.read('s18_c02j', p, None, 'C:/kyty/s288/s18c/s18_c02.json')
check('s18_c02 with its json is not the form of 630 (g): HARNESS (%s)' % r2['form'][:2], r2['cls'] == 'HARNESS')
# cp1250 strict output, usage
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
c = subprocess.run([sys.executable, HERE + '/f26c_read.py', '--log', mklog('cp'), '--name', 'cp'], capture_output=True, env=env)
check('cp1250 strict output: rc 0, CLASS line', c.returncode == 0 and b'CLASS COUNTED' in c.stdout)
c = subprocess.run([sys.executable, HERE + '/f26c_read.py'], capture_output=True, env=env)
check('no arguments: usage, rc 2', c.returncode == 2)
c = subprocess.run([sys.executable, HERE + '/f26c_read.py', '--table', '--dir', W + '/ser_1'], capture_output=True, env=env)
check('table rc 0 on GOING (ser_1: 54 counted)', c.returncode == 0 and b'state GOING' in c.stdout)
c = subprocess.run([sys.executable, HERE + '/f26c_read.py', '--table', '--dir', W + '/ser_5'], capture_output=True, env=env)
check('table rc 1 on DETECTOR_STOP (ser_5)', c.returncode == 1 and b'state DETECTOR_STOP' in c.stdout)
print('ALL OK' if not bad else 'FAILED %d: %s' % (len(bad), bad))
sys.exit(0 if not bad else 1)

"""test_f6e_read.py - fixtures of f6e_read.py (F6e, HPP-377): every member of p.287(v)(3), (5)-(7), p.290(b)(2), p.294(b)-(g)
and every edge - the counter line by exact key=value tokens (RC2 (a): SystemSetAttributes is not SourceSetAttributes), no
monotonicity of total and no sum rule (RC2 (b)), stubs from the log only (RC2 (c): the stdout printf lines are not added), the
stub count by symbol and library (F13), the frequency and its open edges, the wake control, the ASSERT member in the log and in
the stdout and the user_msg_param member against the control (294 (b)), the rip print, K2, the hold at the 120 s edge, K3 against
max(base, control) and the one repeat that decides (and does not lift the ASSERT member), the video and the sheet, the
admission (KYTY_PRINT_NAMES N4, precache by default), the form line FixB9a and its one repeat, the window events, the controls of
p.287(v)(6) with their profiles, the stop check, the summary, --repeats, the seal check, win_f6e.decide, the cache signature
manifest, real witness logs (c142_03, v143_03, v144_13 - hard links; the lead's base numbers), and the ASCII output under a
strict cp1250 console.  Last line: ALL OK."""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f6e_read as R  # noqa: E402
import win_f6e as W  # noqa: E402
import cachesig_f6e as CS  # noqa: E402

FX = os.path.join(HERE, 'fx', 'read')
REAL = os.path.join(HERE, 'fx', 'real')
N = [0]
FAIL = []
AP = 'AudioPropagation_v1'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    N[0] += 1
    if not cond:
        FAIL.append(name)
        print('FAIL %s %s' % (name, detail))


def stubline(i, sym, lib=AP):
    if sym == '<bad-record>':
        return 'Unresolved import stub called [%d]: record_id=7 symbol=<bad-record>' % i
    return ('Unresolved import stub called [%d]: patch_vaddr=0x0000000908e36f50 jmprela_index=1241 symbol=%s[%s][%s.0][Func] '
            'type=Func bind=Global program=C:/x/eboot.bin' % (i, sym, lib, lib))


def calls(fields):
    d = dict(fields)
    tot = d.pop('total', 256)
    hnd = d.pop('handles', 5)
    s = 'AudioPropagation: calls total=%d handles=%d' % (tot, hnd)
    names = ('SystemUnregisterMaterial', 'SystemSetRays', 'PortalDestroy', 'SystemSetAttributes', 'SourceSetAudioPaths',
             'SystemCreate', 'SystemRegisterMaterial', 'PortalSetAttributes', 'PortalCreate', 'RoomDestroy', 'SystemDestroy',
             'SourceCreate', 'SourceSetAttributes', 'SourceGetRays', 'SystemQueryMemory', 'SourceGetAudioPathCount',
             'SystemGetRays', 'SourceDestroy', 'SourceRender', 'SourceGetAudioPath', 'RoomCreate', 'SourceCalculateAudioPaths')
    for n in names:
        s += ' %s=%d' % (n, d.get(n, 0))
    return s


PRE = dict(total=40, SourceCreate=10, SourceSetAttributes=3, SystemSetAttributes=1, SourceRender=0)
HOLD = dict(total=512, SourceCreate=20, SourceSetAttributes=50, SystemSetAttributes=1, SourceRender=7, SourceDestroy=9)


def ctl_profile(level):
    return dict(R.PROFILE[level])


def write_run(root, tag, rows=7300, dt=16667, k3=(), k2=(), death=False, death_std=False, rip=0x900f52600, hang=False,
              glitches=0, vframes=8000, sheet=True, env_over=None, env_drop=(), entered=True, scene_change=False,
              binary=None, cmd_val=None, attempts=1, guest=None, fixon='auto', pre_line=True, stubs=None, std_stubs=0,
              pre_calls='auto', hold_calls='auto', hold_at=None, asserts_log=0, asserts_std=0, umsg=0, win=(),
              extra_calls=()):
    cfg = R.cfg_of(tag)
    os.makedirs(root, exist_ok=True)
    one = cfg['fix'] == '1'
    L = ['Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b']
    if isinstance(pre_line, (list, tuple)):
        L.extend(pre_line)
    elif pre_line:
        L.append('PipelinePrecache: 310 recipes -> 310 pipelines in 12.0 s')
    nfix = (1 if one else 0) if fixon == 'auto' else fixon
    for _ in range(nfix):
        L.append('FixB9a: on')
    if pre_calls == 'auto':
        pre_calls = [PRE] if one else []
    if hold_calls == 'auto':
        hold_calls = [HOLD] if one else []
    for c in pre_calls:
        L.append(calls(c))
    for w in win:
        L.append(w)
    if entered:
        L.append('GuestOut: Level has started: %s' % cfg['level'])
    L.append('FrameTrace: n=0 dt_us=500000 draws=10')
    L.append('FrameTrace: n=1 dt_us=900000 draws=500')
    if stubs is None:
        stubs = [] if one else [s for s, n in ctl_profile(cfg['level']).items() for _ in range(n)]
    hat = rows - 50 if hold_at is None else hold_at
    for i in range(rows):
        n = i + 2
        if i == 100:
            for j, s in enumerate(stubs):
                if isinstance(s, tuple):
                    L.append(stubline(j, s[0], s[1]))
                else:
                    L.append(stubline(j, s))
        if i == 200:
            for _ in range(asserts_log):
                L.append('ASSERT: numSamples == m_numOfGrains (file x.cpp line 12)')
            for _ in range(umsg):
                L.append('\t user_msg_param = 0x0000000000000000')
        if i == hat:
            for c in hold_calls:
                L.append(calls(c))
        if scene_change and i == rows - 10:
            L.append('GuestOut: Level has started: other_level')
        d = 1500000 if n in k2 else (150000 if n in k3 else dt)
        L.append('FrameTrace: n=%d dt_us=%d draws=500' % (n, d))
    for c in extra_calls:
        L.append(calls(c))
    if death:
        L.append('Unhandled exception: code=0xc0000005 rip=0x%016x (+0x0) addr=0x0000000000000010 access=0 tid=7 rsp=0x1' % rip)
    if hang:
        L.append('GpuHangAbort: queue stuck')
    L.append('Event: quit')
    with open(os.path.join(root, 'log_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(L) + '\n')
    S = ['stdout']
    for _ in range(std_stubs):
        S.append('Unresolved import stub called: sceAudioPropagationSourceCreate')
    for _ in range(asserts_std):
        S.append('ASSERT: numSamples == m_numOfGrains')
    if death_std:
        S.append('Unhandled exception: code=0xc0000005 rip=0x%016x (+0x0) addr=0x0000000000000010 access=0 tid=7 rsp=0x1' % rip)
    with open(os.path.join(root, 'stdout_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(S) + '\n')
    env = dict(KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_FIX_B9A=cfg['fix'], KYTY_REC='C:\\kyty\\f287\\f6e\\rec_%s.mp4' % tag)
    env.update(env_over or {})
    for k in env_drop:
        env.pop(k, None)
    js = dict(attempts=[dict(label='attempt %d' % (i + 1), hold_s=125, outcome='ok', hold_exit=None) for i in range(attempts)],
              env=env, guest_args=guest or '-lvl %s' % cfg['level'],
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if cmd_val else 'false'],
              binary_sha256=binary or R.BIN_SHA)
    with open(os.path.join(root, '%s.json' % tag), 'w', encoding='ascii') as f:
        json.dump(js, f)
    if vframes is not None:
        with open(os.path.join(root, 'glitch_%s.txt' % tag), 'w', encoding='ascii') as f:
            f.write('rec_%s.mp4: %d frames 960x540\none-frame glitches: %d\n' % (tag, vframes, glitches))
    if sheet:
        open(os.path.join(root, 'sheet_%s.png' % tag), 'wb').write(b'PNG')


def rd(name, tag, **kw):
    root = os.path.join(FX, name)
    shutil.rmtree(root, ignore_errors=True)
    write_run(root, tag, **kw)
    return R.read_tag(tag, root, SC)


SC = R.load()
print('suite test_f6e_read.py sha256 %s target f6e_read.py sha256 %s' % (sha(os.path.abspath(__file__)),
                                                                      sha(os.path.join(HERE, 'f6e_read.py'))))
# --- tag names ---
check('tag names: base, form repeat of any, K3 repeat of =1 only', R.cfg_of('f6e_a1') and R.cfg_of('f6e_c2f') and
      R.cfg_of('f6e_b1r') and R.cfg_of('f6e_c1r') is None and R.cfg_of('f6e_a1rf') is None and R.cfg_of('f3d_a1') is None)
check('a1f is timestop_casino =1, suffix f', R.cfg_of('f6e_a1f')['level'] == R.TC and R.cfg_of('f6e_a1f')['fix'] == '1'
      and R.cfg_of('f6e_a1f')['suffix'] == 'f')
check('constants of p.287(v)(5)-(6)', R.K3_BASE == {R.TC: 1, R.MA: 0} and R.FREQ_MAX == 0.1 and R.HOLD_S == 120 and
      R.FRAMES_V == 3000 and R.CTL_MIN == 1000 and R.BIN_SHA.startswith('d8756dce'))
# --- RC2 (a): exact key=value tokens ---
d = R.parse_calls(b' total=5 handles=2 SystemSetAttributes=9 SourceSetAttributes=0 SystemGetRays=4 SourceGetRays=1')
check('RC2(a) exact key: SourceSetAttributes 0 beside SystemSetAttributes 9', d['SourceSetAttributes'] == 0 and
      d['SystemSetAttributes'] == 9 and d['SourceGetRays'] == 1 and d['SystemGetRays'] == 4, d)
d = R.parse_calls(b' a=b=c SourceCreate=abc SourceRender=3 junk =4 x=')
check('RC2(a) malformed tokens ignored', d == {'SourceRender': 3}, d)
ok, last = R.wake([(10, R.parse_calls(b' SystemSetAttributes=9 SourceSetAttributes=0 SourceRender=0'))])
check('RC2(a) wake: SystemSetAttributes only -> no wake (V1-min caught)', ok is False, last)
check('wake: SourceRender 1 -> yes', R.wake([(1, {'SourceRender': 1, 'SourceSetAttributes': 0})])[0] is True)
check('wake: SourceSetAttributes 1 -> yes', R.wake([(1, {'SourceRender': 0, 'SourceSetAttributes': 1})])[0] is True)
check('wake: no counter line -> no', R.wake([])[0] is False)
check('RC2(b) wake: the last line by position, not the largest total', R.wake(
    [(10, {'total': 768, 'SourceSetAttributes': 4}), (20, {'total': 512, 'SourceSetAttributes': 0, 'SourceRender': 0})])[0] is False)
# --- RC2 (b): frequency by two lines, no monotonicity, no sum rule ---
rows = [(i, 16667, 500, 100 + 10 * i) for i in range(100)]
fr = R.frequency(rows, [(50, {'total': 768, 'SourceCreate': 10}), (600, {'total': 512, 'SourceCreate': 13})], 105, None)
check('RC2(b) total going down by position: read, no error', fr['d_create'] == 3 and fr['rows'] == 50 and abs(fr['freq'] - 0.06) < 1e-9, fr)
fr = R.frequency(rows, [(50, {'total': 1, 'SourceCreate': 10, 'SourceRender': 99}), (600, {'total': 2, 'SourceCreate': 20})], 105, None)
check('RC2(b) sum of fields != total: read, no error', abs(fr['freq'] - 0.2) < 1e-9, fr)
fr = R.frequency(rows, [(50, {'SourceCreate': 1}), (60, {'SourceCreate': 2}), (600, {'SourceCreate': 3}), (900, {'SourceCreate': 8})], 105, None)
check('L0 = last line before the first scene frame, L1 = last line of the hold', fr['l0'][0] == 60 and fr['l1'][0] == 900 and
      fr['d_create'] == 6 and fr['rows'] == 80, fr)
fr = R.frequency(rows, [(50, {'SourceCreate': 1}), (600, {'SourceCreate': 3}), (900, {'SourceCreate': 8})], 105, 700)
check('L1 stops at a scene change', fr['l1'][0] == 600, fr)
fr = R.frequency(rows, [(600, {'SourceCreate': 3})], 105, None)
check('no L0 -> freq None (letter), variant base 0 printed', fr['freq'] is None and fr['var'] and 'base 0' in fr['var'], fr)
fr = R.frequency(rows, [(50, {'SourceCreate': 3})], 105, None)
check('no L1 -> freq None (letter), variant bound printed', fr['freq'] is None and fr['var'] and '< 256' in fr['var'], fr)
fr = R.frequency(rows, [(50, {'SourceCreate': 3}), (101, {'SourceCreate': 4})], 100, None)
check('the first scene frame row lies between L0 and L1: 1 row', fr['rows'] == 1 and fr['freq'] == 1.0, fr)
fr = R.frequency(rows, [(50, {'SourceCreate': 3})], None, None)
check('no first scene frame -> nothing', fr['freq'] is None and fr['l0'] is None, fr)
# --- RC2 (c) and F13: stubs from the log only, by symbol and library ---
r = rd('std_only', 'f6e_a1', std_stubs=5)
check('RC2(c) stdout printf stubs not added: 0 log stubs -> PASS', r['verdict'] == 'PASS' and r['stub_lines'] == 0 and r['stub_std'] == 5,
      (r['verdict'], r['why'], r['stub_lines'], r['stub_std']))
r = rd('stub_other', 'f6e_a1', stubs=[('XyZ123', 'libSceFoo_v1')])
check('=1 stub of another library -> FAIL (any library)', r['verdict'] == 'FAIL' and r['stub_lines'] == 1 and
      r['stub_by_lib'] == {'libSceFoo_v1': 1} and r['stub_ap_lines'] == 0, (r['verdict'], r['stub_by_lib']))
r = rd('stub_ap', 'f6e_a1', stubs=['d84otraxt2s'])
check('=1 one AudioPropagation stub -> FAIL, by symbol', r['verdict'] == 'FAIL' and r['stub_ap'] == {'d84otraxt2s': 1}, (r['verdict'], r['stub_ap']))
r = rd('stub_bad', 'f6e_a1', stubs=['<bad-record>'])
check('bad-record stub line counted in the letter', r['verdict'] == 'FAIL' and r['stub_lines'] == 1, (r['verdict'], r['stub_lines']))
pr = R.stub_profile([(0, 'a', AP, 1), (1, 'a', AP, 2), (2, 'b', 'L2', 3)])
check('F13 profile by symbol / library / AudioPropagation', pr == ({'a': 2, 'b': 1}, {AP: 2, 'L2': 1}, {'a': 2}), pr)
# --- =1 timestop_casino ---
r = rd('a1_ok', 'f6e_a1')
check('a1 ideal PASS', r['verdict'] == 'PASS' and r['admitted'] and r['form_ok'], (r['verdict'], r['why']))
check('a1 frequency from the fixture lines: (20-10)/rows', r['freq']['d_create'] == 10 and r['freq']['rows'] == 7252 and
      r['freq']['freq'] < 0.1, r['freq'])
check('a1 wake yes, last line fields', r['wake'] and r['last_calls']['SourceRender'] == 7 and r['last_calls']['SourceDestroy'] == 9, r['last_calls'])
r = rd('a1_freq_hi', 'f6e_a1', rows=300, hold_at=250, hold_calls=[dict(HOLD, SourceCreate=10 + 26)])
check('a1 SourceCreate per frame 26/251 = 0.1036 -> FAIL', r['verdict'] == 'FAIL' and any('SourceCreate per frame' in w for w in r['why']),
      (r['verdict'], r['why'], r['freq']))
r = rd('a1_freq_edge', 'f6e_a1', rows=7300, hold_at=998, hold_calls=[dict(HOLD, SourceCreate=10 + 100)])
check('a1 frequency exactly 0.1 (100 / 1000 rows) -> FAIL (< 0.1 is the letter)', r['freq']['rows'] == 1000 and
      r['verdict'] == 'FAIL', (r['freq'], r['verdict']))
r = rd('a1_freq_below', 'f6e_a1', rows=7300, hold_at=998, hold_calls=[dict(HOLD, SourceCreate=10 + 99)])
check('a1 frequency 0.099 -> PASS', r['verdict'] == 'PASS', (r['freq'], r['verdict']))
r = rd('a1_nowake', 'f6e_a1', hold_calls=[dict(HOLD, SourceSetAttributes=0, SourceRender=0, SystemSetAttributes=40)])
check('a1 wake 0 (SystemSetAttributes 40) -> FAIL', r['verdict'] == 'FAIL' and any('wake' in w for w in r['why']), (r['verdict'], r['why']))
r = rd('a1_nohold', 'f6e_a1', hold_calls=[])
check('a1 no counter line on the hold -> NOT EVALUABLE (letter), variant printed', r['verdict'] == 'NOT EVALUABLE' and
      r['freq']['var'], (r['verdict'], r['freq']))
r = rd('a1_nopre', 'f6e_a1', pre_calls=[])
check('a1 no counter line before the first scene frame -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['freq']))
r = rd('a1_death', 'f6e_a1', death_std=True, rip=0x900f52600)
check('a1 death -> FAIL, rip offset +0xf52600 printed', r['verdict'] == 'FAIL' and r['deaths'] == 1 and
      r['rips'] == ['rip 0x900f52600 offset +0xf52600 (stdout)'], (r['verdict'], r['rips']))
check('a1 death -> stop with the rip', R.stop_check(json.loads(json.dumps(r, default=str))).startswith('stop: death') and
      '0xf52600' in R.stop_check(r), R.stop_check(r))
r = rd('a1_death_low', 'f6e_a1', death=True, rip=0x7ff612340000)
check('rip outside the guest base prints its offset sign', r['rips'][0].startswith('rip 0x7ff612340000 offset +'), r['rips'])
r = rd('a1_death_neg', 'f6e_a1', death=True, rip=0x800000000)
check('rip below 0x900000000 -> negative offset', r['rips'] == ['rip 0x800000000 offset -0x100000000 (log)'], r['rips'])
r = rd('a1_hang', 'f6e_a1', hang=True)
check('a1 GpuHangAbort -> FAIL (death marker, K2 class)', r['verdict'] == 'FAIL' and r['marks'][0][1] == 'K2', (r['verdict'], r['marks']))
r = rd('a1_k2', 'f6e_a1', k2=(50,))
check('a1 frame >= 1 s in the entry window -> FAIL', r['verdict'] == 'FAIL' and r['k2'] == 1, (r['verdict'], r['why']))
r = rd('a1_k2h', 'f6e_a1', k2=(5000,))
check('a1 frame >= 1 s on the hold -> FAIL', r['verdict'] == 'FAIL' and r['k2'] == 1, (r['verdict'], r['why']))
r = rd('a1_k2edge', 'f6e_a1', dt=999999, rows=200, hold_at=150)
check('dt 999 999 is not K2', r['k2'] == 0, r['k2'])
r = rd('a1_v2999', 'f6e_a1', vframes=2999)
check('a1 video 2999 frames -> FAIL', r['verdict'] == 'FAIL' and any('video frames' in w for w in r['why']), (r['verdict'], r['why']))
r = rd('a1_v3000', 'f6e_a1', vframes=3000)
check('a1 video 3000 frames -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
r = rd('a1_gl', 'f6e_a1', glitches=1)
check('a1 one glitch -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a1_nogl', 'f6e_a1', vframes=None)
check('a1 no glitch file -> FAIL', r['verdict'] == 'FAIL' and 'no glitch reading' in r['why'], (r['verdict'], r['why']))
r = rd('a1_nosheet', 'f6e_a1', sheet=False)
check('a1 no sheet -> FAIL', r['verdict'] == 'FAIL', (r['verdict'], r['why']))
r = rd('a1_h120', 'f6e_a1', rows=7200, hold_at=7000)
check('a1 hold 120.0024 s -> PASS', r['verdict'] == 'PASS' and r['hold_s'] >= 120, (r['verdict'], r['hold_s']))
r = rd('a1_h119', 'f6e_a1', rows=7199, hold_at=7000)
check('a1 hold 119.985 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['hold_s']))
r = rd('a1_noentry', 'f6e_a1', entered=False)
check('a1 not entered -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', (r['verdict'], r['why']))
r = rd('a1_change', 'f6e_a1', scene_change=True)
check('a1 scene change -> FAIL', r['verdict'] == 'FAIL' and r['scene_change'], (r['verdict'], r['why']))
# --- p.294(b): ASSERT and user_msg_param ---
r = rd('a1_as_log', 'f6e_a1', asserts_log=1)
check('294(b) ASSERT: in the log -> FAIL', r['verdict'] == 'FAIL' and r['asserts_log'] == 1 and any('ASSERT' in w for w in r['why']),
      (r['verdict'], r['why']))
r = rd('a1_as_std', 'f6e_a1', asserts_std=1)
check('294(b) ASSERT: in the stdout -> FAIL', r['verdict'] == 'FAIL' and r['asserts_std'] == 1, (r['verdict'], r['why']))
check('294(b) ASSERT first line printed', 'ASSERT: numSamples' in R.text(r), R.text(r)[-400:])
r = rd('c1_as', 'f6e_c1', asserts_log=2, umsg=2)
check('294(b) at =0 the ASSERT count is information (control verdict unchanged)', r['verdict'] == 'CONTROL OK' and
      r['asserts_log'] == 2 and r['umsg_log'] == 2, (r['verdict'], r['why']))
r = rd('b1_umsg', 'f6e_b1', umsg=1)
check('294(b) user_msg_param counted at the tag (decided in the summary)', r['verdict'] == 'PASS' and r['umsg_log'] == 1, r['umsg_log'])
# --- b1 (mini_astro_clock_tower): the mechanism member is not named ---
r = rd('b1_ok', 'f6e_b1', hold_calls=[dict(HOLD, SourceCreate=10000, SourceSetAttributes=0, SourceRender=0)])
check('b1 frequency and wake not members (PASS with a high rate)', r['verdict'] == 'PASS' and r['freq']['freq'] > 1, (r['verdict'], r['freq']))
r = rd('b1_nocalls', 'f6e_b1', pre_calls=[], hold_calls=[])
check('b1 without counter lines -> PASS', r['verdict'] == 'PASS', (r['verdict'], r['why']))
# --- admission ---
for name, kw in (('b9a_true', dict(env_over=dict(KYTY_FIX_B9A='true'))), ('b9a_sp', dict(env_over=dict(KYTY_FIX_B9A='1 '))),
                 ('b9a_none', dict(env_drop=('KYTY_FIX_B9A',))), ('pn', dict(env_over=dict(KYTY_PRINT_NAMES='1'))),
                 ('b1b', dict(env_over=dict(KYTY_FIX_B1B='1'))), ('ds', dict(env_over=dict(KYTY_FIX_DUALSRC='1'))),
                 ('b26', dict(env_over=dict(KYTY_FIX_B26='1'))), ('mini', dict(env_over=dict(KYTY_FIX_MINIMIZE='0'))),
                 ('pc0', dict(env_over=dict(KYTY_PIPELINE_PRECACHE='0'))), ('nopre', dict(pre_line=False)),
                 ('bin', dict(binary='2e6df8f09f006ef8d49173bd4abccea074da94769c5c31b9caeeaadc3eaf74ae')),
                 ('pin', dict(env_drop=('KYTY_GPU_CLOCK_PIN',))), ('ckpt', dict(env_over=dict(KYTY_GPU_CHECKPOINTS='0'))),
                 ('att', dict(attempts=2)), ('guest', dict(guest='-lvl mini_astro_clock_tower')), ('val', dict(cmd_val=True)),
                 ('norec', dict(env_drop=('KYTY_REC',))), ('pvar', dict(env_over=dict(KYTY_PVAR='2'))),
                 ('rec_other', dict(env_over=dict(KYTY_REC='C:/x/rec_f6e_a2.mp4')))):
    r = rd('ad_' + name, 'f6e_a1', **kw)
    check('admission %s -> NOT ADMITTED' % name, r['verdict'] == 'NOT ADMITTED', (r['verdict'], r['why']))
    check('admission %s -> stop' % name, R.stop_check(r).startswith('stop: NOT ADMITTED'), R.stop_check(r))
# --- I10 by p.306(g) B1 (seal 02): a cold variant directory ---
BSL = chr(92)
NO_V = 'PipelinePrecache: no _ShaderCache' + BSL + 'PPSA21564' + BSL + 'variant_fixb26_fixb1b' + BSL + 'pipelines.bin yet'
NO_R = 'PipelinePrecache: no _ShaderCache' + BSL + 'PPSA21564' + BSL + 'pipelines.bin yet'
SAVED = 'PipelinePrecache: saved 405 recipes (3959437 bytes)'
for name, lines, want in (('cold', [NO_V, SAVED], 'PASS'), ('cold_slash', [NO_V.replace(BSL, '/'), SAVED], 'PASS'),
                          ('cold_us', [NO_V, 'PipelinePrecache: saved 2 recipes (722 bytes) (1500 us)'], 'PASS'),
                          ('no_only', [NO_V], 'NOT ADMITTED'), ('saved_only', [SAVED], 'NOT ADMITTED'),
                          ('root_no', [NO_R, SAVED], 'NOT ADMITTED'), ('both', [NO_V, SAVED, 'PipelinePrecache: 310 recipes -> 310 pipelines'], 'PASS'),
                          ('stale', ['PipelinePrecache: stale recipes (signature mismatch), ignored', SAVED], 'NOT ADMITTED'),
                          ('failed', [NO_V, 'PipelinePrecache: failed to write x'], 'NOT ADMITTED')):
    r = rd('i10_' + name, 'f6e_a1', pre_line=lines)
    check('I10 (p.306(g) B1) %s -> %s' % (name, want), r['verdict'] == want, (r['verdict'], r['why'], [a for a in r['admit'] if not a[1]]))
r = rd('i10_cold_c1', 'f6e_c1', pre_line=[NO_V, SAVED])
check('I10 cold variant at the control =0 -> CONTROL OK', r['verdict'] == 'CONTROL OK', (r['verdict'], r['why']))
# the real lines of series 1 (C:/kyty/f287/f6e/series1/log_f6e_a1.txt, p.296(d)): the first 37 000 lines hold line 84 'no ...
# variant_fixb26_fixb1b...pipelines.bin yet' and line 36886 'saved 2 recipes'
S1 = os.path.join(HERE, 'series1', 'log_f6e_a1.txt')
ex_p = os.path.join(FX, 's1_head.txt')
os.makedirs(FX, exist_ok=True)
with open(S1, 'rb') as fi, open(ex_p, 'wb') as fo:
    for k, line in enumerate(fi):
        if k >= 37000:
            break
        fo.write(line)
e1 = R.scan_f6e(ex_p)
check('real series 1 head: recipes-> 0, no-variant 1, saved 1 -> I10 by B1', e1['pre'] == 0 and e1['pre_no'] == 1 and e1['pre_saved'] == 1,
      (e1['pre'], e1['pre_no'], e1['pre_saved']))
r = rd('ad_ctl1', 'f6e_c1', env_over=dict(KYTY_FIX_B9A='1'))
check('control with KYTY_FIX_B9A=1 -> NOT ADMITTED', r['verdict'] == 'NOT ADMITTED', r['verdict'])
# --- form line (p.290(b)(2)) ---
r = rd('fm_0', 'f6e_a1', fixon=0)
check('=1 without FixB9a: on -> INVALID', r['verdict'] == 'INVALID', (r['verdict'], r['why']))
check('INVALID first -> repeat-form <tag>f', R.stop_check(r).startswith('repeat-form: f6e_a1f'), R.stop_check(r))
r = rd('fm_2', 'f6e_a1', fixon=2)
check('=1 with two FixB9a lines -> INVALID', r['verdict'] == 'INVALID', r['verdict'])
r = rd('fm_c', 'f6e_c2', fixon=1)
check('=0 with a FixB9a line -> INVALID', r['verdict'] == 'INVALID', r['verdict'])
r = rd('fm_f', 'f6e_b1f', fixon=0)
check('form repeat INVALID again -> stop', R.stop_check(r).startswith('stop: INVALID again'), R.stop_check(r))
r = rd('fm_r', 'f6e_b1r', fixon=0)
check('K3 repeat INVALID -> stop (no form repeat of a repeat)', R.stop_check(r).startswith('stop: INVALID again'), R.stop_check(r))
# --- window events ---
r = rd('win_min', 'f6e_a1', win=('Window 1 minimized',))
check('minimized -> WINDOW EVENT and stop', r['verdict'] == 'WINDOW EVENT' and R.stop_check(r).startswith('stop: WINDOW EVENT'), r['verdict'])
r = rd('win_rec', 'f6e_c1', win=('Recovering Vulkan swapchain',))
check('Recovering Vulkan swapchain -> WINDOW EVENT', r['verdict'] == 'WINDOW EVENT', r['verdict'])
r = rd('win_other', 'f6e_a1', win=('Window 1 restored', 'Window 1 lost keyboard focus', 'Window 1 resized', 'Window 1 size changed'))
check('other window lines counted, not an event', r['verdict'] == 'PASS' and r['win']['restored'] == 1 and
      r['win']['size changed'] == 1, (r['verdict'], r['win']))
# --- controls (p.287(v)(6)) ---
r = rd('c1_ok', 'f6e_c1')
check('c1 profile 2/295/365/362 -> CONTROL OK', r['verdict'] == 'CONTROL OK' and r['stub_ap_lines'] == 1024, (r['verdict'], r['why']))
r = rd('c2_ok', 'f6e_c2')
check('c2 profile 2/1022 -> CONTROL OK', r['verdict'] == 'CONTROL OK', (r['verdict'], r['why']))
p = ctl_profile(R.TC)
p['b-dYXrjSNZU'] = 3
r = rd('c1_exact', 'f6e_c1', stubs=[s for s, n in p.items() for _ in range(n)])
check('c1 b-dYXrjSNZU 3 (the letter 2) -> CONTROL FAIL', r['verdict'] == 'CONTROL FAIL', (r['verdict'], r['why']))
p = ctl_profile(R.TC)
p['WXMhENV2NcA'] = 310
r = rd('c1_tol', 'f6e_c1', stubs=[s for s, n in p.items() for _ in range(n)])
check('c1 WXMh 310 within +-15 -> CONTROL OK', r['verdict'] == 'CONTROL OK', (r['verdict'], r['why']))
p['WXMhENV2NcA'] = 311
r = rd('c1_tol2', 'f6e_c1', stubs=[s for s, n in p.items() for _ in range(n)])
check('c1 WXMh 311 outside +-15 -> CONTROL FAIL', r['verdict'] == 'CONTROL FAIL', (r['verdict'], r['why']))
p = ctl_profile(R.TC)
p['d84otraxt2s'] = 300
p['G+QLTfyLMYk'] = 300
r = rd('c1_min', 'f6e_c1', stubs=[s for s, n in p.items() for _ in range(n)])
check('c1 AudioPropagation lines 897 < 1000 -> CONTROL FAIL', r['verdict'] == 'CONTROL FAIL' and any('< 1000' in w for w in r['why']),
      (r['verdict'], r['why']))
r = rd('c1_other', 'f6e_c1', stubs=[s for s, n in ctl_profile(R.TC).items() for _ in range(n)] + [('Zz', 'libSceX_v1')])
check('c1 another symbol -> CONTROL FAIL', r['verdict'] == 'CONTROL FAIL' and any('other symbols' in w for w in r['why']), (r['verdict'], r['why']))
r = rd('c1_calls', 'f6e_c1', extra_calls=[PRE])
check('c1 an AudioPropagation: calls line at =0 -> CONTROL FAIL', r['verdict'] == 'CONTROL FAIL', (r['verdict'], r['why']))
r = rd('c2_other', 'f6e_c2', stubs=[s for s, n in ctl_profile(R.MA).items() for _ in range(n)] + ['d84otraxt2s'])
check('c2 SourceCreate stub (not in its profile) -> CONTROL FAIL', r['verdict'] == 'CONTROL FAIL', (r['verdict'], r['why']))
r = rd('c1_short', 'f6e_c1', rows=7199)
check('c1 hold 119.985 s -> NOT EVALUABLE', r['verdict'] == 'NOT EVALUABLE', r['verdict'])
r = rd('c1_death', 'f6e_c1', death=True)
check('c1 death -> stop', R.stop_check(r).startswith('stop: death'), R.stop_check(r))
r = rd('c1_k2', 'f6e_c1', k2=(900,))
check('c1 K2 is information at =0', r['verdict'] == 'CONTROL OK' and r['k2'] == 1, (r['verdict'], r['why']))
# --- K3 hold (letter: whole hold; variant 120 s) ---
r = rd('k3', 'f6e_a2', k3=(300, 600, 601, 5000), rows=12000)
check('K3: rows 300 and 600 in the entry window, 601 and 5000 on the hold', r['k3_window'] == 2 and r['k3_hold'] == 2, (r['k3_window'], r['k3_hold']))
check('K3 within 120 s variant: 601 in, 5000 in (83 s), 11000 out', r['k3_hold120'] == 2, r['k3_hold120'])
r = rd('k3b', 'f6e_a2', k3=(601, 9000), rows=12000)
check('K3 variant 120 s drops a row after 120 s of shown time', r['k3_hold'] == 2 and r['k3_hold120'] == 1, (r['k3_hold'], r['k3_hold120']))
check('K3 alone does not fail the tag (decided in the summary)', r['verdict'] == 'PASS', r['verdict'])
# --- stop check ---
check('stop check: no reading', R.stop_check(None).startswith('stop: no reading'))
r = rd('st_fail', 'f6e_a1', stubs=['d84otraxt2s'])
check('stop check: a FAIL member is data -> continue', R.stop_check(r).startswith('continue: FAIL'), R.stop_check(r))
r = rd('st_ne', 'f6e_a2', rows=7199, hold_at=7000)
check('stop check: NOT EVALUABLE -> continue', R.stop_check(r).startswith('continue: NOT EVALUABLE'), R.stop_check(r))
# --- summary, judge, repeats ---


def series(over=None, drop=(), add=None):
    root = os.path.join(FX, 'series')
    shutil.rmtree(root, ignore_errors=True)
    kw = {t: {} for t in R.SEQ}
    for t, k in (over or {}).items():
        kw.setdefault(t, {}).update(k)
    for t in R.SEQ:
        if t not in drop:
            write_run(root, t, **kw[t])
    for t, k in (add or {}).items():
        write_run(root, t, **k)
    reads = R.all_reads(root, SC)
    txt, word = R.summary(reads)
    return txt, word, R.judge(reads), root


txt, word, (j, due), _ = series()
check('summary all ideal -> PASS', word == 'PASS' and due == [], txt)
check('summary (7) line', '(7) N: timestop_casino =1 entries PASS 2 of 2; mini_astro_clock_tower =1 entries PASS 1 of 1' in txt, txt)
txt, word, (j, due), _ = series(drop=('f6e_c2',))
check('summary control missing -> NOT EVALUABLE, b1 NO CONTROL', word == 'NOT EVALUABLE' and j['f6e_b1']['status'] == 'NO CONTROL', txt)
txt, word, (j, due), root = series(over={'f6e_a1': dict(k3=(1000, 2000))})
check('a1 K3 2 > max(base 1, control 0) -> REPEAT DUE, NOT EVALUABLE', word == 'NOT EVALUABLE' and due == ['f6e_a1r'] and
      j['f6e_a1']['status'] == 'REPEAT DUE', (txt, due))
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--repeats', '--root', root], capture_output=True)
check('--repeats names f6e_a1r', p.returncode == 0 and p.stdout.decode('ascii').strip() == 'repeat: f6e_a1r', p.stdout)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(k3=(1000,))})
check('a1 K3 1 = base 1 -> PASS', word == 'PASS' and j['f6e_a1']['limit'] == 1, txt)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(k3=(1000, 2000, 3000)), 'f6e_c1': dict(k3=(1000, 2000, 3000))})
check('limit = control 3 > base 1 -> PASS', word == 'PASS' and j['f6e_a1']['limit'] == 3, txt)
txt, word, (j, due), _ = series(over={'f6e_b1': dict(k3=(1000,))})
check('b1 K3 1 > base 0 and control 0 -> REPEAT DUE', due == ['f6e_b1r'], (txt, due))
txt, word, (j, due), _ = series(over={'f6e_a1': dict(k3=(1000, 2000))}, add={'f6e_a1r': dict(k3=(1000,))})
check('repeat decides: a1r K3 1 -> PASS', word == 'PASS' and j['f6e_a1']['status'] == 'PASS' and due == [], txt)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(k3=(1000, 2000))}, add={'f6e_a1r': dict(k3=(1000, 2000))})
check('repeat K3 2 again -> FAIL', word == 'FAIL' and j['f6e_a1']['status'] == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(k3=(1000, 2000))}, add={'f6e_a1r': dict(k3=(), asserts_log=1)})
check('294(b) ASSERT on the repeat -> FAIL', word == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(asserts_log=1)}, add={'f6e_a1r': dict()})
check('294(b) a repeat does not lift the ASSERT member', word == 'FAIL' and j['f6e_a1']['status'] == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_b1': dict(umsg=1)})
check('294(b) user_msg_param 1 > control 0 -> FAIL', word == 'FAIL' and j['f6e_b1']['status'] == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_b1': dict(umsg=2), 'f6e_c2': dict(umsg=2)})
check('294(b) user_msg_param 2 = control 2 -> PASS', word == 'PASS', txt)
txt, word, (j, due), _ = series(over={'f6e_a2': dict(umsg=1), 'f6e_c2': dict(umsg=1)})
check('294(b) the control of the SAME level: a2 1 > c1 0 -> FAIL', word == 'FAIL' and j['f6e_a2']['status'] == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_c1': dict(stubs=['d84otraxt2s'])})
check('control fail -> series FAIL', word == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_a2': dict(fixon=0)}, add={'f6e_a2f': dict()})
check('form repeat a2f is the reading of a2 -> PASS', word == 'PASS' and 'f6e_a2f' in txt, txt)
txt, word, (j, due), _ = series(over={'f6e_a2': dict(fixon=0)})
check('INVALID without its form repeat -> NOT EVALUABLE', word == 'NOT EVALUABLE', txt)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(stubs=['d84otraxt2s']), 'f6e_c2': dict(rows=7199)})
check('FAIL beats NOT EVALUABLE', word == 'FAIL', txt)
txt, word, (j, due), _ = series(over={'f6e_a1': dict(win=('Window 1 minimized',))})
check('window event -> NOT EVALUABLE', word == 'NOT EVALUABLE' and 'f6e_a1=WINDOW EVENT' in txt, txt)
# --- text ---
r = rd('tx', 'f6e_a1', stubs=['d84otraxt2s', ('Zz', 'libSceX_v1')], std_stubs=3, asserts_log=1)
t = R.text(r)
check('text: stubs by library and symbol, stdout not added', 'stubs by library' in t and 'stdout printf stub lines (not added, p.294(v)): 3' in t, t)
check('text verdict line', t.split('\n')[-1].startswith('F6E VERDICT f6e_a1: FAIL'), t.split('\n')[-1])
check('text is ASCII', all(ord(c) < 128 for c in t))
# --- seal check ---
sroot = os.path.join(FX, 'seal')
shutil.rmtree(sroot, ignore_errors=True)
os.makedirs(sroot)
open(os.path.join(sroot, 'a.txt'), 'w').write('a')
sa = sha(os.path.join(sroot, 'a.txt'))
open(os.path.join(sroot, 'p.md'), 'w').write('x\nseal: %s a.txt\n' % sa)
check('seal ok', R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
open(os.path.join(sroot, 'p.md'), 'w').write('seal: %s a.txt\n' % ('0' * 64))
check('seal mismatch', not R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
open(os.path.join(sroot, 'p.md'), 'w').write('seal: %s a.txt\nseal: %s a.txt\n' % (sa, sa))
check('seal duplicate line', not R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
open(os.path.join(sroot, 'p.md'), 'w').write('nothing\n')
check('seal missing line', not R.check_seal(os.path.join(sroot, 'p.md'), sroot, ('a.txt',))[0])
check('seal names cover the harness', set(('go_f6e.sh', 'f6e_read.py', 'win_f6e.py', 'cachesig_f6e.py', 'test_f6e_read.py',
                                           'test_go_f6e.py', 'enter_scene.py', R.SC142)) <= set(R.SEALED))
# --- win_f6e.decide ---
ok = {i: ('done', None) for i in W.NEED_DONE + W.NEED_DELIVERED}
ok.update({i: ('blocked', None) for i in W.YIELD_TO})
check('win open', W.decide(ok) == (0, 'open'))
for i in W.YIELD_TO:
    for st in ('todo', 'in_progress'):
        s = dict(ok)
        s[i] = (st, None)
        check('win %s %s closed' % (i, st), W.decide(s) == (5, 'closed'))
    s = dict(ok)
    s[i] = ('blocked', 'run-1')
    check('win %s with a run closed' % i, W.decide(s) == (5, 'closed'))
for i in W.NEED_DELIVERED:
    for st, want in (('in_review', (0, 'open')), ('in_progress', (5, 'closed')), ('blocked', (5, 'closed')), ('todo', (5, 'closed'))):
        s = dict(ok)
        s[i] = (st, None)
        check('win %s %s' % (i, st), W.decide(s) == want, W.decide(s))
    s = dict(ok)
    s[i] = ('done', 'run-2')
    check('win %s done with a run closed' % i, W.decide(s) == (5, 'closed'))
s = dict(ok)
s['HPP-376'] = ('in_review', None)
check('win F6d not done closed', W.decide(s) == (5, 'closed'))
s = dict(ok)
s['HPP-370'] = (None, None)
check('win no answer rc 6', W.decide(s) == (6, 'error'))
s = dict(ok)
s['HPP-353'] = ('in_progress', None)
check('win audit HPP-353 in_progress closed (p.306(d))', W.decide(s) == (5, 'closed'))
s = dict(ok)
s['HPP-353'] = ('in_review', None)
check('win audit HPP-353 in_review closed (needs done)', W.decide(s) == (5, 'closed'))
check('win names F6d, audit s145, F5c, FSc, session run step, P17', W.NEED_DONE == ('HPP-376', 'HPP-353') and set(W.NEED_DELIVERED) == {'HPP-357', 'HPP-370'}
      and set(W.YIELD_TO) == {'HPP-352', 'HPP-364'})
pw = subprocess.run([sys.executable, os.path.join(HERE, 'win_f6e.py')], capture_output=True,
                    env={k: v for k, v in os.environ.items() if not k.startswith('PAPERCLIP_') and k != 'PYTHONIOENCODING'})
check('win without API env refuses rc 6, ASCII line (cp1250)', pw.returncode == 6 and pw.stdout.decode('cp1250').startswith('win_f6e HPP-376 None'), pw)
# --- cache signature manifest ---
croot = os.path.join(FX, 'cache')
shutil.rmtree(croot, ignore_errors=True)
os.makedirs(os.path.join(croot, 'variant_fixb26_fixb1b'))
open(os.path.join(croot, 'a.bin'), 'wb').write(b'KytySC3:699c1e4b7db359067b461e029b913c4b6e78dc90' + b'\0' * 20)
open(os.path.join(croot, 'pipelines.bin'), 'wb').write(b'PIPE')
open(os.path.join(croot, 'variant_fixb26_fixb1b', 'b.bin'), 'wb').write(b'KytySC3:56189185f9e9f9a0ea5174f3f85206e6d099db3d')
ln = CS.line(CS.survey(croot))
check('cachesig: root 2 files (1 sig 699c1e4b, 1 other), variant 1 file of 56189185', ln ==
      'cachesig .: files 2 sig 699c1e4b=1 other 1; variant_fixb26_fixb1b: files 1 sig 56189185=1 other 0; files of signature 56189185: 1', ln)
check('cachesig: no dir', CS.line(CS.survey(os.path.join(croot, 'none'))) == 'cachesig no cache dir; files of signature 56189185: 0')
# --- real witness logs (hard links): the lead's base numbers p.287(b)-(v), p.294(a) ---
os.makedirs(REAL, exist_ok=True)
for src_root, src, tag in (('C:/kyty/s142', 'c142_03', 'f6e_c1'), ('C:/kyty/s143', 'v143_03', 'f6e_c2')):
    for kind in ('log_%s.txt', 'stdout_%s.txt', 'glitch_%s.txt', 'sheet_%s.png'):
        dst = os.path.join(REAL, kind % tag)
        if not os.path.exists(dst):
            os.link(src_root + '/' + kind % src, dst)
    js = json.load(open('%s/%s.json' % (src_root, src), encoding='utf-8'))
    env = dict(js.get('env') or {}, KYTY_FIX_B9A='0')
    env['KYTY_REC'] = 'C:\\kyty\\f287\\f6e\\rec_%s.mp4' % tag
    js['env'] = env
    js['binary_sha256'] = R.BIN_SHA
    json.dump(js, open(os.path.join(REAL, '%s.json' % tag), 'w', encoding='ascii'))
r = R.read_tag('f6e_c1', REAL, SC)
check('real c142_03 as the control: profile 2/295/365/362 (F6b recount) -> CONTROL OK', r['verdict'] == 'CONTROL OK' and
      r['stub_ap'] == {'b-dYXrjSNZU': 2, 'WXMhENV2NcA': 295, 'd84otraxt2s': 365, 'G+QLTfyLMYk': 362} and r['stub_lines'] == 1024,
      (r['verdict'], r['why'], r['stub_ap'], r['stub_lines']))
check('real c142_03: ASSERT 0, user_msg_param 0 (p.294(a))', r['asserts_log'] == 0 and r['asserts_std'] == 0 and r['umsg_log'] == 0,
      (r['asserts_log'], r['asserts_std'], r['umsg_log']))
check('real c142_03: K3 hold 1 = the base of p.287(v)(5)', r['k3_hold'] == 1, r['k3_hold'])
check('real c142_03: stdout printf stub lines present, not added', r['stub_std'] >= 1 and r['stub_lines'] == 1024, r['stub_std'])
check('real c142_03: no counter line, no FixB9a line at the old build', r['calls_lines'] == 0 and r['fixon'] == 0)
r2 = R.read_tag('f6e_c2', REAL, SC)
check('real v143_03 as the control: profile 2/1022 -> CONTROL OK', r2['verdict'] == 'CONTROL OK' and
      r2['stub_ap'] == {'b-dYXrjSNZU': 2, 'WXMhENV2NcA': 1022}, (r2['verdict'], r2['why'], r2['stub_ap']))
check('real v143_03: K3 hold 0 = the base', r2['k3_hold'] == 0, r2['k3_hold'])
check('real v143_03: ASSERT 0, user_msg_param 0', r2['asserts_log'] == 0 and r2['asserts_std'] == 0 and r2['umsg_log'] == 0)
REAL2 = os.path.join(HERE, 'fx', 'real2')
os.makedirs(REAL2, exist_ok=True)
for kind in ('log_%s.txt', 'stdout_%s.txt', 'glitch_%s.txt', 'sheet_%s.png'):
    dst = os.path.join(REAL2, kind % 'f6e_c1')
    if not os.path.exists(dst):
        os.link('C:/kyty/s144/' + kind % 'v144_13', dst)
js = json.load(open('C:/kyty/s144/v144_13.json', encoding='utf-8'))
js['env'] = dict(js.get('env') or {}, KYTY_FIX_B9A='0', KYTY_REC='C:/kyty/f287/f6e/rec_f6e_c1.mp4')
js['binary_sha256'] = R.BIN_SHA
json.dump(js, open(os.path.join(REAL2, 'f6e_c1.json'), 'w', encoding='ascii'))
r3 = R.read_tag('f6e_c1', REAL2, SC)
check('real v144_13 (second base log of timestop_casino): K3 hold 0', r3['k3_hold'] == 0, r3['k3_hold'])
check('real v144_13: profile 2/296/365/361 (F6b) within the control reading -> CONTROL OK', r3['verdict'] == 'CONTROL OK' and
      r3['stub_ap'] == {'b-dYXrjSNZU': 2, 'WXMhENV2NcA': 296, 'd84otraxt2s': 365, 'G+QLTfyLMYk': 361}, (r3['verdict'], r3['why'], r3['stub_ap']))
check('real v144_13: ASSERT 0, user_msg_param 0 (p.294(a))', r3['asserts_log'] == 0 and r3['asserts_std'] == 0 and r3['umsg_log'] == 0)
check('base of timestop_casino = max(c142_03, v144_13) = 1 = K3_BASE', max(r['k3_hold'], r3['k3_hold']) == R.K3_BASE[R.TC])
# --- strict cp1250 console ---
root = os.path.join(FX, 'cp')
shutil.rmtree(root, ignore_errors=True)
write_run(root, 'f6e_a1', stubs=['d84otraxt2s'], asserts_log=1, death=True)
env = {k: v for k, v in os.environ.items() if k != 'PYTHONIOENCODING'}
env['PYTHONIOENCODING'] = 'cp1250:strict'
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--tag', 'f6e_a1', '--root', root], capture_output=True, env=env)
check('cp1250 strict: rc 0 and ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout), p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--summary', '--root', root], capture_output=True, env=env)
check('cp1250 strict: summary rc 0', p.returncode == 0 and b'F6E SERIES VERDICT' in p.stdout, p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--repeats', '--root', root], capture_output=True, env=env)
check('cp1250 strict: --repeats rc 0', p.returncode == 0 and p.stdout.startswith(b'repeat: '), p.stdout)
p = subprocess.run([sys.executable, os.path.join(HERE, 'cachesig_f6e.py'), croot], capture_output=True, env=env)
check('cp1250 strict: cachesig rc 0 ASCII', p.returncode == 0 and all(b < 128 for b in p.stdout), p.stderr[-300:])
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--tag', 'f6e_zz'], capture_output=True, env=env)
check('usage rc 2', p.returncode == 2, p.stdout)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--tag', 'f6e_w1'], capture_output=True, env=env)
check('warm-up f6e_w1 is not read (p.306(g) B2): rc 2', p.returncode == 2, p.stdout)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--tag', 'f6e_c1r'], capture_output=True, env=env)
check('K3 repeat of a control is not a tag: rc 2', p.returncode == 2, p.stdout)
p = subprocess.run([sys.executable, os.path.join(HERE, 'f6e_read.py'), '--tag', 'f6e_a2', '--root', root], capture_output=True, env=env)
check('no log rc 1', p.returncode == 1, p.stdout)
shutil.rmtree(FX, ignore_errors=True)
print('checks %d failed %d' % (N[0], len(FAIL)))
print('ALL OK' if not FAIL else 'SOME FAILED: %s' % FAIL)
sys.exit(0 if not FAIL else 1)

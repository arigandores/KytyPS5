"""F40c (HPP-772): fixtures of f40c_read.py - every admission member, every member of item 692 (g)(1), (g)(4) with item 696 (b)(1)-(3),
the words, the edges (7 200 000 / 7 199 999, 100 000 / 99 999, 50 000 / 49 999, + 2 000 / + 2 001, + 16 667 / + 16 668, flap 50 000 /
49 999, gap = life_min, exit 13.0 / 13.001, 1 000 000 / 999 999 in and out of the window, 300 s, 3 000 / 2 999), the partner rule, the
table and the output in strict cp1250 without PYTHONIOENCODING.  The first output line names the suite and the target with sha256; the
last line is ALL OK only when every check passes.  ASCII only.
usage: python test_f40c_read.py [<reader path>]"""
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'f40c_read.py')
sys.path.insert(0, os.path.dirname(os.path.abspath(TARGET)))
import importlib.util
spec = importlib.util.spec_from_file_location('f40c_read', TARGET)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


print('suite test_f40c_read.py sha256 %s target %s sha256 %s' % (sha(os.path.abspath(__file__)), os.path.basename(TARGET), sha(TARGET)))
CHECKS = [0, 0]
FS11 = 'ea51ae80' + '0' * 56
FS12 = '46892c20080819ae090598511748265dfbac31f303a02f1804e5b10db8acae26'
SIG = R.SIG
F24_BASE = dict(upd_on_main=0, upd_slept_us=0, main_late_max_us=20000, in_posted=90, in_seen=90, in_post_fail=0, in_lat_max_us=20000,
                in_pre_lat_max_us=10000, hung_ms=0, jp_update_max_us=0, jp_tasks=0, pad_posted=380, pad_seen=380, pad_lat_p99_us=17000,
                pad_lat_max_us=30000, attached=0, opened=0, open_failed=0, open_lat_max_us=0, flap_life_min_us=0, flap_life_max_us=0,
                jp_scan_gap_max_us=0)
F24_BY_KIND = {
    'u0': dict(upd_on_main=1, upd_slept_us=8000100, main_late_max_us=8010000, in_lat_max_us=8020000, in_pre_lat_max_us=20000, hung_ms=3000),
    'u1': dict(upd_on_main=0, upd_slept_us=8000100, jp_update_max_us=8000500, main_late_max_us=20000, in_lat_max_us=30000, hung_ms=0),
    'p0': dict(in_posted=0, in_seen=0), 'p1': dict(in_posted=0, in_seen=0),
    'f0': dict(attached=60, opened=60, flap_life_min_us=40000, flap_life_max_us=44000, jp_scan_gap_max_us=0),
    'f1': dict(attached=60, opened=60, flap_life_min_us=40000, flap_life_max_us=44000, jp_scan_gap_max_us=2000, jp_tasks=60),
    'd1': dict(jp_tasks=1),
    'm1': dict(attached=60, opened=20, flap_life_min_us=40000, flap_life_max_us=44000, jp_scan_gap_max_us=1500),
    'm4': dict(jp_tasks=0),
    'm5': dict(upd_on_main=1, main_late_max_us=8010000, in_lat_max_us=8020000),
    'm6': dict(upd_on_main=0, jp_update_max_us=8000500),
}


def default(tag):
    base = R.base_of(tag)
    sp = R.SPEC[base]
    kind = sp['kind']
    f = dict(F24_BASE)
    f.update(F24_BY_KIND.get(kind, {}))
    owner = None if sp['fix'] == '0' else dict(hid=5, helper=5, msg=5, pump=5, main=1)
    if kind == 'm6':
        owner = dict(hid=1, helper=1, msg=1, pump=5, main=1)
    post = [100000] * 3001 if kind == 'n1' else [16000] * 200
    return dict(tag=tag, sp=sp, kind=kind, f24=f, owner=owner, frames_pre=[16000] * 20, frames_win=[16000] * 30,
                frames_post=post, extra_lines=[], drop=set(), mode_line='FixF24: mode=%s b24=1' % sp['fix'],
                json=dict(), env_over={}, env_drop=[], stdout=['ok'], glitch='one-frame glitches: 0', idx=10000, sheet='sheet: x.png',
                installed_before=R.BIN_INST, installed_after=R.BIN_INST, installed_sha=R.BINS[sp['bin']],
                manifest='manifest cmp EQUAL 10 files', level=R.SKY, quit_mark=dict(exit_upper_s=7.5, exit_lower_s=7.1),
                hold_exit=None if sp['mode'] != 'exit' else 0, expired_before_ran=True, init_before_guest=True)


def f24_line(c):
    sp = c['sp']
    f = c['f24']
    return 'TestHidLoss: f24 mode=%s fix=%s ' % (sp['mode'], sp['fix']) + ' '.join('%s=%d' % (k, f[k]) for k in R.F24_KEYS)


def build(c, d):
    """write the fixture dir d from the case c"""
    sp = c['sp']
    kind = c['kind']
    mode = sp['mode']
    L = ['Fork build arigandores/KytyPS5 x, git = abc', 'LogAsync: mode=1 queue=1']
    if 'mode_line' not in c['drop']:
        L.append(c['mode_line'])
    if sp['fix'] == '1' and c['init_before_guest']:
        L.append('FixF24: init tid=5 pump tid=5 main tid=1')
    if c['owner'] is not None and 'owner' not in c['drop']:
        o = c['owner']
        L.append('FixF24: init_owner hid=%d helper=%d msg=%d pump=%d main=%d' % (o['hid'], o['helper'], o['msg'], o['pump'], o['main']))
    L += ['FixF21: mode=1 wait_ms=12000', 'FixB12: mode=1', 'FixB13: mode=1',
          'ShaderSeed: compatibility=ok :KytySC3:%s:x' % c.get('sig', SIG),
          'Shader translation cache: C:/x/%s' % c.get('variant', R.VARIANT_DIR)]
    if mode is not None and 'config' not in c['drop']:
        L.append(c.get('config', 'TestHidLoss: config on delay_s=60 mode=%s hold_ms=3000 edition=2 hold_upd_ms=8000 in_ms=100 probe_ms=20 '
                                 'fix_f24=%s' % (mode, sp['fix'])))
    L.append('GuestOut: hello')
    if sp['fix'] == '1' and not c['init_before_guest']:
        L.append('FixF24: init tid=5 pump tid=5 main tid=1')
    if 'entry' not in c['drop']:
        L.append('GuestOut: Level has started: %s' % R.SKY)
    if mode is not None and 'armed' not in c['drop']:
        L.append('TestHidLoss: armed t_us=1000')
    L.append('FrameTrace: n=1 dt_us=16000 draws=50')
    n = 2
    pre_fire = list(c['frames_pre'])
    if c.get('fire_before_scene'):
        L.append('TestHidLoss: fire mode=%s t_us=5000' % mode)
    L.append('FrameTrace: n=%d dt_us=16000 draws=500' % n)
    n += 1
    if mode is not None:
        if 'attach' not in c['drop']:
            L.append(c.get('attach_line', 'TestHidLoss: attach index=0 t_us=2000 hwnd=1'))
        if 'testpad' not in c['drop']:
            L.append('Controller 0: "KYTY test pad" type=PS5')
        if mode in ('upd', 'pad') and 'pps' not in c['drop']:
            L.append('TestHidLoss: pad probe start t_us=3000')
        if mode == 'pad':
            if 'title' not in c['drop']:
                L.append('TestHidLoss: title off t_us=2900')
            L.append('TestHidLoss: pad probe end t_us=4000 posted=380')
    for dt in pre_fire:
        L.append('FrameTrace: n=%d dt_us=%d draws=500' % (n, dt))
        n += 1
    if mode is not None and not c.get('fire_before_scene') and 'fire' not in c['drop']:
        L.append(c.get('fire_line', 'TestHidLoss: fire mode=%s t_us=5000' % mode))
    if mode == 'flap':
        for i in range(60):
            L.append('Controller %d: "KYTY flap pad" type=PS5' % (10 + i))
    for dt in c['frames_win']:
        L.append('FrameTrace: n=%d dt_us=%d draws=500' % (n, dt))
        n += 1
    if mode == 'exit':
        L.append('TestHidLoss: jp_task posted t_us=5500')
        if 'quit_posted' not in c['drop']:
            L.append('TestHidLoss: quit posted t_us=6000')
        if c['expired_before_ran']:
            if 'expired' not in c['drop']:
                L.append('FixF24: pump_stop_expired t_jp_ms=2000')
            if kind == 'm2' or c.get('ran_after'):
                L.append('TestHidLoss: jp_task ran t_us=13000')
        else:
            L.append('TestHidLoss: jp_task ran t_us=4000')
            L.append('FixF24: pump_stop_expired t_jp_ms=2000')
        L.append('TestHidLoss: done t_us=13000 upd_on_main=0')
    elif mode is not None:
        if mode == 'detach' and 'removed' not in c['drop']:
            L.append('Controller %d: removed' % c.get('removed_id', 0))
        if 'done' not in c['drop']:
            L.append('TestHidLoss: done t_us=13000')
        if c.get('quit_early'):
            L.append('Event: quit')
        if 'stat' not in c['drop']:
            L.append('TestHidLoss: stat mode=%s main_late_max_us=1 probes_posted=1 probes_run=1' % mode)
        if 'f24' not in c['drop']:
            L.append(c.get('f24_raw', f24_line(c)))
    for dt in c['frames_post']:
        L.append('FrameTrace: n=%d dt_us=%d draws=500' % (n, dt))
        n += 1
    L += c['extra_lines']
    L.append('FixB12Stat: passes=1 rewalk=0 rwd=0 lskip=0')
    if mode != 'exit' and not c.get('quit_early'):
        L.append('Event: quit')
    if 'summary' not in c['drop']:
        L.append('LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=1 bytes=1 max_queued_bytes=1 sync_lines=0 drain_timeouts=0')
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'log.txt'), 'wb').write(('\n'.join(L) + '\n').encode())
    open(os.path.join(d, 'stdout.txt'), 'wb').write(('\n'.join(c['stdout']) + '\n').encode())
    open(os.path.join(d, 'seal.md'), 'wb').write(b'seal\n')
    env = dict(KYTY_GUEST_ARGS='-lvl ' + R.SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE='C:/g', KYTY_SAMPLE_GATE='C:/s', KYTY_QUEUE_TRACE='1',
               KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_GPU_HANG_ABORT_S='8', KYTY_FIX_F24=sp['fix'])
    if mode is None:
        env['KYTY_REC'] = 'C:/r.mp4'
    else:
        env['KYTY_TEST_HIDLOSS'] = '60:' + mode
    env.update(c['env_over'])
    for k in c['env_drop']:
        env.pop(k, None)
    att = dict(outcome='ok', hold_exit=c['hold_exit'], hold_s=float(sp['hold']), close_rc=0, close_killed=False, close_s=2.0)
    if mode == 'exit':
        att['quit_mark'] = c['quit_mark']
    js = dict(binary_sha256=R.BINS[sp['bin']], prereg=dict(sha256=sha(os.path.join(d, 'seal.md'))), env=env,
              cmdline=['kyty_emulator.exe', '--vulkan-validation', 'false', '--shader-validation', 'false'], attempts=[att],
              guest_args='-lvl ' + R.SKY, hold_s=sp['hold'])
    for k, v in c['json'].items():
        if k == 'attempt':
            att.update(v)
        else:
            js[k] = v
    json.dump(js, open(os.path.join(d, 'es.json'), 'w'))
    for nm in ('installed_before', 'installed_after', 'installed_sha', 'manifest', 'level'):
        open(os.path.join(d, (nm if nm != 'manifest' else 'manifest_cmp') + '.txt'), 'w').write(str(c[nm]) + '\n')
    if c['glitch'] is not None:
        open(os.path.join(d, 'glitch.txt'), 'w').write(c['glitch'] + '\n')
    if c['sheet'] is not None:
        open(os.path.join(d, 'sheet.txt'), 'w').write(c['sheet'] + '\n')
    if c['idx'] is not None:
        open(os.path.join(d, 'rec.idx'), 'w').write('x\n' * c['idx'])


TMP = tempfile.mkdtemp(prefix='t40c_')
COUNT = [0]


def run(c, partner=None):
    COUNT[0] += 1
    d = os.path.join(TMP, 'c%d' % COUNT[0])
    build(c, d)
    pr = None
    if partner is not None:
        pd = os.path.join(TMP, 'p%d' % COUNT[0])
        build(partner, pd)
        pr = R.read_tag(partner['tag'], R.paths(partner['tag'], pd))
        pr = pr if pr.get('admitted') else None
    return R.read_tag(c['tag'], R.paths(c['tag'], d), pr)


def check(name, cond):
    CHECKS[0] += 1
    if not cond:
        CHECKS[1] += 1
        print('FAIL %s' % name)


def word(c, partner=None):
    return run(c, partner)['word']


def mod(tag, **kw):
    c = default(tag)
    for k, v in kw.items():
        if k == 'f24':
            c['f24'] = dict(c['f24'], **v)
        elif k == 'drop':
            c['drop'] = set(v)
        else:
            c[k] = v
    return c


# --- clean words of every tag
CLEAN = {'f24_u0': 'MEMBERS_PASS', 'f24_p0': 'REFERENCE', 'f24_f0': 'REFERENCE', 'f24_f1': 'MEMBERS_PASS', 'f24_x1': 'MEMBERS_PASS',
         'f24_d1': 'MEMBERS_PASS', 'f24_m1': 'CAUGHT', 'f24_m2': 'CAUGHT', 'f24_m4': 'CAUGHT', 'f24_m5': 'CAUGHT', 'f24_m6': 'CAUGHT',
         'f24_n1': 'MEMBERS_PASS', 'f24_u0b': 'MEMBERS_PASS', 'f24_p0b': 'REFERENCE'}
for t, w in CLEAN.items():
    r = run(default(t))
    check('clean %s admitted (%s)' % (t, [a for a, b in r['admission'] if not b]), r['admitted'])
    check('clean %s word %s (got %s, members %s)' % (t, w, r['word'], r['members']), r['word'] == w)
U0 = default('f24_u0')
P0 = default('f24_p0')
for t, p in (('f24_u1', U0), ('f24_u1b', dict(U0, tag='f24_u0b')), ('f24_p1', P0), ('f24_p1b', dict(P0, tag='f24_p0b'))):
    r = run(default(t), p)
    check('clean %s with partner MEMBERS_PASS (%s)' % (t, r['word']), r['word'] == 'MEMBERS_PASS')
    check('clean %s without partner NO_PARTNER' % t, word(default(t)) == 'NO_PARTNER')
r = run(default('f24_n1'))
check('n1 form members all yes', r['form_ok'] is True)
check('n1 rows', 'pump_update_long 0' in r['row_n1'])

# --- admission members, each failure -> NOT_ADMITTED (stand tag u0 and V tag n1)
ADM = [('json binary', dict(json=dict(binary_sha256='0' * 64))),
       ('installed during', dict(installed_sha='0' * 64)),
       ('installed before FS11', dict(installed_before=FS11)),
       ('installed after FS11', dict(installed_after=FS11)),
       ('installed before FS12 (item 703 (d))', dict(installed_before=FS12)),
       ('installed after FS12 (item 703 (d))', dict(installed_after=FS12)),
       ('prereg', dict(json=dict(prereg=dict(sha256='0' * 64)))),
       ('env extra KYTY_FIX_B24', dict(env_over=dict(KYTY_FIX_B24='1'))),
       ('env extra KYTY_GAME_PATCH', dict(env_over=dict(KYTY_GAME_PATCH='x'))),
       ('env extra KYTY_GPU_CHECKPOINTS', dict(env_over=dict(KYTY_GPU_CHECKPOINTS='1'))),
       ('env missing KYTY_FIX_F24', dict(env_drop=['KYTY_FIX_F24'])),
       ('env hang abort 22', dict(env_over=dict(KYTY_GPU_HANG_ABORT_S='22'))),
       ('ExitFatal stdout', dict(stdout=['ExitFatal: x'])),
       ('ExitFatal log', dict(extra_lines=['ExitFatal: y'])),
       ('validation true', dict(json=dict(cmdline=['e', '--vulkan-validation', 'false', '--vulkan-validation', 'true', '--shader-validation', 'false']))),
       ('shader validation', dict(json=dict(cmdline=['e', '--vulkan-validation', 'false', '--shader-validation', 'true']))),
       ('rd', dict(json=dict(cmdline=['e', '--vulkan-validation', 'false', '--shader-validation', 'false', '--rd']))),
       ('guest args', dict(json=dict(guest_args='-lvl intro_next'))),
       ('level file', dict(level='intro_next')),
       ('hold option', dict(json=dict(hold_s=151))),
       ('outcome timeout', dict(json=dict(attempt=dict(outcome='timeout')))),
       ('no entry line', dict(drop=['entry'])),
       ('minimized', dict(extra_lines=['Window 1 minimized'])),
       ('recovering', dict(extra_lines=['Recovering Vulkan swapchain'])),
       ('signature', dict(sig='1' * 40)),
       ('variant dir', dict(variant='variant_x')),
       ('GamePatch', dict(extra_lines=['GamePatch: x'])),
       ('DiagB32', dict(extra_lines=['DiagB32 x'])),
       ('TestLogStall', dict(extra_lines=['TestLogStall: x'])),
       ('manifest differ', dict(manifest='manifest cmp DIFFER')),
       ('FixF24 mode absent', dict(drop=['mode_line'])),
       ('FixF24 b24=0', dict(mode_line='FixF24: mode=%s b24=0')),
       ('FixF24 twice', dict(extra_lines=['FixF24: mode=0 b24=1'])),
       ('FixF24 tail', dict(mode_line='FixF24: mode=%s b24=1 x')),
       ('another pad', dict(extra_lines=['Controller 7: "DualSense Wireless Controller" type=PS5'])),
       ('summary absent', dict(drop=['summary'])),
       ('summary twice', dict(extra_lines=['LogAsync: full_waits=0 full_wait_us=0 stalls=0 stall_cut=0 lines=1 bytes=1 max_queued_bytes=1 '
                                           'sync_lines=0 drain_timeouts=0']))]
for tag in ('f24_u0', 'f24_n1'):
    for name, kw in ADM:
        c = default(tag)
        for k, v in kw.items():
            if k == 'drop':
                c['drop'] = set(v)
            elif k == 'mode_line':
                c['mode_line'] = v % c['sp']['fix']
            else:
                c[k] = v
        check('admission %s %s -> NOT_ADMITTED' % (tag, name), word(c) == 'NOT_ADMITTED')
check('admission n1: FixF24 mode=0 at =1', word(mod('f24_n1', mode_line='FixF24: mode=0 b24=1')) == 'NOT_ADMITTED')
check('admission u0: env KYTY_FIX_F24=1 at u0', word(mod('f24_u0', env_over=dict(KYTY_FIX_F24='1'))) == 'NOT_ADMITTED')
check('admission u0: env KYTY_TEST_HIDLOSS=60:pad', word(mod('f24_u0', env_over=dict(KYTY_TEST_HIDLOSS='60:pad'))) == 'NOT_ADMITTED')
check('admission u0: KYTY_REC at a stand tag', word(mod('f24_u0', env_over=dict(KYTY_REC='x'))) == 'NOT_ADMITTED')
check('admission n1: KYTY_TEST_HIDLOSS present', word(mod('f24_n1', env_over=dict(KYTY_TEST_HIDLOSS='60:upd'))) == 'NOT_ADMITTED')
check('admission n1: KYTY_REC absent', word(mod('f24_n1', env_drop=['KYTY_REC'])) == 'NOT_ADMITTED')
check('admission n1: TestHidLoss line', word(mod('f24_n1', extra_lines=['TestHidLoss: armed t_us=1'])) == 'NOT_ADMITTED')
c = default('f24_u0')
c['extra_lines'] = []
c['drop'] = {'mode_line'}
c['extra_lines'] = ['FixF24: mode=0 b24=1']
check('admission u0: FixF24 mode line after the first GuestOut', word(c) == 'NOT_ADMITTED')
STAND_ADM = [('config absent', dict(drop=['config'])),
             ('config edition 1', dict(config='TestHidLoss: config on delay_s=60 mode=upd hold_ms=3000 edition=1 hold_upd_ms=8000 in_ms=100 probe_ms=20 fix_f24=0')),
             ('config fix_f24 1', dict(config='TestHidLoss: config on delay_s=60 mode=upd hold_ms=3000 edition=2 hold_upd_ms=8000 in_ms=100 probe_ms=20 fix_f24=1')),
             ('config delay 61', dict(config='TestHidLoss: config on delay_s=61 mode=upd hold_ms=3000 edition=2 hold_upd_ms=8000 in_ms=100 probe_ms=20 fix_f24=0')),
             ('config hold_upd 7000', dict(config='TestHidLoss: config on delay_s=60 mode=upd hold_ms=3000 edition=2 hold_upd_ms=7000 in_ms=100 probe_ms=20 fix_f24=0')),
             ('config invalid', dict(extra_lines=['TestHidLoss: config invalid value="x"'])),
             ('armed absent', dict(drop=['armed'])),
             ('armed twice', dict(extra_lines=['TestHidLoss: armed t_us=9'])),
             ('attach absent', dict(drop=['attach'])),
             ('attach hwnd 0', dict(attach_line='TestHidLoss: attach index=0 t_us=2000 hwnd=0')),
             ('attach failed', dict(extra_lines=['TestHidLoss: attach failed error="x" t_us=1'])),
             ('test pad absent', dict(drop=['testpad'])),
             ('fire absent', dict(drop=['fire'])),
             ('fire mode wrong', dict(fire_line='TestHidLoss: fire mode=pad t_us=5000')),
             ('fire before the first scene frame', dict(fire_before_scene=True)),
             ('pad probe start absent', dict(drop=['pps'])),
             ('done absent', dict(drop=['done'])),
             ('stat absent', dict(drop=['stat'])),
             ('f24 absent', dict(drop=['f24'])),
             ('f24 malformed', dict(f24_raw='TestHidLoss: f24 mode=upd fix=0 upd_on_main=1')),
             ('f24 wrong mode', dict(f24_raw='TestHidLoss: f24 mode=pad fix=0 ' + ' '.join('%s=1' % k for k in R.F24_KEYS))),
             ('quit inside the window', dict(quit_early=True))]
for name, kw in STAND_ADM:
    c = default('f24_u0')
    for k, v in kw.items():
        if k == 'drop':
            c['drop'] = set(v)
        else:
            c[k] = v
    check('stand admission u0 %s -> NOT_ADMITTED' % name, word(c) == 'NOT_ADMITTED')
check('stand admission p0 title off absent', word(mod('f24_p0', drop=['title'])) == 'NOT_ADMITTED')
check('stand admission x1 quit posted absent', word(mod('f24_x1', drop=['quit_posted'])) == 'NOT_ADMITTED')
check('x1: no summary needed (exit tag)', word(mod('f24_x1', drop=['summary'])) == 'MEMBERS_PASS')
check('x1: no f24 line needed', run(default('f24_x1'))['f24'] is None)

# --- u0 members and edges
check('u0 in_lat 7199999 -> DEAD_CONTROL', word(mod('f24_u0', f24=dict(in_lat_max_us=7199999))) == 'DEAD_CONTROL')
check('u0 in_lat 7200000 -> PASS', word(mod('f24_u0', f24=dict(in_lat_max_us=7200000))) == 'MEMBERS_PASS')
check('u0 upd_on_main 0 -> DEAD_CONTROL', word(mod('f24_u0', f24=dict(upd_on_main=0))) == 'DEAD_CONTROL')
check('u0 main_late 7199999 -> FAIL', word(mod('f24_u0', f24=dict(main_late_max_us=7199999))) == 'MEMBERS_FAIL')
check('u0 main_late 7200000 -> PASS', word(mod('f24_u0', f24=dict(main_late_max_us=7200000))) == 'MEMBERS_PASS')
check('u0 in_pre 50000 -> FAIL', word(mod('f24_u0', f24=dict(in_pre_lat_max_us=50000))) == 'MEMBERS_FAIL')
check('u0 in_pre 49999 -> PASS', word(mod('f24_u0', f24=dict(in_pre_lat_max_us=49999))) == 'MEMBERS_PASS')
r = run(mod('f24_u0', f24=dict(hung_ms=0)))
check('u0 hung 0 -> PASS, window member dropped', r['word'] == 'MEMBERS_PASS' and r['window_member_alive'] is False)
check('u0 hung 1 -> window member alive', run(mod('f24_u0', f24=dict(hung_ms=1)))['window_member_alive'] is True)
r = run(mod('f24_u0', frames_win=[2000000]))
check('u0 frame >= 1 s in window: a row, not a member', r['word'] == 'MEMBERS_PASS' and 'wide 1' in r['row_rc6a'])
check('u0 FixF24 other row', 'init 0' in run(default('f24_u0'))['row_fixf24_other'])
# --- u1 members and edges
for name, kw, w in (('upd_on_main 1', dict(upd_on_main=1), 'MEMBERS_FAIL'), ('jp_update 7199999', dict(jp_update_max_us=7199999), 'MEMBERS_FAIL'),
                    ('jp_update 7200000', dict(jp_update_max_us=7200000), 'MEMBERS_PASS'),
                    ('main_late 100000', dict(main_late_max_us=100000), 'MEMBERS_FAIL'), ('main_late 99999', dict(main_late_max_us=99999), 'MEMBERS_PASS'),
                    ('in_lat 100000', dict(in_lat_max_us=100000), 'MEMBERS_FAIL'), ('in_lat 99999', dict(in_lat_max_us=99999), 'MEMBERS_PASS'),
                    ('hung 1 (alive in u0)', dict(hung_ms=1), 'MEMBERS_FAIL'), ('in_posted != in_seen', dict(in_seen=89), 'MEMBERS_FAIL'),
                    ('pad_seen != posted', dict(pad_seen=379), 'PAD_ONLY_FAIL'),
                    ('p99 +2000', dict(pad_lat_p99_us=19000), 'MEMBERS_PASS'), ('p99 +2001', dict(pad_lat_p99_us=19001), 'PAD_ONLY_FAIL'),
                    ('max +16667', dict(pad_lat_max_us=46667), 'MEMBERS_PASS'), ('max +16668', dict(pad_lat_max_us=46668), 'PAD_ONLY_FAIL'),
                    ('pad and non-pad', dict(pad_lat_max_us=46668, in_lat_max_us=100000), 'MEMBERS_FAIL')):
    check('u1 %s -> %s' % (name, w), word(mod('f24_u1', f24=kw), U0) == w)
check('u1 hung 1 with u0 hung 0 -> member dropped, PASS', word(mod('f24_u1', f24=dict(hung_ms=1)), mod('f24_u0', f24=dict(hung_ms=0))) == 'MEMBERS_PASS')
check('u1 frame 1000000 in the window -> FAIL', word(mod('f24_u1', frames_win=[16000, 1000000]), U0) == 'MEMBERS_FAIL')
check('u1 frame 999999 in the window -> PASS', word(mod('f24_u1', frames_win=[16000, 999999]), U0) == 'MEMBERS_PASS')
check('u1 frame >= 1 s just before fire (wide) -> FAIL', word(mod('f24_u1', frames_pre=[16000] * 10 + [1000000]), U0) == 'MEMBERS_FAIL')
check('u1 frame >= 1 s far before fire -> PASS', word(mod('f24_u1', frames_pre=[1000000] + [16000] * 70), U0) == 'MEMBERS_PASS')
check('u1 frame >= 1 s after the stat line -> PASS', word(mod('f24_u1', frames_post=[1000000] + [16000] * 10), U0) == 'MEMBERS_PASS')
check('u1 hid 0 -> WITNESS_DEAD', word(mod('f24_u1', owner=dict(hid=0, helper=5, msg=5, pump=5, main=1)), U0) == 'WITNESS_DEAD')
check('u1 helper 0 -> WITNESS_DEAD', word(mod('f24_u1', owner=dict(hid=5, helper=0, msg=5, pump=5, main=1)), U0) == 'WITNESS_DEAD')
check('u1 no init_owner -> WITNESS_DEAD', word(mod('f24_u1', drop=['owner']), U0) == 'WITNESS_DEAD')
check('u1 hid = main -> FAIL', word(mod('f24_u1', owner=dict(hid=1, helper=1, msg=1, pump=1, main=1)), U0) == 'MEMBERS_FAIL')
check('u1 hid != helper -> FAIL', word(mod('f24_u1', owner=dict(hid=5, helper=6, msg=5, pump=5, main=1)), U0) == 'MEMBERS_FAIL')
check('u1 pump != hid -> FAIL', word(mod('f24_u1', owner=dict(hid=6, helper=6, msg=5, pump=5, main=1)), U0) == 'MEMBERS_FAIL')
check('u1 msg 0 -> PASS (msg is a number)', word(mod('f24_u1', owner=dict(hid=5, helper=5, msg=0, pump=5, main=1)), U0) == 'MEMBERS_PASS')
check('u1 partner not admitted -> NO_PARTNER', word(default('f24_u1'), mod('f24_u0', installed_sha='0' * 64)) == 'NO_PARTNER')
# --- p1
for name, kw, w in (('p99 +2000', dict(pad_lat_p99_us=19000), 'MEMBERS_PASS'), ('p99 +2001', dict(pad_lat_p99_us=19001), 'PAD_ONLY_FAIL'),
                    ('max +16667', dict(pad_lat_max_us=46667), 'MEMBERS_PASS'), ('max +16668', dict(pad_lat_max_us=46668), 'PAD_ONLY_FAIL')):
    check('p1 %s -> %s' % (name, w), word(mod('f24_p1', f24=kw), P0) == w)
# --- flap admission
for t in ('f24_f1', 'f24_m1'):
    check('%s life_max 50000 -> NOT_ADMITTED:flap' % t, word(mod(t, f24=dict(flap_life_max_us=50000))) == 'NOT_ADMITTED:flap')
    check('%s life_max 49999 -> admitted' % t, run(mod(t, f24=dict(flap_life_max_us=49999)))['admitted'])
    check('%s gap = life_min -> NOT_ADMITTED:flap' % t, word(mod(t, f24=dict(jp_scan_gap_max_us=40000))) == 'NOT_ADMITTED:flap')
    check('%s gap = life_min - 1 -> admitted' % t, run(mod(t, f24=dict(jp_scan_gap_max_us=39999)))['admitted'])
    check('%s both lives 0 -> NOT_ADMITTED:flap' % t, word(mod(t, f24=dict(flap_life_min_us=0, flap_life_max_us=0))) == 'NOT_ADMITTED:flap')
    check('%s flap and another member -> NOT_ADMITTED' % t, word(mod(t, f24=dict(flap_life_max_us=50000), manifest='manifest cmp DIFFER')) == 'NOT_ADMITTED')
check('f0 life_max 50000 -> NOT_ADMITTED:flap', word(mod('f24_f0', f24=dict(flap_life_max_us=50000))) == 'NOT_ADMITTED:flap')
check('f0 gap ignored (gap 99999)', word(mod('f24_f0', f24=dict(jp_scan_gap_max_us=99999))) == 'REFERENCE')
check('f1 opened != attached -> FAIL', word(mod('f24_f1', f24=dict(opened=59))) == 'MEMBERS_FAIL')
check('f1 death in stdout -> FAIL', word(mod('f24_f1', stdout=['--- Fatal Error ---'])) == 'MEMBERS_FAIL')
check('f1 death in log -> FAIL', word(mod('f24_f1', extra_lines=['Unhandled exception: x'])) == 'MEMBERS_FAIL')
check('f1 open_failed is a row', word(mod('f24_f1', f24=dict(open_failed=3))) == 'MEMBERS_PASS')
# --- x1
check('x1 no pump_stop_expired -> FAIL', word(mod('f24_x1', drop=['expired'])) == 'MEMBERS_FAIL')
check('x1 exit code 1 -> FAIL', word(mod('f24_x1', hold_exit=1)) == 'MEMBERS_FAIL')
check('x1 process lived -> FAIL', word(mod('f24_x1', hold_exit=None)) == 'MEMBERS_FAIL')
check('x1 jp_task ran after expired -> FAIL', word(mod('f24_x1', ran_after=True)) == 'MEMBERS_FAIL')
check('x1 jp_task ran before expired -> PASS', word(mod('f24_x1', expired_before_ran=False)) == 'MEMBERS_PASS')
check('x1 exit 13.0 -> PASS', word(mod('f24_x1', quit_mark=dict(exit_upper_s=13.0))) == 'MEMBERS_PASS')
check('x1 exit 13.001 -> FAIL', word(mod('f24_x1', quit_mark=dict(exit_upper_s=13.001))) == 'MEMBERS_FAIL')
check('x1 no quit mark -> NOT_EVALUABLE', word(mod('f24_x1', quit_mark={})) == 'NOT_EVALUABLE')
# --- d1
check('d1 removed absent -> FAIL', word(mod('f24_d1', drop=['removed'])) == 'MEMBERS_FAIL')
check('d1 removed of another id -> FAIL', word(mod('f24_d1', removed_id=3)) == 'MEMBERS_FAIL')
check('d1 jp_tasks 0 -> FAIL', word(mod('f24_d1', f24=dict(jp_tasks=0))) == 'MEMBERS_FAIL')
check('d1 frame >= 1 s in the window -> FAIL', word(mod('f24_d1', frames_win=[1000000])) == 'MEMBERS_FAIL')
# --- mutants
check('m1 opened = attached -> NOT_CAUGHT', word(mod('f24_m1', f24=dict(opened=60))) == 'NOT_CAUGHT')
check('m1 opened = attached - 1 -> CAUGHT', word(mod('f24_m1', f24=dict(opened=59))) == 'CAUGHT')
check('m2 no ran after -> NOT_CAUGHT', word(mod('f24_m2', expired_before_ran=False)) == 'NOT_CAUGHT')
check('m2 no expired -> NOT_EVALUABLE', word(mod('f24_m2', drop=['expired'])) == 'NOT_EVALUABLE')
check('m4 jp_tasks 1 -> NOT_CAUGHT', word(mod('f24_m4', f24=dict(jp_tasks=1))) == 'NOT_CAUGHT')
for name, kw in (('upd_on_main 1', dict(upd_on_main=1, main_late_max_us=20000, in_lat_max_us=20000)),
                 ('main_late 100000', dict(upd_on_main=0, main_late_max_us=100000, in_lat_max_us=20000)),
                 ('in_lat 100000', dict(upd_on_main=0, main_late_max_us=20000, in_lat_max_us=100000))):
    check('m5 %s -> CAUGHT' % name, word(mod('f24_m5', f24=kw)) == 'CAUGHT')
check('m5 all u1 members hold -> NOT_CAUGHT', word(mod('f24_m5', f24=dict(upd_on_main=0, main_late_max_us=99999, in_lat_max_us=99999))) == 'NOT_CAUGHT')
check('m6 helper = main only -> CAUGHT', word(mod('f24_m6', owner=dict(hid=5, helper=1, msg=5, pump=5, main=1))) == 'CAUGHT')
check('m6 hid = main only -> CAUGHT', word(mod('f24_m6', owner=dict(hid=1, helper=5, msg=5, pump=5, main=1))) == 'CAUGHT')
check('m6 hid = helper = pump -> NOT_CAUGHT', word(mod('f24_m6', owner=dict(hid=5, helper=5, msg=5, pump=5, main=1))) == 'NOT_CAUGHT')
check('m6 no init_owner -> NOT_EVALUABLE', word(mod('f24_m6', drop=['owner'])) == 'NOT_EVALUABLE')
# --- n1
for name, kw, w in (('video 2999', dict(idx=2999), 'MEMBERS_FAIL'), ('video 3000', dict(idx=3000), 'MEMBERS_PASS'),
                    ('glitch 1', dict(glitch='one-frame glitches: 1'), 'MEMBERS_FAIL'), ('no glitch file', dict(glitch=None), 'MEMBERS_FAIL'),
                    ('no sheet', dict(sheet=None), 'MEMBERS_FAIL'), ('frame 1000000', dict(frames_post=[100000] * 3000 + [1000000]), 'MEMBERS_FAIL'),
                    ('frame 999999', dict(frames_post=[999999] + [100000] * 3000), 'MEMBERS_PASS'),
                    ('death stdout', dict(stdout=['GpuHangAbort: x']), 'MEMBERS_FAIL'),
                    ('lived no', dict(json=dict(attempt=dict(hold_exit=3))), 'MEMBERS_FAIL'),
                    ('init after GuestOut', dict(init_before_guest=False), 'MEMBERS_FAIL'),
                    ('hid 0', dict(owner=dict(hid=0, helper=5, msg=5, pump=5, main=1)), 'WITNESS_DEAD'),
                    ('hid = main', dict(owner=dict(hid=1, helper=1, msg=1, pump=1, main=1)), 'MEMBERS_FAIL')):
    check('n1 %s -> %s' % (name, w), word(mod('f24_n1', **kw)) == w)
# hold: scene frames sum 300 s exactly / one us less
c = mod('f24_n1', frames_pre=[], frames_win=[], frames_post=[100000] * 3000)
check('n1 hold 300.0 s -> PASS', word(c) == 'MEMBERS_PASS')
c = mod('f24_n1', frames_pre=[], frames_win=[], frames_post=[100000] * 2999 + [99999])
check('n1 hold 299.999999 s -> FAIL', word(c) == 'MEMBERS_FAIL')
r = run(mod('f24_n1', extra_lines=['FixF21: wait_expired']))
check('n1 wait_expired -> form member NO, members word unchanged', r['form_ok'] is False and r['word'] == 'MEMBERS_PASS')
# --- windows function edges
fr = [(1, 1, 400000), (2, 2, 400000), (3, 3, 300000), (4, 4, 100000), (10, 5, 16000), (20, 6, 16000)]
wide, strict = R.windows(fr, 5, 15)
check('windows strict = frames between fire and stat', strict == {4})
check('windows wide takes back while the sum after <= 1 s (frame 0 in: 800 000 after it)', wide == {0, 1, 2, 3, 4})
fr2 = [(1, 1, 16000), (2, 2, 600000), (3, 3, 500000), (4, 4, 16000), (10, 5, 16000)]
check('windows wide stops when the sum after > 1 s (frame 0 out: 1 116 000 after it)', R.windows(fr2, 5, 15)[0] == {1, 2, 3, 4})
check('windows None without fire', R.windows(fr, None, 15) == (None, None))
# --- partner_read picks the admitted of the family
PR = tempfile.mkdtemp(prefix='t40cp_')
for name, adm in (('f24_u0', False), ('f24_u0_r1', True), ('f24_u0_r2', False)):
    os.makedirs(os.path.join(PR, name))
    json.dump(dict(tag=name, admitted=adm), open(os.path.join(PR, name, 'read.json'), 'w'))
check('partner_read picks the admitted f24_u0_r1', (R.partner_read('f24_u0', PR) or {}).get('tag') == 'f24_u0_r1')
check('partner_read none admitted -> None', R.partner_read('f24_p0', PR) is None)
# --- tag names
for t, ok in (('f24_u0', True), ('f24_u1b', True), ('f24_f1_r2', True), ('f24_f1_r3', False), ('f24_c0', False), ('f24_m3', False),
              ('f24_n1_r1', True), ('f25_v', False)):
    check('tag name %s %s' % (t, ok), (R.base_of(t) is not None) == ok)
# --- rows, table, json, cp1250 output of the script
d = os.path.join(TMP, 'cli')
build(default('f24_u0'), d)
out = os.path.join(TMP, 'cli.json')
env = dict((k, v) for k, v in os.environ.items() if k not in ('PYTHONIOENCODING', 'PYTHONUTF8'))
pr = subprocess.run([sys.executable, TARGET, '--dir', d, '--tag', 'f24_u0', '--json', out], capture_output=True, env=env)
check('cli rc 0 (%s)' % pr.stderr[-200:], pr.returncode == 0)
try:
    pr.stdout.decode('cp1250', 'strict')
    okc = all(b < 128 for b in pr.stdout)
except UnicodeDecodeError:
    okc = False
check('cli output strict cp1250 and ASCII', okc)
check('cli json word', json.load(open(out)).get('word') == 'MEMBERS_PASS')
rd = os.path.join(TMP, 'runs')
os.makedirs(os.path.join(rd, 'f24_u0'))
shutil.copy(out, os.path.join(rd, 'f24_u0', 'read.json'))
pt = subprocess.run([sys.executable, TARGET, '--table', '--runs', rd], capture_output=True, env=env)
check('table rc 0 and the row', pt.returncode == 0 and b'| f24_u0 | ddf0ca91 | ADMITTED | MEMBERS_PASS |' in pt.stdout)
check('rows ASCII', all(all(ord(ch) < 128 for ch in l) for l in R.rows_out(run(default('f24_n1')))))
shutil.rmtree(TMP, ignore_errors=True)
shutil.rmtree(PR, ignore_errors=True)
print('checks %d failed %d' % (CHECKS[0], CHECKS[1]))
print('ALL OK' if CHECKS[1] == 0 else 'FAILED')
sys.exit(0 if CHECKS[1] == 0 else 1)

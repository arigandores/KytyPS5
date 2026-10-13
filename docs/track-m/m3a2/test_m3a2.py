"""Track M link M3a2 (HPP-861): fixtures of the harness of the series M3 of wave 2 (port of M3a test_m3a.py) - the tag table (go_m3a2.sh
dry run = m3a2_read.plan_line, every tag of the seal section 3 and the theme arms; unknown tags refused by both), the cache dirs of the
plans, the reader on the MS1 support log of M3a m3_sg_v_r1 read as the G5 arm m3w2_g5_a1 (admitted, members ALL YES; negative controls
of each admission member the harness writes; read as MS2 - refused by binary and signature), the W members on the MS1 W log m3_sg_w of
M3a, the track M pass scan_m with the T125 lines and the T125 members on synthetic logs (each member and edge, item 790 (b)), the G5
measure, the words of g5_m3a2.py on the edges +1.0 % / -1.0 %, kset_m3a2.py cmp4, the G7 selector of the M3a MS1 logs, the theme arm
gate of launch_m3a2.sh, and the cp1250 output of the tools.  First line: suite / target sha256; last line ALL OK.  Refuses under the
lock (exit 3) and with the stop file (exit 4).  usage: python test_m3a2.py"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP - exit 4')
    sys.exit(4)
G = 'C:/kyty/m657/m3a2'
sys.path.insert(0, G)
import m3a2_read as M  # noqa: E402

A = 'C:/kyty/m657/m3a'
BASH = 'C:/Program Files/Git/bin/bash.exe'
FAILS = []
N = [0]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond, val=''):
    N[0] += 1
    print('[%s] %s %s' % ('ok' if cond else 'FAIL', name, str(val)[:200]))
    if not cond:
        FAILS.append(name)


TAGS = ['m3w2_i'] + ['m3w2_%s_%s' % (L, k) for L in ('sg', 'hb', 'mg') for k in ('w', 'v')] + \
    ['m3w2_g5_ap', 'm3w2_g5_a1', 'm3w2_g5_b1', 'm3w2_g5_b2', 'm3w2_g5_a2', 'm3w2_g6',
     'm3w2_sg_t1250', 'm3w2_hb_t1250w', 'm3w2_g5_t1250', 'm3w2_mg_t3060p', 'm3w2_mg_t3060', 'm3w2_mg_t3060w', 'm3w2_g5_t3060p',
     'm3w2_g5_t3060', 'm3w2_sg_v_r1', 'm3w2_g5_a1_r2']
BAD = ['m3w2_x', 'm3w2_sg_f', 'm3w2_ac_v', 'm3_sg_v', 'm3w2_g5_t1250w', 'm3w2_g5_t1250p', 'm3w2_sg_t1250p', 'm3w2_g5_t3060w',
       'm3w2_sg_t2330', 'm3w2_g6_t1250', 'm3w2_i_r4']


def dry(tag):
    env = dict(os.environ, M3A2_DRYRUN='1')
    r = subprocess.run([BASH, G + '/go_m3a2.sh', tag], capture_output=True, env=env)
    lines = [l for l in r.stdout.decode('ascii', 'replace').splitlines() if l.startswith('dryrun ')]
    return r.returncode, lines[0] if lines else None


def parse_dry(line):
    w = line.split()
    d = {}
    for k in ('bin', 'level', 'kind', 'sd', 'timeout', 'hold', 'cache', 'save'):
        d[k] = w[w.index(k) + 1]
    knob = [x for x in w if x.startswith('KYTY_M_T')]
    patch = any(x.startswith('KYTY_GAME_PATCH=') for x in w)
    return 'bin %s level %s kind %s sd %s timeout %s hold %s cache %s save %s knob %s patch %d' % (
        d['bin'], d['level'], d['kind'], d['sd'], d['timeout'], d['hold'], d['cache'], d['save'], knob[0] if knob else '-',
        1 if patch else 0)


def plan_table():
    for t in TAGS:
        rc, line = dry(t)
        pl = M.plan_line(t)
        check('plan %s: go dry run = reader plan' % t, rc == 0 and line is not None and parse_dry(line) == pl,
              '%s | %s' % (parse_dry(line) if line else rc, pl))
    for t in BAD:
        rc, line = dry(t)
        check('plan %s: refused by go (rc 2) and the reader (None)' % t, rc == 2 and line is None and M.plan_line(t) is None, rc)
    D0 = 'variant_fixb26_fixb1b_fixf10_fixf19'
    check('dir of MS2 defaults = ..._mw1_3b', M.dir_of(M.plan_of('m3w2_sg_v')) == D0 + '_mw1_3b', M.dir_of(M.plan_of('m3w2_sg_v')))
    check('dir of the T306 arm = ..._mw1_33', M.dir_of(M.plan_of('m3w2_mg_t3060')) == D0 + '_mw1_33')
    check('dir of MS1 = ..._mw1_33', M.dir_of(M.plan_of('m3w2_g5_a1')) == D0 + '_mw1_33')
    check('T125 arm keeps mask 0x3b, MT125 want 0, MT265 want 1', M.mask_of(M.plan_of('m3w2_sg_t1250')) == 0x3b and
          M.hle_want(M.plan_of('m3w2_sg_t1250'), '125') == 0 and M.hle_want(M.plan_of('m3w2_sg_t1250'), '265') == 1)
    check('MS1 plan: MT125 want None (0 lines member)', M.hle_want(M.plan_of('m3w2_g5_a1'), '125') is None)
    check('signatures: MS2 0d2da32c, MS1 8dcf3177', M.SIG['ms2'].startswith('0d2da32c') and M.SIG['ms1'].startswith('8dcf3177'))
    check('REF_OPENED = 3 (the support log m3_sg_v_r1, comment of HPP-861 06:53Z)', M.REF_OPENED == 3)


def fixture(d, plan_txt, src='m3_sg_v_r1', inst=M.MS1, level='underwater_aerial_garden'):
    os.makedirs(d, exist_ok=True)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha',
                                                         'level', 'sheet', 'plan', 'k0_cmp', 'base_cmp'))
    p.update(log=os.path.join(A, 'log_%s.txt' % src), stdout=os.path.join(A, 'stdout_%s.txt' % src), run=os.path.join(A, '%s.json' % src),
             idx=os.path.join(A, 'rec_%s.mp4.idx' % src), seal=os.path.join(A, 'pred.md'))
    for nm, v in (('installed_before', M.MS1), ('installed_after', M.MS1), ('installed_sha', inst),
                  ('manifest_cmp', 'manifest cmp EQUAL files 1 listsha x'), ('level', level),
                  ('sheet', 'sheet x.png 16 frames'), ('plan', plan_txt), ('k0_cmp', 'KSET EQUAL4 files 1; GLCache row'),
                  ('base_cmp', 'manifest cmp EQUAL files 1')):
        open(p[nm], 'w', encoding='ascii').write(v + '\n')
    g = os.path.join(A, 'runs', src, 'glitch.txt')
    shutil.copyfile(g, p['glitch']) if os.path.exists(g) else open(p['glitch'], 'w').write('one-frame glitches: 0 of 1\n')
    return p


def reader(tmp):
    pl = 'ms1 %s KA none v' % M.MS1
    p = fixture(os.path.join(tmp, 'a'), pl)
    r = M.read_tag('m3w2_g5_a1', p)
    bad = [a for a, b in r['admission'] if not b]
    check('m3_sg_v_r1 (MS1) as m3w2_g5_a1: ADMITTED', r['admitted'], bad)
    check('m3_sg_v_r1 as m3w2_g5_a1: members ALL YES (MT125 0 lines at MS1)', r['ok'] is True, [a for a, b in (r['members'] or []) if not b])
    check('m3_sg_v_r1 as m3w2_g5_a1: form FS15 ALL YES', r['form_ok'] is True, [a for a, b in (r['form'] or []) if not b])
    check('m3_sg_v_r1: no T125 members on a G5 arm', r.get('t125_ok') is None, r.get('t125_ok'))
    t1 = (r.get('info') or {}).get('t125') or {}
    check('m3_sg_v_r1 T125 rows: opened 3 (= REF_OPENED), failures 0, FixF8 1, MT125 none', t1.get('opened') == 3 and
          t1.get('open_failed') == 0 and t1.get('init_failed') == 0 and t1.get('fixf8') == 1 and t1.get('mt125') == [], t1)
    check('m3_sg_v_r1: G5 measure end A n > 0 and end B n >= end A n', r['g5'] and r['g5']['end_a']['n'] > 0 and
          r['g5']['end_b']['n'] >= r['g5']['end_a']['n'], r['g5'])
    neg = (('plan', 'ms1 %s K0 none v' % M.MS1, 'plan of go'), ('k0_cmp', 'KSET DIFFER4 only-a 1', 'K0'),
           ('installed_sha', M.MS2, 'installed during'), ('installed_after', M.MS2, 'before = after'),
           ('installed_before', M.MS2, 'before = after'),
           ('manifest_cmp', 'manifest cmp DIFFER', 'caches returned'), ('level', 'hoover_beach', 'guest args'),
           ('base_cmp', 'manifest cmp DIFFER', 'live caches of the run = KA'))
    for i, (nm, val, member) in enumerate(neg):
        q = fixture(os.path.join(tmp, 'n%d' % i), pl)
        open(q[nm], 'w', encoding='ascii').write(val + '\n')
        r = M.read_tag('m3w2_g5_a1', q)
        bad = [a for a, b in r['admission'] if not b]
        check('negative %s=%s: NOT_ADMITTED by "%s"' % (nm, val[:20], member), not r['admitted'] and any(member in a for a in bad), bad[:2])
    q = fixture(os.path.join(tmp, 'm'), 'ms2 %s K1 K1 v' % M.MS2, inst=M.MS2)
    r = M.read_tag('m3w2_sg_v', q)
    bad = [a for a, b in r['admission'] if not b]
    check('MS1 log read as MS2 m3w2_sg_v: NOT_ADMITTED by json binary and signature', not r['admitted'] and
          any('json binary_sha256' in a for a in bad) and any('translation signature' in a for a in bad), bad[:3])
    q = fixture(os.path.join(tmp, 'b'), pl)
    js = json.load(open(q['run'], encoding='utf-8'))
    js['env']['KYTY_M_T125'] = '0'
    q['run'] = os.path.join(tmp, 'b', 'es.json')
    json.dump(js, open(q['run'], 'w', encoding='utf-8'))
    r = M.read_tag('m3w2_g5_a1', q)
    check('negative env extra KYTY_M_T125: NOT_ADMITTED by env', not r['admitted'] and any('env = the form' in a for a, b in r['admission']
                                                                                           if not b))
    save = M.plan_of
    try:
        M.plan_of = lambda t: dict(save('m3w2_sg_w'), bin='ms1') if t == 'm3w2_sg_w' else save(t)
        q = fixture(os.path.join(tmp, 'w'), 'ms1 %s K1 K1 w' % M.MS1, src='m3_sg_w')
        r = M.read_tag('m3w2_sg_w', q)
        bad = [a for a, b in r['admission'] if not b]
        check('m3_sg_w (MS1 W) with an MS1 W plan: ADMITTED', r['admitted'], bad)
        check('m3_sg_w: W members ALL YES (0 [Vulkan][E], [Vulkan][W] > 0, DualSrcBlend, MS1 0 MT125 lines)', r['ok'] is True,
              [a for a, b in (r['members'] or []) if not b])
    finally:
        M.plan_of = save


def synth_log(path, mask=b'0x3b', t125=b'1', stats=((47, 27),), opened=4, open_failed=0, init_failed=0, in_failed=0, f8=1, astat=()):
    with open(path, 'wb') as f:
        f.write(b'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19_mw1_3b\n')
        f.write(b'MWave1: mask=' + mask + b' T234=1 T233=1 T256=0 T306=1 T032=1 T203=1\n')
        f.write(b'MT265: mode=1\nMT272: mode=1\nMT231: mode=1\n')
        if t125 is not None:
            f.write(b'MT125: mode=' + t125 + b'\n')
        for k in range(f8):
            f.write(b'FixF8: mode=1\n')
        for k in range(opened):
            f.write(b'AudioOut: opened SDL device "x" (48000 Hz, 2 ch, format 0x8120)\n')
        for k in range(open_failed):
            f.write(b'AudioOut: SDL_OpenAudioDevice failed: x\n')
        for k in range(init_failed):
            f.write(b'AudioOut: SDL audio init failed: x\n')
        for k in range(in_failed):
            f.write(b'AudioIn: SDL init failed: x\n')
        for v in astat:
            f.write(b'AudioStat: t_us=1 port=1 dev=2 status=1 queued=0 pushes=3 q_fail=0 init_calls=%d acq=5\n' % v)
        f.write(b'GuestOut: Level has started: underwater_aerial_garden\n')
        for n in range(1, 2001):
            f.write(b'FrameTrace: n=%d dt_us=%d draws=150\n' % (n, 20000 if n <= 1500 else 40000))
            if n == 1800:
                f.write(b'Event: quit\n')
        for a, b in stats:
            f.write(b'MT125Stat: when=exit mixed=%d mixed_nz=%d\n' % (a, b))


def _mk(tmp, name, **kw):
    q = os.path.join(tmp, name + '.log')
    synth_log(q, **kw)
    return q


def synth(tmp):
    lg = os.path.join(tmp, 'syn.log')
    synth_log(lg)
    y = M.scan_m(lg)
    p = M.plan_of('m3w2_sg_v')
    check('scan_m: MWave1 0x3b, MT125 [1], MT125Stat [(47, 27)], opened 4, FixF8 1', y['mw'] == [0x3b] and y['mt']['125'] == [1] and
          y['mts'] == [(47, 27)] and y['opened'] == 4 and y['f8'] == 1, (y['mw'], y['mt']['125'], y['mts'], y['opened']))
    mm = M.m_members(p, y)
    check('m_members MS2 defaults ALL YES', all(b for a, b in mm), [a for a, b in mm if not b])
    tm = M.t125_members(p, y)
    check('t125 members ALL YES on the good log (Q2 A)', all(b for a, b in tm), [a for a, b in tm if not b])
    cases = (
        ('opened 3 (= support, the mix device missing)', dict(opened=3), 'opened SDL device'),
        ('opened 5', dict(opened=5), 'opened SDL device'),
        ('mixed_nz 0', dict(stats=((47, 0),)), 'mixed_nz'),
        ('two MT125Stat lines', dict(stats=((47, 27), (1, 1))), 'exactly one line'),
        ('no MT125Stat line', dict(stats=()), 'exactly one line'),
        ('MT125 mode=0', dict(t125=b'0'), 'MT125: mode=1'),
        ('no MT125 line', dict(t125=None), 'MT125: mode=1'),
        ('one SDL_OpenAudioDevice failed', dict(open_failed=1), 'SDL_OpenAudioDevice failed'),
        ('one SDL audio init failed', dict(init_failed=1), 'SDL_OpenAudioDevice failed'),
        ('item 790 (b)(1): no FixF8 line', dict(f8=0), 'FixF8: mode=1'),
    )
    for i, (nm, kw, member) in enumerate(cases):
        q = os.path.join(tmp, 's%d.log' % i)
        synth_log(q, **kw)
        tm = M.t125_members(p, M.scan_m(q))
        bad = [a for a, b in tm if not b]
        check('t125 negative %s: NO in "%s"' % (nm, member), len(bad) >= 1 and any(member in a for a in bad), bad[:2])
    check('t125: FixF8 member reads 2 lines as YES', [b for a, b in M.t125_members(p, M.scan_m(_mk(tmp, 'f8x2', f8=2)))
                                                     if 'FixF8' in a] == [True])
    check('t125: no init_calls member left (item 790 (b): not measured)', not any('init_calls of the AudioStat' in a for a, b in tm))
    for nm, kw, want in (('clean', dict(), True), ('AudioOut init failed', dict(init_failed=1), False),
                         ('AudioIn init failed', dict(in_failed=1), False), ('both', dict(init_failed=2, in_failed=1), False),
                         ('AudioStat init_calls 2 only (not a member)', dict(astat=(2,)), True)):
        a, b = M.audio_init_member(M.scan_m(_mk(tmp, 'ai_' + str(abs(hash(nm)) % 10000), **kw)))
        check('item 790 (b)(2) audio init member, %s -> %s' % (nm, want), b is want and 'item 790 (b)(2)' in a, a)
    pa = M.plan_of('m3w2_g5_ap')
    check('item 790 (a): m3w2_g5_ap = MS1 V 330 s on K0 saved as KA, a reference tag', pa['bin'] == 'ms1' and pa['kind'] == 'v' and
          pa['hold'] == 330 and pa['cache'] == 'K0' and pa['save'] == 'KA' and M.REF_TAGS == ('m3w2_g5_ap',), pa)
    p1 = M.plan_of('m3w2_g5_a1')
    q = os.path.join(tmp, 'ms1.log')
    synth_log(q, mask=b'0x33')
    mm = M.m_members(p1, M.scan_m(q))
    check('m_members MS1: an MT125 line is a NO, mask 0x33 YES', mm[0][1] and any('0 lines MT125' in a and not b for a, b in mm),
          [a for a, b in mm if not b])
    mm = M.m_members(p, M.scan_m(q))
    check('m_members MS2 on a 0x33 log: MWave1 NO', not mm[0][1])
    R = M.load_r('underwater_aerial_garden')
    x = R.scan(lg)
    g = M.g5_measure(x, R)
    check('G5 end B: rows n 1502..2000, mean 40000', g['end_b']['n'] == 499 and g['end_b']['mean'] == 40000.0, g['end_b'])
    check('G5 end A: rows before Event: quit (n <= 1800) - 299 rows', g['end_a']['n'] == 299 and g['end_a']['mean'] == 40000.0, g['end_a'])


def g5_words(tmp):
    rd = os.path.join(tmp, 'g5runs')

    def put(t, mean, adm=True):
        os.makedirs(os.path.join(rd, t), exist_ok=True)
        json.dump(dict(admitted=adm, bin='x', ok=True, g5=dict(end_a=dict(n=1000, mean=mean, sd=100.0, se=3.0),
                                                                end_b=dict(n=1001, mean=mean, sd=100.0, se=3.0))),
                  open(os.path.join(rd, t, 'read.json'), 'w'))

    def word(a1, b1, b2, a2, adm=True, culprit=False):
        put('m3w2_g5_a1', a1)
        put('m3w2_g5_b1', b1, adm)
        put('m3w2_g5_b2', b2)
        put('m3w2_g5_a2', a2)
        r = subprocess.run([sys.executable, G + '/g5_m3a2.py', '--runs', rd] + (['--culprit'] if culprit else []), capture_output=True)
        out = r.stdout.decode('ascii').splitlines()
        return [l for l in out if l.startswith('G5 WORD')][0], out
    check('G5 delta exactly +1.0 % -> NOT_WORSE', 'end A NOT_WORSE' in word(30000, 30300, 30300, 30000)[0], '')
    check('G5 delta +1.01 % -> FAIL', 'end A FAIL' in word(30000, 30303, 30303, 30000)[0], '')
    check('G5 delta -1.0 % -> NOT_WORSE (BETTER)', 'end A NOT_WORSE (BETTER' in word(30000, 29700, 29700, 30000)[0], '')
    check('G5 an arm not admitted -> NOT_EVALUABLE', 'end A NOT_EVALUABLE' in word(30000, 30000, 30000, 30000, adm=False)[0], '')
    put('m3w2_g5_t1250', 30150)
    w, out = word(30000, 30303, 30303, 30000, culprit=True)
    cl = [l for l in out if l.startswith('CULPRIT ARM')]
    check('G5 culprit rows: T125 arm +0.5000 %, T306 arm NOT_EVALUABLE', len(cl) == 2 and '+0.5000 %' in cl[0] and
          'm3w2_g5_t1250' in cl[0] and 'NOT_EVALUABLE' in cl[1] and 'm3w2_g5_t3060' in cl[1], cl)


def kset(tmp):
    a = os.path.join(tmp, 'a.tsv')
    b = os.path.join(tmp, 'b.tsv')
    open(a, 'w').write('GLCache\tx\t1\taa\n_ShaderCache\ty\t1\tbb\n')
    open(b, 'w').write('GLCache\tz\t1\tcc\n_ShaderCache\ty\t1\tbb\n')
    r = subprocess.run([sys.executable, G + '/kset_m3a2.py', 'cmp4', a, b], capture_output=True)
    check('kset: GLCache differs only -> EQUAL4 rc 0', r.returncode == 0 and r.stdout.startswith(b'KSET EQUAL4'), r.stdout[:60])
    open(b, 'w').write('GLCache\tx\t1\taa\n_ShaderCache\ty\t1\tbX\n')
    r = subprocess.run([sys.executable, G + '/kset_m3a2.py', 'cmp4', a, b], capture_output=True)
    check('kset: _ShaderCache differs -> DIFFER4 rc 1', r.returncode == 1 and r.stdout.startswith(b'KSET DIFFER4'), r.stdout[:60])


def g7_selector():
    sys.argv = ['x']
    import g7_m3a2 as S7  # noqa: E402
    sel = S7.m3a_ms1
    yes = ['m3_i', 'm3_sg_v', 'm3_sg_v_r1', 'm3_sg_w', 'm3_g5_b1', 'm3_g6', 'm3_sg_t2310', 'm3_f2_w']
    no = ['m3_sg_f', 'm3_f2_f', 'm3_g5_a1', 'm3_g5_a2']
    check('G7 MS1 baseline selector: MS1 tags of M3a in', all(sel('C:/kyty/m657/m3a/log_%s.txt' % t) == t for t in yes))
    check('G7 MS1 baseline selector: FS15 tags of M3a out', all(sel('C:/kyty/m657/m3a/log_%s.txt' % t) is None for t in no))
    check('G7 tag_of: m3w2 tags only', S7.tag_of('C:/kyty/m657/m3a2/log_m3w2_sg_v.txt') == 'm3w2_sg_v' and
          S7.tag_of('C:/kyty/m657/m3a2/log_m3_sg_v.txt') is None)
    check('G7 support logs exist (sg hb mg)', all(os.path.exists('%s/log_%s.txt' % (A, t)) for t in S7.SUPPORT.values()), S7.SUPPORT)
    check('G7 M3a loglist and segments exist', os.path.exists(A + '/g7/loglist_f32a.tsv') and os.path.isdir(A + '/g7/seg'))


def launch_gate(tmp):
    env = dict(os.environ, M3A2_DRYRUN='2', M3A2_DISP_SKIP='1', M3A2_QUEUE_SKIP='1', M3A2_TIMES=os.path.join(tmp, 'times.txt'))
    env.pop('M3A2_ARM_OK', None)
    env.pop('M3A2_REPEAT_OK', None)
    r = subprocess.run([BASH, G + '/launch_m3a2.sh', 'm3w2_sg_t1250'], capture_output=True, env=env)
    check('launch: theme arm without M3A2_ARM_OK -> exit 12', r.returncode == 12, r.returncode)
    r = subprocess.run([BASH, G + '/launch_m3a2.sh', 'm3w2_sg_t1250'], capture_output=True, env=dict(env, M3A2_ARM_OK='1'))
    check('launch: theme arm with M3A2_ARM_OK=1 -> dryrun2 rc 0', r.returncode == 0 and b'dryrun2' in r.stdout, (r.returncode, r.stdout[-80:]))
    r = subprocess.run([BASH, G + '/launch_m3a2.sh', 'm3w2_sg_v_r1'], capture_output=True, env=env)
    check('launch: repeat without M3A2_REPEAT_OK -> exit 11', r.returncode == 11, r.returncode)
    r = subprocess.run([BASH, G + '/launch_m3a2.sh', 'm3w2_sg_v'], capture_output=True, env=env)
    check('launch: a seal tag -> dryrun2 rc 0', r.returncode == 0 and b'dryrun2' in r.stdout, (r.returncode, r.stdout[-80:]))
    r = subprocess.run([BASH, G + '/launch_m3a2.sh', 'm3w2_zz'], capture_output=True, env=env)
    check('launch: unknown tag -> exit 2', r.returncode == 2, r.returncode)
    for t, w in (('m3w2_hb_w', b'plan-w yes'), ('m3w2_hb_v', b'plan-w no')):
        r = subprocess.run([BASH, G + '/post_m3a2.sh', t], capture_output=True, env=dict(os.environ, M3A2_POST_PLANONLY='1'))
        check('post plan-only %s: %s' % (t, w.decode()), r.returncode == 0 and w in r.stdout, r.stdout[-60:])


def cp1250():
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    for args, rc in ((['m3a2_read.py', '--plan', 'm3w2_g6'], 0), (['m3a2_read.py', '--table'], 0), (['g5_m3a2.py'], 0),
                     (['g7_m3a2.py'], 2)):
        r = subprocess.run([sys.executable, G + '/' + args[0]] + args[1:], capture_output=True, env=env)
        check('cp1250 strict output of %s: rc %d, no UnicodeEncodeError' % (' '.join(args), rc), r.returncode == rc and
              b'UnicodeEncodeError' not in r.stderr, (r.returncode, r.stderr[-120:]))


def main():
    me = os.path.abspath(__file__)
    print('suite test_m3a2.py sha256 %s target m3a2_read.py sha256 %s go_m3a2.sh sha256 %s g5_m3a2.py sha256 %s kset_m3a2.py sha256 %s '
          'g7_m3a2.py sha256 %s launch_m3a2.sh sha256 %s' % (
              sha(me), sha(G + '/m3a2_read.py'), sha(G + '/go_m3a2.sh'), sha(G + '/g5_m3a2.py'), sha(G + '/kset_m3a2.py'),
              sha(G + '/g7_m3a2.py'), sha(G + '/launch_m3a2.sh')))
    tmp = tempfile.mkdtemp(prefix='m3a2_fx_', dir=os.environ.get('PAPERCLIP_RUN_SCRATCH_DIR') or None)
    try:
        plan_table()
        reader(tmp)
        synth(tmp)
        g5_words(tmp)
        kset(tmp)
        g7_selector()
        launch_gate(tmp)
        cp1250()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('checks %d, failed %d %s' % (N[0], len(FAILS), FAILS[:10]))
    print('ALL OK' if not FAILS else 'FAILED')
    return 0 if not FAILS else 1


if __name__ == '__main__':
    sys.exit(main())

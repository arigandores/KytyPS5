"""Track M link M3a (HPP-842): fixtures of the harness of the series M3 - the tag table (go_m3a.sh dry run = m3a_read.plan_line, every
tag of the seal section 3 and the theme arms; unknown tags refused by both), the reader m3a_read.py on the logs of FS15c (fs15_v as the
FS15 sheet arm m3_sg_f: admitted, members ALL YES; negative controls of each admission member the harness writes), the W members on
fs15_w, the track M pass scan_m and the G5 measure on synthetic logs, the words of g5_m3a.py on the edges +1.0 % / -1.0 %, kset_m3a.py
cmp4, and the cp1250 output of the tools.  First line: suite / target sha256; last line ALL OK.  Refuses under the lock (exit 3) and
with the stop file (exit 4).  usage: python test_m3a.py"""
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
G = 'C:/kyty/m657/m3a'
sys.path.insert(0, G)
import m3a_read as M  # noqa: E402

F = 'C:/kyty/f287/fs15c'
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


TAGS = ['m3_i'] + ['m3_%s_%s' % (L, k) for L in ('sg', 'hb', 'mg', 'ac', 'f1', 'f2') for k in ('w', 'v', 'f')] + \
    ['m3_g5_a1', 'm3_g5_b1', 'm3_g5_b2', 'm3_g5_a2', 'm3_g6', 'm3_sg_t2310', 'm3_g5_t2330p', 'm3_g5_t2330',
     'm3_hb_t2330p', 'm3_hb_t2330', 'm3_hb_t2330w', 'm3_mg_t0320', 'm3_ac_t2650', 'm3_f1_t2720w', 'm3_f2_t2030p', 'm3_sg_v_r1']
BAD = ['m3_x', 'm3_sg_q', 'm3_g5_t2340', 'm3_i_t2340', 'm3_g6_t2650', 'm3_g5_t2330w', 'm3_hb_t2650p', 'm3_hb_t3060', 'm3_g5_c1', 'fs15_v']


def dry(tag):
    env = dict(os.environ, M3A_DRYRUN='1')
    r = subprocess.run([BASH, G + '/go_m3a.sh', tag], capture_output=True, env=env)
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
    p = M.plan_of('m3_hb_t2330')
    check('dir of a T233 arm = ..._mw1_31', M.dir_of(p) == 'variant_fixb26_fixb1b_fixf10_fixf19_mw1_31', M.dir_of(p))
    check('dir of MS1 defaults = ..._mw1_33', M.dir_of(M.plan_of('m3_sg_v')) == 'variant_fixb26_fixb1b_fixf10_fixf19_mw1_33')
    check('dir of FS15 = ..._fixf19', M.dir_of(M.plan_of('m3_sg_f')) == M.DIR0)
    check('HLE arm keeps mask 0x33, T265 want 0', M.mask_of(M.plan_of('m3_ac_t2650')) == 0x33 and
          M.hle_want(M.plan_of('m3_ac_t2650'), '265') == 0 and M.hle_want(M.plan_of('m3_ac_t2650'), '272') == 1)


def fixture(d, tag, plan_txt, inst=M.FS15, src='fs15_v'):
    os.makedirs(d, exist_ok=True)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha',
                                                         'level', 'sheet', 'plan', 'k0_cmp', 'base_cmp'))
    p.update(log=os.path.join(F, 'log_%s.txt' % src), stdout=os.path.join(F, 'stdout_%s.txt' % src), run=os.path.join(F, '%s.json' % src),
             idx=os.path.join(F, 'rec_%s.mp4.idx' % src), seal=os.path.join(F, 'pred', 'fs15c_seal.md'))
    for nm, v in (('installed_before', M.FS15), ('installed_after', M.FS15), ('installed_sha', inst),
                  ('manifest_cmp', 'manifest cmp EQUAL files 1 listsha x'), ('level', 'underwater_aerial_garden'),
                  ('sheet', 'sheet x.png 16 frames'), ('plan', plan_txt), ('k0_cmp', 'KSET EQUAL4 files 1; GLCache row'),
                  ('base_cmp', 'manifest cmp EQUAL files 1')):
        open(p[nm], 'w', encoding='ascii').write(v + '\n')
    g = os.path.join(F, 'runs', src, 'glitch.txt')
    shutil.copyfile(g, p['glitch']) if os.path.exists(g) else open(p['glitch'], 'w').write('one-frame glitches: 0 of 1\n')
    return p


def reader(tmp):
    pl = 'fs15 %s K0 none v' % M.FS15
    p = fixture(os.path.join(tmp, 'a'), 'm3_sg_f', pl)
    r = M.read_tag('m3_sg_f', p)
    bad = [a for a, b in r['admission'] if not b]
    check('fs15_v as m3_sg_f: ADMITTED', r['admitted'], bad)
    check('fs15_v as m3_sg_f: members ALL YES', r['ok'] is True, [a for a, b in (r['members'] or []) if not b])
    check('fs15_v as m3_sg_f: form FS15 ALL YES', r['form_ok'] is True, [a for a, b in (r['form'] or []) if not b])
    check('fs15_v: G5 measure end A n > 0 and end B n >= end A n', r['g5'] and r['g5']['end_a']['n'] > 0 and
          r['g5']['end_b']['n'] >= r['g5']['end_a']['n'], r['g5'])
    neg = (('plan', 'ms1 %s K1 K1 v' % M.MS1, 'plan of go'), ('k0_cmp', 'KSET DIFFER4 only-a 1', 'K0'),
           ('installed_sha', M.MS1, 'installed during'), ('installed_after', M.MS1, 'before = after'),
           ('manifest_cmp', 'manifest cmp DIFFER', 'caches returned'), ('level', 'hoover_beach', 'guest args'))
    for i, (nm, val, member) in enumerate(neg):
        q = fixture(os.path.join(tmp, 'n%d' % i), 'm3_sg_f', pl)
        open(q[nm], 'w', encoding='ascii').write(val + '\n')
        r = M.read_tag('m3_sg_f', q)
        bad = [a for a, b in r['admission'] if not b]
        check('negative %s=%s: NOT_ADMITTED by "%s"' % (nm, val[:20], member), not r['admitted'] and any(member in a for a in bad), bad[:2])
    q = fixture(os.path.join(tmp, 'm'), 'm3_sg_v', 'ms1 %s K1 K1 v' % M.MS1, inst=M.MS1)
    r = M.read_tag('m3_sg_v', q)
    bad = [a for a, b in r['admission'] if not b]
    check('FS15 log read as MS1 m3_sg_v: NOT_ADMITTED by json binary and signature', not r['admitted'] and
          any('json binary_sha256' in a for a in bad) and any('translation signature' in a for a in bad), bad[:3])
    q = fixture(os.path.join(tmp, 'b'), 'm3_sg_f', pl)
    js = json.load(open(q['run'], encoding='utf-8'))
    js['env']['KYTY_M_T233'] = '0'
    q['run'] = os.path.join(tmp, 'b', 'es.json')
    json.dump(js, open(q['run'], 'w', encoding='utf-8'))
    r = M.read_tag('m3_sg_f', q)
    check('negative env extra KYTY_M_T233: NOT_ADMITTED by env', not r['admitted'] and any('env = the form' in a for a, b in r['admission']
                                                                                           if not b))
    # W members on fs15_w: an FS15 W plan does not exist in the table - the members are read with a patched table entry
    save = M.plan_of
    try:
        M.plan_of = lambda t: dict(save('m3_sg_w'), bin='fs15') if t == 'm3_sg_w' else save(t)
        q = fixture(os.path.join(tmp, 'w'), 'm3_sg_w', 'fs15 %s K1 K1 w' % M.FS15, src='fs15_w')
        r = M.read_tag('m3_sg_w', q)
        bad = [a for a, b in r['admission'] if not b]
        check('fs15_w with an FS15 W plan: ADMITTED', r['admitted'], bad)
        mm = dict((a.split(' (')[0], b) for a, b in (r['members'] or []))
        check('fs15_w: W members ALL YES (0 [Vulkan][E], [Vulkan][W] > 0, DualSrcBlend, FS15 0 M lines)', r['ok'] is True,
              [a for a, b in (r['members'] or []) if not b])
    finally:
        M.plan_of = save


def synth(tmp):
    lg = os.path.join(tmp, 'syn.log')
    with open(lg, 'wb') as f:
        f.write(b'Shader translation cache: _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19_mw1_33\n')
        f.write(b'MWave1: mask=0x33 T234=1 T233=1 T256=0 T306=0 T032=1 T203=1\n')
        f.write(b'MT265: mode=1\nMT272: mode=0\nMT231: mode=1\nMT231: mode=x\n')
        f.write(b'GamePatch: file a eboot b\nGamePatch: applied sha=3b5100797fe83663 pokes=2 pvar=2 audio_sync=0\n')
        f.write(b'GamePatch: poke 0x00000009002a470b <- c5\n')
        f.write(b'[x] vkWaitForFences returned ErrorDeviceLost\n')
        f.write(b'GuestOut: Level has started: underwater_aerial_garden\n')
        for n in range(1, 2001):
            f.write(b'FrameTrace: n=%d dt_us=%d draws=150\n' % (n, 20000 if n <= 1500 else 40000))
            if n == 1800:
                f.write(b'Event: quit\n')
    y = M.scan_m(lg)
    check('scan_m: MWave1 mask 0x33', y['mw'] == [0x33] and y['mw_bad'] == 0, y['mw'])
    check('scan_m: MT lines parsed, one unparsable', y['mt']['265'] == [1] and y['mt']['272'] == [0] and y['mt']['231'] == [1] and
          y['mt_bad'] == 1, (y['mt'], y['mt_bad']))
    check('scan_m: GamePatch applied 1, poke 1, lines 3', y['gp_applied'] == [('3b5100797fe83663', 2)] and y['gp_poke'] == 1 and
          y['gp'] == 3, y['gp_applied'])
    check('scan_m: device lost 1', y['devlost'] == 1, y['devlost'])
    p = M.plan_of('m3_sg_v')
    mm = M.m_members(p, y)
    check('m_members MS1 defaults: MT272 mode 0 is a NO, unparsable MT is a NO, MWave1 YES',
          mm[0][1] and not mm[2][1] and not mm[4][1] and mm[1][1] and mm[3][1], [b for a, b in mm])
    p2 = M.plan_of('m3_sg_t2720')
    check('m_members T272 arm: MT272 mode 0 YES', M.m_members(p2, y)[2][1])
    R = M.load_r('underwater_aerial_garden')
    x = R.scan(lg)
    g = M.g5_measure(x, R)
    # first scene frame = n 1; rows after: n 2..2000; start t of row n = (n-2)*20000 while n <= 1501
    # rows with start >= 30 s: n >= 1502 (start (1500)*20000 = 30.0 s) - n 1502..2000 are 40000 us
    check('G5 end B: rows n 1502..2000, mean 40000', g['end_b']['n'] == 499 and g['end_b']['mean'] == 40000.0, g['end_b'])
    check('G5 end A: rows before Event: quit (n <= 1800) - 299 rows', g['end_a']['n'] == 299 and g['end_a']['mean'] == 40000.0, g['end_a'])


def g5_words(tmp):
    rd = os.path.join(tmp, 'g5runs')

    def put(t, mean, adm=True):
        os.makedirs(os.path.join(rd, t), exist_ok=True)
        json.dump(dict(admitted=adm, bin='x', ok=True, g5=dict(end_a=dict(n=1000, mean=mean, sd=100.0, se=3.0),
                                                                end_b=dict(n=1001, mean=mean, sd=100.0, se=3.0))),
                  open(os.path.join(rd, t, 'read.json'), 'w'))

    def word(a1, b1, b2, a2, adm=True):
        put('m3_g5_a1', a1)
        put('m3_g5_b1', b1, adm)
        put('m3_g5_b2', b2)
        put('m3_g5_a2', a2)
        r = subprocess.run([sys.executable, G + '/g5_m3a.py', '--runs', rd], capture_output=True)
        return [l for l in r.stdout.decode('ascii').splitlines() if l.startswith('G5 WORD')][0]
    check('G5 delta exactly +1.0 % -> NOT_WORSE', 'end A NOT_WORSE' in word(30000, 30300, 30300, 30000), '')
    check('G5 delta +1.01 % -> FAIL', 'end A FAIL' in word(30000, 30303, 30303, 30000), '')
    check('G5 delta -1.0 % -> NOT_WORSE (BETTER)', 'end A NOT_WORSE (BETTER' in word(30000, 29700, 29700, 30000), '')
    check('G5 an arm not admitted -> NOT_EVALUABLE', 'end A NOT_EVALUABLE' in word(30000, 30000, 30000, 30000, adm=False), '')


def kset(tmp):
    a = os.path.join(tmp, 'a.tsv')
    b = os.path.join(tmp, 'b.tsv')
    open(a, 'w').write('GLCache\tx\t1\taa\n_ShaderCache\ty\t1\tbb\n')
    open(b, 'w').write('GLCache\tz\t1\tcc\n_ShaderCache\ty\t1\tbb\n')
    r = subprocess.run([sys.executable, G + '/kset_m3a.py', 'cmp4', a, b], capture_output=True)
    check('kset: GLCache differs only -> EQUAL4 rc 0', r.returncode == 0 and r.stdout.startswith(b'KSET EQUAL4'), r.stdout[:60])
    open(b, 'w').write('GLCache\tx\t1\taa\n_ShaderCache\ty\t1\tbX\n')
    r = subprocess.run([sys.executable, G + '/kset_m3a.py', 'cmp4', a, b], capture_output=True)
    check('kset: _ShaderCache differs -> DIFFER4 rc 1', r.returncode == 1 and r.stdout.startswith(b'KSET DIFFER4'), r.stdout[:60])


def cp1250():
    env = dict(os.environ)
    env.pop('PYTHONIOENCODING', None)
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    for args in (['m3a_read.py', '--plan', 'm3_g6'], ['m3a_read.py', '--table'], ['g5_m3a.py']):
        r = subprocess.run([sys.executable, G + '/' + args[0]] + args[1:], capture_output=True, env=env)
        check('cp1250 strict output of %s: rc 0, no UnicodeEncodeError' % ' '.join(args), r.returncode == 0 and
              b'UnicodeEncodeError' not in r.stderr, r.stderr[-120:])


def main():
    me = os.path.abspath(__file__)
    print('suite test_m3a.py sha256 %s target m3a_read.py sha256 %s go_m3a.sh sha256 %s g5_m3a.py sha256 %s kset_m3a.py sha256 %s' % (
        sha(me), sha(G + '/m3a_read.py'), sha(G + '/go_m3a.sh'), sha(G + '/g5_m3a.py'), sha(G + '/kset_m3a.py')))
    tmp = tempfile.mkdtemp(prefix='m3a_fx_', dir=os.environ.get('PAPERCLIP_RUN_SCRATCH_DIR') or None)
    try:
        plan_table()
        reader(tmp)
        synth(tmp)
        g5_words(tmp)
        kset(tmp)
        cp1250()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('checks %d, failed %d %s' % (N[0], len(FAILS), FAILS[:10]))
    print('ALL OK' if not FAILS else 'FAILED')
    return 0 if not FAILS else 1


if __name__ == '__main__':
    sys.exit(main())

"""Fixtures of f16q_read.py, f16q_pair.py and f16q_luma.py (track F link F16q, HPP-597): one fixture per member of each control (pair A
arms, pair B arms, warm-up), per equality of the identities of item 496 (b)(5) and item 507 (b)(4) (VARIANT member, LETTER reference),
per frame-line identity, per limit edge (cmask_fce 1024, nohit 64, dcc_stale 256), apply_late of item 515 (v) (equal; present differs;
gpu differs; both differ; no adopt line of the n; declined), per admission row (skipceil, item 515 N1), the DiagF5 line of 64 names (63 is
malformed), the pair matchings (pair A cmask and dcc with fix and without exact - RC2; pair B by (site, image, dcc)), the reading classes,
the window p-1..p+2, skipped draw near [gpu-1, gpu+3], the sheet selection, the first scene frame, the strict cp1250 output.  The first
output line names the suite and the targets with their sha256; the last line is ALL OK.  ASCII only.   usage: python test_f16q_read.py"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f16q_read as R
import f16q_pair as P
import f16q_luma as LU

N_OK = [0]
FAIL = []
# diagF5.cpp of 365cc3c2 :211-:223 - written here, not imported
EXPECTED_TAIL = ['f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback', 'dcc_stale_bucket_only', 'dcc_stale_fallback',
                 'cmask_rt_bucket_only', 'f5cmu_exact_cpu', 'f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback',
                 'f26_deferred_declined']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond):
    if cond:
        N_OK[0] += 1
    else:
        FAIL.append(name)
        print('FAIL %s' % name)


def f5vals(s, extra=None):
    d = dict((n, 0) for n in R.F5_NAMES)
    d.update(rt_resolves=100 * s, dcc_rt=10 * s, dcc_fce=3 * s, dcc_fce_image=2 * s, dcc_fce_no_image=s, meta_refused_known=2 * s,
             meta_cs_tracked=s, meta_cs_untracked=s, cmask_fce=4 * s, cmask_fce_meta=2 * s, cmask_fce_b42=s, cmask_fce_unapplied=s,
             zero_disp=40)
    if extra:
        d.update(extra)
    return d


def f5line(frame, d, names=None):
    return 'DiagF5: frame=%d ' % frame + ' '.join('%s=%d' % (n, d[n]) for n in (names or R.F5_NAMES))


def ev(n, present, fix, why=None, image='510d10000', cmask='56c05e000', extent='1920x1080', applied=1):
    t = ('DiagF5Ev: cmask_fce n=%d present=%d gpu=%d image=0x%016x cmask=0x%016x extent=%s applied=%d fix=%s'
         % (n, present, present + 1, int(image, 16), int(cmask, 16), extent, applied, fix))
    return t + (' why=%s' % why if why else '')


def nohit(n, present, fix, why=None, b42='none', image='600000000', cmask='610000000', extent='1024x1024'):
    t = ('DiagF5Ev: cmask_fce_nohit n=%d b42=%s present=%d gpu=%d image=0x%016x cmask=0x%016x extent=%s fix=%s'
         % (n, b42, present, present + 1, int(image, 16), int(cmask, 16), extent, fix))
    return t + (' why=%s' % why if why else '')


def ds(n, site, present, fix, exact='fresh', why=None, image='520000000', dcc='530000000', extent='2432x1368', gpu=None):
    t = ('DiagF5Ev: dcc_stale site=%s n=%d present=%d gpu=%d image=0x%016x dcc=0x%016x extent=%s exact=%s fix=%s'
         % (site, n, present, present + 1 if gpu is None else gpu, int(image, 16), int(dcc, 16), extent, exact, fix))
    return t + (' why=%s' % why if why else '')


def da(n, present, result, gpu=None, image='520000000', dcc='530000000', layers=1):
    return ('DiagF5Ev: dcc_stale_apply n=%d present=%d gpu=%d image=0x%016x dcc=0x%016x result=%s layers=0x%08x'
            % (n, present, present + 1 if gpu is None else gpu, int(image, 16), int(dcc, 16), result, layers))


F26_GOOD = dict(f26_kept=3, f26_kept_applied=2, f26_exact_stale=1, f26_fallback=1, f26_deferred_declined=1, dcc_stale_bucket_only=3)


class Fx(object):
    """A synthetic tag of the F16o2 binary: mode lines, event lines, three DiagF5 frame lines, 400 FrameTrace rows of 0.9 s."""

    def __init__(self, tag='f5cmu_1b'):
        self.tag = tag
        self.level, self.kind = R.TAGS[tag]
        self.cnt = [dict() for _ in range(3)]
        self.ev_before = []
        self.ev_scene = [[], [], []]
        self.ev_tail = []
        self.mode = 'before'
        self.extra = []
        self.dt = 900000
        self.rows = 400
        self.level_line = self.level
        self.gates = ''
        self.env = {'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_DIAG_F5': '1'}
        k = self.kind
        if k == 'warm':
            self.env.update(KYTY_FIX_F5CMU='0', KYTY_FIX_F26='0')
            self.ev_scene[0] = [ev(1, 3, 'off'), ds(1, 'adopt', 4, 'off', exact='na')]
        elif k == 'pair0':
            self.env['KYTY_FIX_F5CMU'] = '0'
            self.ev_scene[0] = [ev(1, 3, 'off'), ev(2, 8, 'off'), ds(1, 'adopt', 4, 'off', exact='na')]
        elif k == 'pair1':
            self.env['KYTY_FIX_F5CMU'] = '1'
            self.ev_scene[0] = [ev(1, 3, 'kept_applied'), ev(2, 8, 'exact_stale', 'cpu'), ds(1, 'adopt', 4, 'off', exact='fresh')]
            self.ev_scene[1] = [nohit(1, 20, 'kept', 'decode')]
            c = [dict(f5cmu_kept=1, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1),
                 dict(f5cmu_kept=2, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1),
                 dict(f5cmu_kept=2, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1)]
            self.cnt = c
        elif k == 'f26_0':
            self.env.update(KYTY_DIAG_F5ID='1', KYTY_FIX_F26='0')
            self.ev_scene[0] = [ds(1, 'prepare', 5, 'off'), ds(2, 'adopt', 9, 'off', why='cpu')]
            self.cnt = [dict(dcc_stale_bucket_only=2) for _ in range(3)]
        else:
            self.env.update(KYTY_DIAG_F5ID='1', KYTY_FIX_F26='1')
            self.ev_scene[0] = [ds(1, 'prepare', 5, 'kept_applied'), ds(2, 'adopt', 9, 'kept', why='deferred'), da(2, 9, 'cleared'),
                                ds(3, 'adopt', 12, 'kept', why='deferred'), da(3, 12, 'declined'),
                                ds(4, 'prepare', 15, 'exact_stale', exact='stale'), ds(5, 'adopt', 18, 'fallback', exact='fallback')]
            self.cnt = [dict(F26_GOOD) for _ in range(3)]
        self.att = {'outcome': 'ok', 'hold_exit': None, 'hold_s': 330.1, 'close_rc': 0, 'close_killed': False}
        self.installed = R.BIN_EXPECT
        self.before = R.WANT
        self.after = R.WANT
        self.manifest = 'manifest cmp EQUAL files 3323 listsha 00'
        self.idx_n = 9000 if k != 'warm' else None
        self.glitch = 'x: 9000 frames 960x540, index entries 9000\none-frame glitches: 0\n'
        self.f5names = None

    def log(self):
        L = ['[main] Fork build arigandores/KytyPS5 KytyPS5-2026-09-15-6a2987a-2264-g365cc3c2, x64',
             'Shader translation cache: _ShaderCache\\PPSA21564\\' + R.DIR_FIX]
        modes = ['DiagF5: mode=1']
        if self.kind == 'pair1':
            modes.append('FixF5Cmu: mode=1')
        if self.kind == 'f26_1':
            modes.append('FixF26: mode=1')
        if self.kind in ('f26_0', 'f26_1'):
            modes.append('DiagF5Id: mode=1')
        if self.mode == 'before':
            L += modes
        L.append('GuestOut: boot')
        if self.mode == 'after':
            L += modes
        L += self.ev_before
        L.append('GuestOut: Level has started: %s' % self.level_line)
        L.append('FrameTrace: n=100 dt_us=16000 draws=300')
        per = self.rows // 3
        for i in range(3):
            for j in range(per):
                L.append('FrameTrace: n=%d dt_us=%d draws=300' % (101 + i * per + j, self.dt))
            L += self.ev_scene[i]
            L.append(f5line(100 + (i + 1) * per, f5vals(i + 1, self.cnt[i]), self.f5names))
        L += self.ev_tail
        L += self.extra
        L.append('Event: quit')
        return '\n'.join(L) + '\n'

    def make(self, base):
        if os.path.isdir(base):
            shutil.rmtree(base)
        os.makedirs(base)
        open(os.path.join(base, 'log.txt'), 'w', newline='\n').write(self.log())
        open(os.path.join(base, 'stdout.txt'), 'w').write('stdout\n')
        json.dump({'env': self.env, 'attempts': [self.att], 'gates': self.gates}, open(os.path.join(base, 'es.json'), 'w'))
        for k, v in (('installed_sha', self.installed), ('installed_before', self.before), ('installed_after', self.after),
                     ('manifest_cmp', self.manifest), ('warm', 'variant form: x/%s present at T' % R.DIR_FIX),
                     ('glitch', self.glitch), ('sheet', 'sheet: x.png frames 9000 step 187 tiles 8x6'),
                     ('luma', 'LUMA x\nSCENE first > 5: video 400 present 401 mean 30.0')):
            open(os.path.join(base, k + '.txt'), 'w').write(v + '\n')
        open(os.path.join(base, 'bin.exe'), 'wb').write(b'MZ..' + R.VERSIONS[0] + b'..')
        if self.idx_n:
            open(os.path.join(base, 'rec.idx'), 'w').write(''.join('%d %d %.3f\n' % (i, i + 1, i / 60.0) for i in range(self.idx_n)))
        return R.read(R.paths(self.tag, base), self.tag)


TMP = tempfile.mkdtemp(prefix='f16q_fx_')
K = [0]


def run(fx):
    K[0] += 1
    return fx.make(os.path.join(TMP, 'fx%03d' % K[0]))


def ctl(res, sub):
    for name, val in res['control']:
        if sub in name:
            return val
    return 'ABSENT'


def adm(r):
    ok = (r['sha_ok'] and r['before_ok'] and r['after_ok'] and r['env_ok'] and r['entry_line'] is not None and r['hold_len_ok']
          and r['hold_ok'] and r['manifest_ok'] and not r['interference'])
    if r['kind'] != 'warm':
        ok = ok and (r['idx_records'] or 0) >= R.VIDEO_MIN
    return ok


def cnt3(fx, **kw):
    fx.cnt = [dict(c, **kw) for c in fx.cnt]


def jcopy(x):
    return json.loads(json.dumps(x, default=list))


def main():
    me = os.path.abspath(__file__)
    t_read, t_pair, t_luma = [os.path.join(HERE, n) for n in ('f16q_read.py', 'f16q_pair.py', 'f16q_luma.py')]
    print('suite test_f16q_read.py sha256 %s target f16q_read.py sha256 %s target f16q_pair.py sha256 %s target f16q_luma.py sha256 %s'
          % (sha(me), sha(t_read), sha(t_pair), sha(t_luma)))
    # 0. names and constants against the code (written here)
    check('F5 names: 64, tail of F16o2 in order', len(R.F5_NAMES) == 64 and R.F5_NAMES[-13:] == EXPECTED_TAIL)
    check('limits 1024 / 64 / 256', (R.LIM_FCE, R.LIM_NOHIT, R.LIM_DCC) == (1024, 64, 256))
    check('binary 7e4ded19, installed 9325446c', R.BIN_EXPECT.startswith('7e4ded19f577cc9b') and R.WANT.startswith('9325446cdd3c960b'))
    # 1. good tags
    for tag in R.TAGS:
        r = run(Fx(tag))
        if R.TAGS[tag][1] == 'warm':
            check('good warm: control not read (None), admission rows', r['control_alive'] is None and adm(r))
            check('good warm: no CONTROL line', not any(x.startswith('  CONTROL ') for x in R.rows(r)))
            continue
        check('good %s control alive' % tag, r['control_alive'] is True)
        check('good %s admission rows' % tag, adm(r))
        check('good %s 3 frame lines, health' % tag, r['f5']['lines'] == 3 and r['f5']['health'])
        check('good %s CONTROL line' % tag, ('  CONTROL %s ALIVE' % r['kind'].upper()) in R.rows(r))
    r = run(Fx('f5cmu_1b'))
    check('pair1 cmask events 3 (two fce, one nohit), dcc lines 1 not in cmask', r['limits']['fce_lines'] == 2
          and r['limits']['nohit_lines'] == 1 and len(r['events']) == 3 and len(r['dcc']) == 1)
    check('pair1 identity variant and letter equal (5 rows)', all(x[3] for x in r['id496_variant']) and all(x[3] for x in r['id496_letter'])
          and len(r['id496_variant']) == 5)
    r = run(Fx('f26_1'))
    check('f26_1 parsed: dcc 5 (prepare 2, adopt 3), apply 2 (cleared 1, declined 1)', len(r['dcc']) == 5 and r['dcc_sites'] ==
          dict(prepare=2, adopt=3) and r['apply_counts'] == dict(cleared=1, declined=1))
    check('f26_1 identity 507 variant 6 rows equal, letter equal', len(r['id507_variant']) == 6 and all(x[3] for x in r['id507_variant'])
          and all(x[3] for x in r['id507_letter']))
    check('f26_1 why deferred and exact parsed', [e['why'] for e in r['dcc']] == [None, 'deferred', 'deferred', None, None]
          and [e['exact'] for e in r['dcc']] == ['fresh', 'fresh', 'fresh', 'stale', 'fallback'])
    check('f26_1 apply_late 0, orphan 0', r['apply_late'] == [] and r['apply_orphan'] == [])
    # 2. pair1 members
    fx = Fx('f5cmu_1b')
    fx.mode = 'after'
    check('pair1: FixF5Cmu mode after GuestOut -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1b')
    fx.ev_scene = [[ds(1, 'adopt', 4, 'off')], [], []]
    fx.cnt = [dict(), dict(), dict()]
    r = run(fx)
    check('pair1: 0 cmask events (a dcc line only) -> dead', ctl(r, 'cmask_fce event lines >= 1') is False and not r['control_alive'])
    fx = Fx('f5cmu_1b')
    fx.ev_scene[1].append('DiagF5Ev: dcc_stale site=adopt n=x present=1')
    check('pair1: malformed dcc event -> dead', run(fx)['control_alive'] is False)
    for i, name in enumerate(['f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback']):
        fx = Fx('f5cmu_1b')
        fx.cnt[2] = dict(fx.cnt[2])
        fx.cnt[2][name] = fx.cnt[2].get(name, 0) + 1
        if name == 'f5cmu_kept_applied':
            fx.cnt[2]['f5cmu_kept'] += 1
            r = run(fx)
            check('pair1: identity kept_applied off -> dead', not r['id496_variant'][1][3] and r['control_alive'] is False)
            continue
        r = run(fx)
        check('pair1: identity %s off -> dead' % name, not r['id496_variant'][i][3] and r['control_alive'] is False)
    fx = Fx('f5cmu_1b')
    fx.cnt[2] = dict(fx.cnt[2], f5cmu_exact_cpu=0)
    r = run(fx)
    check('pair1: exact_cpu row is not a member', not r['id496_variant'][4][3] and r['control_alive'])
    fx = Fx('f5cmu_1b')
    fx.ev_tail = [ev(3, 400, 'fallback')]
    r = run(fx)
    check('pair1: event after the last frame line - LETTER different, VARIANT equal -> alive (member VARIANT, item 502 (b))',
          not r['id496_letter'][3][3] and all(x[3] for x in r['id496_variant'][:4]) and r['control_alive'] is True)
    fx = Fx('f5cmu_1b')
    fx.ev_scene[0].append(ds(2, 'adopt', 6, 'kept', why='deferred'))
    r = run(fx)
    check('pair1: a dcc line fix=kept is not counted by identity 496 (rows equal) but kills the dcc member',
          all(x[3] for x in r['id496_variant'][:4]) and ctl(r, 'every dcc_stale line fix=off') is False and not r['control_alive'])
    for n, lim in ((1024, True), (1023, False)):
        fx = Fx('f5cmu_1b')
        fx.ev_scene[2] = [ev(n, 300, 'fallback')]
        r = run(fx)
        check('pair1: cmask_fce n=%d -> limit %s' % (n, lim), r['limits']['fce_exhausted'] is lim and r['id496_limit'] is lim
              and (r['control_alive'] is True if lim else r['control_alive'] is False))
    for b42, lim in ((1023, True), (1022, False)):
        fx = Fx('f5cmu_1b')
        cnt3(fx, cmask_fce_b42=b42, cmask_fce_unapplied=2, cmask_fce=b42 + 2 + 4)
        fx.cnt[2] = dict(fx.cnt[2], f5cmu_kept=3)
        r = run(fx)
        check('pair1: b42 + unapplied = %d -> limit %s' % (b42 + 2, lim), r['limits']['fce_exhausted'] is lim)
    for n, lim in ((64, True), (63, False)):
        fx = Fx('f5cmu_1b')
        fx.ev_scene[1] = [nohit(n, 20, 'kept', 'decode')]
        r = run(fx)
        check('pair1: nohit n=%d -> limit %s' % (n, lim), r['limits']['nohit_exhausted'] is lim)
    fx = Fx('f5cmu_1b')
    fx.cnt[1] = dict(fx.cnt[1], f5cmu_kept_applied=3)
    check('pair1: kept_applied > kept on the middle line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1b')
    fx.cnt[0] = dict(fx.cnt[0], f5cmu_exact_cpu=2)
    check('pair1: exact_cpu > exact_stale on the first line -> dead', run(fx)['control_alive'] is False)
    for extra, name in ((['DiagF5Id: mode=1'], 'a DiagF5Id line'), (['FixF26: mode=1'], 'a FixF26 line'),
                        ([da(1, 4, 'declined')], 'a dcc_stale_apply line')):
        fx = Fx('f5cmu_1b')
        fx.extra = extra
        check('pair1: %s -> dead' % name, run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1b')
    fx.cnt[1] = dict(fx.cnt[1], f26_fallback=1)
    fx.cnt[2] = dict(fx.cnt[2], f26_fallback=1)
    check('pair1: f26_* != 0 -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1b')
    fx.ev_scene[1] = [nohit(1, 20, 'kept', 'decode', b42='drawn')]
    r = run(fx)
    check('pair1: b42=drawn -> interference', r['drawn'] == 1 and r['interference'] and not adm(r))
    # 3. pair0 members
    for extra, name in ((['FixF5Cmu: mode=1'], 'FixF5Cmu line'), ([nohit(1, 30, 'off')], 'a nohit line'),
                        (['DiagF5Id: sum frame=1'], 'a DiagF5Id line'), (['FixF26: mode=1'], 'a FixF26 line'),
                        ([da(1, 4, 'cleared')], 'an apply line'), ([ev(3, 30, 'fresh')], 'a cmask event fix fresh'),
                        ([ds(2, 'prepare', 30, 'exact_stale', exact='stale')], 'a dcc event fix exact_stale')):
        fx = Fx('f5cmu_0b')
        fx.extra = extra
        check('pair0: %s -> dead' % name, run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0b')
    fx.ev_scene[1] = [ds(2, 'prepare', 30, 'off', exact='na')]
    check('pair0: another dcc event fix=off -> alive', run(fx)['control_alive'] is True)
    fx = Fx('f5cmu_0b')
    cnt3(fx, f5cmu_fallback=1)
    check('pair0: f5cmu_* != 0 -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0b')
    fx.ev_scene = [[ds(1, 'adopt', 4, 'off')], [], []]
    check('pair0: 0 cmask events -> dead', run(fx)['control_alive'] is False)
    # 4. f26_1 members
    fx = Fx('f26_1')
    fx.mode = 'after'
    check('f26_1: mode lines after GuestOut -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f26_1')
    fx.ev_scene = [[ev(1, 3, 'off')], [], []]
    fx.cnt = [dict(), dict(), dict()]
    check('f26_1: 0 dcc lines -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f26_1')
    fx.cnt[1] = dict(fx.cnt[1], f26_kept_applied=3)
    r = run(fx)
    check('f26_1: kept_applied + declined > kept on the middle line -> dead', r['f5']['f26_bad_n'] == 1 and r['control_alive'] is False)
    fx = Fx('f26_1')
    fx.cnt[1] = dict(fx.cnt[1], dcc_stale_bucket_only=4)
    r = run(fx)
    check('f26_1: f26_kept != dcc_stale_bucket_only on the middle line -> dead', r['f5']['f26_bad_n'] == 1 and not r['control_alive'])
    for i, (name, upd) in enumerate((('f26_kept', dict(f26_kept=4, dcc_stale_bucket_only=4)), ('f26_kept_applied', dict(f26_kept_applied=1)),
                                     ('f26_exact_stale', dict(f26_exact_stale=2)), ('f26_fallback', dict(f26_fallback=0)),
                                     ('f26_deferred_declined', dict(f26_deferred_declined=0)))):
        fx = Fx('f26_1')
        fx.cnt[2] = dict(fx.cnt[2], **upd)
        r = run(fx)
        check('f26_1: identity 507 row %s off -> dead' % name, not r['id507_variant'][i][3] and r['control_alive'] is False)
    fx = Fx('f26_1')
    fx.ev_scene[0][1] = ds(2, 'adopt', 9, 'kept_applied')
    fx.ev_scene[0][2] = da(9, 9, 'declined')
    fx.ev_scene[0] = [x for x in fx.ev_scene[0] if 'n=9 ' not in x]
    fx.cnt = [dict(F26_GOOD, f26_kept_applied=2, f26_deferred_declined=1) for _ in range(3)]
    r = run(fx)
    check('f26_1: a line site=adopt fix=kept_applied -> identity row 6 off, dead; row 2 counts prepare only (1)', r['id507_variant'][5][1] == 1
          and r['id507_variant'][1][1] == 1
          and not r['id507_variant'][5][3] and r['control_alive'] is False)
    fx = Fx('f26_1')
    fx.ev_tail = [ds(6, 'prepare', 400, 'fallback', exact='fallback')]
    r = run(fx)
    check('f26_1: dcc line after the last frame line - LETTER different, VARIANT equal -> alive', not r['id507_letter'][3][3]
          and all(x[3] for x in r['id507_variant']) and r['control_alive'] is True)
    fx = Fx('f26_1')
    fx.ev_tail = [da(3, 12, 'declined')]
    r = run(fx)
    check('f26_1: apply line after the last frame line - LETTER different, VARIANT equal', not r['id507_letter'][4][3]
          and r['id507_variant'][4][3])
    for n, lim in ((256, True), (255, False)):
        fx = Fx('f26_1')
        fx.ev_scene[2] = [ds(n, 'prepare', 300, 'fallback', exact='fallback')]
        r = run(fx)
        check('f26_1: dcc n=%d -> limit %s' % (n, lim), r['limits']['dcc_exhausted'] is lim and r['id507_limit'] is lim
              and (r['control_alive'] is True if lim else r['control_alive'] is False))
    for kept, lim in ((255, True), (254, False)):
        fx = Fx('f26_1')
        cnt3(fx, f26_kept=kept, dcc_stale_bucket_only=kept)
        r = run(fx)
        check('f26_1: f26_kept+exact_stale+fallback = %d -> limit %s' % (kept + 2, lim), r['limits']['dcc_exhausted'] is lim)
    fx = Fx('f26_0')
    cnt3(fx, f26_kept=300)
    check('f26_0: counter sum > 256 is not a limit on =0 (dcc by n only)', run(fx)['limits']['dcc_exhausted'] is False)
    fx = Fx('f26_1')
    fx.extra = ['FixF5Cmu: mode=1']
    check('f26_1: FixF5Cmu line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f26_1')
    cnt3(fx, f5cmu_fallback=1)
    check('f26_1: f5cmu_* != 0 -> dead', run(fx)['control_alive'] is False)
    # 5. apply_late (item 515 (v)) and orphans
    for name, line, late in (('equal present and gpu', da(2, 9, 'cleared'), False), ('present differs', da(2, 10, 'cleared', gpu=10), True),
                             ('gpu differs', da(2, 9, 'cleared', gpu=11), True), ('both differ', da(2, 11, 'cleared'), True),
                             ('declined with present differing', da(2, 11, 'declined'), False)):
        fx = Fx('f26_1')
        fx.ev_scene[0][2] = line
        if 'declined' in name:
            fx.cnt = [dict(F26_GOOD, f26_kept_applied=1, f26_deferred_declined=2) for _ in range(3)]
        r = run(fx)
        check('apply_late: %s -> %s; identity still equal' % (name, late), (len(r['apply_late']) == 1) is late
              and all(x[3] for x in r['id507_variant']))
    fx = Fx('f26_1')
    fx.ev_scene[0][2] = da(9, 9, 'cleared')
    r = run(fx)
    check('apply: no adopt line of its n -> orphan, not late', len(r['apply_orphan']) == 1 and r['apply_late'] == [])
    fx = Fx('f26_1')
    fx.ev_scene[0][2] = da(2, 10, 'cleared', gpu=10)
    rr = R.rows(run(fx))
    check('rows: APPLY_LATE line with the pair n=2 event 9/10 outcome 10/10', any('APPLY_LATE (item 515 (v)): 1 lines [n=2 event present=9 '
                                                                                'gpu=10 outcome present=10 gpu=10]' in x for x in rr))
    # 6. f26_0 members
    for extra, name in ((['FixF26: mode=1'], 'FixF26 line'), ([da(1, 5, 'declined')], 'apply line'),
                        ([ds(3, 'adopt', 30, 'kept', why='deferred')], 'dcc fix kept'), (['FixF5Cmu: mode=1'], 'FixF5Cmu line')):
        fx = Fx('f26_0')
        fx.extra = extra
        check('f26_0: %s -> dead' % name, run(fx)['control_alive'] is False)
    fx = Fx('f26_0')
    fx.cnt[2] = dict(fx.cnt[2], f26_exact_stale=1)
    check('f26_0: f26_* != 0 on the last line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f26_0')
    fx.ev_scene = [[ev(1, 3, 'off')], [], []]
    check('f26_0: 0 dcc lines -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f26_0')
    fx.mode = 'after'
    check('f26_0: DiagF5Id mode after GuestOut -> dead', run(fx)['control_alive'] is False)
    # 7. admission rows
    for attr, val, name in (('installed', 'f' * 64, 'sha_ok'), ('before', 'e' * 64, 'before_ok'), ('after', 'e' * 64, 'after_ok')):
        fx = Fx('f26_1')
        setattr(fx, attr, val)
        check('admission %s NO' % name, run(fx)[name] is False)
    for tag, k, v in (('f5cmu_1b', 'KYTY_FIX_F5CMU', '0'), ('f5cmu_0b', 'KYTY_FIX_F5CMU', '1'), ('f5cmu_1b', 'KYTY_DIAG_F5ID', '1'),
                      ('f5cmu_0b', 'KYTY_FIX_F26', '0'), ('f26_1', 'KYTY_FIX_F26', '0'), ('f26_0', 'KYTY_FIX_F26', '1'),
                      ('f26_1', 'KYTY_FIX_F5CMU', '0'), ('f26_0', 'KYTY_DIAG_F5ID', '0'), ('f26_1', 'KYTY_DIAG_F5', '0'),
                      ('f16q_w', 'KYTY_FIX_F26', '1'), ('f16q_w', 'KYTY_DIAG_F5ID', '1'), ('f26_1', 'KYTY_FIX_B42', '1'),
                      ('f26_1', 'KYTY_SKIP_CEILING', '3'), ('f5cmu_1b', 'KYTY_GAME_PATCH', 'x'), ('f26_0', 'KYTY_GPU_CHECKPOINTS', '1')):
        fx = Fx(tag)
        fx.env[k] = v
        check('env %s %s=%s -> NO' % (tag, k, v), run(fx)['env_ok'] is False)
    for tag, k in (('f16q_w', 'KYTY_FIX_F5CMU'), ('f16q_w', 'KYTY_FIX_F26'), ('f26_1', 'KYTY_FIX_F26'), ('f5cmu_0b', 'KYTY_FIX_F5CMU')):
        fx = Fx(tag)
        del fx.env[k]
        check('env %s without %s -> NO' % (tag, k), run(fx)['env_ok'] is False)
    fx = Fx('f26_1')
    fx.gates = 'skipceil=3'
    check('gate text with skipceil -> env NO (item 515 N1)', run(fx)['env_ok'] is False)
    fx = Fx('f26_1')
    fx.level_line = 'final_stage'
    check('other level -> not entered', run(fx)['entry_line'] is None)
    fx = Fx('f26_1')
    fx.rows = 330
    check('hold 296 s -> NO', run(fx)['hold_len_ok'] is False)
    fx = Fx('f26_1')
    fx.att = dict(fx.att, hold_exit=3)
    check('hold_exit set -> NO', run(fx)['hold_ok'] is False)
    fx = Fx('f26_1')
    fx.manifest = 'manifest cmp DIFFERENT 1'
    check('manifest differs -> NO', run(fx)['manifest_ok'] is False)
    for t in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: x'):
        fx = Fx('f26_0')
        fx.extra = [t]
        check('interference %r' % t, run(fx)['interference'] is True)
    fx = Fx('f26_1')
    fx.extra = ['Window 1 lost keyboard focus']
    check('focus loss is not interference', run(fx)['interference'] is False)
    for n, ok in ((2999, False), (3000, True)):
        fx = Fx('f26_1')
        fx.idx_n = n
        check('video %d records -> admission %s' % (n, ok), adm(run(fx)) is ok)
    fx = Fx('f26_1')
    fx.glitch = 'x\none-frame glitches: 2\n  video   100 present    101 t=   1.67s diff_prev=9\n  video   200 present    201 t=  3.33s'
    r = run(fx)
    check('glitches 2 at presents 101, 201 (report)', r['glitches'] == 2 and r['glitch_presents'] == [101, 201] and adm(r))
    fx = Fx('f26_1')
    fx.extra = ['FrameTrace: n=999 dt_us=2000000 draws=300', 'GpuHangAbort: x', 'AsyncPipelines: skipped draw h frame=77']
    r = run(fx)
    check('frame >= 1 s, death, skipped draw are report rows', r['k2_after'] == 1 and len(r['death']) == 1 and r['control_alive']
          and r['skips'][0][2] == 77 and r['skipped_draw'] == 1)
    check('luma row read', r['luma'] == ['SCENE first > 5: video 400 present 401 mean 30.0'])
    # 8. the DiagF5 line forms
    fx = Fx('f26_1')
    fx.f5names = R.F5_NAMES[:-1]
    r = run(fx)
    check('63-name line (no f26_deferred_declined) is malformed -> dead', r['f5']['malformed'] == 3 and r['control_alive'] is False)
    fx = Fx('f26_0')
    fx.ev_before = [ds(1, 'prepare', 1, 'off')]
    fx.ev_scene[0] = [ds(2, 'adopt', 3, 'off')]
    r = run(fx)
    check('event before the entry: scene flag False', r['dcc'][0]['scene'] is False and r['dcc'][1]['scene'] is True
          and r['dcc_counts_scene']['off'] == 1 and r['dcc_counts']['off'] == 2)
    # 9. pair A (cmu)
    r0, r1 = run(Fx('f5cmu_0b')), run(Fx('f5cmu_1b'))
    i0 = dict((q, q - 1) for q in range(1, 9001))
    i1 = dict((q, q - 1) for q in range(1, 9001))
    res = P.build('cmu', r0, r1, i0, i1)
    c = res['cmask']
    check('pair A cmask: 2 pairs, nohit of arm 1 1, order kept', c['pairs'] == 2 and c['nohit_arm1'] == 1 and c['order']
          and c['unpaired0'] == 0 and c['unpaired1'] == 1)
    check('pair A cmask window p-1..p+2 (3 -> 2..5)', c['items'][0]['W'] == [2, 3, 4, 5] and c['items'][0]['fix1'] == 'kept_applied')
    d = res['dcc']
    check('pair A dcc: 1 pair although exact differs (na / fresh) - exact not compared (RC2)', d['pairs'] == 1
          and d['items'][0]['exact0'] == 'na' and d['items'][0]['exact1'] == 'fresh')
    r1x = jcopy(r1)
    r1x['dcc'][0] = dict(r1x['dcc'][0], fix='kept')
    d = P.build('cmu', r0, r1x, i0, i1)['dcc']
    check('pair A dcc: fix differs -> unpaired (key carries fix, RC2)', d['pairs'] == 0 and d['unpaired0'] == 1 and d['unpaired1'] == 1)
    r1x = jcopy(r1)
    r1x['dcc'][0] = dict(r1x['dcc'][0], site='prepare')
    check('pair A dcc: site differs -> unpaired', P.build('cmu', r0, r1x, i0, i1)['dcc']['pairs'] == 0)
    r1b = jcopy(r1)
    r1b['events'][0] = dict(r1b['events'][0], present=6)
    check('pair A window over both arms (3 and 6 -> 2..8)', P.build('cmu', r0, r1b, i0, i1)['cmask']['items'][0]['W'] == [2, 3, 4, 5, 6, 7, 8])
    r0c, r1c = jcopy(r0), jcopy(r1)
    r0c['events'][0] = dict(r0c['events'][0], image='a')
    r0c['events'][1] = dict(r0c['events'][1], image='b')
    r1c['events'][0] = dict(r1c['events'][0], image='b')
    r1c['events'][1] = dict(r1c['events'][1], image='a')
    check('pair A: crossed order -> order kept NO', P.build('cmu', r0c, r1c, i0, i1)['cmask']['order'] is False)
    i1m = dict(i1)
    del i1m[3]
    del i1m[5]
    it = P.build('cmu', r0, r1, i0, i1m)['cmask']['items'][0]
    check('pair A: p not in idx of arm 1, window presents 3 and 5 absent', it['p_in1'] is False and it['miss1'] == [3, 5] and it['p_in0'])
    r1g, r0g = jcopy(r1), jcopy(r0)
    r1g['glitch_presents'] = [5, 50]
    r0g['glitch_presents'] = [50]
    its = P.build('cmu', r0g, r1g, i0, i1)['cmask']['items']
    check('pair A: glitch only in arm 1 inside the window', its[0]['gl_only1'] == [5] and its[1]['gl_only1'] == [])
    r0g['glitch_presents'] = [5]
    check('pair A: glitch in both arms is not GLITCH_ONLY_1', P.build('cmu', r0g, r1g, i0, i1)['cmask']['items'][0]['gl_only1'] == [])
    nh = [x for x in res['cmask']['items'] if x['kind'] == 'NOHIT_ARM1'][0]
    check('pair A: nohit window p1-1..p1+2', nh['W'] == [19, 20, 21, 22] and nh['e0'] is None)
    sel = P.sheet_items(res)
    check('pair A sheets: kept_applied and exact_stale pairs and the nohit (3 of 3; no fresh here)', len(sel) == 3)
    r1f = jcopy(r1)
    r1f['events'][0] = dict(r1f['events'][0], fix='fresh')
    sel = P.sheet_items(P.build('cmu', r0, r1f, i0, i1))
    check('pair A sheets: a fresh pair has no event sheet (variant of the executor)', len(sel) == 2
          and all(x[2]['fix1'] != 'fresh' for x in sel))
    pr = P.rows(res)
    check('pair A rows: the RC2 note and ITEM lines', any('reads the ring on the DCC sites (read only, the decision is the old one)' in x
                                                          for x in pr) and sum(1 for x in pr if ' ITEM ' in x) == 4)
    # 10. pair B (f26)
    q0, q1 = run(Fx('f26_0')), run(Fx('f26_1'))
    f0x = Fx('f26_0')
    f0x.ev_scene[0] = [ds(1, 'prepare', 5, 'off'), ds(2, 'adopt', 9, 'off'), ds(3, 'adopt', 12, 'off'), ds(4, 'prepare', 15, 'off',
                                                                                                          exact='na'),
                       ds(5, 'adopt', 18, 'off')]
    q0 = run(f0x)
    res = P.build('f26', q0, q1, i0, i1)
    d = res['dcc']
    check('pair B: 5 pairs by (site, image, dcc) with different fix, order kept', d['pairs'] == 5 and d['order'] and d['unpaired0'] == 0)
    check('pair B classes: kept_applied 2 (prepare + adopt cleared), kept_declined 1, exact_stale 1, fallback 1',
          res['classes'] == dict(kept_applied=2, kept_declined=1, exact_stale=1, fallback=1))
    q1x = jcopy(q1)
    q1x['apply'][0] = dict(q1x['apply'][0], present=10)
    c2 = P.build('f26', q0, q1x, i0, i1)['dcc']['items'][1]
    check('pair B: apply cleared with present differing -> kept_apply_late, window by the event', c2['cls'] == 'kept_apply_late'
          and c2['W'] == [8, 9, 10, 11])
    q1x = jcopy(q1)
    q1x['apply'] = [q1x['apply'][1]]
    check('pair B: no apply line of the n -> kept_no_apply', P.build('f26', q0, q1x, i0, i1)['dcc']['items'][1]['cls'] == 'kept_no_apply')
    q1x = jcopy(q1)
    q1x['apply'][0] = dict(q1x['apply'][0], gpu=12, present=12)
    q1x['dcc'][1] = dict(q1x['dcc'][1], present=12, gpu=12)
    c2 = P.build('f26', q0, q1x, i0, i1)['dcc']['items'][1]
    check('pair B: adopt cleared equal -> kept_applied, window by the apply present (9 / 12 -> 8..14)', c2['cls'] == 'kept_applied'
          and c2['p1'] == 12 and c2['W'] == list(range(8, 15)))
    q0s, q1s = jcopy(q0), jcopy(q1)
    q0s['skips'] = [[1, 'AsyncPipelines', 4], [2, 'AsyncPipelines', 5], [3, 'BindFloor', 9], [4, 'AsyncPipelines', 10]]
    q1s['skips'] = [[1, 'AsyncPipelines', 9], [2, 'AsyncPipelines', 14]]
    it = P.build('f26', q0s, q1s, i0, i1)['dcc']['items'][0]
    check('pair B: skipped draw near [gpu-1, gpu+3] edges (gpu 6: 5 and 9 in, 4 and 10 out)', it['skip0'] == [5, 9] and it['skip1'] == [9])
    q1y = jcopy(q1)
    q1y['dcc'][0] = dict(q1y['dcc'][0], image='999')
    d = P.build('f26', q0, q1y, i0, i1)['dcc']
    check('pair B: image differs -> unpaired both', d['pairs'] == 4 and d['unpaired0'] == 1 and d['unpaired1'] == 1)
    q1y = jcopy(q1)
    q1y['dcc'][0] = dict(q1y['dcc'][0], site='adopt')
    d = P.build('f26', q0, q1y, i0, i1)['dcc']
    check('pair B: site differs -> unpaired both', d['unpaired0'] >= 1 and d['unpaired1'] >= 1)
    check('pair B sheets: every item', len(P.sheet_items(res)) == 5)
    pr = P.rows(res)
    check('pair B rows: classes line and apply line', any('reading classes of arm 1: exact_stale=1 fallback=1 kept_applied=2 kept_declined=1'
                                                          in x for x in pr) and any('arm1 apply: n=2' in x for x in pr))
    # 11. luma
    check('luma first > 5', LU.first_scene([0, 3, 6, 2, 9, 9, 9], 1) == 2)
    check('luma first > 5 held 3', LU.first_scene([0, 3, 6, 2, 9, 9, 9], 3) == 4)
    check('luma held not reached -> None', LU.first_scene([0, 6, 6], 3) is None)
    check('luma threshold strict (5.0 is not > 5)', LU.first_scene([5.0, 5.1], 1) == 1)
    # 12. strict cp1250 output as processes (no PYTHONIOENCODING)
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    base = os.path.join(TMP, 'cp')
    Fx('f26_1').make(base)
    pr = subprocess.run([sys.executable, t_read, '--dir', base, '--tag', 'f26_1'], capture_output=True, env=env)
    check('reader rc 0 under strict cp1250, ASCII, CONTROL F26_1 ALIVE', pr.returncode == 0 and all(b < 128 for b in pr.stdout)
          and b'CONTROL F26_1 ALIVE' in pr.stdout)
    pr = subprocess.run([sys.executable, t_read, '--dir', base, '--tag', 'f5id_ef'], capture_output=True, env=env)
    check('unknown tag refused', pr.returncode != 0)
    for which, a, b in (('cmu', r0, r1), ('f26', q0, q1)):
        j0, j1 = os.path.join(TMP, 'a.json'), os.path.join(TMP, 'b.json')
        json.dump(a, open(j0, 'w'), default=list)
        json.dump(b, open(j1, 'w'), default=list)
        ix = os.path.join(TMP, 'i.idx')
        open(ix, 'w').write(''.join('%d %d 0.0\n' % (i, i + 1) for i in range(100)))
        pr = subprocess.run([sys.executable, t_pair, which, '--json0', j0, '--json1', j1, '--idx0', ix, '--idx1', ix], capture_output=True,
                            env=env)
        check('pair %s rc 0 under strict cp1250, ASCII' % which, pr.returncode == 0 and all(x < 128 for x in pr.stdout)
              and b'F16Q PAIR' in pr.stdout)
    vid = os.path.join(TMP, 'v.mp4')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=64x36:r=60:d=1', '-f',
                    'lavfi', '-i', 'color=c=gray:s=64x36:r=60:d=2', '-filter_complex', '[0:v][1:v]concat=n=2:v=1[o]', '-map', '[o]',
                    '-pix_fmt', 'yuv420p', vid], capture_output=True)
    vix = os.path.join(TMP, 'v.idx')
    open(vix, 'w').write(''.join('%d %d 0.0\n' % (i, i + 11) for i in range(180)))
    pr = subprocess.run([sys.executable, t_luma, vid, vix], capture_output=True, env=env)
    check('luma rc 0 under strict cp1250, ASCII, scene at video 60 present 71', pr.returncode == 0 and all(x < 128 for x in pr.stdout)
          and b'SCENE first > 5: video 60 present 71' in pr.stdout and b'SCENE first > 5 held 60 frames: video 60 present 71' in pr.stdout)
    shutil.rmtree(TMP, ignore_errors=True)
    print('checks %d failed %d' % (N_OK[0] + len(FAIL), len(FAIL)))
    if FAIL:
        print('NOT OK')
        return 1
    print('ALL OK')
    return 0


if __name__ == '__main__':
    try:
        rc = main()
    except Exception as e:  # a crash of the suite is a failure, never a pass
        print('EXCEPTION %s: %s' % (type(e).__name__, str(e)[:200].encode('ascii', 'replace').decode('ascii')))
        print('checks %d failed %d' % (N_OK[0] + len(FAIL) + 1, len(FAIL) + 1))
        print('NOT OK')
        rc = 1
    sys.exit(rc)

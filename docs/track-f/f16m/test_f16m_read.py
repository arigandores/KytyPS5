"""Fixtures of f16m_read.py and f16m_pair.py (track F link F16m, HPP-585): one fixture per member of each control (pair arms =0 / =1, id tags),
per equality of the identity of item 496 (b)(5) (LETTER and VARIANT, the limit), per admission row, per field of the branch 2 / 3 key rows, the
DiagF5 line of 59 names (the old 58-name line is malformed, item 500 (b)(2)), the b42=drawn interference (item 501 (b)(1)), the pair matching,
the window p-1..p+2 (item 495 (g)), the idx presence and the glitch rows, the strict cp1250 output.  The first output line names the suite
and the targets with their sha256; the last line is ALL OK.  ASCII only.   usage: python test_f16m_read.py"""
import hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f16m_read as R
import f16m_pair as P

N_OK = [0]
FAIL = []
# diagF5.cpp of ed4f96d8 :159-:218 - written here, not imported
EXPECTED_TAIL = ['zero_disp', 'f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback', 'dcc_stale_bucket_only',
                 'dcc_stale_fallback', 'cmask_rt_bucket_only', 'f5cmu_exact_cpu']
EXPECTED_ID_LAST = ['keys_fce', 'keys_cs', 'overflow_fce', 'overflow_cs', 'stamp_late']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond):
    if cond:
        N_OK[0] += 1
    else:
        FAIL.append(name)
        print('FAIL %s' % name)


def f5vals(s, cmu=None):
    d = dict((n, 0) for n in R.F5_NAMES)
    d.update(rt_resolves=100 * s, dcc_rt=10 * s, dcc_fce=3 * s, dcc_fce_image=2 * s, dcc_fce_no_image=s, meta_refused_known=2 * s,
             meta_cs_tracked=s, meta_cs_untracked=s, cmask_fce=4 * s, cmask_fce_meta=2 * s, cmask_fce_b42=s, cmask_fce_unapplied=s,
             zero_disp=40)
    if cmu:
        d.update(cmu)
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


def idsum(frame, c=None, exit_=0, id_fce='ok', id_cs='ok'):
    d = dict((n, 0) for n in R.ID_NAMES)
    d.update(fce=2, r5=2, cs=3, img_clear=1, exec_nofill=1, tracked=1, keys_fce=1, keys_cs=2)
    if c:
        d.update(c)
    tail = dict(marks=0, open=0, dcc_fce_no_image=2, meta_cs_untracked=2, meta_cs_tracked=1)
    return ('DiagF5Id: sum frame=%d exit=%d ' % (frame, exit_) + ' '.join('%s=%d' % (n, d[n]) for n in R.ID_NAMES) + ' '
            + ' '.join('%s=%d' % (n, tail[n]) for n in R.SUM_TAIL) + ' id_fce=%s id_cs=%s' % (id_fce, id_cs))


FCE_LINE = ('DiagF5Id: fce frame=10 present=9 slot=0 base=0x0000000510d10000 dcc=0x000000056d898000 fmt=10 nfmt=0 extent=1920x1080 '
            'pitch=1920 size=0x7e9000 dcc_size=0x10000 clear=00000000/00000000 dcc_en=1 key_en=1 reason=r5 info=0x0 entry=absent '
            'clear_mask=0x00000000 fill=0x00000000 fill_size=0x0 fill_seq=0 after=absent after_mask=0x00000000 wr_after=%s cpu_mod=%s key_n=%d')
KF_LINE = ('DiagF5Id: key site=fce base=0x0000000510d10000 dcc=0x000000056d898000 reason=r5 n=%d texture=%d target=0 none=0 exit=0 '
           'cleared=0 bufreads=0')
CS_LINE = ('DiagF5Id: cs frame=12 present=11 shader=0x00000000deadbeef addr=0x000000056c05e000 size=0x1000 read=0 class=exec sub=nofill '
           'value=0x00000000 vclass=- entry=PendingDcc clear_mask=0x00000001 fill=0x00000000 fill_size=0x1000 changed=0 mark=1 key_n=%d')
KC_LINE = 'DiagF5Id: key site=cs shader=0x00000000deadbeef addr=0x000000056c05e000 class=exec n=%d stale_apply=%d'


class Fx(object):
    """A synthetic tag of the F16k2 binary: mode lines, event / id lines, three DiagF5 frame lines, 400 FrameTrace rows of 0.9 s."""

    def __init__(self, tag='f5cmu_1'):
        self.tag = tag
        self.level, self.kind = R.TAGS[tag]
        self.cmu = [dict() for _ in range(3)]
        self.ev_before = []          # event lines before the entry
        self.ev_scene = [[], [], []]  # event lines after the entry, before frame line i
        self.ev_tail = []            # event lines after the last frame line
        self.id_before = []
        self.id_scene = [[], [], []]
        self.mode = 'before'
        self.extra_before = []
        self.extra = []
        self.dt = 900000
        self.rows = 400
        self.level_line = self.level
        self.env = {'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0', 'KYTY_DIAG_F5': '1'}
        if self.kind == 'pair0':
            self.env['KYTY_FIX_F5CMU'] = '0'
            self.ev_scene[0] = [ev(1, 3, 'off'), ev(2, 8, 'off')]
        elif self.kind == 'pair1':
            self.env['KYTY_FIX_F5CMU'] = '1'
            self.ev_scene[0] = [ev(1, 3, 'kept_applied'), ev(2, 8, 'exact_stale', 'cpu')]
            self.ev_scene[1] = [nohit(1, 20, 'kept', 'decode')]
            self.cmu = [dict(f5cmu_kept=1, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1),
                        dict(f5cmu_kept=2, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1),
                        dict(f5cmu_kept=2, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1)]
        else:
            self.env['KYTY_DIAG_F5ID'] = '1'
            self.id_before = [FCE_LINE % ('none', '0', 1), KF_LINE % (1, 0), idsum(5, dict(fce=1, r5=1, cs=1, exec_nofill=1, tracked=0,
                                                                                          img_clear=0, keys_cs=1),
                                                                                 ) .replace('dcc_fce_no_image=2', 'dcc_fce_no_image=1')
                              .replace('meta_cs_untracked=2', 'meta_cs_untracked=1').replace('meta_cs_tracked=1', 'meta_cs_tracked=0')]
            self.id_scene[0] = [FCE_LINE % ('exact', '1', 2), CS_LINE % 1, KC_LINE % (1, 0), KF_LINE % (2, 1), idsum(700)]
            self.id_scene[2] = [idsum(1300, dict(stamp_late=0)), 'DiagF5Id: stale_apply site=mat addr=0x000000056c05e000 '
                                'image=0x0000000510d10000 shader=0x00000000deadbeef class=exec dframes=100', KC_LINE % (1, 1)]
        self.att = {'outcome': 'ok', 'hold_exit': None, 'hold_s': 330.1, 'close_rc': 0, 'close_killed': False}
        self.installed = R.BIN_EXPECT
        self.before = R.WANT
        self.after = R.WANT
        self.manifest = 'manifest cmp EQUAL files 3323 listsha 00'
        self.idx_n = 9000 if self.kind != 'id' else None
        self.glitch = 'x: 9000 frames 960x540, index entries 9000\none-frame glitches: 0\n'
        self.f5names = None

    def log(self):
        L = ['[main] Fork build arigandores/KytyPS5 KytyPS5-2026-09-15-6a2987a-2240-ged4f96d8, x64',
             'Shader translation cache: _ShaderCache\\PPSA21564\\' + R.DIR_FIX]
        modes = ['DiagF5: mode=1']
        if self.kind == 'pair1':
            modes.append('FixF5Cmu: mode=1')
        if self.kind == 'id':
            modes.append('DiagF5Id: mode=1')
        if self.mode == 'before':
            L += modes
        L += self.extra_before
        L.append('GuestOut: boot')
        if self.mode == 'after':
            L += modes
        L += self.ev_before + self.id_before
        L.append('GuestOut: Level has started: %s' % self.level_line)
        L.append('FrameTrace: n=100 dt_us=16000 draws=300')
        per = self.rows // 3
        for i in range(3):
            for j in range(per):
                L.append('FrameTrace: n=%d dt_us=%d draws=300' % (101 + i * per + j, self.dt))
            L += self.ev_scene[i] + self.id_scene[i]
            L.append(f5line(100 + (i + 1) * per, f5vals(i + 1, self.cmu[i]), self.f5names))
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
        json.dump({'env': self.env, 'attempts': [self.att]}, open(os.path.join(base, 'es.json'), 'w'))
        for k, v in (('installed_sha', self.installed), ('installed_before', self.before), ('installed_after', self.after),
                     ('manifest_cmp', self.manifest), ('warm', 'variant form: x/%s present at T' % R.DIR_FIX),
                     ('glitch', self.glitch), ('sheet', 'sheet: x.png frames 9000 step 187 tiles 8x6')):
            open(os.path.join(base, k + '.txt'), 'w').write(v + '\n')
        open(os.path.join(base, 'bin.exe'), 'wb').write(b'MZ..' + R.VERSIONS[0] + b'..')
        if self.idx_n:
            open(os.path.join(base, 'rec.idx'), 'w').write(''.join('%d %d %.3f\n' % (i, i + 1, i / 60.0) for i in range(self.idx_n)))
        return R.read(R.paths(self.tag, base), self.tag)


TMP = tempfile.mkdtemp(prefix='f16m_fx_')
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
    if r['kind'] != 'id':
        ok = ok and (r['idx_records'] or 0) >= R.VIDEO_MIN
    return ok


def main():
    me = os.path.abspath(__file__)
    t_read = os.path.join(HERE, 'f16m_read.py')
    t_pair = os.path.join(HERE, 'f16m_pair.py')
    print('suite test_f16m_read.py sha256 %s target f16m_read.py sha256 %s target f16m_pair.py sha256 %s' % (sha(me), sha(t_read),
                                                                                                         sha(t_pair)))
    # 0. the name lists against the code (written here)
    check('F5 names: 59, tail of F16k2 in order', len(R.F5_NAMES) == 59 and R.F5_NAMES[-9:] == EXPECTED_TAIL)
    check('Id names: 36, stamp_late last', len(R.ID_NAMES) == 36 and R.ID_NAMES[-5:] == EXPECTED_ID_LAST)
    # 1. good tags
    for tag in R.TAGS:
        r = run(Fx(tag))
        check('good %s control alive' % tag, r['control_alive'])
        check('good %s admission rows' % tag, adm(r))
        check('good %s 3 frame lines, health' % tag, r['f5']['lines'] == 3 and r['f5']['health'])
        rows = R.rows(r)
        check('good %s CONTROL line' % tag, ('  CONTROL %s ALIVE' % r['kind'].upper()) in rows)
    r = run(Fx('f5cmu_1'))
    check('pair1 events 3: two fce, one nohit', r['limits']['fce_lines'] == 2 and r['limits']['nohit_lines'] == 1)
    check('pair1 fix counts', r['ev_counts']['kept_applied'] == 1 and r['ev_counts']['exact_stale'] == 1 and r['ev_counts']['kept'] == 1)
    check('pair1 why=cpu parsed', [e['why'] for e in r['events']] == [None, 'cpu', 'decode'])
    check('pair1 nohit b42 none, applied None', r['events'][2]['b42'] == 'none' and r['events'][2]['applied'] is None)
    check('pair1 identity letter all equal', all(x[3] for x in r['id496_letter']) and len(r['id496_letter']) == 5)
    check('pair1 hold 359.1', abs(r['hold_s'] - 0.9 * 399) < 0.05)
    # 2. pair1 members
    fx = Fx('f5cmu_1')
    fx.mode = 'after'
    check('pair1: FixF5Cmu mode after GuestOut -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1')
    fx.ev_scene = [[], [], []]
    fx.cmu = [dict(), dict(), dict()]
    r = run(fx)
    check('pair1: 0 events -> dead (member DiagF5Ev >= 1)', ctl(r, 'DiagF5Ev lines >= 1') is False and not r['control_alive'])
    fx = Fx('f5cmu_1')
    fx.ev_scene[1].append('DiagF5Ev: cmask_fce n=x present=1')
    check('pair1: malformed event -> dead', run(fx)['control_alive'] is False)
    for i, name in enumerate(['f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback']):
        fx = Fx('f5cmu_1')
        fx.cmu[2] = dict(fx.cmu[2])
        fx.cmu[2][name] = fx.cmu[2].get(name, 0) + 1
        if name == 'f5cmu_kept_applied':
            fx.cmu[2]['f5cmu_kept'] += 1
            r = run(fx)
            check('pair1: identity kept_applied off -> dead', not r['id496_letter'][1][3] and r['control_alive'] is False)
            continue
        r = run(fx)
        check('pair1: identity %s off -> dead' % name, not r['id496_letter'][i][3] and r['control_alive'] is False)
    fx = Fx('f5cmu_1')
    fx.cmu[2] = dict(fx.cmu[2], f5cmu_exact_cpu=0)
    r = run(fx)
    check('pair1: exact_cpu row beyond the letter is not a member', not r['id496_letter'][4][3] and r['control_alive'])
    fx = Fx('f5cmu_1')
    fx.ev_tail = [ev(3, 400, 'fallback')]
    r = run(fx)
    check('pair1: event after the last frame line - LETTER different, VARIANT equal', not r['id496_letter'][3][3]
          and all(x[3] for x in r['id496_variant'][:4]) and r['control_alive'] is False)
    fx = Fx('f5cmu_1')
    fx.ev_scene[2] = [ev(64, 300, 'fallback')]
    r = run(fx)
    check('pair1: limit exhausted (n=64) -> LIMIT row, control alive', r['id496_limit'] and r['control_alive'])
    fx = Fx('f5cmu_1')
    fx.cmu[1] = dict(f5cmu_kept=2, f5cmu_kept_applied=1, f5cmu_exact_stale=1, f5cmu_exact_cpu=1)
    for i in range(3):
        fx.cmu[i] = dict(fx.cmu[i])
    fx.cmu[1]['f5cmu_kept_applied'] = 3
    fx.cmu[1]['f5cmu_kept'] = 2
    r = run(fx)
    check('pair1: kept_applied > kept on the middle line -> dead', r['control_alive'] is False and r['f5']['ident_bad_n'] >= 1)
    fx = Fx('f5cmu_1')
    fx.cmu[0] = dict(fx.cmu[0], f5cmu_exact_cpu=2)
    check('pair1: exact_cpu > exact_stale on the first line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1')
    fx.extra = ['DiagF5Id: mode=0 needs=KYTY_DIAG_F5']
    check('pair1: a DiagF5Id line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_1')
    fx.ev_scene[1] = [nohit(1, 20, 'kept', 'decode', b42='drawn')]
    r = run(fx)
    check('pair1: b42=drawn -> interference row, drawn 1', r['drawn'] == 1 and r['interference'] and not adm(r))
    # 3. pair0 members
    fx = Fx('f5cmu_0')
    fx.extra = ['FixF5Cmu: mode=1']
    check('pair0: a FixF5Cmu line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0')
    fx.ev_scene[1] = [ev(3, 30, 'fresh')]
    check('pair0: an event fix != off -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0')
    fx.ev_scene[1] = [nohit(1, 30, 'off')]
    check('pair0: a nohit line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0')
    fx.cmu[1] = dict(f5cmu_fallback=1)
    fx.cmu[2] = dict(f5cmu_fallback=1)
    check('pair0: f5cmu_* != 0 on a line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0')
    fx.extra = ['DiagF5Id: sum frame=1']
    check('pair0: a DiagF5Id line -> null control dead', run(fx)['control_alive'] is False)
    fx = Fx('f5cmu_0')
    fx.ev_scene = [[], [], []]
    check('pair0: 0 events -> dead', run(fx)['control_alive'] is False)
    # 4. id members
    for tag in ('f5id_sg', 'f5id_ef'):
        fx = Fx(tag)
        fx.mode = 'after'
        check('%s: DiagF5Id mode after GuestOut -> dead' % tag, run(fx)['control_alive'] is False)
    for pos, which in ((0, 'fce'), (1, 'cs'), (2, 'fce')):
        fx = Fx('f5id_bh')
        if pos == 0:
            fx.id_before[2] = fx.id_before[2].replace('id_fce=ok', 'id_fce=bad')
        elif pos == 1:
            fx.id_scene[0][4] = fx.id_scene[0][4].replace('id_cs=ok', 'id_cs=bad')
        else:
            fx.id_scene[2][0] = fx.id_scene[2][0].replace('id_fce=ok', 'id_fce=bad')
        r = run(fx)
        check('id: id_%s=bad on sum line %d -> dead' % (which, pos), r['control_alive'] is False and len(r['id_bad_lines']) == 1)
    for name, c in (('reasons != dcc_fce_no_image', dict(r5=3, fce=3)), ('fce != reasons', dict(fce=3)), ('r0 != 0', dict(r0=1)),
                    ('cs classes != meta_cs_untracked', dict(exec_fill_other=1)), ('tracked != meta_cs_tracked', dict(tracked=2)),
                    ('meta_clear in the cs sum', dict(meta_clear=1))):
        fx = Fx('f5id_bh')
        fx.id_scene[2][0] = idsum(1300, c)
        r = run(fx)
        check('id recount: %s with printed ok -> dead' % name, r['control_alive'] is False and len(r['id_bad_lines']) == 1)
    fx = Fx('f5id_bh')
    fx.id_scene[2][0] = fx.id_scene[2][0].replace(' stamp_late=0', '')
    r = run(fx)
    check('id: a sum line without stamp_late is malformed -> dead', r['sum_bad'] == 1 and r['control_alive'] is False)
    fx = Fx('f5id_bh')
    fx.id_before = []
    fx.id_scene = [[], [], []]
    check('id: no sum line -> dead', run(fx)['control_alive'] is False)
    for tag, alive in (('f5id_ef', False), ('f5id_eb', False), ('f5id_sg', True), ('f5id_bh', True)):
        fx = Fx(tag)
        fx.id_scene[2][0] = idsum(1300, dict(fce=0, r5=0, keys_fce=0)).replace('dcc_fce_no_image=2', 'dcc_fce_no_image=0')
        r = run(fx)
        check('id %s: fce = 0 on the last sum -> control %s' % (tag, 'alive' if alive else 'dead'), r['control_alive'] is alive)
    fx = Fx('f5id_sg')
    fx.id_scene[2][0] = idsum(1300, dict(cs=0, img_clear=0, exec_nofill=0, tracked=0)).replace(
        'meta_cs_untracked=2', 'meta_cs_untracked=0').replace('meta_cs_tracked=1', 'meta_cs_tracked=0')
    check('id: cs = 0 on the last sum -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5id_sg')
    fx.extra = ['FixF5Cmu: mode=1']
    check('id: FixF5Cmu line -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5id_sg')
    fx.cmu[2] = dict(f5cmu_kept=1)
    check('id: f5cmu_* != 0 -> dead', run(fx)['control_alive'] is False)
    fx = Fx('f5id_sg')
    fx.id_scene[2][0] = idsum(1300, dict(meta_clear=1, exec_nofill=0))
    check('id: meta_clear > 0 -> dead', run(fx)['control_alive'] is False)
    # 5. branch keys
    r = run(Fx('f5id_ef'))
    b2 = r['branch2']
    check('B2 one key, n 2, n_at_entry 1, in scene 1', len(b2) == 1 and b2[0]['n'] == 2 and b2[0]['n_at_entry'] == 1
          and b2[0]['in_scene'] == 1)
    check('B2 fields: wr_after none,exact; cpu_mod 0,1; dcc_en 1; entry absent; texture 1', b2[0]['wr_after'] == ['exact', 'none']
          and b2[0]['cpu_mod'] == ['0', '1'] and b2[0]['dcc_en'] == ['1'] and b2[0]['entry'] == ['absent'] and b2[0]['next']['texture'] == 1)
    check('B2 printed 2, in scene 1', b2[0]['printed'] == 2 and b2[0]['printed_in_scene'] == 1)
    fx = Fx('f5id_ef')
    fx.id_before = [x for x in fx.id_before if 'key site=fce' not in x]
    b2x = run(fx)['branch2']
    check('B2 n_at_entry from the event line key_n without a key line before the entry', b2x[0]['n_at_entry'] == 1
          and b2x[0]['in_scene'] == 1)
    b3 = r['branch3']
    check('B3 one key exec n 1 stale_apply 1 (last key line)', len(b3) == 1 and b3[0]['cls'] == 'exec' and b3[0]['stale_apply'] == 1
          and b3[0]['in_scene'] == 1 and b3[0]['sub'] == ['nofill'] and b3[0]['mark'] == ['1'])
    check('stale_apply line parsed', len(r['stale_lines']) == 1 and r['stale_lines'][0]['site'] == 'mat')
    check('stamp_late of the last sum 0', r['stamp_late'] == 0)
    fx = Fx('f5id_ef')
    fx.id_scene[2][0] = idsum(1300, dict(stamp_late=3))
    check('stamp_late 3 read (no member)', run(fx)['stamp_late'] == 3)
    rows = R.rows(r)
    check('rows: B2KEY and B3KEY lines', any(x.startswith('  B2KEY ') for x in rows) and any(x.startswith('  B3KEY ') for x in rows))
    # 6. admission rows
    for attr, val, name in (('installed', 'f' * 64, 'sha_ok'), ('before', 'e' * 64, 'before_ok'), ('after', 'e' * 64, 'after_ok')):
        fx = Fx('f5cmu_1')
        setattr(fx, attr, val)
        check('admission %s NO' % name, run(fx)[name] is False)
    for tag, k, v in (('f5cmu_1', 'KYTY_FIX_F5CMU', '0'), ('f5cmu_0', 'KYTY_FIX_F5CMU', '1'), ('f5cmu_1', 'KYTY_DIAG_F5ID', '1'),
                      ('f5id_sg', 'KYTY_FIX_F5CMU', '1'), ('f5id_sg', 'KYTY_DIAG_F5ID', '0'), ('f5cmu_0', 'KYTY_DIAG_F5', '0'),
                      ('f5id_eb', 'KYTY_FIX_B42', '1'), ('f5cmu_1', 'KYTY_GAME_PATCH', 'x'), ('f5cmu_1', 'KYTY_GPU_CHECKPOINTS', '1'),
                      ('f5id_bh', 'KYTY_DIAG_F6', '1')):
        fx = Fx(tag)
        fx.env[k] = v
        check('env %s %s=%s -> NO' % (tag, k, v), run(fx)['env_ok'] is False)
    fx = Fx('f5cmu_0')
    del fx.env['KYTY_FIX_F5CMU']
    check('env f5cmu_0 without KYTY_FIX_F5CMU -> NO', run(fx)['env_ok'] is False)
    fx = Fx('f5cmu_1')
    fx.level_line = 'final_stage'
    check('other level -> not entered', run(fx)['entry_line'] is None)
    fx = Fx('f5cmu_1')
    fx.rows = 330
    check('hold 296 s -> NO', run(fx)['hold_len_ok'] is False)
    fx = Fx('f5cmu_1')
    fx.att = dict(fx.att, hold_exit=3)
    check('hold_exit set -> NO', run(fx)['hold_ok'] is False)
    fx = Fx('f5cmu_1')
    fx.manifest = 'manifest cmp DIFFERENT 1'
    check('manifest differs -> NO', run(fx)['manifest_ok'] is False)
    for t in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: x'):
        fx = Fx('f5cmu_0')
        fx.extra = [t]
        check('interference %r' % t, run(fx)['interference'] is True)
    fx = Fx('f5cmu_1')
    fx.extra = ['Window 1 lost keyboard focus']
    check('focus loss is not interference', run(fx)['interference'] is False)
    fx = Fx('f5cmu_1')
    fx.idx_n = 2999
    check('video 2999 records -> admission NO', not adm(run(fx)))
    fx = Fx('f5cmu_1')
    fx.idx_n = 3000
    check('video 3000 records -> admission YES', adm(run(fx)))
    fx = Fx('f5cmu_1')
    fx.glitch = 'x\none-frame glitches: 2\n  video   100 present    101 t=   1.67s diff_prev=9\n  video   200 present    201 t=  3.33s'
    r = run(fx)
    check('glitches 2 at presents 101, 201 (report)', r['glitches'] == 2 and r['glitch_presents'] == [101, 201] and adm(r))
    fx = Fx('f5cmu_1')
    fx.extra = ['FrameTrace: n=999 dt_us=2000000 draws=300', 'GpuHangAbort: x']
    r = run(fx)
    check('frame >= 1 s and death are report rows', r['k2_after'] == 1 and len(r['death']) == 1 and r['control_alive'])
    # 7. the DiagF5 line forms
    fx = Fx('f5cmu_0')
    fx.f5names = R.F5_NAMES[:-1]
    r = run(fx)
    check('58-name line (no f5cmu_exact_cpu) is malformed -> dead', r['f5']['malformed'] == 3 and r['control_alive'] is False)
    fx = Fx('f5cmu_0')
    fx.ev_before = [ev(1, 1, 'off')]
    fx.ev_scene[0] = [ev(2, 3, 'off')]
    r = run(fx)
    check('event before the entry: scene flag False', r['events'][0]['scene'] is False and r['events'][1]['scene'] is True
          and r['ev_counts_scene']['off'] == 1 and r['ev_counts']['off'] == 2)
    r = run(Fx('f5id_sg'))
    check('F26 row values', r['f26'] == dict(dcc_stale_bucket_only=0, dcc_stale_fallback=0, cmask_rt_bucket_only=0))
    # 8. the pair
    r0 = run(Fx('f5cmu_0'))
    fx = Fx('f5cmu_1')
    r1 = run(fx)
    i0 = dict((q, q - 1) for q in range(1, 9001))
    i1 = dict((q, q - 1) for q in range(1, 9001))
    res = P.build(r0, r1, i0, i1)
    check('pair: 2 pairs, nohit of arm 1 1, order kept', res['pairs'] == 2 and res['nohit_arm1'] == 1 and res['order']
          and res['unpaired0'] == 0 and res['unpaired1'] == 1)
    it = res['items'][0]
    check('pair window p-1..p+2 (p0 = p1 = 3 -> 2..5)', it['W'] == [2, 3, 4, 5] and it['fix1'] == 'kept_applied')
    r1b = json.loads(json.dumps(r1, default=list))
    r1b['events'][0] = dict(r1b['events'][0], present=6)
    res = P.build(r0, r1b, i0, i1)
    check('pair window over both arms (3 and 6 -> 2..8)', res['items'][0]['W'] == [2, 3, 4, 5, 6, 7, 8])
    r0b = json.loads(json.dumps(r0, default=list))
    r0b['events'][0] = dict(r0b['events'][0], image='abc')
    res = P.build(r0b, r1, i0, i1)
    check('pair: another image -> unpaired both', res['pairs'] == 1 and res['unpaired0'] == 1 and res['unpaired1'] == 2)
    r0c = json.loads(json.dumps(r0, default=list))
    r1c = json.loads(json.dumps(r1, default=list))
    r0c['events'][0] = dict(r0c['events'][0], image='a')
    r0c['events'][1] = dict(r0c['events'][1], image='b')
    r1c['events'][0] = dict(r1c['events'][0], image='b')
    r1c['events'][1] = dict(r1c['events'][1], image='a')
    res = P.build(r0c, r1c, i0, i1)
    check('pair: crossed order -> pairs 2, order kept NO', res['pairs'] == 2 and res['order'] is False)
    check('pair: order kept YES on the good pair', P.build(r0, r1, i0, i1)['order'] is True)
    i1m = dict(i1)
    del i1m[3]
    del i1m[5]
    res = P.build(r0, r1, i0, i1m)
    check('pair: p not in idx of arm 1, window present 5 absent', res['items'][0]['p_in1'] is False and res['items'][0]['miss1'] == [3, 5]
          and res['items'][0]['p_in0'] is True)
    r1g = json.loads(json.dumps(r1, default=list))
    r1g['glitch_presents'] = [5, 50]
    r0g = json.loads(json.dumps(r0, default=list))
    r0g['glitch_presents'] = [50]
    res = P.build(r0g, r1g, i0, i1)
    check('pair: glitch only in arm 1 inside the window', res['items'][0]['gl_only1'] == [5] and res['items'][1]['gl_only1'] == [])
    r0g['glitch_presents'] = [5]
    res = P.build(r0g, r1g, i0, i1)
    check('pair: glitch in both arms is not GLITCH_ONLY_1', res['items'][0]['gl_only1'] == [])
    nh = [x for x in P.build(r0, r1, i0, i1)['items'] if x['kind'] == 'NOHIT_ARM1'][0]
    check('pair: nohit window p1-1..p1+2 in both arms', nh['W'] == [19, 20, 21, 22] and nh['e0'] is None and nh['fix1'] == 'kept')
    pr = P.rows(P.build(r0, r1, i0, i1))
    check('pair rows ASCII and ITEM lines', all(all(ord(c) < 128 for c in x) for x in pr) and sum(1 for x in pr if '  ITEM ' in x) == 3)
    # 9. strict cp1250 output of both scripts as processes (no PYTHONIOENCODING)
    base = os.path.join(TMP, 'cp')
    Fx('f5id_ef').make(base)
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    pr = subprocess.run([sys.executable, t_read, '--dir', base, '--tag', 'f5id_ef'], capture_output=True, env=env)
    check('reader rc 0 under strict cp1250', pr.returncode == 0)
    check('reader output ASCII only', all(b < 128 for b in pr.stdout) and len(pr.stdout) > 1000)
    check('reader output has CONTROL ID ALIVE', b'CONTROL ID ALIVE' in pr.stdout)
    pr = subprocess.run([sys.executable, t_read, '--dir', base, '--tag', 'f5_xx'], capture_output=True, env=env)
    check('unknown tag refused', pr.returncode != 0)
    j0, j1 = os.path.join(TMP, 'r0.json'), os.path.join(TMP, 'r1.json')
    json.dump(r0, open(j0, 'w'), default=list)
    json.dump(r1, open(j1, 'w'), default=list)
    ix = os.path.join(TMP, 'i.idx')
    open(ix, 'w').write(''.join('%d %d 0.0\n' % (i, i + 1) for i in range(100)))
    pr = subprocess.run([sys.executable, t_pair, '--json0', j0, '--json1', j1, '--idx0', ix, '--idx1', ix], capture_output=True, env=env)
    check('pair rc 0 under strict cp1250, ASCII', pr.returncode == 0 and all(b < 128 for b in pr.stdout) and b'F16M PAIR' in pr.stdout)
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

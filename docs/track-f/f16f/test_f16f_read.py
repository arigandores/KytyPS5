"""Fixtures of f16f_read.py (track F link F16f, HPP-523): one fixture per member of the controls, per identity (violation on the first,
a middle and the last line; all lines holding), per line_mismatch (both directions, LETTER and VARIANT), per member of item 433 (v)(i)-(iv)
inputs, per admission row, the null control, the B set, the strict cp1250 output.  The first output line names the suite and the target with
their sha256; the last line is ALL OK.  ASCII only.   usage: python test_f16f_read.py"""
import copy, hashlib, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f16f_read as R

N_OK = [0]
FAIL = []
# F16d report section 2 (KytyPS5 236b6504:docs/track-f/f16d.md table) and diagF5.h of 56b04817 - written here, not imported
EXPECTED_FAMILIES = [
    ('dcc_rt_pending', ['dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial', 'dcc_rt_skip_decode', 'dcc_rt_skip_layers']),
    ('dcc_mat_pending', ['dcc_mat_cleared', 'dcc_mat_undecoded']),
    ('dcc_fce', ['dcc_fce_image', 'dcc_fce_no_image']),
    ('dcc_fill_meta', ['dcc_fill_clear', 'dcc_fill_uncompressed', 'dcc_fill_unknown']),
    ('meta_refused_known', ['meta_cs_tracked', 'meta_cs_untracked', 'meta_dma_untracked', 'meta_dma_noclear']),
    ('cmask_rt_pending', ['cmask_rt_cleared', 'cmask_rt_skip_value', 'cmask_rt_skip_partial', 'cmask_rt_skip_decode', 'cmask_rt_skip_layers']),
    ('cmask_fce', ['cmask_fce_noimage', 'cmask_fce_meta', 'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill', 'cmask_fce_drawn',
                   'cmask_fce_b42', 'cmask_fce_unapplied'])]
# item 427 (b) and item 458 (b)
EXPECTED_B = ['dcc_fill_unknown', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial', 'dcc_rt_skip_decode', 'dcc_rt_skip_layers',
              'dcc_mat_undecoded', 'dcc_fce_no_image', 'meta_cs_untracked', 'meta_dma_untracked', 'cmask_rt_skip_value',
              'cmask_rt_skip_partial', 'cmask_rt_skip_decode', 'cmask_rt_skip_layers', 'cmask_fce_msaa', 'cmask_fce_nofill',
              'cmask_fce_unapplied', 'cmask_fce_layout']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check(name, cond):
    if cond:
        N_OK[0] += 1
    else:
        FAIL.append(name)
        print('FAIL %s' % name)


def f5vals(s):
    d = dict((n, 0) for n in R.F5_NAMES)
    d.update(rt_resolves=100 * s, dcc_rt=10 * s, rtcheck_meta=5, dcc_rt_pending=4 * s, dcc_rt_cleared=4 * s, dcc_mat_pending=2 * s,
             dcc_mat_cleared=2 * s, dcc_fce=3 * s, dcc_fce_image=3 * s, dcc_fill_all=40, dcc_fill_meta=6 * s, dcc_fill_clear=5 * s,
             dcc_fill_uncompressed=s, meta_refused_known=2 * s, meta_cs_tracked=2 * s, cmask_rt_pending=s, cmask_rt_cleared=s,
             cmask_fce=4 * s, cmask_fce_meta=2 * s, cmask_fce_b42=s, cmask_fce_drawn=s, round_unorm=3, ds_unbound=2, ds_unbound_clear=1,
             stereo_writes=20, zero_disp=40, fmask_read=s)
    return d


def f6vals(s):
    return dict(draws=10 * s, draws_idx=4 * s, draws_auto=2 * s, draws_ind=s, draws_mesh=3 * s, ps_draws=9 * s, s_bound=20 * s,
                s_addr0_fmt=0, s_addr0_nofmt=5 * s, s_mask0_addr=5 * s, s_empty=50 * s, h_bound=20 * s, bound_missing=0, bound_extra=0,
                w_total=30 * s, w_bound=20 * s, w_mask0=6 * s, w_addr0_fmt=0, w_addr0_nofmt=4 * s, w_ge8=0)


def line(tag, frame, d, names, drop=None):
    return '%s: frame=%d ' % (tag, frame) + ' '.join('%s=%d' % (n, d[n]) for n in names if n != drop)


class Fx(object):
    """A synthetic tag: knobs on, journal lines, three DiagF5 / DiagF6 frame lines, 400 FrameTrace rows of 0.9 s after the entry."""

    def __init__(self, tag='f5_sg'):
        self.tag = tag
        self.level, self.kind = R.TAGS[tag]
        self.diag = self.kind == 'diag'
        self.f5 = [f5vals(s) for s in (1, 2, 3)]
        self.f6 = [f6vals(s) for s in (1, 2, 3)]
        self.journal = dict(meta=1, round=1, ds=1, stereo=16, zero=32, fill=32)
        self.journal_after = {}
        self.mode5 = self.mode6 = 'before'
        self.dt = 900000
        self.rows = 400
        self.extra = []
        self.extra_before = []
        self.drop5 = None
        self.level_line = self.level
        self.scene_change_at = None
        self.env = {'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
        if self.diag:
            self.env.update(KYTY_DIAG_F5='1', KYTY_DIAG_F6='1')
        self.att = {'outcome': 'ok', 'hold_exit': None, 'hold_s': 330.1, 'close_rc': 0, 'close_killed': False}
        self.installed = R.BIN_EXPECT
        self.before = R.WANT
        self.after = R.WANT
        self.manifest = 'manifest cmp EQUAL files 3323 listsha 00'
        self.binver = True
        self.prefix5 = ''

    def log(self):
        L = ['[main] Fork build arigandores/KytyPS5 KytyPS5-2026-09-15-6a2987a-1881-g4950557a, x64',
             'Shader translation cache: C:\\kyty\\KytyPS5\\ps5 em\\_ShaderCache\\PPSA21564\\' + R.DIR_FIX]
        if self.diag and self.mode5 == 'before':
            L.append('DiagF5: mode=1')
        if self.diag and self.mode6 == 'before':
            L.append('DiagF6: mode=1')
        L += self.extra_before
        L.append('GuestOut: boot')
        if self.diag and self.mode5 == 'after':
            L.append('DiagF5: mode=1')
        if self.diag and self.mode6 == 'after':
            L.append('DiagF6: mode=1')
        names = [('meta', 'RenderTarget: temporary: ignoring PS5 color metadata fast_clear=true dcc=false'),
                 ('round', 'RenderTarget: temporary: ignoring PS5 color round mode'),
                 ('ds', 'DepthTarget: ignoring enabled depth/stencil state without a bound attachment'),
                 ('stereo', 'warning: ignoring indirect uc reg GE_STEREO_CNTL at 0x10, value = 0x00000000'),
                 ('zero', 'GraphicsRenderDispatchDirect: skipping zero-sized dispatch groups=0x1x1'),
                 ('fill', 'GraphicsRenderDispatchDirect: metadata fill shader=0x1 addr=0x2')]
        for k, t in names:
            L += [t] * self.journal[k]
        L.append('GuestOut: Level has started: %s' % self.level_line)
        L.append('FrameTrace: n=100 dt_us=16000 draws=300')
        per = self.rows // 3
        for i in range(3):
            for j in range(per):
                n = 101 + i * per + j
                if self.scene_change_at is not None and n == self.scene_change_at:
                    L.append('GuestOut: Level has started: other_level')
                L.append('FrameTrace: n=%d dt_us=%d draws=300' % (n, self.dt))
            if self.diag:
                L.append(self.prefix5 + line('DiagF5', 100 + (i + 1) * per, self.f5[i], R.F5_NAMES,
                                             self.drop5 if i == 1 else None))
                L.append(line('DiagF6', 100 + (i + 1) * per, self.f6[i], R.F6_NAMES))
        for k, t in names:
            L += [t] * self.journal_after.get(k, 0)
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
                     ('manifest_cmp', self.manifest),
                     ('warm', 'warm form: x/%s present at 2026-10-04T00:00:00Z' % R.DIR_FIX)):
            open(os.path.join(base, k + '.txt'), 'w').write(v + '\n')
        open(os.path.join(base, 'bin.exe'), 'wb').write(b'MZ..' + (R.VERSION if self.binver else b'other') + b'..')
        return R.read(R.paths(self.tag, base), self.tag)


TMP = tempfile.mkdtemp(prefix='f16f_fx_')
K = [0]


def run(fx):
    K[0] += 1
    return fx.make(os.path.join(TMP, 'fx%03d' % K[0]))


def ctl(res, knob, sub):
    for name, val in res[knob]['control']:
        if sub in name:
            return val
    return 'ABSENT'


def main():
    me = os.path.abspath(__file__)
    target = os.path.join(HERE, 'f16f_read.py')
    print('suite test_f16f_read.py sha256 %s target f16f_read.py sha256 %s' % (sha(me), sha(target)))
    # 1. the good tags
    for tag in ('f5_sg', 'f5_ef', 'f5_bh', 'f5_eb'):
        r = run(Fx(tag))
        check('good %s F5 alive' % tag, r['f5']['control_alive'])
        check('good %s F6 alive' % tag, r['f6']['control_alive'])
        check('good %s admission rows' % tag, r['sha_ok'] and r['version_ok'] and r['before_ok'] and r['after_ok'] and r['env_ok']
              and r['entry_line'] is not None and r['hold_len_ok'] and r['hold_ok'] and r['manifest_ok'] and not r['interference'])
        check('good %s B sum 0' % tag, r['f5']['b_sum'] == 0)
        check('good %s mismatch letter 0' % tag, all(r['f5']['mismatch_letter'][k] == 0 for k, _ in R.JOURNAL))
        check('good %s last line = third' % tag, r['f5']['last'] == dict(f5vals(3), frame=r['f5']['last']['frame']))
        check('good %s 3 lines each' % tag, r['f5']['lines'] == 3 and r['f6']['lines'] == 3)
        check('good %s rev and dir and warm' % tag, r['rev_row'] == 'YES' and r['dir_ok'] and r['warm_ok'])
    r = run(Fx('f5_sg'))
    check('good hold 359.1 s', abs(r['hold_s'] - 0.9 * 399) < 0.05)
    check('good parents zero none', r['f5']['parents_zero'] == [])
    check('good F6 inputs all 0', all(v == 0 for v in r['f6']['inputs'].values()))
    rows = R.rows(r)
    check('rows: CONTROL F5 ALIVE line', '  CONTROL F5 ALIVE' in rows and '  CONTROL F6 ALIVE' in rows)
    check('rows: no B > 0', '  F5 B > 0: none' in rows)
    # 2. the null control
    r = run(Fx('f5_sg0'))
    check('null good', r['null_ok'] and r['env_ok'] and r['hold_len_ok'])
    check('null rows HOLDS', '  CONTROL NULL HOLDS' in R.rows(r))
    for t in ('DiagF5: mode=1', 'DiagF6: mode=1', 'DiagF5: frame=1 rt_resolves=0', 'x DiagF6: frame=1'):
        fx = Fx('f5_sg0')
        fx.extra = [t]
        r = run(fx)
        check('null broken by %r' % t, not r['null_ok'])
    fx = Fx('f5_sg0')
    fx.env['KYTY_DIAG_F5'] = '1'
    check('null env with KYTY_DIAG_F5 -> env NO', run(fx)['env_ok'] is False)
    fx = Fx('f5_sg0')
    fx.rows, fx.dt = 90, 900000
    r = run(fx)
    check('null hold 79 s >= 60', r['hold_len_ok'])
    fx.dt = 600000
    r = run(fx)
    check('null hold 53 s < 60', not r['hold_len_ok'])
    # 3. F5 identities: the families of F16d section 2 written here independently of the reader
    check('families = F16d section 2 (independent list)', [(p, list(ch)) for p, ch in R.FAMILIES] == EXPECTED_FAMILIES)
    check('B set = item 427 (b) U {cmask_fce_layout} (independent list)', sorted(R.B_SET) == sorted(EXPECTED_B))
    check('pairs <= = F16d section 2', R.F5_LE == [('dcc_rt', 'rt_resolves'), ('stereo_nonzero', 'stereo_writes'),
                                                  ('ds_unbound_clear', 'ds_unbound')])
    check('F5 names 51, F6 names 20', len(R.F5_NAMES) == 51 and len(R.F6_NAMES) == 20)
    for p, ch in EXPECTED_FAMILIES:
        for c in ch:
            fx = Fx('f5_ef')
            fx.f5[2][c] += 1
            fx.f5[2][p] += 1
            r = run(fx)
            check('F5 family %s: child %s +1 with the parent +1 holds' % (p, c), r['f5']['ident_bad_n'] == 0
                  and (r['f5']['control_alive'] or c == 'cmask_fce_noimage'))
            fx = Fx('f5_ef')
            fx.f5[2][c] += 1
            r = run(fx)
            check('F5 family %s: child %s +1 alone violates' % (p, c), r['f5']['ident_bad_n'] == 1 and not r['f5']['control_alive'])
    # each family, child +1 and parent +1, on the first / middle / last line
    for p, ch in EXPECTED_FAMILIES:
        for pos in (0, 1, 2):
            for what in ('child', 'parent'):
                fx = Fx('f5_ef')
                fx.f5[pos][ch[0] if what == 'child' else p] += 1
                r = run(fx)
                ok = (not r['f5']['control_alive'] and r['f5']['ident_bad_n'] == 1 and r['f5']['ident_bad'][0][0] == pos + 1
                      and ctl(r, 'f5', 'identities') is False)
                check('F5 family %s %s+1 line %d' % (p, what, pos + 1), ok)
    for a, b in R.F5_LE:
        for pos in (0, 2):
            fx = Fx('f5_ef')
            fx.f5[pos][a] = fx.f5[pos][b] + 1
            if pos == 0:
                fx.f5[1][a] = max(fx.f5[1][a], fx.f5[0][a])
                fx.f5[2][a] = max(fx.f5[2][a], fx.f5[0][a])
            if (a, b) == ('stereo_nonzero', 'stereo_writes'):
                pass
            r = run(fx)
            check('F5 pair %s <= %s violated line %d' % (a, b, pos + 1), r['f5']['ident_bad_n'] >= 1 and not r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.f5[2]['dcc_rt'] = fx.f5[2]['rt_resolves']
    check('F5 pair dcc_rt = rt_resolves holds', run(fx)['f5']['control_alive'])
    # 4. F6 identities, each, first / middle / last line
    f6mut = [('slot classes', 's_empty'), ('h_bound', 'h_bound'), ('w_total', 'w_total'), ('draw kinds', 'draws_idx')]
    for nm, key in f6mut:
        for pos in (0, 1, 2):
            fx = Fx('f5_ef')
            fx.f6[pos][key] += 1
            r = run(fx)
            check('F6 identity %s line %d' % (nm, pos + 1), r['f6']['ident_bad_n'] == 1 and r['f6']['ident_bad'][0][0] == pos + 1
                  and not r['f6']['control_alive'] and r['f5']['control_alive'])
    for nm, key in f6mut:
        fx = Fx('f5_ef')
        fx.f6[2][key] -= 1
        r = run(fx)
        check('F6 identity %s, sum short by 1 on the last line' % nm, r['f6']['ident_bad_n'] == 1 and not r['f6']['control_alive'])
    fx = Fx('f5_ef')
    fx.f6[2]['ps_draws'] = fx.f6[2]['draws'] + 1
    r = run(fx)
    check('F6 ps_draws > draws', r['f6']['ident_bad_n'] == 1 and not r['f6']['control_alive'])
    fx = Fx('f5_ef')
    fx.f6[2]['ps_draws'] = fx.f6[2]['draws']
    check('F6 ps_draws = draws holds', run(fx)['f6']['control_alive'])
    # 5. malformed line, interleaved prefix
    fx = Fx('f5_ef')
    fx.drop5 = 'dcc_fce'
    r = run(fx)
    check('malformed middle line counted, control dead', r['f5']['malformed'] == 1 and not r['f5']['control_alive']
          and r['f5']['last']['rt_resolves'] == 300)
    fx = Fx('f5_ef')
    fx.prefix5 = '[12][00:00:01.000] other text '
    r = run(fx)
    check('line with a foreign prefix parsed', r['f5']['malformed'] == 0 and r['f5']['lines'] == 3 and r['f5']['control_alive'])
    # 6. monotonicity
    fx = Fx('f5_ef')
    fx.f5[2]['fmask_read'] = 0
    r = run(fx)
    check('monotone: a counter decreases', r['f5']['mono_bad_n'] == 1 and not r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.f5[2] = copy.deepcopy(fx.f5[1])
    r = run(fx)
    check('monotone: equal sums (no growth)', r['f5']['mono_bad_n'] == 1 and not r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.f6[1]['draws_auto'] = 0
    fx.f6[1]['draws'] -= 4
    fx.f6[1]['s_empty'] -= 32
    r = run(fx)
    check('monotone F6: a counter decreases', r['f6']['mono_bad_n'] >= 1 and not r['f6']['control_alive'])
    # 7. mode lines
    for knob in ('5', '6'):
        fx = Fx('f5_ef')
        setattr(fx, 'mode' + knob, 'after')
        r = run(fx)
        check('mode F%s after GuestOut -> dead' % knob, not r['f' + knob]['control_alive'] and r['f' + knob]['mode_ok'] is False)
        fx = Fx('f5_ef')
        setattr(fx, 'mode' + knob, 'none')
        r = run(fx)
        check('mode F%s missing -> dead' % knob, not r['f' + knob]['control_alive'])
    # 8. rt_resolves = 0
    fx = Fx('f5_ef')
    for d in fx.f5:
        d['rt_resolves'] = 0
        d['dcc_rt'] = 0
    r = run(fx)
    check('rt_resolves = 0 -> dead', not r['f5']['control_alive'] and ctl(r, 'f5', 'rt_resolves') is False)
    # 9. line_mismatch, both directions
    cases = [('meta', 'journal', 0), ('meta', 'counter', ('rtcheck_meta', 0)), ('round', 'journal', 0),
             ('round', 'counter', ('round_unorm', 0)), ('ds', 'journal', 0), ('ds', 'counter', ('ds_unbound', 0)),
             ('stereo', 'journal', 15), ('stereo', 'journal', 17), ('stereo', 'counter', ('stereo_writes', 10)),
             ('zero', 'journal', 31), ('zero', 'counter', ('zero_disp', 31)), ('fill', 'journal', 31), ('fill', 'counter', ('dcc_fill_all', 31))]
    for k, how, v in cases:
        fx = Fx('f5_ef')
        if how == 'journal':
            fx.journal[k] = v
        else:
            for d in fx.f5:
                d[v[0]] = v[1]
                if v[0] == 'ds_unbound':
                    d['ds_unbound_clear'] = 0
                if v[0] == 'stereo_writes':
                    d['stereo_nonzero'] = 0
        r = run(fx)
        mm = r['f5']['mismatch_letter']
        check('mismatch %s %s %s' % (k, how, v), mm[k] == 1 and sum(mm[x] for x, _ in R.JOURNAL) == 1 and not r['f5']['control_alive'])
    # equalities below the limit hold
    fx = Fx('f5_ef')
    fx.journal['stereo'] = 10
    for d in fx.f5:
        d['stereo_writes'] = 10
    check('stereo 10 = 10 holds', run(fx)['f5']['mismatch_letter']['stereo'] == 0)
    fx = Fx('f5_ef')
    fx.journal.update(meta=0, round=0, ds=0, stereo=0, zero=0, fill=0)
    for d in fx.f5:
        d.update(rtcheck_meta=0, round_unorm=0, ds_unbound=0, ds_unbound_clear=0, stereo_writes=0, zero_disp=0, dcc_fill_all=0)
    r = run(fx)
    check('all journal 0 and counters 0 hold', all(r['f5']['mismatch_letter'][x] == 0 for x, _ in R.JOURNAL) and r['f5']['control_alive'])
    # 10. LETTER vs VARIANT: a journal line after the last DiagF5 line
    fx = Fx('f5_ef')
    fx.journal['stereo'] = 10
    fx.journal_after['stereo'] = 1
    for d in fx.f5:
        d['stereo_writes'] = 10
    r = run(fx)
    check('letter counts the line after the last DiagF5 line, variant does not',
          r['f5']['mismatch_letter']['stereo'] == 1 and r['f5']['mismatch_variant']['stereo'] == 0 and not r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.journal['meta'] = 0
    fx.journal_after['meta'] = 1
    r = run(fx)
    check('meta line only after the last line: letter 0, variant 1', r['f5']['mismatch_letter']['meta'] == 0
          and r['f5']['mismatch_variant']['meta'] == 1 and r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.extra = ['A warning: ignoring indirect uc reg GE_STEREO_CNTL x B warning: ignoring indirect uc reg GE_STEREO_CNTL y']
    fx.journal['stereo'] = 14
    check('two journal messages in one line count 2', run(fx)['f5']['mismatch_letter']['stereo'] == 0)
    # 11. cmask_fce_noimage > 0
    fx = Fx('f5_ef')
    fx.f5[2]['cmask_fce_noimage'] = 1
    fx.f5[2]['cmask_fce'] += 1
    r = run(fx)
    check('cmask_fce_noimage > 0 -> dead without identity violation', r['f5']['ident_bad_n'] == 0 and not r['f5']['control_alive']
          and ctl(r, 'f5', 'cmask_fce_noimage') is False)
    # 12. f5_sg members
    for key, kids in (('dcc_rt', None), ('dcc_rt_pending', ['dcc_rt_cleared'])):
        for tag, alive in (('f5_sg', False), ('f5_ef', True)):
            fx = Fx(tag)
            for d in fx.f5:
                d[key] = 0
                for c in kids or []:
                    d[c] = 0
            r = run(fx)
            check('%s = 0 on %s -> F5 %s' % (key, tag, 'alive' if alive else 'dead'), r['f5']['control_alive'] is alive)
    fx = Fx('f5_ef')
    check('f5_ef has no f5_sg member', ctl(run(fx), 'f5', 'f5_sg') == 'ABSENT')
    # 13. F6 control members
    for key in ('draws', 's_bound', 'ps_draws'):
        fx = Fx('f5_ef')
        for s, d in enumerate(fx.f6, 1):
            d[key] = 0
            if key == 'draws':
                d.update(draws_idx=0, draws_auto=0, draws_ind=0, draws_mesh=0, ps_draws=0, s_empty=0, s_addr0_nofmt=0, s_mask0_addr=0,
                         s_bound=0, h_bound=0)
            if key == 's_bound':
                d['s_empty'] += 20 * s
                d['h_bound'] = 0
        r = run(fx)
        check('F6 %s = 0 -> dead' % key, not r['f6']['control_alive'] and r['f6']['ident_bad_n'] == 0)
    fx = Fx('f5_ef')
    for s, d in enumerate(fx.f6, 1):
        d.update(w_mask0=0, w_addr0_nofmt=0, w_total=20 * s)
    r = run(fx)
    check('F6 w_mask0 + w_addr0_fmt + w_addr0_nofmt = 0 -> dead', not r['f6']['control_alive'] and r['f6']['ident_bad_n'] == 0)
    for tag, alive in (('f5_sg', False), ('f5_ef', True)):
        fx = Fx(tag)
        for s, d in enumerate(fx.f6, 1):
            d['draws_mesh'] = 0
            d['draws_idx'] += 3 * s
        r = run(fx)
        check('draws_mesh = 0 on %s -> F6 %s' % (tag, 'alive' if alive else 'dead'), r['f6']['control_alive'] is alive)
    # 14. the B set: each of the 17 with its parent +1 -> B > 0, the control stays alive (except none)
    parent_of = dict((c, p) for p, ch in R.FAMILIES for c in ch)
    for n in R.B_SET:
        fx = Fx('f5_ef')
        for d in fx.f5:
            d[n] += 1
            d[parent_of[n]] += 1
        r = run(fx)
        check('B %s > 0 seen, control alive' % n, r['f5']['b'][n] == 1 and r['f5']['b_sum'] == 1 and r['f5']['control_alive']
              and ('  F5 B > 0: %s' % n) in R.rows(r))
    check('B set has 17 names, all in families', len(R.B_SET) == 17 and all(n in parent_of for n in R.B_SET))
    for n in ('meta_dma_noclear', 'cmask_fce_drawn', 'dcc_fill_uncompressed', 'dcc_fill_clear', 'cmask_fce_meta', 'cmask_fce_b42',
              'cmask_fce_noimage'):
        check('%s not in B' % n, n not in R.B_SET)
    fx = Fx('f5_ef')
    for d in fx.f5:
        d['dcc_mat_pending'] = d['dcc_mat_cleared'] = 0
    r = run(fx)
    check('parent = 0 listed (reference)', r['f5']['parents_zero'] == ['dcc_mat_pending'] and r['f5']['control_alive'])
    # 15. F6 inputs of item 433 (v)(i)-(iv)
    fx = Fx('f5_ef')
    for s, d in enumerate(fx.f6, 1):
        d['w_addr0_fmt'] = s
        d['w_total'] += s
    r = run(fx)
    check('(ii) w_addr0_fmt > 0 in inputs, control alive', r['f6']['inputs']['w_addr0_fmt'] == 3 and r['f6']['control_alive'])
    fx = Fx('f5_ef')
    for s, d in enumerate(fx.f6, 1):
        d['bound_missing'] = s
        d['h_bound'] -= s
    r = run(fx)
    check('(iii) bound_missing > 0 in inputs', r['f6']['inputs']['bound_missing'] == 3 and r['f6']['control_alive'])
    fx = Fx('f5_ef')
    for s, d in enumerate(fx.f6, 1):
        d['bound_extra'] = s
        d['h_bound'] += s
    r = run(fx)
    check('(iii) bound_extra > 0 in inputs', r['f6']['inputs']['bound_extra'] == 3 and r['f6']['control_alive'])
    fx = Fx('f5_ef')
    for s, d in enumerate(fx.f6, 1):
        d['w_ge8'] = s
        d['w_total'] += s
    r = run(fx)
    check('(iv) w_ge8 > 0 in inputs', r['f6']['inputs']['w_ge8'] == 3 and r['f6']['control_alive'])
    fx = Fx('f5_ef')
    for s, d in enumerate(fx.f6, 1):
        d['s_addr0_fmt'] = s
        d['s_empty'] -= s
    r = run(fx)
    check('s_addr0_fmt > 0 (reference) in inputs', r['f6']['inputs']['s_addr0_fmt'] == 3 and r['f6']['control_alive'])
    # 16. admission rows
    fx = Fx('f5_ef')
    fx.installed = 'f' * 64
    check('tag binary sha wrong -> NO', run(fx)['sha_ok'] is False)
    fx = Fx('f5_ef')
    fx.binver = False
    check('version string absent -> NO', run(fx)['version_ok'] is False)
    fx = Fx('f5_ef')
    fx.after = 'e' * 64
    check('installed after wrong -> NO', run(fx)['after_ok'] is False)
    fx = Fx('f5_ef')
    fx.before = 'e' * 64
    check('installed before wrong -> NO', run(fx)['before_ok'] is False)
    for k, v in (('KYTY_FIX_B4', '1'), ('KYTY_GAME_PATCH', 'x'), ('KYTY_GPU_CHECKPOINTS', '1')):
        fx = Fx('f5_ef')
        fx.env[k] = v
        check('env %s -> NO' % k, run(fx)['env_ok'] is False)
    for k in ('KYTY_DIAG_F5', 'KYTY_DIAG_F6'):
        fx = Fx('f5_ef')
        del fx.env[k]
        check('diag env without %s -> NO' % k, run(fx)['env_ok'] is False)
    fx = Fx('f5_ef')
    fx.dt = 700000
    check('hold 279 s < 300 -> NO', run(fx)['hold_len_ok'] is False)
    fx = Fx('f5_ef')
    fx.scene_change_at = 200
    r = run(fx)
    check('scene change stops the hold', r['scene_change_line'] is not None and r['hold_len_ok'] is False)
    fx = Fx('f5_ef')
    fx.att['outcome'] = 'timeout'
    check('outcome not ok -> NO', run(fx)['hold_ok'] is False)
    fx = Fx('f5_ef')
    fx.att['hold_exit'] = 3
    check('hold_exit set -> NO', run(fx)['hold_ok'] is False)
    fx = Fx('f5_ef')
    fx.manifest = 'manifest cmp DIFFER 2'
    check('manifest differs -> NO', run(fx)['manifest_ok'] is False)
    for t in ('Window 1 minimized', 'Recovering Vulkan swapchain', 'GamePatch: applied'):
        fx = Fx('f5_ef')
        fx.extra = [t]
        r = run(fx)
        check('interference %r' % t, r['interference'] and r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.extra = ['Window 1 lost keyboard focus']
    check('focus loss is not interference', not run(fx)['interference'])
    fx = Fx('f5_ef')
    fx.level_line = 'final_stage'
    check('other level -> not entered', run(fx)['entry_line'] is None)
    fx = Fx('f5_ef')
    fx.extra_before = ['FrameTrace: n=5 dt_us=2000000 draws=300']
    fx.extra = ['GpuHangAbort: x']
    r = run(fx)
    check('frame >= 1 s before the entry not counted; death marker is a report row', r['k2_after'] == 0 and len(r['death']) == 1
          and r['f5']['control_alive'])
    fx = Fx('f5_ef')
    fx.dt = 1000000
    r = run(fx)
    check('frames >= 1 s after the entry counted (REPORT), control alive', r['k2_after'] == 399 and r['f5']['control_alive'])
    # 17. set rows
    js = []
    for tag in ('f5_sg', 'f5_ef'):
        r = run(Fx(tag))
        p = os.path.join(TMP, 'set_%s.json' % tag)
        json.dump(r, open(p, 'w'), default=list)
        js.append(json.load(open(p)))
    fx = Fx('f5_bh')
    for d in fx.f5:
        d['dcc_rt_skip_levels'] += 1
        d['dcc_rt_pending'] += 1
    js.append(json.loads(json.dumps(run(fx), default=list)))
    js.append(json.loads(json.dumps(run(Fx('f5_sg0')), default=list)))
    sr = R.set_rows(js)
    check('set rows: per tag + summary', len(sr) == 5)
    check('set rows: B > 0 tag named', sr[-1].endswith('tags with B > 0: f5_bh') and 'F5 control alive on 3' in sr[-1])
    check('set rows: null HOLDS', 'NULL HOLDS' in sr[3])
    # 18. strict cp1250 output of the reader as a process (no PYTHONIOENCODING)
    base = os.path.join(TMP, 'cp')
    Fx('f5_sg').make(base)
    env = dict(os.environ)
    env.pop('PYTHONIOENCODING', None)
    env['PYTHONIOENCODING'] = 'cp1250:strict'
    pr = subprocess.run([sys.executable, target, '--dir', base, '--tag', 'f5_sg'], capture_output=True, env=env)
    check('reader rc 0 under strict cp1250', pr.returncode == 0)
    check('reader output ASCII only', all(b < 128 for b in pr.stdout) and len(pr.stdout) > 1000)
    check('reader output has CONTROL F5 ALIVE', b'CONTROL F5 ALIVE' in pr.stdout)
    pr = subprocess.run([sys.executable, target, '--dir', base, '--tag', 'f5_xx'], capture_output=True, env=env)
    check('unknown tag refused', pr.returncode != 0)
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

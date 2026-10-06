"""F20l3 (HPP-655): edits of the ported b32_read.py (ROADMAP s122 item 591 (v), (g), (d)): tags b32_pa / b32_pa2 / b32_s01..60 /
b32_z0c1..5, the installed S18 b3cee576 by the full sha256, the cold-form admission members, the PK-A domain of item 591 (v)(2), the
member 'not called' (v)(3), U5(3) 'not computable' (v)(6), the U5(1) rule of item 555 (b)(2) with the exact two-sided Mann-Whitney test
and the base of item 591 (d)(2), the series summary (item 550 (e)(2)-(3)).  Each edit is an exact-string replacement that must match once.
LF.  usage: python edit_f20l3.py <b32_read.py>"""
import sys

E = []

E.append(('''"""Track F link F20l3 (HPP-655; ROADMAP s122 item 574 (d), (e); item 581 (v)(2), (v)(5), (zh); item 584 (v); the rule of item 550 (g) with
the amendments of items 551 (v), 552 (v)(3), (g), 553 (v), 554 (g)): the reader of the repeated KYTY_DIAG_B32 controls b32_z0b, b32_ppb,
b32_pcb on the F20j4 test binary 2d0c8815, and the reference reread of the F20l log b32_pd (F20j2 test binary b9e0ee00) with theta_load.
NO VERDICT - F20m2 (lead).  theta_load is read from the seal (line 'theta_load: <x>', item 574 (b)(6): 0.4562).  ASCII only.

    python b32_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f20l3; b32_pd - files of
                                                                    C:/kyty/f287/f20l, the reference reread of item 574 (e))
    python b32_read.py --dir <fixture dir> --tag <tag> [--json <out>]
                                                                    fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt,
                                                                    installed_before.txt, installed_after.txt, manifest_cmp.txt,
                                                                    seal.md, load.json
    python b32_read.py --table [--runs <dir>]                       the table of item 550 (z)(5) over every runs/<tag>/read.json
    python b32_read.py --check-seal [--seal <md>]                   every 'seal: <sha256> <path>' line against the file
''', '''"""Track F link F20l3 (HPP-655; ROADMAP s122 item 591 (v), (g), (d), (zh); the rule of item 550 (g) with the amendments of items 551 (v),
552 (v)(3), (g), 553 (v), 554 (g), 574 (d), 581 (v)(2), (v)(5)): the reader of the PK-A tags of the cold form b32_pa / b32_pa2 and of the
KYTY_DIAG_B32 series b32_s01..b32_s60 (and the U5(1) base tags b32_z0c1..b32_z0c5 at KYTY_DIAG_B32=0) on the F20j4 test binary 2d0c8815.
NO VERDICT - F20m3 (lead).  theta_load is read from the seal (line 'theta_load: <x>', item 574 (b)(6): 0.4562).  ASCII only.

    python b32_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f20l3)
    python b32_read.py --dir <fixture dir> --tag <tag> [--json <out>]
                                                                    fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt,
                                                                    installed_before.txt, installed_after.txt, manifest_cmp.txt,
                                                                    seal.md, reserve_move.txt, reserve_cold.txt, reserve_check.txt
    python b32_read.py --table [--runs <dir>]                       the table over every runs/<tag>/read.json
    python b32_read.py --pka [--runs <dir>]                         the PK-A member of item 591 (v)(2)-(4) over b32_pa / b32_pa2
    python b32_read.py --series [--runs <dir>] [--upto <k>]         the series summary: holds, K, classes, the stop rule of item
                                                                    550 (e)(2)-(3), U5 of item 550 (zh) / 555 (b) / 591 (d), (v)(6)
                                                                    (--upto 10: the first 10 admitted series tags only)
    python b32_read.py --check-seal [--seal <md>]                   every 'seal: <sha256> <path>' line against the file
'''))

E.append(('''PK-A (item 550 (d)(7))  the B5 hold frames classified by (i)-(iv) (no count gate); armed member: EMU_RUN:Gpu or a path EMU_CALL:<...> that
                  ends on GuestGpu.
''', '''PK-A (item 550 (d)(7))  the B5 hold frames classified by (i)-(iv) (no count gate); armed member: EMU_RUN:Gpu or a path EMU_CALL:<...> that
                  ends on GuestGpu (printed for every tag as before - 'pk_a').
PK-A COLD (item 591 (v)(2)-(4), the member of b32_pa / b32_pa2)  the domain: every scene frame of the F20c reader (frames after the first
                  scene frame, which follows the first line 'Level has started: underwater_aerial_garden'; no 10 s threshold) that the F20c
                  reader attributes to B5, with dt_us - instr_us >= 100 000 (instr_us 0 without a DiagB32: line); each classified by
                  (i)-(iv) with theta_load.  Member: frames >= 3 and armed >= 2/3 (3 x armed >= 2 x frames) - ARMED; frames >= 3 and
                  armed < 2/3 - FAIL (the repeated failure of U1, item 574 (v)(2)); frames < 3 - NOT_CALLED (b32_pa -> b32_pa2; b32_pa2
                  again < 3 -> PK-A 'not called', item 591 (v)(3)).  Reference: frames from the level line to the first scene frame with
                  dt_us >= 100 000 (the F20c reader does not attribute them); B5 frames with dt_us - instr_us < 100 000.
SERIES (item 550 (e)(2)-(3), item 591 (g)(5))  the admitted tags b32_sNN (a repeat b32_sNN_rK stands for its interfered name); holds =
                  admitted tags with a hold; K = holds with >= 1 frame in the count; class of a hold = class of its longest frame in count.
                  Stop: holds < 29 - CONTINUE; >= 29: K >= 3 - STOP_READ; K = 0 - STOP_U2; K = 1-2 - CONTINUE up to K = 3 (STOP_READ) or
                  60 holds (STOP_U2PRIME); the tag budget 60 series tags + repeats <= 6.
U5 of the series (item 550 (zh), 555 (b), 591 (d), (v)(6))  over the admitted series tags (=1): (1) fires only when BOTH the median of the
                  tag medians of idx 723..828 deviates from the base median by > 2 % AND the exact two-sided Mann-Whitney test (ties by mid
                  ranks) of the tag medians against the base medians gives p < 0.05; base - the 11 F20e tags (median 36 171.5), or after
                  the five b32_z0c tags the 7 tags b32_z0, b32_z0b, b32_z0c1..5 (item 591 (d)(2)); the share of tags with a median > 40 000
                  is printed (reference, item 555 (b)(3)); (2) frames >= 70 ms per hold > 1.5 x 0.561; (3) mean dt_us of the pooled B5
                  frames > 1.25 x 134 767.7, 'not computable' without B5 frames (not in 'any of'); (4) a nonzero _w invariant in >= 2 tags.
'''))

E.append(('''G_F20L = 'C:/kyty/f287/f20l'          # the F20l files: reference reread of b32_pd (item 574 (e))
SEAL_F20L = G_F20L + '/pred/f20l_seal.md'
BIN_F20J2 = 'b9e0ee0092ca1504979ebd674abb21c8d67015fd030bc33615eb2c87acb90f91'    # F20j2 test binary of the F20l log b32_pd
''', ''))

E.append(('''BIN_FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'      # installed FS8 (before = after)
''', '''BIN_INST = 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a'     # installed S18 (item 590, 591 (g)(3)), before = after
'''))

E.append(('''FORM = {'b32_z0b': dict(KYTY_DIAG_B32='0', KYTY_GPU_WALL='1'),
        'b32_ppb': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1', KYTY_TEST_B32='60:present:200'),
        'b32_pcb': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1', KYTY_TEST_B32='60:gpusleep:200'),
        'b32_pd': dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1')}
LOADER = {'b32_pd': 'all'}
TAG_RX = re.compile(r'^(b32_z0b|b32_ppb|b32_pcb|b32_pd)(_r[1-6])?$')
''', '''TAG_RX = re.compile(r'^(b32_pa2?|b32_s(?:0[1-9]|[1-5][0-9]|60)|b32_z0c[1-5])(_r[1-6])?$')
COLD = ('b32_pa', 'b32_pa2')
LOADER = {}


def form_of(base):
    """The env form of a tag (item 591 (v)(1), (g)(2), (d)(2)): KYTY_DIAG_B32=0 only for b32_z0c1..5."""
    return dict(KYTY_DIAG_B32='0' if base.startswith('b32_z0c') else '1', KYTY_GPU_WALL='1')


# U5(1) bases (item 555 (b)(2), 591 (d)(2)): the 11 F20e tag medians (base_f20l.txt lines 33-43, median 36 171.5) and the two =0 tags
# after the known-scenes catalogue (F20l b32_z0 read.json, F20l2 b32_z0b read.json); the five b32_z0c tags are read from runs/
U5_F20E_MEDS = (36818.5, 46632.0, 34904.5, 35800.0, 36171.5, 36082.0, 36443.0, 35844.0, 35115.0, 41596.0, 45939.5)
U5_Z0_MEDS = (('b32_z0', 36451.5), ('b32_z0b', 41478.5))
SECOND_MODE_US = 40000
HOLDS_MIN, HOLDS_MAX, K_STOP = 29, 60, 3
'''))

E.append(('''        if line.startswith(b'TestB32:'):
            r['test'].append(dict(text=line.decode('ascii', 'replace').strip()[:160], after_n=last_n))
            continue
''', '''        if line.startswith(b'TestB32:'):
            r['test'].append(dict(text=line.decode('ascii', 'replace').strip()[:160], after_n=last_n))
            continue
        if line.startswith(b'PipelinePrecache: '):
            if line.startswith(b'PipelinePrecache: no '):
                r['precache_no'] += 1
            elif PRECACHE_RECIPES.match(line):
                r['precache_recipes'] += 1
            continue
        if line.startswith(b'ShaderSeed: ') and not line.startswith(b'ShaderSeed: compatibility='):
            if len(r['seed_other']) < 4:
                r['seed_other'].append(line.decode('ascii', 'replace').strip()[:120])
            continue
        if r['lvl_after_n'] is None and b'Level has started: underwater_aerial_garden' in line:
            r['lvl_after_n'] = last_n if last_n is not None else -1
''' ))

E.append(('''    r = dict(ft=ft, diag=diag, mode=[], invalid=[], test=[], recovering=0, minimized=0, diag_lines=0, diag_bad_prefix=0, ft_order=[],
             sig=[], variant_dir=[])
''', '''    r = dict(ft=ft, diag=diag, mode=[], invalid=[], test=[], recovering=0, minimized=0, diag_lines=0, diag_bad_prefix=0, ft_order=[],
             sig=[], variant_dir=[], precache_no=0, precache_recipes=0, seed_other=[], lvl_after_n=None)
'''))

E.append(('''SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
''', '''SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
PRECACHE_RECIPES = re.compile(rb'^PipelinePrecache: \\d+ recipes ')
'''))

E.append(('''    res['hold_class'] = max(cnt, key=lambda x: x['dt_us'])['cls'] if cnt and hold else None
''', '''    res['hold_class'] = max(cnt, key=lambda x: x['dt_us'])['cls'] if cnt and hold else None
    res['hold_family'] = max(cnt, key=lambda x: x['dt_us'])['family'] if cnt and hold else None
    # PK-A of the cold form (item 591 (v)(2)): every scene frame of the F20c reader attributed to B5, no 10 s threshold
    pk3, pk3_instr = [], []
    for x in frames:
        if x[2] < SLOW_US or F.attr(x, BIN_TEST, 'letter') != 'B5':
            continue
        n = x[1]
        d = diag.get(n)
        h = d['hdr'] if d else None
        instr = (num(h.get('instr_us'), 0) or 0) if h else 0
        if x[2] - instr < SLOW_US:
            pk3_instr.append(dict(n=n, dt_us=x[2], instr_us=instr))
            continue
        f = ft.get(n)
        b = base_of(ft, neighbours(frames, pos[n]))
        fr = dict(n=n, dt=x[2], lat=f[1] if f else None, gbusy=f[2] if f else None)
        c = classify(fr, d, b, theta) if b else dict(cls='UNDETERMINED', family='UNDETERMINED', note='no base')
        pk3.append(dict(n=n, idx=x[0], dt_us=x[2], t_s=round(x[3] / 1e6, 3), instr_us=instr if h else None, diag=h is not None,
                        cls=c['cls'], family=c.get('family'), term_role=c.get('role'), path=c.get('path'), note=c.get('note'),
                        holder=c.get('holder')))
    for x in pk3:
        x['armed'] = armed_b5(x)
    res['pk_a3'] = pk3
    res['pk_a3_instr'] = pk3_instr
    res['pk_a3_armed'] = sum(1 for x in pk3 if x['armed'])
    res['pk_a3_member'] = pka_member(len(pk3), res['pk_a3_armed'])
    # reference: frames from the level line to the first scene frame (not attributed by the F20c reader)
    order = s['ft_order']
    pre = []
    if s['lvl_after_n'] is not None and r['first_n'] is not None and r['first_n'] in ft:
        k0 = order.index(s['lvl_after_n']) + 1 if s['lvl_after_n'] in order else 0
        k1 = order.index(r['first_n'])
        pre = [(n, ft[n][0]) for n in order[k0:k1 + 1] if ft[n][0] >= SLOW_US]
    res['pre_scene_slow'] = pre
    res['precache_no'] = s['precache_no']
    res['precache_recipes'] = s['precache_recipes']
    res['seed_other'] = s['seed_other']
'''))

E.append(('''def armed_b5(x):
    if x['cls'] == 'EMU_RUN:Gpu':
        return True
    return x['cls'].startswith('EMU_CALL:') and x.get('term_role') == 'Gpu'
''', '''def armed_b5(x):
    if x['cls'] == 'EMU_RUN:Gpu':
        return True
    return x['cls'].startswith('EMU_CALL:') and x.get('term_role') == 'Gpu'


def pka_member(n, armed):
    """Item 591 (v)(2)-(4): frames >= 3 and armed >= 2/3 - ARMED; frames >= 3, armed < 2/3 - FAIL; frames < 3 - NOT_CALLED."""
    if n < 3:
        return 'NOT_CALLED'
    return 'ARMED' if 3 * armed >= 2 * n else 'FAIL'
'''))

E.append(('''    gg, seal = (G_F20L, SEAL_F20L) if TAG_RX.match(tag) and TAG_RX.match(tag).group(1) == 'b32_pd' else (G, SEAL_PATH)
    d = os.path.join(gg, 'runs', tag)
''', '''    gg, seal = G, SEAL_PATH
    d = os.path.join(gg, 'runs', tag)
'''))

E.append(('''    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha')
''', '''    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'reserve_move', 'reserve_cold',
             'reserve_check')
'''))

E.append(('''    base_tag = TAG_RX.match(tag).group(1)
    form = FORM[base_tag]
    theta = read_theta(p['theta_src'])
    want_bin = BIN_F20J2 if base_tag == 'b32_pd' else BIN_TEST
''', '''    base_tag = TAG_RX.match(tag).group(1)
    form = form_of(base_tag)
    theta = read_theta(p['theta_src'])
    want_bin = BIN_TEST
    cold = base_tag in COLD
'''))

E.append(('''        ('json binary_sha256 = %s (%s)' % ('F20j2 test b9e0ee00 (reference reread)' if base_tag == 'b32_pd' else 'F20j4 test 2d0c8815',
                                           (jbin or '-')[:16]), jbin == want_bin),
        ('installed before = after = FS8 2c9b69b9 (%s / %s)' % ((inst_b or '-')[:8], (inst_a or '-')[:8]),
         inst_b == BIN_FS8 and inst_a == BIN_FS8),
''', '''        ('json binary_sha256 = F20j4 test 2d0c8815 (%s)' % (jbin or '-')[:16], jbin == want_bin),
        ('installed before = after = S18 %s (%s / %s)' % (BIN_INST, (inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),
'''))

E.append(('''        ('loader ran (%s)' % (None if load is None else load.get('status')),
         (load is not None and load.get('status') == 'done' and load.get('mode') == LOADER[base_tag]) if base_tag in LOADER
         else load is None),
    ]
''', '''        ('no loader (%s)' % (None if load is None else load.get('status')), load is None),
    ]
    rmv = (F.text(p['reserve_move']) or '').strip()
    rcl = (F.text(p['reserve_cold']) or '').strip()
    rck = (F.text(p['reserve_check']) or '').strip()
    if cold:
        adm += [
            ('cold form: reserve moved (%s)' % rmv[:60], rmv.startswith('RESERVE MOVED')),
            ('cold form: live folder cold before the start (%s)' % rcl[:40], rcl.startswith('COLD OK')),
            ('cold form: reserve back in manifest after (%s)' % rck[:40], rck.startswith('RESERVE IN AFTER')),
            ('cold form: log PipelinePrecache no recipes yet %s, recipes loaded %s, other ShaderSeed lines %s' % (
                (r or {}).get('precache_no'), (r or {}).get('precache_recipes'), (r or {}).get('seed_other')),
             r is not None and r['precache_no'] >= 1 and r['precache_recipes'] == 0 and not r['seed_other']),
        ]
    else:
        adm += [('warm form: no cold reserve files (%s / %s / %s)' % (bool(rmv), bool(rcl), bool(rck)), not rmv and not rcl and not rck)]
'''))

E.append(('''    out.append('U5(3) mean dt_us of B5 frames %s (n %s; base %s, member > 1.25 x base: %s) [reference]' % (
        r.get('u5_b5_mean'), r.get('u5_b5_n'), b['mean_dt_b5'],
        'yes' if r.get('u5_b5_mean') and b['mean_dt_b5'] and r['u5_b5_mean'] > 1.25 * b['mean_dt_b5'] else 'no'))
''', '''    out.append('U5(3) mean dt_us of B5 frames %s (n %s; base %s, member > 1.25 x base: %s) [reference]' % (
        r.get('u5_b5_mean'), r.get('u5_b5_n'), b['mean_dt_b5'],
        ('yes' if r['u5_b5_mean'] > 1.25 * b['mean_dt_b5'] else 'no') if r.get('u5_b5_mean') else 'not computable (no B5 frames)'))
'''))

E.append(('''        out.append('  PK-A B5 frames %d, armed member (EMU_RUN:Gpu / EMU_CALL on GuestGpu) %d: %s' % (
            len(r['pk_a']), r['pk_a_armed'], [(x['n'], x['cls']) for x in r['pk_a']][:10]))
''', '''        out.append('  PK-A B5 frames %d, armed member (EMU_RUN:Gpu / EMU_CALL on GuestGpu) %d: %s' % (
            len(r['pk_a']), r['pk_a_armed'], [(x['n'], x['cls']) for x in r['pk_a']][:10]))
        out.append('  PK-A COLD DOMAIN (item 591 (v)(2)): frames %d, armed %d, member %s%s' % (
            len(r['pk_a3']), r['pk_a3_armed'], r['pk_a3_member'], ' [the PK-A tag]' if res['form'] in COLD else ' [reference]'))
        for x in r['pk_a3'][:40]:
            out.append('    PKA n %d idx %d dt_us %d t %.1f s instr_us %s | %s%s | holder %s | %s | %s' % (
                x['n'], x['idx'], x['dt_us'], x['t_s'], x['instr_us'], x['cls'], ' ARMED' if x['armed'] else '', x['holder'],
                ' > '.join(x['path'] or []), x['note']))
        out.append('    B5 frames out of the domain (dt_us - instr_us < 100 000): %s; frames >= 100 ms from the level line to the first scene '
                   'frame (not attributed by F20c, reference): %s' % ([(x['n'], x['dt_us'], x['instr_us']) for x in r['pk_a3_instr']][:10],
                                                                     r['pre_scene_slow'][:10]))
        out.append('    PipelinePrecache: no recipes yet %d, recipes loaded %d; other ShaderSeed lines %s' % (
            r['precache_no'], r['precache_recipes'], r['seed_other']))
'''))

E.append(('''def table(rd):
    tags = sorted(t for t in os.listdir(rd) if (TAG_RX.match(t) or t == 'b32_pd_ref') and os.path.exists(os.path.join(rd, t, 'read.json'))) \\
        if os.path.isdir(rd) else []
    out = ['| tag | adm | bin / sig | K_I / K | in count | classes (n: class) | INSTR_MADE | kq_n=0 | m5r | prev>=100 | PK-A B5 armed | U5(1) | U5(4) '
           '| load ratio | recov |', '|' + '---|' * 15]
''', '''def mw_exact(a, b):
    """Exact two-sided Mann-Whitney (Wilcoxon rank-sum) test, ties by mid ranks; the permutation distribution of the rank sum of the
    smaller group over all C(N, m) splits of the pooled mid ranks.  Returns (U of a, p); p = P(|S - E S| >= |s - E S|)."""
    pooled = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    n = len(pooled)
    r2 = [0] * n           # doubled mid ranks (integers)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pooled[j + 1][0] == pooled[i][0]:
            j += 1
        for k in range(i, j + 1):
            r2[k] = i + j + 2
        i = j + 1
    g = 1 if len(b) <= len(a) else 0
    m = len(b) if g == 1 else len(a)
    s_obs = sum(r2[k] for k in range(n) if pooled[k][1] == g)
    dp = [dict() for _ in range(m + 1)]
    dp[0][0] = 1
    for idx, v in enumerate(r2):
        for k in range(min(idx + 1, m), 0, -1):
            cur = dp[k]
            for s, c in dp[k - 1].items():
                cur[s + v] = cur.get(s + v, 0) + c
    total = sum(dp[m].values())
    mean2 = m * (n + 1)            # E of the doubled rank sum
    dev = abs(s_obs - mean2)
    extreme = sum(c for s, c in dp[m].items() if abs(s - mean2) >= dev)
    ra = sum(r2[k] for k in range(n) if pooled[k][1] == 0) / 2.0
    u_a = ra - len(a) * (len(a) + 1) / 2.0
    return u_a, extreme / total


def u5_one(meds, base_meds):
    """Item 555 (b)(2): fires when |median(meds) / median(base) - 1| > 0.02 AND exact two-sided Mann-Whitney p < 0.05."""
    if not meds:
        return dict(n=0, fires=None, note='no tag medians')
    mm = statistics.median(meds)
    bm = statistics.median(base_meds)
    dev = (mm - bm) / bm
    u, p = mw_exact(list(meds), list(base_meds))
    return dict(n=len(meds), median=mm, base_median=bm, base_n=len(base_meds), dev=round(dev, 4), u=u, p=p,
                fires=bool(abs(dev) > 0.02 and p < 0.05),
                second_mode=sum(1 for x in meds if x > SECOND_MODE_US), base_second_mode=sum(1 for x in base_meds if x > SECOND_MODE_US))


def load_runs(rd):
    out = {}
    if not os.path.isdir(rd):
        return out
    for t in os.listdir(rd):
        if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json')):
            out[t] = json.load(open(os.path.join(rd, t, 'read.json'), encoding='utf-8'))
    return out


def series_tags(runs):
    """The admitted series tags in the order of their number; one per number (the admitted one among b32_sNN, b32_sNN_r1..6)."""
    by = {}
    for t, res in runs.items():
        base = TAG_RX.match(t).group(1)
        if not base.startswith('b32_s') or not res.get('admitted'):
            continue
        by.setdefault(base, []).append(t)
    out = []
    for base in sorted(by):
        out.append((base, sorted(by[base])))
    return out


def z0_base(runs):
    """Item 591 (d)(2): the 7 =0 tags after the catalogue - b32_z0, b32_z0b (fixed) and b32_z0c1..5 (admitted, from runs/)."""
    meds = [('%s' % t, v) for t, v in U5_Z0_MEDS]
    for k in range(1, 6):
        name = 'b32_z0c%d' % k
        got = [res for t, res in runs.items() if TAG_RX.match(t).group(1) == name and res.get('admitted')]
        if got and got[0]['log'] and got[0]['log'].get('u5_med_dt') is not None:
            meds.append((name, got[0]['log']['u5_med_dt']))
    return meds


def series(rd, upto=None):
    runs = load_runs(rd)
    st = series_tags(runs)
    if upto is not None:
        st = st[:upto]
    out = ['SERIES over %s: admitted series tags %d%s' % (rd, len(st), (' (first %d)' % upto) if upto else '')]
    holds = k = 0
    fam = {}
    meds, slow70, b5sum, b5n, nz = [], 0, 0.0, 0, 0
    for base, tags in st:
        t = tags[0]
        r = runs[t]['log'] or {}
        h = bool(r.get('hold'))
        holds += 1 if h else 0
        k += 1 if h and r.get('K') else 0
        if h and r.get('K'):
            fam[r.get('hold_family')] = fam.get(r.get('hold_family'), 0) + 1
        if r.get('u5_med_dt') is not None:
            meds.append(r['u5_med_dt'])
        slow70 += r.get('u5_slow70') or 0
        if r.get('u5_b5_n'):
            b5sum += r['u5_b5_mean'] * r['u5_b5_n']
            b5n += r['u5_b5_n']
        bad = any((r.get('zero_w_sum') or {}).values())
        nz += 1 if bad else 0
        out.append('  %s (%s) hold %s K %s class %s family %s | u5_med %s slow70 %s B5 %s | zero_w %s | read %s' % (
            base, t, h, r.get('K'), r.get('hold_class'), r.get('hold_family'), r.get('u5_med_dt'), r.get('u5_slow70'), r.get('u5_b5_n'),
            'NZ' if bad else '0', (sha_file(os.path.join(rd, t, 'read.txt')) or '-')[:16]))
    out.append('HOLDS %d K %d' % (holds, k))
    if holds < HOLDS_MIN:
        stop = 'CONTINUE (holds %d < %d)' % (holds, HOLDS_MIN)
    elif k >= K_STOP:
        stop = 'STOP_READ (K %d >= 3 at %d holds, item 550 (e)(2))' % (k, holds)
    elif k == 0:
        stop = 'STOP_U2 (K 0 at %d holds, item 550 (e)(2), (zh))' % holds
    elif holds >= HOLDS_MAX:
        stop = 'STOP_U2PRIME (K %d at %d holds, item 550 (e)(3))' % (k, holds)
    else:
        stop = 'CONTINUE (K %d at %d holds, up to K 3 or %d holds)' % (k, holds, HOLDS_MAX)
    out.append('STOP RULE %s' % stop)
    if k:
        def sh(names):
            return sum(v for f, v in fam.items() if f in names) / float(k)
        out.append('CLASSES (family of the hold class, of K %d): %s' % (k, sorted(fam.items(), key=lambda x: (-x[1], str(x[0])))))
        out.append('  (i) UNDETERMINED + UNMARKED + NO_SAMPLES %.4f; (ii) HOST_LOAD %.4f; (iii) HOST_FREEZE + HOST_LOAD + HOST_PREEMPT + '
                   'DRV_HOST %.4f; (iv) top family %s %.4f [reference - the reading is F20m3]' % (
                       sh(('UNDETERMINED', 'UNMARKED', 'NO_SAMPLES')), sh(('HOST_LOAD',)),
                       sh(('HOST_FREEZE', 'HOST_LOAD', 'HOST_PREEMPT', 'DRV_HOST')),
                       max(fam.items(), key=lambda x: x[1])[0], max(fam.values()) / float(k)))
    u1 = u5_one(meds, U5_F20E_MEDS)
    out.append('U5(1) vs F20e 11: %s' % u1)
    zb = z0_base(runs)
    if len(zb) == 7:
        u1z = u5_one(meds, [v for _, v in zb])
        out.append('U5(1) vs the 7 =0 tags after the catalogue %s: %s' % ([n for n, _ in zb], u1z))
    else:
        u1z = None
        out.append('U5(1) base of item 591 (d)(2): %d of 7 tags (%s) - not used' % (len(zb), [n for n, _ in zb]))
    per = slow70 / float(holds) if holds else None
    u2 = (per > 1.5 * U5_BASE['slow70_per_hold']) if per is not None else None
    out.append('U5(2) frames >= 70 ms %d per hold %s (base %s, member > 1.5 x base): %s' % (
        slow70, round(per, 4) if per is not None else None, U5_BASE['slow70_per_hold'], u2))
    if b5n:
        b5m = b5sum / b5n
        u3 = b5m > 1.25 * U5_BASE['mean_dt_b5']
        out.append('U5(3) mean dt_us of B5 frames %.1f (n %d; base %s, member > 1.25 x base): %s' % (b5m, b5n, U5_BASE['mean_dt_b5'], u3))
    else:
        u3 = None
        out.append('U5(3) not computable (no B5 frames in the =1 series tags, item 591 (v)(6)) - not in "any of"')
    u4 = nz >= 2
    out.append('U5(4) tags with a nonzero _w invariant %d (member >= 2): %s' % (nz, u4))
    u1f = u1z['fires'] if u1z is not None else u1['fires']
    anyf = bool(u1f) or bool(u2) or bool(u3) or u4
    out.append('U5 ANY %s (U5(1) by %s: %s; U5(2) %s; U5(3) %s; U5(4) %s)' % (
        'FIRES' if anyf else 'no', '7 =0 tags' if u1z is not None else 'F20e 11', u1f, u2, u3, u4))
    return out


def pka(rd):
    runs = load_runs(rd)
    out = []
    got = {}
    for name in COLD:
        tags = sorted(t for t in runs if TAG_RX.match(t).group(1) == name and runs[t].get('admitted'))
        if tags:
            r = runs[tags[0]]['log']
            got[name] = r
            out.append('  %s (%s): frames %d armed %d member %s' % (name, tags[0], len(r['pk_a3']), r['pk_a3_armed'], r['pk_a3_member']))
        else:
            out.append('  %s: no admitted tag' % name)
    a = got.get('b32_pa')
    b = got.get('b32_pa2')
    if a is None:
        res = 'PENDING (b32_pa)'
    elif a['pk_a3_member'] != 'NOT_CALLED':
        res = '%s on b32_pa' % a['pk_a3_member']
    elif b is None:
        res = 'PENDING (b32_pa < 3 frames -> b32_pa2, item 591 (v)(3))'
    elif b['pk_a3_member'] != 'NOT_CALLED':
        res = '%s on b32_pa2' % b['pk_a3_member']
    else:
        res = 'NOT_CALLED (b32_pa and b32_pa2 < 3 frames each - stop before the series, item 591 (v)(3))'
    out.insert(0, 'PK-A %s' % res)
    if a is not None and b is not None:
        n = len(a['pk_a3']) + len(b['pk_a3'])
        arm = a['pk_a3_armed'] + b['pk_a3_armed']
        out.append('  executor variant (b32_pa + b32_pa2 pooled): frames %d armed %d member %s' % (n, arm, pka_member(n, arm)))
    return out


def table(rd):
    tags = sorted(t for t in os.listdir(rd) if TAG_RX.match(t) and os.path.exists(os.path.join(rd, t, 'read.json'))) \\
        if os.path.isdir(rd) else []
    out = ['| tag | adm | bin / sig | K_I / K | in count | classes (n: class) | INSTR_MADE | kq_n=0 | m5r | prev>=100 | PK-A B5 armed | PK-A cold '
           '| U5(1) | U5(4) | load ratio | recov |', '|' + '---|' * 16]
'''))

E.append(('''        out.append('| %s | %s | %s / %s | %s / %s | %s | %s | %s/%s | %s/%s | %s | %s | %s/%s | %s | %s | %s | %s |' % (
            t, 'Y' if res['admitted'] else 'N', (res['binary_sha256'] or '-')[:8], (res['ref'].get('signature') or '-')[:8], r.get('K_I'),
            r.get('K'), r.get('in_count'),
            ' '.join(cl) or '-', r.get('instr_made'), r.get('P_I'), r.get('kq0'), r.get('P_I'), r.get('m5r'), r.get('prev_slow_in_count'),
            r.get('pk_a_armed'), len(r.get('pk_a') or []), r.get('u5_med_dt'), 'NZ' if any((r.get('zero_w_sum') or {}).values()) else '0',
            lr or '-', r.get('recovering')))
''', '''        out.append('| %s | %s | %s / %s | %s / %s | %s | %s | %s/%s | %s/%s | %s | %s | %s/%s | %s/%s %s | %s | %s | %s | %s |' % (
            t, 'Y' if res['admitted'] else 'N', (res['binary_sha256'] or '-')[:8], (res['ref'].get('signature') or '-')[:8], r.get('K_I'),
            r.get('K'), r.get('in_count'),
            ' '.join(cl) or '-', r.get('instr_made'), r.get('P_I'), r.get('kq0'), r.get('P_I'), r.get('m5r'), r.get('prev_slow_in_count'),
            r.get('pk_a_armed'), len(r.get('pk_a') or []), r.get('pk_a3_armed'), len(r.get('pk_a3') or []), r.get('pk_a3_member'),
            r.get('u5_med_dt'), 'NZ' if any((r.get('zero_w_sum') or {}).values()) else '0', lr or '-', r.get('recovering')))
'''))

E.append(('''    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        for l in table(rd):
            print(l)
        return 0
''', '''    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        for l in table(rd):
            print(l)
        return 0
    if '--pka' in argv or '--series' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        if '--pka' in argv:
            lines = pka(rd)
        else:
            lines = series(rd, int(argv[argv.index('--upto') + 1]) if '--upto' in argv else None)
        print('reader b32_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in lines:
            print(l)
        return 0
'''))

E.append(('''        print('usage: b32_read.py b32_z0b|b32_ppb|b32_pcb|b32_pd[_r1..6] | --dir D --tag T | --table | --check-seal')
''', '''        print('usage: b32_read.py b32_pa|b32_pa2|b32_s01..60|b32_z0c1..5[_r1..6] | --dir D --tag T | --table | --pka | --series | --check-seal')
'''))


def main(argv):
    path = argv[0]
    s = open(path, 'rb').read().decode('utf-8')
    assert '\r' not in s
    for i, (a, b) in enumerate(E):
        c = s.count(a)
        if c != 1:
            print('edit %d matches %d times - refused: %r' % (i, c, a[:80]))
            return 1
        s = s.replace(a, b)
    open(path, 'wb').write(s.encode('ascii'))
    print('edits %d applied to %s' % (len(E), path))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

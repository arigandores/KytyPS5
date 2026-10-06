# ---- PK-A of the cold form (item 591 (v)(2)-(4)): domain, member, 'not called'
EARLY = 5            # idx 5 starts at ~0.13 s of the scene (below the old 10 s threshold)
GPU_RUN = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', R=S), thr(2, 'DrawThread', 'guest', W={'eq': S})]
res = read('pk3_early', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=0, threads=GPU_RUN,
                                                                     waits=[dict(slot=2, kind='eq', waker=1)]))}, b5_idx=(EARLY,)))
check('PK-A cold: a B5 frame at 0.13 s is in the domain and armed (EMU_RUN:Gpu); not in the >= 10 s pk_a',
      [x['n'] for x in res['pk_a3']] == [FIRST + EARLY] and res['pk_a3'][0]['armed'] and res['pk_a3'][0]['cls'] == 'EMU_RUN:Gpu' and
      res['pk_a'] == [], (res['pk_a3'], res['pk_a']))
check('PK-A cold: one frame -> member NOT_CALLED', res['pk_a3_member'] == 'NOT_CALLED' and res['pk_a3_armed'] == 1, res['pk_a3_member'])
res = read('pk3_late', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, instr=0, threads=GPU_RUN,
                                                                 waits=[dict(slot=2, kind='eq', waker=1)]))}, b5_idx=(T0,)))
check('PK-A cold: a B5 frame after 10 s is in both domains', len(res['pk_a3']) == 1 and len(res['pk_a']) == 1, (res['pk_a3'], res['pk_a']))
res = read('pk3_instr', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=100001, threads=GPU_RUN)),
                               EARLY + 30: dict(dt=200000, diag=diag_block(FIRST + EARLY + 30, 200000, instr=100000, threads=GPU_RUN))},
                              b5_idx=(EARLY, EARLY + 30)))
check('PK-A cold: dt - instr 99 999 out of the domain, 100 000 in it', [x['n'] for x in res['pk_a3']] == [FIRST + EARLY + 30] and
      [x['n'] for x in res['pk_a3_instr']] == [FIRST + EARLY], (res['pk_a3'], res['pk_a3_instr']))
res = read('pk3_slow', build({EARLY: dict(dt=99999, diag=None), EARLY + 30: dict(dt=100000, diag=None)}, b5_idx=(EARLY, EARLY + 30)))
check('PK-A cold: dt 99 999 not in the domain, 100 000 in it (no DiagB32 line: instr 0, NO_SAMPLES, not armed)',
      [x['n'] for x in res['pk_a3']] == [FIRST + EARLY + 30] and res['pk_a3'][0]['cls'] == 'NO_SAMPLES' and not res['pk_a3'][0]['armed'] and
      res['pk_a3'][0]['instr_us'] is None, res['pk_a3'])
res = read('pk3_notb5', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=0, threads=GPU_RUN))}))
check('PK-A cold: a frame without dump lines (not B5) is not in the domain', res['pk_a3'] == [], res['pk_a3'])
_t = {}
for k in range(4):
    _t[EARLY + 30 * k] = dict(dt=200000, diag=diag_block(FIRST + EARLY + 30 * k, 200000, instr=0, threads=GPU_RUN if k < 2 else [
        thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)],
        waits=[dict(slot=2, kind='eq', waker=1)] if k < 2 else None))
res = read('pk3_fail', build(_t, b5_idx=tuple(_t)))
check('PK-A cold: 4 frames, 2 armed (EMU_RUN:Gpu) and 2 UNMARKED:DrawThread -> FAIL (2/4 < 2/3)', len(res['pk_a3']) == 4 and
      res['pk_a3_armed'] == 2 and res['pk_a3_member'] == 'FAIL', (res['pk_a3_armed'], res['pk_a3_member']))
_t = {}
for k in range(3):
    _t[EARLY + 30 * k] = dict(dt=200000, diag=diag_block(FIRST + EARLY + 30 * k, 200000, instr=0, threads=GPU_RUN if k < 2 else [
        thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', r=S), thr(2, 'DrawThread', 'guest', S=S)],
        waits=[dict(slot=2, kind='eq', waker=1)] if k < 2 else None))
res = read('pk3_arm', build(_t, b5_idx=tuple(_t)))
check('PK-A cold: 3 frames, 2 armed -> ARMED (2/3 exactly)', res['pk_a3_armed'] == 2 and res['pk_a3_member'] == 'ARMED',
      (res['pk_a3_armed'], res['pk_a3_member']))
_t = {}
for k in range(3):
    _t[EARLY + 30 * k] = dict(dt=200000, diag=diag_block(FIRST + EARLY + 30 * k, 200000, instr=0, threads=[
        thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', H={'qsubmit': S}), thr(2, 'DrawThread', 'guest', W={'eq': S})],
        waits=[dict(slot=2, kind='eq', waker=1)]))
res = read('pk3_call', build(_t, b5_idx=tuple(_t)))
check('PK-A cold: EMU_CALL ending on GuestGpu armed, 3 of 3 -> ARMED', res['pk_a3_armed'] == 3 and res['pk_a3_member'] == 'ARMED' and
      res['pk_a3'][0]['cls'].startswith('EMU_CALL:qsubmit'), res['pk_a3'])
for n, a, want in ((0, 0, 'NOT_CALLED'), (2, 2, 'NOT_CALLED'), (3, 2, 'ARMED'), (3, 1, 'FAIL'), (6, 4, 'ARMED'), (6, 3, 'FAIL'),
                   (9, 6, 'ARMED'), (9, 5, 'FAIL'), (3, 3, 'ARMED')):
    check('pka_member(%d, %d) = %s' % (n, a, want), R.pka_member(n, a) == want, R.pka_member(n, a))
_pre = ['FrameTrace: n=%d dt_us=300000 lat_us=12000 gpu_proc=0 draws=10 gpu_busy_us=15000 cpu_gpu_us=30000' % (FIRST - 2),
        'FrameTrace: n=%d dt_us=99999 lat_us=12000 gpu_proc=0 draws=10 gpu_busy_us=15000 cpu_gpu_us=30000' % (FIRST - 1)]
res = read('pk3_pre', build({}, pre_scene=_pre))
check('reference: frames >= 100 ms between the level line and the first scene frame (300 000 yes, 99 999 no)',
      res['pre_scene_slow'] == [(FIRST - 2, 300000)] or res['pre_scene_slow'] == [[FIRST - 2, 300000]], res['pre_scene_slow'])
check('the first scene frame is still n=FIRST with pre-scene frames', res['first_n'] == FIRST, res['first_n'])
res = read('pk3_cold_lines', build({}, pre=['PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\\pipelines.bin yet\n',
                                            'ShaderSeed: installed (730 shaders)\n']))
check('precache and seed lines counted (no 1, recipes 0, other seed 1)', res['precache_no'] == 1 and res['precache_recipes'] == 0 and
      res['seed_other'] == ['ShaderSeed: installed (730 shaders)'], (res['precache_no'], res['precache_recipes'], res['seed_other']))
res = read('pk3_warm_lines', build({}, pre=['PipelinePrecache: 1856 recipes -> 1713 graphics + 143 compute pipelines queued\n',
                                            'PipelinePrecache: all pipelines created, 546 ms\n']))
check('warm precache line counted as recipes (the "all pipelines created" line is neither)', res['precache_no'] == 0 and
      res['precache_recipes'] == 1 and res['seed_other'] == [], (res['precache_no'], res['precache_recipes']))

# ---- admission (--dir form)
S18, TB = R.BIN_INST, R.BIN_TEST
FS8_OLD = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
COLD_OK = dict(reserve_move='RESERVE MOVED files 1460 bytes 600000000 (dirs 2, root files 1345) listsha ab', reserve_cold='COLD OK',
               reserve_check='RESERVE IN AFTER 1460 of 1460')


def adm_dir(name, tag, env_extra, log_text, binary=TB, inst_b=S18, inst_a=S18, mcmp='manifest cmp EQUAL', load=None, hold=330,
            seal_text='seal\ntheta_load: 0.4562\n', reserve=None):
    d = os.path.join(TMP, 'adm_' + name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'log.txt'), 'w', encoding='ascii', newline='\n') as f:
        f.write(log_text)
    with open(os.path.join(d, 'seal.md'), 'w', encoding='ascii', newline='\n') as f:
        f.write(seal_text)
    env = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_GUEST_ARGS='-lvl underwater_aerial_garden', KYTY_GPU_CLOCK_PIN='1',
               KYTY_GPU_MARKERS='0')
    env.update(env_extra)
    js = dict(binary_sha256=binary, prereg=dict(sha256=R.sha_file(os.path.join(d, 'seal.md'))), env=env,
              cmdline=['x', '--vulkan-validation', 'false', '--shader-validation', 'false'], guest_args='-lvl underwater_aerial_garden',
              hold_s=hold, attempts=[dict(outcome='STABLE')])
    with open(os.path.join(d, 'es.json'), 'w', encoding='ascii') as f:
        json.dump(js, f)
    for nm, v in (('installed_before', inst_b), ('installed_after', inst_a), ('manifest_cmp', mcmp)):
        with open(os.path.join(d, nm + '.txt'), 'w', encoding='ascii') as f:
            f.write(v + '\n')
    for nm in ('reserve_move', 'reserve_cold', 'reserve_check'):
        p = os.path.join(d, nm + '.txt')
        if reserve is not None and reserve.get(nm) is not None:
            with open(p, 'w', encoding='ascii') as f:
                f.write(reserve[nm] + '\n')
        elif os.path.exists(p):
            os.remove(p)
    lp = os.path.join(d, 'load.json')
    if load is not None:
        with open(lp, 'w', encoding='ascii') as f:
            json.dump(load, f)
    elif os.path.exists(lp):
        os.remove(lp)
    return R.read_tag(tag, R.paths(tag, d))


def fails(r):
    return [a[0][:60] for a in r['admission'] if not a[1]]


MODE = 'DiagB32: mode=1 period_us=5000 print_us=100000 ncpu=32 kstate=1'
PC_NO = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10_fixf19\\pipelines.bin yet\n'
PC_YES = 'PipelinePrecache: 1856 recipes -> 1713 graphics + 143 compute pipelines queued, 0 skipped\n'
log_on = build({}, pre=[MODE + '\n', PC_YES])
log_off = build({}, pre=[PC_YES])
log_cold = build({}, pre=[MODE + '\n', PC_NO])
F1 = R.form_of('b32_s01')
F0 = R.form_of('b32_z0c1')
check('form_of: =1 for b32_pa, b32_pa2, b32_sNN; =0 for b32_z0c1..5; GPU_WALL=1 always',
      R.form_of('b32_pa') == F1 == R.form_of('b32_pa2') == R.form_of('b32_s60') == dict(KYTY_DIAG_B32='1', KYTY_GPU_WALL='1') and
      F0 == R.form_of('b32_z0c5') == dict(KYTY_DIAG_B32='0', KYTY_GPU_WALL='1'), (F1, F0))
r = adm_dir('pa', 'b32_pa', F1, log_cold, reserve=COLD_OK)
check('admission pa (cold) PASS', r['admitted'], fails(r))
check('theta in the reading = 0.4562 from the seal', r['theta'] == 0.4562, r['theta'])
r = adm_dir('pa2', 'b32_pa2', F1, log_cold, reserve=COLD_OK)
check('admission pa2 (cold) PASS', r['admitted'], fails(r))
r = adm_dir('pa_warmlog', 'b32_pa', F1, log_on, reserve=COLD_OK)
check('admission pa with a warm log (recipes loaded, no "no recipes yet") FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_both', 'b32_pa', F1, build({}, pre=[MODE + '\n', PC_NO, PC_YES]), reserve=COLD_OK)
check('admission pa with both precache lines FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_seed', 'b32_pa', F1, build({}, pre=[MODE + '\n', PC_NO, 'ShaderSeed: installed (730 shaders)\n']), reserve=COLD_OK)
check('admission pa with a ShaderSeed install line FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_nomove', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_move=None))
check('admission pa without reserve_move FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_movefail', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_move='RESERVE FAILED the live set is incomplete'))
check('admission pa with RESERVE FAILED FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_notcold', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_cold='COLD NOT 1 items: _ShaderSeeds/PPSA21564'))
check('admission pa with COLD NOT FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_noback', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_check='RESERVE NOT IN AFTER missing 3 of 1460'))
check('admission pa with the reserve not back FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_nocheck', 'b32_pa', F1, log_cold, reserve=dict(COLD_OK, reserve_check=None))
check('admission pa without reserve_check FAIL', not r['admitted'], fails(r))
r = adm_dir('pa_off', 'b32_pa', F0, build({}, pre=[PC_NO]), reserve=COLD_OK)
check('admission pa with KYTY_DIAG_B32=0 FAIL', not r['admitted'], fails(r))
r = adm_dir('s01', 'b32_s01', F1, log_on)
check('admission s01 (warm) PASS', r['admitted'], fails(r))
r = adm_dir('s01_res', 'b32_s01', F1, log_on, reserve=COLD_OK)
check('admission s01 with cold reserve files FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_res1', 'b32_s01', F1, log_on, reserve=dict(reserve_move=None, reserve_cold=None, reserve_check='RESERVE IN AFTER 1 of 1'))
check('admission s01 with one reserve file FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_cold', 'b32_s01', F1, log_cold)
check('admission s01 with a cold log (warm form: precache line is reference) PASS', r['admitted'], fails(r))
r = adm_dir('s60', 'b32_s60', F1, log_on)
check('admission s60 PASS', r['admitted'], fails(r))
r = adm_dir('z0c', 'b32_z0c1', F0, log_off)
check('admission z0c1 (=0) PASS', r['admitted'], fails(r))
r = adm_dir('z0c_diag', 'b32_z0c1', F0, log_on)
check('admission z0c1 with a DiagB32 mode line FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_off', 'b32_s01', F1, log_off)
check('admission s01 without the DiagB32 mode line FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_f0', 'b32_s01', F0, log_on)
check('admission s01 with the env KYTY_DIAG_B32=0 FAIL', not r['admitted'], fails(r))
r = adm_dir('nothe', 'b32_s01', F1, log_on, seal_text='seal\n')
check('admission: no theta_load line in the seal FAIL, the log is not read', not r['admitted'] and r['log'] is None)
check('admission: the theta_load row itself FAIL when the seal has no line',
      [a[1] for a in r['admission'] if a[0].startswith('theta_load from the seal')] == [False], fails(r))
r = adm_dir('s01_stand', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], test_fire_idx=T0))
check('admission s01 with stand lines FAIL', not r['admitted'], fails(r))
r = adm_dir('s01_load', 'b32_s01', F1, log_on, load=dict(status='done', mode='all', n_start=1, n_end=2))
check('admission s01 with a loader json FAIL', not r['admitted'], fails(r))
r = adm_dir('bin_s18', 'b32_s01', F1, log_on, binary=S18)
check('admission: json binary S18 (not the test binary) FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_fs8', 'b32_s01', F1, log_on, inst_b=FS8_OLD, inst_a=FS8_OLD)
check('admission: installed FS8 (not S18) before and after FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_after', 'b32_s01', F1, log_on, inst_a=TB)
check('admission: installed after = test binary FAIL', not r['admitted'], fails(r))
r = adm_dir('inst_before', 'b32_s01', F1, log_on, inst_b=S18[:63] + '0')
check('admission: installed before differs in the last hex digit FAIL', not r['admitted'], fails(r))
r = adm_dir('env_extra', 'b32_s01', dict(F1, KYTY_X='1'), log_on)
check('admission: extra env FAIL', not r['admitted'], fails(r))
r = adm_dir('env_nowall', 'b32_s01', dict(KYTY_DIAG_B32='1'), log_on)
check('admission: no KYTY_GPU_WALL FAIL', not r['admitted'], fails(r))
r = adm_dir('sig', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[SEED_LINES[0], SEED_LINES[1].replace('9177b426', '9177b427')]))
check('admission: translation signature not FS8 FAIL', not r['admitted'] and r['ref']['signature'].startswith('9177b427'))
r = adm_dir('vdir', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[SEED_LINES[0].replace('fixf19', 'fixf18'), SEED_LINES[1]]))
check('admission: cache variant dir not _fixf19 FAIL', not r['admitted'], fails(r))
r = adm_dir('noseed', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], seed=[]))
check('admission: no ShaderSeed line FAIL', not r['admitted'], fails(r))
r = adm_dir('recov', 'b32_s01', F1, build({}, pre=[MODE + '\n', PC_YES], recovering=True))
check('admission: Recovering Vulkan swapchain FAIL', not r['admitted'], fails(r))
r = adm_dir('cache', 'b32_s01', F1, log_on, mcmp='manifest cmp DIFFER only-before 1 only-after 1')
check('admission: caches not returned FAIL', not r['admitted'], fails(r))
r = adm_dir('hold', 'b32_s01', F1, log_on, hold=300)
check('admission: hold 300 FAIL', not r['admitted'], fails(r))
rd = build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, cum={'rep_drop': 1}))}, pre=[MODE + '\n', PC_YES])
r = adm_dir('repdrop', 'b32_s01', F1, rd)
check('admission: rep_drop != 0 FAIL', not r['admitted'] and r['log']['rep_drop'] == 1, fails(r))
r = adm_dir('repeat', 'b32_s07_r1', F1, log_on)
check('a repeat name b32_s07_r1 reads with the form of b32_s07', r['admitted'] and r['form'] == 'b32_s07', fails(r))
r = adm_dir('repeat_pa', 'b32_pa_r2', F1, log_cold, reserve=COLD_OK)
check('a repeat name b32_pa_r2 is cold too', r['admitted'] and r['form'] == 'b32_pa' and
      any(a[0].startswith('cold form: reserve moved') for a in r['admission']), fails(r))
for good in ('b32_pa', 'b32_pa2', 'b32_s01', 'b32_s09', 'b32_s10', 'b32_s59', 'b32_s60', 'b32_z0c1', 'b32_z0c5', 'b32_s60_r6', 'b32_pa2_r1',
             'b32_z0c3_r4'):
    check('tag name %s accepted' % good, R.TAG_RX.match(good) is not None)
for bad in ('b32_s00', 'b32_s61', 'b32_s1', 'b32_s100', 'b32_pa3', 'b32_z0c0', 'b32_z0c6', 'b32_s01_r7', 'b32_s01_r0', 'b32_z0b', 'b32_ppb',
            'b32_pcb', 'b32_pd', 'b32_z0', 'f20_v25', '', 'b32_pa_r'):
    check('tag name %r refused' % bad, R.TAG_RX.match(bad) is None)
_p = R.paths('b32_s07')
check('paths b32_s07: F20l3 files and seal', _p['log'].replace('\\', '/') == 'C:/kyty/f287/f20l3/log_b32_s07.txt' and
      _p['seal'] == R.SEAL_PATH and _p['theta_src'] == R.SEAL_PATH and _p['reserve_move'].replace('\\', '/').endswith(
          'f20l3/runs/b32_s07/reserve_move.txt'), _p)
check('installed S18 constant = the full sha256 of item 590 / 591 (g)(3)',
      R.BIN_INST == 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a')

# ---- exact two-sided Mann-Whitney (item 555 (b)(2)) against a brute force over every split
import itertools  # noqa: E402


def brute_p(a, b):
    pooled = sorted(a + b)
    n = len(pooled)
    rank = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and pooled[j + 1] == pooled[i]:
            j += 1
        rank[pooled[i]] = (i + j + 2) / 2.0
        i = j + 1
    vals = [rank[v] for v in a + b]
    m = len(b)
    mean = m * (n + 1) / 2.0
    obs = abs(sum(rank[v] for v in b) - mean)
    tot = ext = 0
    for comb in itertools.combinations(range(n), m):
        tot += 1
        if abs(sum(vals[k] for k in comb) - mean) >= obs - 1e-9:
            ext += 1
    return ext / float(tot)


for a, b, want in (([1, 2, 3], [4, 5, 6], 0.1), ([1, 2, 3, 4], [5, 6, 7, 8], 2.0 / 70), ([4, 5, 6], [1, 2, 3], 0.1),
                   ([1, 2, 3], [1, 2, 3], 1.0)):
    u, p = R.mw_exact(a, b)
    check('mw_exact %s vs %s p = %.4f' % (a, b, want), abs(p - want) < 1e-12, p)
for a, b in (([1, 1, 2, 5, 7], [2, 3, 3, 9]), ([10, 20, 20, 30, 30, 30], [20, 30, 40, 40]), ([5, 6, 7, 8, 9, 10, 11], [1, 2, 6, 7]),
             ([36000, 36500, 41000, 37000, 35000, 36000], [36171.5, 35115, 46632, 36000, 34904.5]),
             ([1, 2, 3, 4, 5, 6, 7, 8], [2, 4, 6])):
    check('mw_exact = brute force over every split %s / %s' % (a[:3], b[:3]), abs(R.mw_exact(a, b)[1] - brute_p(a, b)) < 1e-12,
          (R.mw_exact(a, b)[1], brute_p(a, b)))
check('mw_exact U of a: [1,2,3] vs [4,5,6] -> 0', R.mw_exact([1, 2, 3], [4, 5, 6])[0] == 0.0, R.mw_exact([1, 2, 3], [4, 5, 6]))
_base = list(R.U5_F20E_MEDS)
check('U5 F20e base: 11 medians, median 36 171.5', len(_base) == 11 and statistics.median(_base) == 36171.5, statistics.median(_base))
u = R.u5_one(_base, _base)
check('u5_one: the base against itself - dev 0, p 1, does not fire', u['dev'] == 0 and abs(u['p'] - 1.0) < 1e-12 and u['fires'] is False, u)
hi = [x * 1.10 for x in _base] + [40000.0]
u = R.u5_one(hi, _base)
check('u5_one: +10 %% on 12 tags - dev > 2 %% and p < 0.05 -> fires', u['fires'] is True and u['p'] < 0.05 and u['dev'] > 0.02, u)
u = R.u5_one([40000.0], _base)
check('u5_one: one tag +10.6 %% - p >= 0.05 -> does not fire (the test, not the 2 %% alone)', u['fires'] is False and u['p'] >= 0.05, u)
near = [36171.5 * 1.019 + k for k in range(12)]
u = R.u5_one(near, _base)
check('u5_one: median +1.9 %% - does not fire even when p is small', u['fires'] is False and abs(u['dev']) <= 0.02, u)
lo = [x * 0.9 for x in _base] + [30000.0]
u = R.u5_one(lo, _base)
check('u5_one: -10 %% two-sided -> fires', u['fires'] is True and u['dev'] < -0.02, u)
check('u5_one: second mode counted > 40 000 (F20e 3 of 11)', R.u5_one(_base, _base)['base_second_mode'] == 3)
check('u5_one: no medians -> fires None', R.u5_one([], _base)['fires'] is None)

# ---- series summary, stop rule, U5 of the series, PK-A over b32_pa / b32_pa2 (fake runs/<tag>/read.json)
RUNS = os.path.join(TMP, 'runs_series')


def put(tag, admitted=True, hold=True, K=0, cls=None, fam=None, med=36000.0, slow70=0, b5=(), zw=0, pk3=None):
    d = os.path.join(RUNS, tag)
    os.makedirs(d, exist_ok=True)
    pk3 = pk3 or []
    log = dict(hold=hold, K=K, hold_class=cls, hold_family=fam, u5_med_dt=med, u5_slow70=slow70, u5_b5_n=len(b5),
               u5_b5_mean=(sum(b5) / float(len(b5))) if b5 else None, zero_w_sum=dict(torn_w=zw),
               pk_a3=[dict(n=k, armed=a) for k, a in enumerate(pk3)], pk_a3_armed=sum(1 for a in pk3 if a),
               pk_a3_member=R.pka_member(len(pk3), sum(1 for a in pk3 if a)))
    with open(os.path.join(d, 'read.json'), 'w', encoding='ascii') as f:
        json.dump(dict(admitted=admitted, log=log), f)
    with open(os.path.join(d, 'read.txt'), 'w', encoding='ascii') as f:
        f.write(tag + '\n')


def series_of(upto=None):
    return R.series(RUNS, upto)


def line(out, key):
    return [x for x in out if x.startswith(key)]


shutil.rmtree(RUNS, ignore_errors=True)
for k in range(1, 29):
    put('b32_s%02d' % k)
out = series_of()
check('series: 28 holds -> CONTINUE', line(out, 'HOLDS 28 K 0') and line(out, 'STOP RULE CONTINUE (holds 28'), out[-12:])
put('b32_s29')
out = series_of()
check('series: 29 holds K 0 -> STOP_U2', line(out, 'STOP RULE STOP_U2 ') or line(out, 'STOP RULE STOP_U2 (K 0'), line(out, 'STOP RULE'))
put('b32_s29', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
put('b32_s05', K=1, cls='UNMARKED:Gpu', fam='UNMARKED')
out = series_of()
check('series: 29 holds K 2 -> CONTINUE up to K 3 or 60', line(out, 'HOLDS 29 K 2') and line(out, 'STOP RULE CONTINUE (K 2 at 29'),
      line(out, 'STOP RULE'))
put('b32_s12', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
out = series_of()
check('series: 29 holds K 3 -> STOP_READ', line(out, 'STOP RULE STOP_READ (K 3 >= 3 at 29'), line(out, 'STOP RULE'))
check('series: class shares of K - (iv) top family EMU_RUN 2/3', any('top family EMU_RUN 0.6667' in x for x in out),
      [x for x in out if 'top family' in x])
check('series: (i) UNDETERMINED + UNMARKED + NO_SAMPLES 1/3', any('(i) UNDETERMINED + UNMARKED + NO_SAMPLES 0.3333' in x for x in out),
      [x for x in out if '(i)' in x])
put('b32_s12', K=0)
put('b32_s30', admitted=False, K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
put('b32_s30_r1', K=0)
out = series_of()
check('series: an interfered tag is replaced by its admitted repeat (s30 not admitted, s30_r1 counts once)',
      line(out, 'HOLDS 30 K 2') and line(out, 'SERIES over') and 'admitted series tags 30' in out[0], out[0])
put('b32_s31', hold=False)
out = series_of()
check('series: an admitted tag without a hold is not a hold', line(out, 'HOLDS 30 K 2') and 'admitted series tags 31' in out[0], out[0])
put('b32_pa', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
put('b32_z0c1', K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
out = series_of()
check('series: b32_pa and b32_z0c tags are not series holds', line(out, 'HOLDS 30 K 2'), line(out, 'HOLDS'))
for k in range(32, 61):
    put('b32_s%02d' % k)
out = series_of()
check('series: 59 holds K 2 -> STOP_U2PRIME only at 60 holds (s31 has no hold)', line(out, 'HOLDS 59 K 2') and
      line(out, 'STOP RULE CONTINUE (K 2 at 59'), line(out, 'STOP RULE'))
put('b32_s31')
out = series_of()
check('series: 60 holds K 2 -> STOP_U2PRIME', line(out, 'HOLDS 60 K 2') and line(out, 'STOP RULE STOP_U2PRIME'), line(out, 'STOP RULE'))
out = series_of(10)
check('series --upto 10: the first 10 admitted series tags', 'admitted series tags 10 (first 10)' in out[0] and line(out, 'HOLDS 10 K 1'),
      (out[0], line(out, 'HOLDS')))
# U5 of the series
shutil.rmtree(RUNS, ignore_errors=True)
for k in range(1, 11):
    put('b32_s%02d' % k, med=36000.0 + 10 * k)
out = series_of()
check('series U5(1) vs F20e: base medians near 36 000 -> does not fire', any(x.startswith('U5(1) vs F20e 11') and "'fires': False" in x
                                                                             for x in out), line(out, 'U5(1)'))
check('series U5(3): no B5 frames -> not computable, not in any of', line(out, 'U5(3) not computable') and line(out, 'U5 ANY no'),
      line(out, 'U5'))
check('series U5(1): 2 of 7 =0 tags without the b32_z0c tags -> not used', line(out, 'U5(1) base of item 591 (d)(2): 2 of 7'),
      line(out, 'U5(1) base'))
for k in range(1, 11):
    put('b32_s%02d' % k, med=47000.0 + 10 * k)
out = series_of()
check('series U5(1) vs F20e: medians 47 000 -> fires, U5 ANY FIRES', any(x.startswith('U5(1) vs F20e 11') and "'fires': True" in x
                                                                        for x in out) and line(out, 'U5 ANY FIRES'), line(out, 'U5'))
for k in range(1, 5):
    put('b32_z0c%d' % k, med=47000.0 + 7 * k)
out = series_of()
check('series U5(1): 4 of 5 b32_z0c -> base not used, F20e base decides', line(out, 'U5(1) base of item 591 (d)(2): 6 of 7') and
      line(out, 'U5 ANY FIRES (U5(1) by F20e 11'), line(out, 'U5'))
put('b32_z0c5', admitted=False, med=47000.0)
out = series_of()
check('series U5(1): a non-admitted b32_z0c5 does not complete the base', line(out, 'U5(1) base of item 591 (d)(2): 6 of 7'), line(out, 'U5(1)'))
put('b32_z0c5_r1', med=47035.0)
out = series_of()
check('series U5(1): 7 =0 tags (b32_z0, b32_z0b, b32_z0c1..5) -> base decides, medians 47 055 vs base 47 014 -> no',
      any(x.startswith('U5(1) vs the 7 =0 tags') and "'fires': False" in x for x in out) and line(out, 'U5 ANY no (U5(1) by 7 =0 tags'),
      line(out, 'U5'))
put('b32_s03', med=47030.0, b5=(200000.0,))
out = series_of()
check('series U5(3): pooled B5 mean 200 000 > 1.25 x 134 767.7 -> yes, U5 ANY FIRES', any(x.startswith('U5(3) mean dt_us of B5 frames 200000.0')
                                                                                        and x.endswith('True') for x in out) and
      line(out, 'U5 ANY FIRES'), line(out, 'U5'))
put('b32_s03', med=47030.0, b5=(160000.0, 170000.0))
out = series_of()
check('series U5(3): pooled B5 mean 165 000 <= 168 459.6 -> no', any(x.startswith('U5(3) mean dt_us of B5 frames 165000.0') and
                                                                    x.endswith('False') for x in out), line(out, 'U5(3)'))
put('b32_s04', med=47040.0, zw=1)
out = series_of()
check('series U5(4): one tag with a nonzero invariant -> no', line(out, 'U5(4) tags with a nonzero _w invariant 1 (member >= 2): False'),
      line(out, 'U5(4)'))
put('b32_s05', med=47050.0, zw=2)
out = series_of()
check('series U5(4): two tags -> FIRES', line(out, 'U5(4) tags with a nonzero _w invariant 2 (member >= 2): True') and line(out, 'U5 ANY FIRES'),
      line(out, 'U5'))
put('b32_s04', med=47040.0)
put('b32_s05', med=47050.0)
put('b32_s06', med=47060.0, slow70=10)
out = series_of()
check('series U5(2): 10 frames >= 70 ms over 10 holds = 1.0 > 0.8415 -> True', line(out, 'U5(2) frames >= 70 ms 10 per hold 1.0') and
      line(out, 'U5 ANY FIRES'), line(out, 'U5(2)'))
put('b32_s06', med=47060.0, slow70=8)
out = series_of()
check('series U5(2): 0.8 per hold <= 0.8415 -> False', any(x.startswith('U5(2) frames >= 70 ms 8 per hold 0.8') and x.endswith('False')
                                                          for x in out), line(out, 'U5(2)'))
# PK-A over b32_pa / b32_pa2
shutil.rmtree(RUNS, ignore_errors=True)
out = R.pka(RUNS)
check('pka: nothing -> PENDING (b32_pa)', out[0] == 'PK-A PENDING (b32_pa)', out[0])
put('b32_pa', pk3=[True, True, False])
check('pka: b32_pa 3 frames 2 armed -> ARMED on b32_pa', R.pka(RUNS)[0] == 'PK-A ARMED on b32_pa', R.pka(RUNS)[0])
put('b32_pa', pk3=[True, False, False])
check('pka: b32_pa 3 frames 1 armed -> FAIL on b32_pa', R.pka(RUNS)[0] == 'PK-A FAIL on b32_pa', R.pka(RUNS)[0])
put('b32_pa', pk3=[True, True])
check('pka: b32_pa 2 frames -> PENDING b32_pa2', R.pka(RUNS)[0].startswith('PK-A PENDING (b32_pa < 3 frames -> b32_pa2'), R.pka(RUNS)[0])
put('b32_pa2', pk3=[True])
out = R.pka(RUNS)
check('pka: b32_pa 2 + b32_pa2 1 -> NOT_CALLED (each < 3), pooled variant printed ARMED', out[0].startswith('PK-A NOT_CALLED') and
      any('pooled): frames 3 armed 3 member ARMED' in x for x in out), out)
put('b32_pa2', pk3=[False, False, False, True])
check('pka: b32_pa2 4 frames 1 armed -> FAIL on b32_pa2', R.pka(RUNS)[0] == 'PK-A FAIL on b32_pa2', R.pka(RUNS)[0])
put('b32_pa2', admitted=False, pk3=[True, True, True])
put('b32_pa2_r1', pk3=[True, True, True])
check('pka: a non-admitted b32_pa2 is replaced by its admitted repeat -> ARMED on b32_pa2', R.pka(RUNS)[0] == 'PK-A ARMED on b32_pa2',
      R.pka(RUNS))
put('b32_pa', admitted=False, pk3=[True, True, True])
check('pka: a non-admitted b32_pa -> PENDING (b32_pa)', R.pka(RUNS)[0] == 'PK-A PENDING (b32_pa)', R.pka(RUNS)[0])
shutil.rmtree(RUNS, ignore_errors=True)


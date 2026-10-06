# ---- fixtures added after the first sens_b32.py run (12 edits missed of 172)
r = adm_dir('pa_nolines', 'b32_pa', F1, build({}, pre=[MODE + '\n']), reserve=COLD_OK)
check('admission pa without any PipelinePrecache line FAIL (the "no recipes yet" line is required)', not r['admitted'], fails(r))
_c5 = [SEED_LINES[0]] + [SEED_LINES[1]] * 5
res = read('seed5', build({}, seed=_c5))
check('five compatibility lines: none of them is an "other ShaderSeed line"', res['seed_other'] == [] and len(res['sig']) == 4,
      (res['seed_other'], len(res['sig'])))
res = read('pk3_load', build({EARLY: dict(dt=200000, diag=diag_block(FIRST + EARLY, 200000, instr=0, threads=GPU_RUN,
                                                                    waits=[dict(slot=2, kind='eq', waker=1)], other=int(0.8 * 32 * 200000)))},
                             b5_idx=(EARLY,)), theta=0.4562)
check('PK-A cold domain is classified with theta_load (other_us 0.8 -> HOST_LOAD, not armed)', res['pk_a3'][0]['cls'] == 'HOST_LOAD' and
      not res['pk_a3'][0]['armed'], res['pk_a3'])
_pre = ['FrameTrace: n=%d dt_us=100000 lat_us=12000 gpu_proc=0 draws=10 gpu_busy_us=15000 cpu_gpu_us=30000' % (FIRST - 1)]
res = read('pk3_pre100', build({}, pre_scene=_pre))
check('reference pre-scene frames: dt exactly 100 000 counts', [list(x) for x in res['pre_scene_slow']] == [[FIRST - 1, 100000]],
      res['pre_scene_slow'])
_m = [37000.0] * 11 + [50000.0] * 10
u = R.u5_one(_m, _base)
check('u5_one: median +2.29 %% (between 2 %% and 3 %%) with p < 0.05 -> fires', 0.02 < u['dev'] < 0.03 and u['p'] < 0.05 and u['fires'] is True,
      u)
_m = [41000.0 + 10 * k for k in range(1, 11)]
u = R.u5_one(_m, _base)
check('u5_one: dev > 2 %% and 0.05 <= p < 0.10 -> does not fire', u['dev'] > 0.02 and 0.05 <= u['p'] < 0.10 and u['fires'] is False, u)
check('U5 F20e base: the 11 medians of base_f20l.txt lines 33-43 exactly', tuple(R.U5_F20E_MEDS) == (
    36818.5, 46632.0, 34904.5, 35800.0, 36171.5, 36082.0, 36443.0, 35844.0, 35115.0, 41596.0, 45939.5), R.U5_F20E_MEDS)
_z = []
for _f in ('C:/kyty/f287/f20l/runs/b32_z0/read.json', 'C:/kyty/f287/f20l2/runs/b32_z0b/read.json'):
    _z.append(json.load(open(_f, encoding='utf-8'))['log']['u5_med_dt'] if os.path.exists(_f) else None)
check('U5 =0 base: b32_z0 and b32_z0b medians = the F20l / F20l2 read.json', R.U5_Z0_MEDS == (('b32_z0', _z[0]), ('b32_z0b', _z[1])) and
      _z == [36451.5, 41478.5], (R.U5_Z0_MEDS, _z))
shutil.rmtree(RUNS, ignore_errors=True)
for k in range(1, 30):
    put('b32_s%02d' % k)
put('b32_s07', hold=False, K=1, cls='EMU_RUN:Gpu', fam='EMU_RUN')
out = series_of()
check('series: a tag without a hold but with K 1 is not in K', line(out, 'HOLDS 28 K 0'), line(out, 'HOLDS'))
put('b32_s07')
put('b32_s08', b5=(170000.0,))
out = series_of()
check('series U5(3): pooled B5 mean 170 000 (between 1.25 x and 1.3 x base) -> True', any(
    x.startswith('U5(3) mean dt_us of B5 frames 170000.0') and x.endswith('True') for x in out), line(out, 'U5(3)'))
shutil.rmtree(RUNS, ignore_errors=True)
put('b32_pa', pk3=[True, True, True])
put('b32_pa2', pk3=[False, False, False])
check('pka: b32_pa ARMED decides, b32_pa2 (not needed) does not override', R.pka(RUNS)[0] == 'PK-A ARMED on b32_pa', R.pka(RUNS))
shutil.rmtree(RUNS, ignore_errors=True)
_tp = [dict(text='TestB32: armed delay_s=60 mode=present ms=200'), dict(text='TestB32: fire mode=present ms=200'),
       dict(text='TestB32: done mode=present slept_us=200000')]
check('stand_ok: present lines do not satisfy a gpusleep stand; they satisfy a present stand',
      not R.stand_ok(_tp, '60:gpusleep:200') and R.stand_ok(_tp, '60:present:200'))


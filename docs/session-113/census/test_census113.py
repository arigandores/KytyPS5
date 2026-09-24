#!/usr/bin/env python3
"""test_census113.py -- fixtures for census113.py (run BEFORE any real log is read).

Generates small synthetic logs with known answers under bda113/fixtures/ and checks every
definition of the census: OLD and NEW runs (two of each in one build, so the within-build
difference is known exactly), a log without bda_scan, a run that switches mid-run, a run with
too few rows, a content duplicate carried by a later folder, `_warmup` attempt mapping, a
schedule (ABBA) run whose bda_scan depends on the arm, a log with two process segments (n restarts),
and an old-format run (json with `sha256`, phases file, no FrameTrace-x lines).

  python test_census113.py      -> prints PASS/FAIL per check, exit 0 only when all pass
"""
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
sys.path.insert(0, HERE)
import census113 as C  # noqa: E402

FX = HERE + '/fixtures'
FAILS = []


def check(name, got, want):
    ok = got == want
    print('%s  %-58s got=%r%s' % ('PASS' if ok else 'FAIL', name, got, '' if ok else ' want=%r' % (want,)))
    if not ok:
        FAILS.append(name)


def check_true(name, cond, info=''):
    print('%s  %-58s %s' % ('PASS' if cond else 'FAIL', name, info))
    if not cond:
        FAILS.append(name)


# ---------------------------------------------------------------------------------------------
# value patterns

def d5(n):
    return (n % 5) - 2


def old_bda(n):
    return 0 if n <= 240 else 1066 + d5(n)


def new_bda(n):
    return 0 if n <= 120 else 52 + d5(n)


def values(n, bda, steady_dt, cls, stable=282):
    old = cls == 'OLD'
    return dict(
        dt_us=60000 if n <= stable else steady_dt,
        cpu_gpu_us=50000 if n <= stable else steady_dt - 1000,
        gpu_busy_us=12000, draws=100 if n <= 200 else 6000, faults=10, fault_us=500, faults_gpu=3,
        spin_gpu_us=100, prot_us=4000, prot_gpu_us=1800,
        buf_new=(20 if old else 2) if n <= 300 else 3, buf_new_us=5, img_new=4, img_up=12, bufepoch=11000,
        bda_n=150, bda_scan=bda(n), bda_skip=24000, da_take_us=3500,
        up_series=7, sync_up_kb=20000, buflru_n=50000 if n <= 300 else (60000 if old else 55000),
        buflru_rep=40000, fbp_n=1, fbp_ns=900, rt_att=10, rt_kpx=20160)


def write_log(path, ns, fn, with_bda=True, with_x=True, arm_fn=None, extra=None, level='underwater_aerial_garden'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    extra = extra or {}
    with open(path, 'wb') as fh:
        fh.write(b'TITLE_ID, string = PPSA21564\n')
        fh.write(b'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)\n')
        fh.write(b'PipelinePrecache: 10 recipes -> 8 graphics + 2 compute pipelines queued\n')
        for n in ns:
            for ln in extra.get(n, []):
                fh.write(ln.encode() + b'\n')
            v = fn(n)
            arm = arm_fn(n) if arm_fn else 0
            main = ('FrameTrace: n=%d dt_us=%d lat_us=1 gpu_proc=0 submits=3 draws=%d faults=%d fault_us=%d '
                    'gpu_busy_us=%d cpu_gpu_us=%d faults_gpu=%d fault_gpu_us=0' % (
                        n, v['dt_us'], v['draws'], v['faults'], v['fault_us'], v['gpu_busy_us'], v['cpu_gpu_us'],
                        v['faults_gpu']))
            if with_x:
                main += ' arm=%d blk=0 rt_w=3840 rt_h=2160' % arm
            fh.write(main.encode() + b'\n')
            if n == 100 and level:
                fh.write(b'GuestOut: Level has started: \n')
                fh.write(b'GuestOut: Level has started: ' + level.encode() + b'\n')
            draw = ('FrameTrace-draw: n=%d logs=1 spin_gpu_us=%d prot_us=%d buf_new=%d buf_new_us=%d img_new=%d '
                    'img_up=%d bufepoch=%d bda_us=0 bda_n=%d' % (
                        n, v['spin_gpu_us'], v['prot_us'], v['buf_new'], v['buf_new_us'], v['img_new'], v['img_up'],
                        v['bufepoch'], v['bda_n']))
            if with_bda:
                draw += ' bda_scan=%d bda_skip=%d' % (v['bda_scan'], v['bda_skip'])
            draw += ' da_take_us=%d prot_gpu_us=%d' % (v['da_take_us'], v['prot_gpu_us'])
            fh.write(draw.encode() + b'\n')
            fh.write(('FrameTrace-rp: n=%d ends=1 restarts=0\n' % n).encode())
            if with_x:
                fh.write(('FrameTrace-x: n=%d ds_ring_new=0 up_series=%d sync_up_kb=%d buflru_n=%d buflru_rep=%d '
                          'fbp_n=%d fbp_ns=%d a_mut_us=0 rt_att=%d rt_kpx=%d bda_scan_us=1\n' % (
                              n, v['up_series'], v['sync_up_kb'], v['buflru_n'], v['buflru_rep'], v['fbp_n'],
                              v['fbp_ns'], v['rt_att'], v['rt_kpx'])).encode())
            fh.write(b'FrameTrace-wait: other=1/1\n')
            fh.write(b'Vulkan something unrelated FrameTrace: n=999999 dt_us=1\n')


def write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        json.dump(d, fh)


def run_json(tag, sha, started, stable=282, attempts=None, env=None, schedule=None, gates='', extra=None):
    d = _run_json(tag, sha, started, stable, attempts, env, schedule, gates)
    d.update(extra or {})
    return d


def _run_json(tag, sha, started, stable, attempts, env, schedule, gates):
    e = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden'}
    e.update(env or {})
    if schedule:
        e['KYTY_GATE_SCHEDULE'] = schedule
    return dict(tag=tag, binary_sha256=sha, started=started, env=e, schedule=schedule, gates=gates,
                attempts=attempts or [dict(label='attempt 1', attempt=1, stable_frame=stable, outcome='ok',
                                           level='underwater_aerial_garden', hold_s=100.0, document_s=10.0,
                                           started_s=12.0, stable_s=15.0)])


def make_fixtures():
    if os.path.isdir(FX):
        shutil.rmtree(FX)
    A, B, Cc, D = 'a' * 64, 'b' * 64, 'c' * 64, 'd' * 64
    N = range(1, 3001)
    # s901: two OLD and two NEW runs of one build
    for tag, bda, dt, cls, started in (('old901', old_bda, 40000, 'OLD', '2026-01-01T00:00:00'),
                                       ('new901', new_bda, 33000, 'NEW', '2026-01-01T01:00:00'),
                                       ('old901b', old_bda, 42000, 'OLD', '2026-01-01T02:00:00'),
                                       ('new901b', new_bda, 35000, 'NEW', '2026-01-01T03:00:00')):
        write_log(FX + '/s901/log_%s.txt' % tag, N, lambda n, b=bda, t=dt, c=cls: values(n, b, t, c))
        write_json(FX + '/s901/%s.json' % tag, run_json(tag, A, started, gates='copy=1 bdastamp=1 fslean=0'))
    # s902: no bda_scan field; a mid-run switch
    write_log(FX + '/s902/log_nob902.txt', N, lambda n: values(n, new_bda, 33000, 'NEW'), with_bda=False)
    write_json(FX + '/s902/nob902.json', run_json('nob902', B, '2026-01-02T00:00:00'))
    def sw_vals(n):
        v = values(n, (lambda k: 52 + d5(k) if k <= 1500 else 1066 + d5(k)), 36000, 'NEW')
        v['buf_new'] = 1 if v['bda_scan'] >= 500 else 0     # object creation exactly on the k>=1 flips
        if n >= 1483:
            v['dt_us'] = 37000                                 # the OLD episode (windows from n=1483) is slower
        return v
    write_log(FX + '/s902/log_sw902.txt', N, sw_vals)
    write_json(FX + '/s902/sw902.json', run_json('sw902', B, '2026-01-02T01:00:00'))
    # a NEW run with one 180-flip OLD burst (n 962..1141): transient, not a switch
    write_log(FX + '/s902/log_tr902.txt', N,
              lambda n: values(n, (lambda k: 1066 + d5(k) if 962 <= k <= 1141 else new_bda(k)), 36000, 'NEW'))
    write_json(FX + '/s902/tr902.json', run_json('tr902', B, '2026-01-02T02:00:00'))
    # s903: too few rows, no json; a content duplicate of s901/old901 carried by a later folder
    write_log(FX + '/s903/log_few903.txt', range(1, 151), lambda n: values(n, new_bda, 33000, 'NEW'))
    shutil.copyfile(FX + '/s901/log_old901.txt', FX + '/s903/log_old901.txt')
    # s904: warmup + ABBA run whose arm 1 scans like OLD; a log with two process segments
    sched = '90+1800:bdaall=1|bdaall=0'

    def arm_of(n):
        return 0 if n < 1800 else [0, 1, 1, 0][((n - 1800) // 90) % 4]

    def abba_vals(n):
        a = arm_of(n)
        v = values(n, (lambda k: 1066 + d5(k)) if a == 1 else new_bda, 36000 if a == 1 else 33000, 'NEW')
        return v
    extra = {}
    for b in range(0, 14):
        f = 1800 + 90 * b
        a = [0, 1, 1, 0][b % 4]
        extra[f] = ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=bdaall=%d' % (a, b, f, 1 - a),
                    'Gate: bdaall=%d frame=%d' % (1 - a, f)]
    write_log(FX + '/s904/log_abba904.txt', N, abba_vals, arm_fn=arm_of, extra=extra)
    write_log(FX + '/s904/log_abba904_warmup.txt', range(1, 1001), lambda n: values(n, new_bda, 33000, 'NEW', 290))
    write_json(FX + '/s904/abba904.json', run_json(
        'abba904', Cc, '2026-01-03T00:00:00', schedule=sched, env={'KYTY_GATE_SCHEDULE_ABBA': '1'},
        attempts=[dict(label='warmup', attempt=0, stable_frame=290, outcome='ok', level='underwater_aerial_garden'),
                  dict(label='attempt 1', attempt=1, stable_frame=282, outcome='ok', level='underwater_aerial_garden')]))
    path = FX + '/s904/log_cat904.txt'
    write_log(path, range(1, 501), lambda n: values(n, old_bda, 40000, 'OLD'))
    tmp = FX + '/s904/cat_tmp.txt'
    write_log(tmp, range(1, 2501), lambda n: values(n, new_bda, 33000, 'NEW'))
    with open(path, 'ab') as fo, open(tmp, 'rb') as fi:
        fo.write(fi.read())
    os.remove(tmp)
    # s906: an identical-launch series (one build, one tag family): two OLD, two NEW
    for i, (bda, dt, cls) in enumerate(((old_bda, 40000, 'OLD'), (new_bda, 33000, 'NEW'),
                                        (old_bda, 41000, 'OLD'), (new_bda, 34000, 'NEW')), 1):
        tag = 'ser906_%d' % i
        write_log(FX + '/s906/log_%s.txt' % tag, range(1, 1201), lambda n, b=bda, t=dt, c=cls: values(n, b, t, c))
        write_json(FX + '/s906/%s.json' % tag, run_json(tag, 'e' * 64, '2026-01-06T0%d:00:00' % i))
    # s907: runs of build a that must stay out of the comparisons: BDA-instrumented (KYTY_BDA_ALL=1),
    # a Vulkan-validation run, and a failed first attempt (_a1)
    write_log(FX + '/s907/log_ins907.txt', N, lambda n: values(n, old_bda, 90000, 'OLD'))
    write_json(FX + '/s907/ins907.json', run_json('ins907', A, '2026-01-07T01:00:00', env={'KYTY_BDA_ALL': '1'}))
    write_log(FX + '/s907/log_val907.txt', N, lambda n: values(n, old_bda, 91000, 'OLD'))
    write_json(FX + '/s907/val907.json', run_json('val907', A, '2026-01-07T02:00:00',
                                                  extra={'cmdline': ['kyty_emulator.exe', '--vulkan-validation', 'true']}))
    write_log(FX + '/s907/log_fa907_a1.txt', N, lambda n: values(n, new_bda, 90000, 'NEW'))
    write_json(FX + '/s907/fa907.json', run_json(
        'fa907', A, '2026-01-07T03:00:00',
        attempts=[dict(label='attempt 1', attempt=1, stable_frame=None, outcome='GpuHangAbort'),
                  dict(label='attempt 2', attempt=2, stable_frame=282, outcome='ok', level='underwater_aerial_garden')]))
    # an _a1 log whose json kept only the (ok) attempt the plain log belongs to; a hung-speed run
    write_log(FX + '/s907/log_amb907.txt', N, lambda n: values(n, new_bda, 33500, 'NEW'))
    write_log(FX + '/s907/log_amb907_a1.txt', N, lambda n: values(n, new_bda, 33600, 'NEW'))
    write_json(FX + '/s907/amb907.json', run_json('amb907', 'f' * 64, '2026-01-07T04:00:00'))
    write_log(FX + '/s907/log_slow907.txt', N, lambda n: values(n, new_bda, 120000, 'NEW'))
    write_json(FX + '/s907/slow907.json', run_json('slow907', A, '2026-01-07T05:00:00'))
    # s905: old launch_run format: json with sha256, phases file, no FrameTrace-x lines
    write_log(FX + '/s905/log_oldfmt905.txt', N, lambda n: values(n, old_bda, 40000, 'OLD'), with_x=False,
              level=None)
    write_json(FX + '/s905/oldfmt905.json', {'pid': 1, 'sha256': D, 'env': {'KYTY_FRAME_TRACE': 'lite',
                                                                             'KYTY_KEYS': '@2170:j,@2460:j'}})
    write_json(FX + '/s905/gates_oldfmt905.json', [{'name': 'base_a', 'gates': 'drawahead=0', 'first': 2500, 'last': 2600},
                                                   {'name': 'da_a', 'gates': 'drawahead=1', 'first': 2700, 'last': 2800}])


def by_tag(recs, session, tag):
    for r in recs:
        if r['session'] == session and r['tag'] == tag:
            return r
    raise KeyError((session, tag))


def main():
    make_fixtures()
    # unit checks
    check('classify 1066', C.classify(1066), 'OLD')
    check('classify 52', C.classify(52), 'NEW')
    check('classify 300', C.classify(300), 'MID')
    check('wclass 0 is IDLE', C.wclass(0), 'IDLE')
    att = [dict(label='warmup', attempt=0, stable_frame=None, outcome='GpuHangAbort'),
           dict(label='attempt 1', attempt=1, stable_frame=None, outcome='GpuHangAbort'),
           dict(label='attempt 2', attempt=2, stable_frame=276, outcome='ok')]
    check('pick_attempt plain -> last ok', C.pick_attempt(att, None)['attempt'], 2)
    check('pick_attempt a1', C.pick_attempt(att, 'a1')['attempt'], 1)
    check('pick_attempt warmup', C.pick_attempt(att, 'warmup')['label'], 'warmup')
    check('gate_highlights', C.gate_highlights('copy=1 bdastamp=1 bdaall=0 fslean=0', '90+1800:bdaall=1|bdaall=0'),
          ('bdaall=0 bdastamp=1 fslean=0', 'bdaall'))
    sep = C.separation([20, 21], [2, 3, 2])
    check('separation clean', (sep['clean'], sep['errors'], sep['auc']), (True, 0, 1.0))
    sep = C.separation([3, 3], [3, 3])
    check('separation tie not clean', (sep['clean'], sep['auc']), (False, 0.5))

    # scan the fixtures
    cache = FX + '/cache'
    done = C.scan(pattern=FX + '/s*/log_*.txt', jpattern=FX + '/s*/*.json', cache_dir=cache, budget_s=600,
                  lock=None, verbose=False)
    check('scan finished', done, True)
    recs = C.load_records(cache)
    check('records', len(recs), 23)

    r = by_tag(recs, 901, 'old901')
    res = r['res']
    check('old901 status', r['status'], 'ok')
    check('old901 regime', res['regime'], 'OLD')
    check('old901 bda steady median', res['bda_steady_median'], 1066)
    check('old901 stable json 282', (res['stable_frame'], res['stable_src']), (282, 'json'))
    check('old901 steady rows', res['steady_rows'], 3000 - 282)
    check('old901 est_n', res['est_n'], 241)
    check('old901 settled_n', res['settled_n'], 241)
    check('old901 switched', res['switched'], False)
    check('old901 post_est_changes', res['post_est_changes'], 0)
    check('old901 steady dt', res['med']['steady']['dt_us'], 40000)
    check('old901 start dt', res['med']['start']['dt_us'], 60000)
    check('old901 first600 dt', res['med']['first600']['dt_us'], 40000)
    check('old901 start buf_new', res['med']['start']['buf_new'], 20)
    check('old901 steady buf_new', res['med']['steady']['buf_new'], 3)
    check('old901 steady buflru_n', res['med']['steady']['buflru_n'], 60000)
    check('old901 start buflru_n', res['med']['start']['buflru_n'], 50000)
    check('old901 buflru fields', res['buflru_fields'], ['buflru_n', 'buflru_rep'])
    check('old901 start bda median', res['bda_start_median'], 0)
    check('old901 drs ratio', res['drs_ratio_median'], 2016.0)
    check('old901 dt mean', res['dt_mean_steady'], 40000.0)
    check('old901 arm_dependent', res['arm_dependent'], False)
    check('old901 level marker', r['markers']['levels'], [['underwater_aerial_garden', 100]])
    check('old901 pin marker', r['markers']['pin'], '1')
    check('old901 decoy line ignored (rows)', res['rows'], 3000)
    check('old901 k steady', (res['k']['steady']['hi'], res['k']['steady']['k1'], res['k']['steady']['k0']), (1.0, 1.0, 0.0))
    check('old901 k start hi (60 of 300)', res['k']['start']['hi'], 0.2)
    check('old901 k1_med / k0_med', (res['k1_med'], res['k0_med']), (1066, None))
    check('old901 episodes', (res['episodes'], res['persist_switches'], res['transient_windows']), ('OLD@283', 0, 0))
    check('old901 json timings', (r['meta']['document_s'], r['meta']['level_started_s'], r['meta']['stable_s']),
          (10.0, 12.0, 15.0))
    check('old901 no episode diff (one class)', res['ep_dt_old_minus_new'], None)
    check('old901 load burst (first in-scene window n=181..240 has bda 0)',
          (res['load_burst'], res['load_burst_n'], res['first_k0_scene_n']), ('IDLE', 181, None))

    res = by_tag(recs, 901, 'new901')['res']
    check('new901 regime', res['regime'], 'NEW')
    check('new901 bda steady median', res['bda_steady_median'], 52)
    check('new901 est_n', res['est_n'], 121)
    check('new901 settled_n (IDLE windows skipped)', res['settled_n'], 121)
    check('new901 steady dt', res['med']['steady']['dt_us'], 33000)
    check('new901 start buf_new', res['med']['start']['buf_new'], 2)
    check('new901 k steady hi / k0', (res['k']['steady']['hi'], res['k']['steady']['k0']), (0.0, 1.0))
    check('new901 k0_med', res['k0_med'], 52)
    check('new901 episodes', (res['episodes'], res['persist_switches']), ('NEW@283', 0))
    check('new901 load burst', (res['load_burst'], res['load_burst_n'], res['first_k0_scene_n']), ('NEW', 181, 181))

    check('nob902 status', by_tag(recs, 902, 'nob902')['status'], 'no_bda_scan')

    res = by_tag(recs, 902, 'sw902')['res']
    check('sw902 regime by median', res['regime'], 'OLD')
    check('sw902 bda steady median', res['bda_steady_median'], 1064)
    check('sw902 switched', res['switched'], True)
    check('sw902 switch_n', res['switch_n'], 1483)
    check('sw902 steady windows', res['steady_w300'], 'NEW*4,OLD*5')
    check('sw902 est_n', res['est_n'], 1501)
    check('sw902 regime_clean', C.regime_clean(res), 'SWITCH')
    check('sw902 hi steady', round(res['k']['steady']['hi'], 6), round(1500 / 2718.0, 6))
    check('sw902 episodes', (res['episodes'], res['persist_switches']), ('NEW@283,OLD@1483', 1))
    check('sw902 link buf_new', (res['link']['buf_new']['p_pos'], res['link']['buf_new']['p_zero']), (1.0, 0.0))
    check('sw902 link buf_new pos_frac', round(res['link']['buf_new']['pos_frac'], 6), round(1500 / 2718.0, 6))
    check('sw902 link buf_new lag1 p_pos', res['link']['buf_new_lag1']['p_pos'], 1.0)
    check('sw902 link img_new (always > 0)', (res['link']['img_new']['p_zero'], res['link']['img_new']['pos_frac']), (None, 1.0))
    check('sw902 episode stats', [(s['cls'], s['n0'], s['n1'], s['rows'], s['dt_mean']) for s in res['episode_stats']],
          [('NEW', 283, 1482, 1200, 36000.0), ('OLD', 1483, 2982, 1500, 37000.0)])
    check('sw902 episode dt OLD - NEW', res['ep_dt_old_minus_new'], 1000.0)

    res = by_tag(recs, 902, 'tr902')['res']
    check('tr902 regime', res['regime'], 'NEW')
    check('tr902 spec switch flag (300-windows)', (res['switched'], res['steady_w300']), (True, 'NEW*2,OLD*1,NEW*6'))
    check('tr902 transient kept NEW', (C.regime_clean(res), res['transient_windows']), ('NEW', 1))
    check('tr902 no persistent episode', (res['episodes'], res['persist_switches']), ('NEW@283', 0))
    check('tr902 hi steady', round(res['k']['steady']['hi'], 6), round(180 / 2718.0, 6))

    r = by_tag(recs, 903, 'few903')
    res = r['res']
    check('few903 regime', res['regime'], 'TOO_FEW')
    check('few903 stable default', (res['stable_frame'], res['stable_src']), (2100, 'default'))
    check('few903 start dt', res['med']['start']['dt_us'], 60000)
    check('few903 start bda', res['bda_start_median'], 0)
    check('few903 est_n none', res['est_n'], None)

    r = by_tag(recs, 903, 'old901')
    check('duplicate detected', (r['status'], r['duplicate_of'].endswith('/s901/log_old901.txt')), ('duplicate', True))

    r = by_tag(recs, 904, 'abba904_warmup')
    check('warmup attempt label', r['meta']['attempt_label'], 'warmup')
    check('warmup stable 290', r['res']['stable_frame'], 290)
    check('warmup sha from parent json', r['meta']['sha'], 'c' * 64)
    check('warmup regime', r['res']['regime'], 'NEW')

    r = by_tag(recs, 904, 'abba904')
    res = r['res']
    check('abba904 attempt label', r['meta']['attempt_label'], 'attempt 1')
    check('abba904 gatearm first frame', r['markers']['gatearm_first_frame'], 1800)
    check('abba904 gatearm count', r['markers']['gatearm_n'], 14)
    check('abba904 arm_dependent', res['arm_dependent'], True)
    check('abba904 arm classes', {k: C.classify(v) for k, v in res['arm_bda'].items()}, {'0': 'NEW', '1': 'OLD'})
    check('abba904 arm dt', res['arm_dt'], {'0': 33000, '1': 36000})
    check('abba904 regime (all rows)', res['regime'], 'NEW')
    check('abba904 regime_clean', C.regime_clean(res), 'ARMDEP')
    check('abba904 gate bda changes captured', len(r['markers']['gate_bda']), 14)

    r = by_tag(recs, 904, 'cat904')
    check('cat904 segments', r['segments'], [500, 2500])
    check('cat904 rows (last segment)', r['res']['rows'], 2500)
    check('cat904 regime', r['res']['regime'], 'NEW')
    check('cat904 steady rows', r['res']['steady_rows'], 400)

    r = by_tag(recs, 905, 'oldfmt905')
    res = r['res']
    check('oldfmt905 sha', r['meta']['sha'], 'd' * 64)
    check('oldfmt905 stable from phases', (res['stable_frame'], res['stable_src']), (2499, 'phases'))
    check('oldfmt905 steady rows', res['steady_rows'], 501)
    check('oldfmt905 regime', res['regime'], 'OLD')
    check('oldfmt905 no x fields', (res['med']['steady']['up_series'], res['buflru_fields']), (None, []))

    # report
    rows, wb, sep_rows = C.build_report(recs, FX + '/census.csv', FX + '/census_summary.md', FX + '/separation.csv')
    check('csv rows', len(rows), 21)
    check('csv INSTR (KYTY_BDA_ALL=1)', (cr_ := {(r['session'], r['tag']): r for r in rows})[(907, 'ins907')]['regime_clean'], 'INSTR')
    check('csv validation excluded', (cr_[(907, 'val907')]['regime_clean'], cr_[(907, 'val907')]['excl']), ('OLD', 'validation'))
    check('csv failed attempt excluded', (cr_[(907, 'fa907_a1')]['excl'], cr_[(907, 'fa907_a1')]['stable_src'],
                                          cr_[(907, 'fa907_a1')]['attempt']), ('failed-attempt', 'default', 'attempt 1'))
    check('bda_instrumented rules', (C.bda_instrumented({}, '90+1800:bdaevery=1|bdaevery=0', ''),
                                     C.bda_instrumented({}, None, 'bdastamp=0'), C.bda_instrumented({}, None, 'bdastamp=1 bdaall=0'),
                                     C.bda_instrumented({'KYTY_BDA_REGION_STAMPS': '0'}, None, '')), (True, True, False, True))
    cr = {(r['session'], r['tag']): r for r in rows}
    check('csv scene intro_keys (old format)', cr[(905, 'oldfmt905')]['scene'], 'intro_keys')
    check('csv scene from json', cr[(901, 'old901')]['scene'], 'underwater_aerial_garden')
    check('csv schedule names', (cr[(904, 'abba904')]['schedule'], cr[(904, 'abba904')]['sched_names']), ('yes', 'bdaall'))
    check('csv gates_bda', cr[(901, 'old901')]['gates_bda'], 'bdastamp=1 fslean=0')
    check('csv build order', [cr[(901, t)]['build_order'] for t in ('old901', 'new901', 'old901b', 'new901b')], [1, 2, 3, 4])
    check('csv warmup ordered first', (cr[(904, 'abba904_warmup')]['build_order'], cr[(904, 'abba904')]['build_order']), (1, 2))
    check('within-build builds', [b['sha'] for b in wb], ['a' * 12, 'e' * 12])
    check('csv arm0 class', (cr[(904, 'abba904')]['arm0_class'], cr[(901, 'old901')]['arm0_class']), ('NEW', ''))
    check('csv family', (cr[(906, 'ser906_3')]['family'], cr[(904, 'abba904_warmup')]['family']), ('ser906', 'abba904'))
    sg = C.series_groups(rows)
    check('series groups', [(g['family'], g['n_old'], g['n_new']) for g in sg], [('ser906', 2, 2)])
    check('series dt diff', sg[0]['comp']['dt_mean_steady']['diff'], 7000.0)
    check('series Welch SE', round(sg[0]['comp']['dt_mean_steady']['se'], 3), round(math.sqrt(500000.0), 3))
    iv = C.pooled_ivw(sg)
    check('series inverse-variance pool', (iv['mean'], round(iv['se'], 3), iv['series']), (7000.0, round(math.sqrt(500000.0), 3), 1))
    check('series build order means', (sg[0]['comp']['build_order']['old_mean'], sg[0]['comp']['build_order']['new_mean']),
          (2.0, 3.0))
    b = wb[0]
    check('within-build n', (b['n_old'], b['n_new']), (2, 2))
    check('within-build dt_mean diff', b['comp']['dt_mean_steady']['diff'], 7000.0)
    check('within-build steady dt diff', b['comp']['steady_dt_us']['diff'], 7000.0)
    check('within-build steady dt n', (b['comp']['steady_dt_us']['n_old'], b['comp']['steady_dt_us']['n_new']), (2, 2))
    S = {(s, n, p): v for s, n, p, v, _, _ in sep_rows}
    check('separation start buf_new clean', S[('all scenes', 'buf_new', 'start')]['clean'], True)
    check('separation steady buf_new not clean', S[('all scenes', 'buf_new', 'steady')]['clean'], False)
    check('separation steady buflru_n clean', S[('all scenes', 'buflru_n', 'steady')]['clean'], True)
    check('separation start buflru_n not clean', S[('all scenes', 'buflru_n', 'start')]['clean'], False)
    check('separation steady buflru_n sides', (S[('all scenes', 'buflru_n', 'steady')]['n_old'],
                                               S[('all scenes', 'buflru_n', 'steady')]['n_new']), (4, 7))
    check('separation hi steady clean', S[('all scenes', 'hi', 'steady')]['clean'], True)
    check('csv hi columns', (cr[(901, 'old901')]['hi_steady'], cr[(901, 'new901')]['hi_steady'],
                             cr[(901, 'old901')]['hi_start']), (1.0, 0.0, 0.2))
    check('csv link columns', (cr[(902, 'sw902')]['p_hi_buf_new_pos'], cr[(902, 'sw902')]['p_hi_buf_new_zero']), (1.0, 0.0))
    ps = C.pooled_slope([r for r in rows if r['sha'] == 'a' * 12], 'dt_mean_steady')
    check('pooled slope build a', (ps['slope'], ps['groups'], ps['runs'], ps['se']), (7000.0, 1, 4, None))
    ps = C.pooled_slope(rows, 'dt_mean_steady')
    check('pooled slope skips ARMDEP/single-run groups', (ps['groups'], ps['runs']), (3, 10))
    check_true('pooled slope jackknife SE with 3 groups', ps['se'] is not None)
    md = open(FX + '/census_summary.md', encoding='utf8').read()
    check_true('summary lists the switched run', 'sw902' in md and 'SWITCH' in md)
    check_true('summary has within-build row for build a', ('| ' + 'a' * 12 + ' | underwater_aerial_garden') in md)
    check_true('separation.csv written', os.path.getsize(FX + '/separation.csv') > 100)
    cats, by = C.counts_table(rows, 'session')
    check('counts s901', (by[901]['OLD'], by[901]['NEW']), (2, 2))
    check('counts s902', (by[902]['SWITCH'], by[902]['NEW']), (1, 1))
    check('counts s903', by[903]['TOO_FEW'], 1)
    # the ABBA fixture toggles bdaall, so it and its warmup are INSTR (INSTR wins over ARMDEP)
    check('counts s904', (by[904]['NEW'], by[904]['ARMDEP'], by[904]['INSTR']), (1, 0, 2))
    check('counts s905', by[905]['OLD'], 1)
    check('counts s906', (by[906]['OLD'], by[906]['NEW']), (2, 2))
    check('counts s907', (by[907]['INSTR'], by[907]['OLD'], by[907]['NEW']), (1, 1, 4))
    check('csv attempt-ambiguous', (cr_[(907, 'amb907_a1')]['excl'], cr_[(907, 'amb907_a1')]['stable_src'],
                                    cr_[(907, 'amb907')]['excl'], cr_[(907, 'amb907')]['stable_src']),
          ('attempt-ambiguous', 'default', '', 'json'))
    check('csv slow excluded', cr_[(907, 'slow907')]['excl'], 'slow')
    check_true('summary has series table row', '| ser906 | ' + 'e' * 12 in md)
    check_true('summary has within-run episode row', '| s902/sw902 |' in md)

    print()
    print('ALL PASS' if not FAILS else 'FAILED: %d -> %s' % (len(FAILS), ', '.join(FAILS)))
    if not FAILS and '--keep' not in sys.argv:
        shutil.rmtree(FX)   # ~37 MB of synthetic logs; regenerate with --keep to inspect them
    return 0 if not FAILS else 1


if __name__ == '__main__':
    sys.exit(main())

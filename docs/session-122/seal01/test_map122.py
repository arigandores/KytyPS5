"""Session 122: fixtures for map122.py - synthetic FrameTrace / -draw / -x / GateArm / Gate / Burn logs (LF, built in
memory), one fixture per admission check, per slope zone at its threshold AND one integer past it, per window edge,
per estimator term, per counter group of the knob (the block codes 1/4/7/8 and the spread codes 2/3, the code-7
coverage split, the dead code-4 site), per scene-classification term (GPU-bound and "pinched" at their thresholds)
and per not-evaluable reason (the 24-pair floor at 23/24/25, the BDA regime, a single pair).  Sizes, thresholds and
the 2SE arithmetic come from this suite, never from the scorer.
    python test_map122.py <map122.py> [--real]
--real also scores the UNSEALED six-arm burn smoke C:/kyty/s122/log_bsky122.txt and the session-121 log
C:/kyty/s121/log_shp121.txt (no burn counters at all): both must end in a clean NOT_ADMITTED with named reasons,
never a crash.
"""
import hashlib
import importlib.util
import json
import re
import shutil
import statistics
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, ValueError):
    pass
SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s122/fx_map122')
NL = chr(10)
spec = importlib.util.spec_from_file_location('map122', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if BASE.exists():
    shutil.rmtree(BASE)
BASE.mkdir(parents=True)

TAG = 'sky122'
BUILD = '2baf8742676255fefd37c72f727e6c27c024be9b67d3afa987bed7fe334af86b'
PERIOD = 90
START = 1800
KEEP = (10, 89)
WIN = KEEP[1] - KEEP[0]          # 79 window frames a block
SMALL = 4                        # pairs in the small fixtures
BLOCKS = 2 * SMALL
ABBA = (0, 1, 1, 0)
DOSE = 2000
PRED_STANDIN = BASE / 'pred' / '01_map122.md'
PRED_STANDIN.parent.mkdir(parents=True)
PRED_STANDIN.write_bytes(b'stand-in pre-registration for the fixtures' + NL.encode())
PSHA = hashlib.sha256(PRED_STANDIN.read_bytes()).hexdigest()
PBYTES = len(PRED_STANDIN.read_bytes())
PRED_FWD = str(PRED_STANDIN).replace('\\', '/')
PRED_BACK = PRED_FWD.replace('/', '\\')
GATES_REAL = 'C:/kyty/s122/gates_base.txt'
GATES_TEXT = ' '.join(Path(GATES_REAL).read_text(encoding='utf-8').split())
LEVEL = 'underwater_aerial_garden'
# the plan the fixtures score against: the real sky122 / skyp122 / skym122 entries plus one tag per counter group
PLAN = {
    'sky122':  dict(level=LEVEL, burn=102000),     # code 1 GuestGpu, block
    'skyp122': dict(level=LEVEL, burn=802000),     # code 8 placebo, block
    'skym122': dict(level=LEVEL, burn=None),       # unsealed arm (the lead's constant)
    'rec122':  dict(level=LEVEL, burn=202000),     # code 2 record thread, spread
    'm1_122':  dict(level=LEVEL, burn=302000),     # code 3 M1 workers, spread, four armings a frame
    'sub122':  dict(level=LEVEL, burn=702000),     # code 7 guest submit, block, coverage burn_s_seen
    'main122': dict(level=LEVEL, burn=402000),     # code 4 main guest thread, block (the site the smoke found dead)
    'bad122':  dict(level=LEVEL, burn=902000),     # a code outside CODE_GROUP
    'des122':  dict(level='intro_next', burn=102000),   # item 18 (c): read by its base arm, not by this name
}
# the scorer's PLAN_DEFAULT as the seal records it (ROADMAP s122 items 2, 13 (b), 17 (d)): written here, never read
# back; skym122 is absent - the code-7 arm left the map (csky122 (unsealed smoke, 2026-09-26): code 7 armed (dose 2 000.3-2 000.5 us a frame) but burn_s_main = 0 in every block)
EXPECTED_PLAN = {
    'sky122':  dict(level='underwater_aerial_garden', burn=102000),
    'skyp122': dict(level='underwater_aerial_garden', burn=802000),
    'atl122':  dict(level='penguin_atlantis', burn=102000),
    'ght122':  dict(level='time_stopper_ghost_world', burn=102000),
    'dnn122':  dict(level='rotating_level_day_and_night', burn=102000),
    'des122':  dict(level='intro_next', burn=102000),
    'mgg122':  dict(level='mini_giants_garden', burn=102000),
    'hub122':  dict(level='hub_crashsite', burn=102000),
    'hov122':  dict(level='hoover_beach', burn=102000),
    'ice122':  dict(level='ice_iceberg', burn=102000),
}
LAUNCHED = '2026-09-26T22:00:00'
FINISHED = '2026-09-26T22:06:01'


def hostdev_text(tag, verdict='RUN_CLEAN - no host device event, no stall', launched=LAUNCHED, finished=FINISHED):
    """The report hostdev122.py <tag> --pad 0 prints (its format_report), with this verdict line."""
    return NL.join(['hostdev122 %s' % tag, 'window %s .. %s (padded)' % (launched, finished),
                    'events 0 (fatal 0, warn 0)', 'VERDICT: %s' % verdict]) + NL
THREAD = {1: 'GuestGpu', 2: 'Record', 3: 'M1', 4: 'Main', 7: 'Submit', 8: 'Placebo'}
PREFIX = {1: 'g', 2: 'r', 3: 'm', 4: 't', 7: 't', 8: 'p'}
WORKERS = {3: 4}                 # code 3 spreads the dose over the four M1 workers (RC7)
SELFTEST = ('Burn: selftest target_us=1000 tsc_us=1000.1 qpc_us=1000.1 spin_us=1000.0 cycles_per_ns=2.495240 '
            'rdtsc_gap_ns=8.0')
PIN = 'GpuClockPin: mode 1 - the guest GPU clock ignores the pacer speed (KYTY_GPU_CLOCK_PIN)'
BURN_SEEN = dict(burn_g_seen=1, burn_r_seen=1, burn_m_seen=4, burn_m0_seen=1, burn_t_seen=1, burn_s_seen=1,
                 burn_s_main=0, burn_p_seen=1, burn_late=0, burn_cpu_bad=0)
BURN_ZERO = dict({'burn_%s_%s' % (p, s): 0 for p in 'grmtp' for s in ('ns', 'n', 'cpu_ns', 'cpu_w')},
                 burn_r_q=0, burn_m_q=0, **BURN_SEEN)
MAIN_A = dict(dt_us=33300, cpu_gpu_us=31000, gpu_busy_us=15000, cpu_main_us=9500, draws=4600, dispatches=260,
              submits=30)
DELTA = 2000                     # the armed arm is one full dose slower => slope 1.0
X_BASE = dict(rec_spin_us=25000)
ENV_BASE = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8',
            'KYTY_GATE_FILE': 'C:\\kyty\\s122\\gates.req', 'KYTY_SAMPLE_GATE': 'C:\\kyty\\s122\\sample.req',
            'KYTY_QUEUE_TRACE': '1', 'KYTY_GUEST_ARGS': '-lvl ' + LEVEL,
            'KYTY_GATE_SCHEDULE': '90+1800:burn=0|burn=102000', 'KYTY_GATE_SCHEDULE_ABBA': '1',
            'KYTY_GPU_CLOCK_PIN': '1', 'KYTY_GPU_MARKERS': '0'}
RESULTS = []


def arm_of(block, order=ABBA):
    return order[block % 4]


def burnt(code, dose=DOSE, cpu_wall=0.968):
    """The -x burn fields of one ARMED frame of that code: ns a frame = dose, n = the armings a frame."""
    p = PREFIX[code]
    out = dict(BURN_ZERO)
    ns = int(dose * 1000)
    out['burn_%s_ns' % p] = ns
    out['burn_%s_n' % p] = WORKERS.get(code, 1)
    out['burn_%s_cpu_ns' % p] = int(ns * cpu_wall)
    out['burn_%s_cpu_w' % p] = ns
    if code == 7:
        out['burn_s_main'] = 1
    return out


def two_se_of(delta, spread):
    """The 2SE this suite builds: the four pairs carry delta -+ spread alternately."""
    diffs = [delta - spread, delta + spread, delta - spread, delta + spread]
    return 2.0 * statistics.stdev(diffs) / 2.0


def make(name, blocks=BLOCKS, main=None, x=None, draw=None, env=None, pins=(PIN,), meta=None, gate_arm=None,
         gate_lines=None, drop=(), dup=(), extra_log=(), stdout_lines=(), pre=5, order=ABBA, strip=(), after=None,
         gates_copy=None, tag=TAG, code=1, dose=DOSE, burn_lines=None, last=None, level=LEVEL, hostdev='clean'):
    """A fixture directory.  main/x/draw: callables (n, block, arm, pos) -> overrides for that frame (pre-schedule
    rows get block -1, arm 0, pos -1); burn_lines: the Burn* lines (None = the selftest plus one arm line of `code`);
    after: callable n -> lines right after frame n's lines; last: the last frame written; hostdev: 'clean' = a clean
    witness report of this run, None = no report, a str = that report text."""
    root = BASE / name
    root.mkdir(parents=True)
    texts = ('burn=0', 'burn=%d' % (code * 100000 + dose))
    values = tuple(dict(p.split('=') for p in t.split()) for t in texts)
    lines = list(pins)
    if burn_lines is None:
        lines.append(SELFTEST)
        lines.append('Burn: arm code=%d thread=%s dose_us=%d q_ns=0' % (code, THREAD.get(code, '?'), dose))
    else:
        lines.extend(burn_lines)
    prev = None
    end = START + PERIOD * blocks if last is None else last
    for n in range(START - pre + 1, end + 1):
        if n > START and (n - START - 1) % PERIOD == 0:
            b = (n - START - 1) // PERIOD
            arm = arm_of(b, order)
            if gate_arm is not None:
                lines.extend(gate_arm(b, arm))
            else:
                lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                             % (arm, b, START + PERIOD * b, texts[arm]))
            if gate_lines is not None:
                lines.extend(gate_lines(b, arm))
            else:
                for k, v in values[arm].items():
                    if (prev is None and v != '0') or (prev is not None and values[prev][k] != v):
                        lines.append('Gate: %s=%s frame=%d' % (k, v, START + PERIOD * b))
            prev = arm
        if n <= START:
            b, pos, arm = -1, -1, 0
        else:
            b, pos = (n - START - 1) // PERIOD, (n - START - 1) % PERIOD
            arm = arm_of(b, order)
        mv = dict(MAIN_A, arm=arm if n > START else 0, blk=b if n > START else 0)
        if arm == 1 and n > START:
            mv['dt_us'] = MAIN_A['dt_us'] + DELTA
        armed = arm == 1 and n > START and code in PREFIX
        xv = dict(X_BASE, **(burnt(code, dose) if armed else BURN_ZERO))
        dv = dict(bda_scan=55)
        if main:
            mv.update(main(n, b, arm, pos))
        if x:
            xv.update(x(n, b, arm, pos))
        if draw:
            dv.update(draw(n, b, arm, pos))
        for kind, sn, field in strip:
            if sn == n:
                {'main': mv, 'draw': dv, 'x': xv}[kind].pop(field, None)
        if ('main', n) not in drop:
            lines.append('FrameTrace: n=%d ' % n + ' '.join('%s=%d' % kv for kv in mv.items()))
        if ('draw', n) not in drop:
            lines.append('FrameTrace-draw: n=%d ' % n + ' '.join('%s=%d' % kv for kv in dv.items()))
        if ('x', n) not in drop:
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xv.items()))
        if n in dup:
            lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in xv.items()))
        if after:
            lines.extend(after(n))
    lines.extend(extra_log)
    (root / ('log_%s.txt' % tag)).write_bytes((NL.join(lines) + NL).encode('utf-8'))
    (root / ('stdout_%s.txt' % tag)).write_bytes((NL.join(stdout_lines) + NL).encode('utf-8'))
    sched = '%d+%d:%s|%s' % (PERIOD, START, texts[0], texts[1])
    env_ok = dict(ENV_BASE, KYTY_GATE_SCHEDULE=sched, KYTY_GUEST_ARGS='-lvl ' + level,
                  VK_SDK_PATH='C:\\VulkanSDK\\1.4.357.0')
    m = dict(tag=tag, binary_sha256=BUILD, env=dict(env_ok if env is None else env), schedule=sched, hold_s=300,
             gates=GATES_TEXT, attempts=[dict(label='attempt 1', outcome='ok', hold_exit=None, stable_frame=439)],
             prereg=dict(path=PRED_BACK, sha256=PSHA, bytes=PBYTES), pre_run=dict(gpu_util_median=2),
             launched=LAUNCHED, finished=FINISHED, started=FINISHED)
    if meta:
        m.update(meta)
    (root / ('%s.json' % tag)).write_text(json.dumps(m), encoding='utf-8')
    if hostdev is not None:
        (root / ('hostdev_%s.txt' % tag)).write_bytes((hostdev_text(tag) if hostdev == 'clean'
                                                       else hostdev).encode('utf-8'))
    if gates_copy is not None:
        (root / 'gates_base.txt').write_bytes(gates_copy if isinstance(gates_copy, bytes)
                                              else gates_copy.encode('utf-8'))
    return root


def get(res, path):
    for part in path.split('.'):
        res = res[int(part)] if isinstance(res, list) else res[part]
    return res


def run(name, root, installed=BUILD, min_pairs=SMALL, pred=(PSHA, PBYTES), pred_path=PRED_FWD, draft=False,
        gates_file=None, tag=TAG, plan=None, hostdev_py=None, **expect):
    """min_pairs / plan = 'default' hand the scorer's own MIN_PAIRS / PLAN_DEFAULT (so a mutant of those constants is
    observable); anything else is this suite's value."""
    gf = str(root / 'gates_base.txt') if gates_file == 'copy' else (gates_file or GATES_REAL)
    res = mod.evaluate(str(root), tag, draft=draft, installed_sha=installed,
                       min_pairs=None if min_pairs == 'default' else min_pairs, pred_sha=pred[0],
                       pred_bytes=pred[1], pred_path=pred_path, gates_file=gf,
                       plan=None if plan == 'default' else (PLAN if plan is None else plan), hostdev_py=hostdev_py)
    bad = []
    try:
        json.dumps(res, allow_nan=False)
    except ValueError as exc:
        bad.append('json: %s' % exc)
    text = NL.join(mod.format_report(res))
    if re.search(r'(?i)\bnan\b|\binf\b', text):
        bad.append('nan/inf in the report')
    for key, want in expect.items():
        if key == 'failed':
            got = sorted(k for k, v in res['checks'].items() if not v)
            want = sorted(want)
        elif key == 'failed_has':
            got = sorted(k for k, v in res['checks'].items() if not v)
            miss = [w for w in want if w not in got]
            if miss:
                bad.append('failed lacks %r in %r' % (miss, got))
            continue
        elif key == 'ne':
            got = res['not_evaluable']
        elif key == 'lines_has':
            for w in want:
                if w not in text:
                    bad.append('report lacks %r' % w)
            continue
        elif key == 'lines_not':
            for w in want:
                if w in text:
                    bad.append('report has %r' % w)
            continue
        elif key in ('last_has', 'last_not'):
            last = text.split(NL)[-1]
            for w in want:
                if (w in last) != (key == 'last_has'):
                    bad.append('last line %r: %s %r' % (last[:70], key, w))
            continue
        else:
            got = get(res, key[2:] if key.startswith('x_') else key.replace('__', '.'))
        if isinstance(want, float) and isinstance(got, (int, float)) and not isinstance(got, bool):
            if abs(got - want) > 1e-6:
                bad.append('%s=%r want %r' % (key, got, want))
        elif got != want:
            bad.append('%s=%r want %r' % (key, got, want))
    RESULTS.append((name, not bad, bad))
    return res


def case(name, expect, **kw):
    runner = {k: kw.pop(k) for k in ('installed', 'min_pairs', 'pred', 'pred_path', 'draft', 'gates_file', 'plan',
                                     'hostdev_py') if k in kw}
    if 'tag' in kw:
        runner['tag'] = kw['tag']
    return run(name, make(name, **kw), **runner, **expect)


def check(name, got, want):
    RESULTS.append((name, got == want, [] if got == want else ['%r want %r' % (got, want)]))


A = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 0 and n > START else {})
B = lambda f: (lambda n, b, arm, i: f(n, b, i) if arm == 1 and n > START else {})
AT = lambda blk, pos, d: (lambda n, b, arm, i: d if (b, i) == (blk, pos) else {})
OK = dict(admission='ADMITTED', failed=[], ne=[])
SA = 16667.0 / 33300.0
SB = 16667.0 / 35300.0

# ------------------------------------------------------------------ the admitted base: every reported term
case('ok', dict(OK, verdict='CRITICAL', zone='CRITICAL', pairs=4, blocks=8, complete_blocks=8,
                dt_us__delta=2000.0, dt_us__two_se=0.0, dt_us__A=33300.0, dt_us__B=35300.0,
                slope__s=1.0, slope__two_se=0.0, slope__lo=1.0, slope__hi=1.0,
                cpu_gpu_us__delta=0.0, gpu_busy_us__delta=0.0, est_frames__A=4 * WIN, est_frames__B=4 * WIN,
                code=1, prefix='g', dose_us=DOSE, dose_kind='block', level=LEVEL, burn_value=102000,
                burn__measure__per_frame_us=2000.0, burn__measure__per_unit_us=2000.0, burn__measure__n=4 * WIN,
                burn__measure__frames=4 * WIN, burn__measure__cpu_wall=0.968, burn__coverage__counter='burn_g_seen',
                burn__coverage__value=4 * WIN, burn__coverage__role=None, burn__late=0, burn__selftest=1,
                burn__cpu_bad=0, burn__reject=0, burn__notsc=0,
                scene__vblank_top=2, scene__vblank_top_share=1.0, scene__pinched=True, scene__gpu_bound=False,
                scene__dt_median=35300, scene__frames=8 * WIN, scene__rec_spin_us=25000.0, scene__draws=4600.0,
                scene__ratios={'gpu_busy/dt': 15000.0 / 33300.0, 'cpu_gpu/dt': 31000.0 / 33300.0,
                               'cpu_main/dt': 9500.0 / 33300.0},
                bda_scan__A=55.0, bda_scan__B=55.0, bda_scan__A_regime='NEW', bda_scan__B_regime='NEW',
                speed__A=SA, speed__B=SB, x_tag=TAG, x_draft=False, build_sha256=BUILD,
                lines_has=['Delta dt_us (B - A) 2000.0 +- 0.0 us (2SE, 4 pairs); A 33300.0 B 35300.0 us',
                           'SLOPE s = Delta / dose 1.000 +- 0.000 (interval 1.000 .. 1.000); zones: superlinear '
                           's-2SE>1.0, critical s-2SE>0.5 and s+2SE>=1.0, not critical s+2SE<0.3',
                           'dose measured: 2000.0 us a frame (want 2000 +-5 %), 2000.0 us an armed unit over 316 '
                           'armings on 316 B frames; cpu/wall 0.968 (block codes ~1.00 by construction - printed '
                           'diagnostics, not a verdict)',
                           'coverage burn_g_seen = 316', 'bda_scan A 55.0 (NEW) B 55.0 (NEW)',
                           "burn lines: selftest 1, arm [(1, 'GuestGpu', 2000, 0)], late 0, rejected 0, no-TSC 0, "
                           'burn_cpu_bad 0 (must be 0)',
                           'top 2x = 100.0 % => PINCHED', 'GPU-bound: no', 'not evaluable: -', 'ADMISSION: ADMITTED',
                           'VERDICT: CRITICAL slope=1.000 2se=0.000 interval=1.000..1.000 pairs=4 bda=NEW '
                           'reading=SPEED',
                           'game speed (16 667 / mean dt_us) A 0.5005 B 0.4722 (-5.67 % speed change under the dose)',
                           'DRAW-ADJUSTED (report only): Delta 2000.0 +- 0.0 us, slope 1.000 +- 0.000, zone CRITICAL; '
                           'Delta draws (B - A) 0.0 +- 0.0',
                           'outlier pairs dropped 0 (limit 2; more => the run is INVALID)',
                           'host events (hostdev_sky122.txt): RUN_CLEAN',
                           'skipped draws: 0 fatal (frame >= 1811), 0 before the population (largest frame None)',
                           '  blocks 8 complete 8 pairs 4 (floor 4); estimator frames A 316 B 316',
                           '  scene underwater_aerial_garden; arm B burn=102000 (code 1 g, dose 2000 us), arm A '
                           'burn=0', 'map122 tag sky122  scorer '],
                reading='SPEED', dropped_pairs=0, outliers=[], host='RUN_CLEAN', first_population_frame=1811,
                draw_adjusted__zone='CRITICAL', draw_adjusted__differs=False, draw_adjusted__est__delta=2000.0,
                draw_adjusted__est__draws_delta=0.0,
                lines_not=['REPORT OF A NOT_ADMITTED RUN', 'DRAFT', 'OUTLIER', 'NOT QUOTED', 'ZONE DIFFERS'],
                last_has=['CONSEQUENCE: CRITICAL - "критичен', '1:1'], last_not=['HEADROOM', 'BDA OLD']))

# ------------------------------------------------------------------ the four slope zones, each threshold straddled
SPREAD = 100                                    # => 2SE = 115.4701 us = 0.05774 of a dose
check('two_se_math', round(two_se_of(2000, SPREAD), 4), 115.4701)


def slope_case(name, delta, verdict, spread=SPREAD, **extra):
    """The four pairs carry delta -+ spread: the B block of each pair is shifted by +-spread."""
    offs = {1: -spread, 2: spread, 5: -spread, 6: spread}
    se = two_se_of(delta, spread)
    case(name, dict(OK, verdict=verdict, zone=verdict, dt_us__delta=float(delta), dt_us__two_se=se,
                    slope__s=delta / float(DOSE), slope__lo=(delta - se) / DOSE, slope__hi=(delta + se) / DOSE,
                    **extra),
         main=B(lambda n, b, i: {'dt_us': MAIN_A['dt_us'] + delta + offs.get(b, 0)}))


# "the interval reaches 1" crosses at delta = 1884.53 (2SE 115.47): 1885 is CRITICAL, 1884 is not
slope_case('zone_critical_reach_1', 1885, 'CRITICAL')
slope_case('zone_reach_1_one_short', 1884, 'NOT_RESOLVED')
check('reach_1_edge', ((1885 + two_se_of(1885, SPREAD)) / DOSE >= 1.0,
                       (1884 + two_se_of(1884, SPREAD)) / DOSE >= 1.0), (True, False))
# "s - 2SE > 0.5" with the interval still reaching 1 (both conditions of CRITICAL bind only for a wide interval):
# delta 1600 with 2SE 461.88 passes both; the same delta with 2SE 600.44 keeps hi >= 1 but drops lo to 0.4998
slope_case('zone_critical_lo_over_half', 1600, 'CRITICAL', spread=400)
slope_case('zone_lo_at_half_hi_still_1', 1600, 'NOT_RESOLVED', spread=520)
check('half_edge', ((1600 - two_se_of(1600, 400)) / DOSE > 0.5, (1600 + two_se_of(1600, 400)) / DOSE >= 1.0,
                    (1600 - two_se_of(1600, 520)) / DOSE > 0.5, (1600 + two_se_of(1600, 520)) / DOSE >= 1.0),
      (True, True, False, True))
# s - 2SE crosses 1 at delta = 2115.47: 2116 is SUPERLINEAR, 2115 is only CRITICAL
slope_case('zone_superlinear', 2116, 'SUPERLINEAR')
slope_case('zone_superlinear_one_short', 2115, 'CRITICAL')
check('super_edge', ((2116 - two_se_of(2116, SPREAD)) / DOSE > 1.0,
                     (2115 - two_se_of(2115, SPREAD)) / DOSE > 1.0), (True, False))
# s + 2SE crosses 0.3 at delta = 484.53: 484 is NOT_CRITICAL, 485 is not
slope_case('zone_not_critical', 484, 'NOT_CRITICAL')
slope_case('zone_not_critical_one_over', 485, 'NOT_RESOLVED')
check('flat_edge', ((484 + two_se_of(484, SPREAD)) / DOSE < 0.3,
                    (485 + two_se_of(485, SPREAD)) / DOSE < 0.3), (True, False))
slope_case('zone_negative_still_flat', -500, 'NOT_CRITICAL')       # a faster armed arm is "not critical", not a win

# ------------------------------------------------------------------ GPU-bound and "pinched" at their thresholds
FLAT = 480                                       # slope 0.24 with 2SE 0 => NOT_CRITICAL, the GPU question is open
GB = lambda f: (lambda n, b, arm, i: dict({'gpu_busy_us': int(round(f * (MAIN_A['dt_us'] + (FLAT if arm == 1 else 0))))},
                                          **({'dt_us': MAIN_A['dt_us'] + FLAT} if arm == 1 else {})) if n > START
               else {})
case('gpu_bound_exact_09', dict(OK, verdict='NOT_CRITICAL', scene__gpu_bound=True,
                                lines_has=['GPU-bound: yes (median gpu_busy/dt >= 0.9 and GuestGpu not critical)']),
     main=GB(0.9))
case('gpu_bound_just_under', dict(OK, verdict='NOT_CRITICAL', scene__gpu_bound=False,
                                  lines_has=['GPU-bound: no']),
     main=GB(0.8999))
case('gpu_bound_but_critical', dict(OK, verdict='CRITICAL', scene__gpu_bound=False),
     main=lambda n, b, arm, i: {'gpu_busy_us': 10 ** 5} if n > START else {})
case('gpu_bound_na_other_code', dict(OK, verdict='NOT_CRITICAL', scene__gpu_bound=None, code=8,
                                     burn__coverage__counter='burn_p_seen',
                                     lines_has=['GPU-bound: n/a (not the GuestGpu arm - only code 1 can answer it)']),
     tag='skyp122', code=8, main=GB(0.95))
# pinched: with ten blocks the window rows are 790; two whole blocks on three vblanks are exactly 20 %
case('pinched_exact_80', dict(OK, verdict='NOT_RESOLVED', scene__pinched=True, scene__vblank_top=2,
                             scene__vblank_top_share=0.8, pairs=5,
                             lines_has=['top 2x = 80.0 % => PINCHED (>= 80 %: a saving smaller than the distance to '
                                        'the next step does not move FPS)']),
     blocks=10, main=lambda n, b, arm, i: {'dt_us': 50000} if n > START and b in (0, 1) else {})
case('pinched_just_under', dict(OK, verdict='NOT_RESOLVED', scene__pinched=False, pairs=5,
                               lines_has=['=> not pinched']),
     blocks=10,
     main=lambda n, b, arm, i: {'dt_us': 50000} if n > START and (b in (0, 1) or (b == 2 and i == 10)) else {})

# ------------------------------------------------------------------ the counter groups: spread codes, code 7, code 4
case('spread_code2', dict(OK, verdict='CRITICAL', code=2, prefix='r', dose_kind='spread',
                          burn__measure__per_frame_us=2000.0, burn__measure__per_unit_us=2000.0,
                          burn__coverage__counter='burn_r_seen',
                          lines_has=['cpu/wall 0.968 (spread codes ~1.33 by construction']),
     tag='rec122', code=2)
case('spread_code3_per_worker', dict(OK, verdict='CRITICAL', code=3, prefix='m', dose_kind='spread',
                                     burn__measure__per_frame_us=2000.0, burn__measure__per_unit_us=500.0,
                                     burn__measure__n=4 * 4 * WIN, burn__coverage__counter='burn_m_seen',
                                     burn__coverage__value=4 * 4 * WIN,
                                     lines_has=['2000.0 us a frame (want 2000 +-5 %), 500.0 us an armed unit over '
                                                '1264 armings on 316 B frames']),
     tag='m1_122', code=3)
case('code7_coverage_split', dict(OK, verdict='CRITICAL', code=7, prefix='t',
                                  burn__coverage__counter='burn_s_seen', burn__coverage__value=4 * WIN,
                                  burn__coverage__role='burn_s_main', burn__coverage__role_value=4 * WIN,
                                  lines_has=['coverage burn_s_seen = 316 (role burn_s_main = 316)']),
     tag='sub122', code=7)
case('code4_dead_site', dict(failed=['armed', 'dose', 'coverage'], admission='NOT_ADMITTED',
                             verdict='NOT_ADMITTED', code=4, burn__coverage__counter='burn_t_seen',
                             burn__coverage__value=0),
     tag='main122', code=4, x=B(lambda n, b, i: dict(BURN_ZERO, burn_t_seen=0)))
case('plan_unsealed_arm', dict(failed_has=['plan_sealed', 'armed', 'arm_lines'], admission='NOT_ADMITTED',
                              verdict='NOT_ADMITTED', burn_value=None, code=None,
                              lines_has=['arm B burn=None (code None None, dose None us)']),
     tag='skym122', code=4)
case('plan_code_out_of_range', dict(failed_has=['plan_sealed'], admission='NOT_ADMITTED', code=9), tag='bad122',
     code=9)

# ------------------------------------------------------------------ every entry of the DEFAULT plan of the scorer
# (the fixtures above pass their own plan; these pin the scene, the code and the dose of each real tag)
for _tag, _entry in sorted(mod.PLAN_DEFAULT.items()):
    if _entry['burn'] is None:
        case('default_plan_%s_unsealed' % _tag,
             dict(failed_has=['plan_sealed'], admission='NOT_ADMITTED', burn_value=None, level=_entry['level']),
             tag=_tag, code=4, level=_entry['level'], plan=mod.PLAN_DEFAULT)
    else:
        case('default_plan_%s' % _tag,
             dict(OK, verdict='CRITICAL', burn_value=_entry['burn'], level=_entry['level'],
                  code=_entry['burn'] // 100000, dose_us=_entry['burn'] % 100000),
             tag=_tag, code=_entry['burn'] // 100000, dose=_entry['burn'] % 100000, level=_entry['level'],
             plan=mod.PLAN_DEFAULT)

# ------------------------------------------------------------------ the chain gate: map122.py --plan-check <tag>
_pc = [__import__('subprocess').run([sys.executable, str(SRC), '--plan-check', t], capture_output=True, text=True)
       for t in ('sky122', 'skyp122', 'skym122', 'zzz122')]
check('plan_check_exit_codes', tuple(p.returncode for p in _pc), (0, 0, 2, 2))
check('plan_check_sealed_line', ('arm burn=102000 (code 1, dose 2000 us) sealed' in _pc[0].stdout,
                                 'arm burn=802000 (code 8, dose 2000 us) sealed' in _pc[1].stdout,
                                 'no PLAN entry for tag skym122' in _pc[2].stdout,
                                 'no PLAN entry' in _pc[3].stdout), (True, True, True, True))
check('plan_default_has_no_skym', 'skym122' in mod.PLAN_DEFAULT, False)
check('plan_check_unsealed_value', mod.plan_check('skym122', PLAN)[0], 1)
check('plan_check_unknown_code', mod.plan_check('bad122', PLAN)[0], 1)
check('plan_check_unknown_tag', mod.plan_check('zzz122', PLAN)[0], 2)
check('plan_default_is_the_seal', mod.PLAN_DEFAULT, EXPECTED_PLAN)

# ------------------------------------------------------------------ the pair floor 23 / 24 / 25 (ROADMAP item 8 (c)),
# on the scorer's own MIN_PAIRS
case('pairs_25_ok', dict(OK, verdict='CRITICAL', pairs=25), blocks=50, min_pairs='default')
case('pairs_24_ok', dict(OK, verdict='CRITICAL', pairs=24), blocks=48, min_pairs='default')
case('pairs_23_not_evaluable', dict(admission='ADMITTED', failed=[], ne=['pairs'], verdict='NOT_EVALUABLE', pairs=23,
                                    lines_has=['not evaluable: pairs', 'blocks 46 complete 46 pairs 23 (floor 24)'],
                                    last_has=['NOT_EVALUABLE', 'наклоном не']),
     blocks=46, min_pairs='default')
case('pairs_two_two_se_defined', dict(OK, verdict='CRITICAL', pairs=2, dt_us__two_se=0.0), blocks=4, min_pairs=2)
case('draft_skips_pair_floor', dict(admission='ADMITTED', failed=[], ne=[], verdict='CRITICAL', pairs=4),
     meta=dict(hold_s=200, prereg=None), draft=True, pred=(None, None), min_pairs='default')
case('pairs_one_two_se_undefined', dict(admission='ADMITTED', failed=[], ne=['two_se_undefined'],
                                        verdict='NOT_EVALUABLE', pairs=1, slope__two_se=None, slope__lo=None,
                                        zone=None, dt_us__two_se=None,
                                        lines_has=['VERDICT: NOT_EVALUABLE slope=1.000 2se=- interval=-..-']),
     blocks=2, min_pairs=1)

# ------------------------------------------------------------------ the BDA regime rule
case('bda_regime_differs', dict(admission='ADMITTED', failed=[], ne=['bda_regime'], verdict='NOT_EVALUABLE',
                                bda_scan__A_regime='NEW', bda_scan__B_regime='OLD',
                                lines_has=['bda_scan A 55.0 (NEW) B 1100.0 (OLD)', 'pairs=4 bda=NEW reading=SPEED']),
     draw=B(lambda n, b, i: {'bda_scan': 1100}))
case('bda_regime_mixed_both', dict(admission='ADMITTED', failed=[], ne=['bda_regime'], verdict='NOT_EVALUABLE',
                                   bda_scan__A_regime='MIXED', bda_scan__B_regime='MIXED'),
     draw=lambda n, b, arm, i: {'bda_scan': 450})
case('bda_regime_old_both_ok', dict(OK, verdict='CRITICAL', bda_scan__A_regime='OLD', bda_scan__B_regime='OLD',
                                    lines_has=['pairs=4 bda=OLD reading=SPEED'],
                                    last_has=['BDA OLD: this scene\'s numbers are quoted only with the regime and never '
                                              'compared with those of NEW scenes']),
     draw=lambda n, b, arm, i: {'bda_scan': 1100})
case('bda_new_edge_300', dict(OK, verdict='CRITICAL', bda_scan__A_regime='NEW', bda_scan__B_regime='NEW'),
     draw=lambda n, b, arm, i: {'bda_scan': 300})
case('bda_old_edge_600', dict(OK, verdict='CRITICAL', bda_scan__A_regime='OLD', bda_scan__B_regime='OLD'),
     draw=lambda n, b, arm, i: {'bda_scan': 600})

# ------------------------------------------------------------------ the window edges and the estimator
EDGE = {(0, 9): 400000, (0, 89): 400000, (1, 9): 400000, (1, 89): 400000}   # below OUTLIER_US: no pair is dropped
case('window_outside_ignored', dict(OK, verdict='CRITICAL', dt_us__A=33300.0, dt_us__B=35300.0, dt_us__delta=2000.0),
     main=lambda n, b, arm, i: {'dt_us': EDGE[(b, i)]} if (b, i) in EDGE else {})
case('window_position_10_counts', dict(OK, verdict='CRITICAL', dt_us__delta=2000.0 + 7900.0 / WIN / 4),
     main=AT(1, 10, {'dt_us': MAIN_A['dt_us'] + DELTA + 7900}))
case('window_position_88_counts', dict(OK, verdict='CRITICAL', dt_us__delta=2000.0 + 7900.0 / WIN / 4),
     main=AT(1, 88, {'dt_us': MAIN_A['dt_us'] + DELTA + 7900}))
case('estimator_drops_low_draws', dict(OK, verdict='CRITICAL', est_frames__B=4 * WIN - 10, dt_us__B=35300.0,
                                       dt_us__delta=2000.0, scene__frames=8 * WIN - 10, scene__dt_median=33300),
     main=lambda n, b, arm, i: {'draws': 100, 'dt_us': 400000} if (b == 1 and 20 <= i < 30) else {})
case('estimator_block_means_not_pooled', dict(OK, verdict='CRITICAL', dt_us__delta=2000.0,
                                              est_frames__B=4 * WIN - 10),
     main=lambda n, b, arm, i: {'draws': 100} if (b == 1 and 20 <= i < 30) else {})
S7 = {1: 100, 2: -100, 5: 0, 6: 0}
SD7 = 2.0 * statistics.stdev([2100.0, 1900.0, 2000.0, 2000.0]) / 2.0
case('estimator_arithmetic', dict(OK, verdict='CRITICAL', dt_us__delta=2000.0, dt_us__two_se=SD7,
                                  dt_us__pair_diffs=[2100.0, 1900.0, 2000.0, 2000.0],
                                  slope__s=1.0, slope__two_se=SD7 / DOSE, scene__dt_median=35200),
     main=B(lambda n, b, i: {'dt_us': MAIN_A['dt_us'] + DELTA + S7.get(b, 0)}))
check('estimator_2se_value', round(SD7, 4), 81.6497)

# ------------------------------------------------------------------ one fixture per admission check
case('binary', dict(failed=['binary'], admission='NOT_ADMITTED',
                    lines_has=['ADMISSION: NOT_ADMITTED failed=binary',
                               'REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED']),
     meta=dict(binary_sha256='ff' * 32))
case('installed_now', dict(failed=['installed_now'], admission='NOT_ADMITTED'), installed='ff' * 32)
case('installed_empty', dict(failed=['installed_now'], admission='NOT_ADMITTED'), installed='')
case('pinned_mode2', dict(failed=['pinned'], admission='NOT_ADMITTED'), pins=('GpuClockPin: mode 2',))
case('pinned_twice', dict(failed=['pinned'], admission='NOT_ADMITTED'), pins=(PIN, PIN))
case('env_extra_key_rec', dict(failed=['env_exact'], admission='NOT_ADMITTED'),
     env=dict(ENV_BASE, KYTY_REC='C:\\kyty\\s122\\rec_sky122.mp4'))
case('env_wrong_level', dict(failed=['env_exact'], admission='NOT_ADMITTED'),
     env=dict(ENV_BASE, KYTY_GUEST_ARGS='-lvl penguin_atlantis'))
case('env_missing_abba', dict(failed=['env_exact'], admission='NOT_ADMITTED'),
     env={k: v for k, v in ENV_BASE.items() if k != 'KYTY_GATE_SCHEDULE_ABBA'})
case('env_schedule_field', dict(failed=['env_exact'], admission='NOT_ADMITTED'),
     meta=dict(schedule='90+1800:burn=0|burn=202000'))
case('env_vk', dict(failed=['env_vk'], admission='NOT_ADMITTED', vk_env=['VK_LAYER_PATH', 'VK_SDK_PATH']),
     env=dict(ENV_BASE, VK_SDK_PATH='x', VK_LAYER_PATH='y'))
case('hold', dict(failed=['hold'], admission='NOT_ADMITTED'), meta=dict(hold_s=200))
case('hold_skipped_in_draft', dict(admission='ADMITTED', failed=[], x_draft=True,
                                   lines_has=['DRAFT: unsealed scoring']),
     meta=dict(hold_s=200, prereg=None), draft=True, pred=(None, None))
case('two_attempts', dict(failed=['one_ok_attempt'], admission='NOT_ADMITTED'),
     meta=dict(attempts=[dict(outcome='timeout', hold_exit=None), dict(outcome='ok', hold_exit=None)]))
case('hold_exit_set', dict(failed=['one_ok_attempt'], admission='NOT_ADMITTED'),
     meta=dict(attempts=[dict(outcome='ok', hold_exit=1)]))
case('prereg_path', dict(failed=['prereg'], admission='NOT_ADMITTED'),
     meta=dict(prereg=dict(path='C:\\kyty\\s122\\pred\\99.md', sha256=PSHA, bytes=PBYTES)))
case('prereg_sha_unsealed', dict(failed=['prereg_sha'], admission='NOT_ADMITTED'), pred=(None, None))
case('prereg_sha_mismatch', dict(failed=['prereg_sha'], admission='NOT_ADMITTED'),
     meta=dict(prereg=dict(path=PRED_BACK, sha256='ab' * 32, bytes=PBYTES)))
case('prereg_bytes_mismatch', dict(failed=['prereg_sha'], admission='NOT_ADMITTED'),
     meta=dict(prereg=dict(path=PRED_BACK, sha256=PSHA, bytes=PBYTES + 1)))
case('gates_sha', dict(failed=['gates_exact'], admission='NOT_ADMITTED'),
     gates_file='copy', gates_copy=GATES_TEXT + ' extra=1')
case('gates_text_differs', dict(failed_has=['gates_exact', 'arm_asserts'], admission='NOT_ADMITTED'),
     meta=dict(gates=GATES_TEXT + ' burn=1'))
case('arm_asserts_gate_names', dict(failed_has=['arm_asserts', 'gates_exact'], admission='NOT_ADMITTED'),
     meta=dict(gates=GATES_TEXT.replace('texmemo2=0', 'texmemo2=1')))
case('arm_text_extra_name', dict(failed_has=['arms', 'arm_asserts'], admission='NOT_ADMITTED'),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b, 'burn=0 fslean=1' if arm == 0 else 'burn=102000')])
case('arms_abba_zero', dict(failed_has=['arms'], admission='NOT_ADMITTED'),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=0 text=%s'
                              % (arm, b, START + PERIOD * b, ('burn=0', 'burn=102000')[arm])])
case('arms_order_abab', dict(failed_has=['arms'], admission='NOT_ADMITTED'), order=(0, 1, 0, 1))
case('arms_wrong_text', dict(failed_has=['arms'], admission='NOT_ADMITTED'),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b, ('burn=0', 'burn=202000')[arm])])
case('arms_three', dict(failed_has=['arms'], admission='NOT_ADMITTED'),
     gate_arm=lambda b, arm: ['GateArm: arm=%d arms=3 block=%d frame=%d period=90 abba=1 text=%s'
                              % (arm, b, START + PERIOD * b, ('burn=0', 'burn=102000')[arm])])
case('gate_lines_wrong_value', dict(failed=['gate_lines'], admission='NOT_ADMITTED'),
     gate_lines=lambda b, arm: ['Gate: burn=%d frame=%d' % (202000 if arm else 0, START + PERIOD * b)])
case('gate_lines_other_name', dict(failed=['gate_lines'], admission='NOT_ADMITTED'),
     gate_lines=lambda b, arm: ['Gate: fslean=1 frame=%d' % (START + PERIOD * b)])
case('gate_lines_off_boundary', dict(failed=['gate_lines'], admission='NOT_ADMITTED'),
     gate_lines=lambda b, arm: ['Gate: burn=%s frame=%d' % (('0', '102000')[arm], START + PERIOD * b + 3)])
case('marker_in_log', dict(failed=['no_marker'], admission='NOT_ADMITTED'),
     extra_log=['GpuHangAbort: tick 12 never completed'])
case('marker_in_stdout', dict(failed=['no_marker'], admission='NOT_ADMITTED'),
     stdout_lines=['--- Error --- something died'])
case('skip_draw_before_window_ok', dict(OK, verdict='CRITICAL', skipped_draws=20, skipped_in_window=0),
     after=lambda n: ['AsyncPipelines: skipped draw'] * 20 if n == START - 2 else [])
case('skip_draw_in_window', dict(failed=['no_skip_window'], admission='NOT_ADMITTED', skipped_in_window=1),
     after=lambda n: ['AsyncPipelines: skipped draw'] if n == START + 1 + 20 else [])
case('streams_missing_draw_row', dict(failed_has=['streams'], admission='NOT_ADMITTED', complete_blocks=7),
     drop=(('draw', START + 1 + 20),))
case('streams_missing_field', dict(failed_has=['streams'], admission='NOT_ADMITTED'),
     strip=(('x', START + 1 + 20, 'rec_spin_us'),))
case('streams_missing_burn_field', dict(failed_has=['streams'], admission='NOT_ADMITTED'),
     strip=(('x', START + 1 + 20, 'burn_cpu_bad'),))
case('streams_missing_main_field', dict(failed_has=['streams'], admission='NOT_ADMITTED'),
     strip=(('main', START + 1 + 20, 'submits'),))
case('streams_duplicate_x_row', dict(failed_has=['streams'], admission='NOT_ADMITTED'), dup=(START + 1 + 20,))
case('streams_last_main_row_exempt', dict(admission='ADMITTED', failed=[], ne=[], verdict='CRITICAL', pairs=3,
                                          complete_blocks=7),
     min_pairs=3, last=START + 1 + PERIOD * 7 + 88,
     drop=(('draw', START + 1 + PERIOD * 7 + 88), ('x', START + 1 + PERIOD * 7 + 88)))
case('idle_gpu_busy', dict(failed=['idle'], admission='NOT_ADMITTED'), meta=dict(pre_run=dict(gpu_util_median=11)))
case('idle_missing', dict(failed=['idle'], admission='NOT_ADMITTED'), meta=dict(pre_run=dict(available=False)))
case('burn_cpu_bad', dict(failed=['burn_ok'], admission='NOT_ADMITTED', burn__cpu_bad=2),
     x=AT(1, 20, {'burn_cpu_bad': 2}))
case('burn_cpu_bad_outside_window', dict(failed=['burn_ok'], admission='NOT_ADMITTED', burn__cpu_bad=1),
     x=AT(0, 89, {'burn_cpu_bad': 1}))
case('burn_rejected_value', dict(failed=['burn_ok'], admission='NOT_ADMITTED', burn__reject=1),
     extra_log=['Burn: value=999999 rejected'])
case('burn_no_tsc', dict(failed=['burn_ok'], admission='NOT_ADMITTED', burn__notsc=1),
     extra_log=['Burn: no calibrated TSC, disabled'])
case('burn_no_selftest', dict(failed=['burn_ok'], admission='NOT_ADMITTED', burn__selftest=0),
     burn_lines=['Burn: arm code=1 thread=GuestGpu dose_us=2000 q_ns=0'])
case('burn_late_reported_not_fatal', dict(OK, verdict='CRITICAL', burn__late=2,
                                          lines_has=['late 2 e.g. code=1 us=2145.8']),
     extra_log=['BurnLate: code=1 us=2145.8 target_us=2000', 'BurnLate: code=1 us=2103.2 target_us=2000'])
case('armed_leak_other_group', dict(failed=['armed'], admission='NOT_ADMITTED'),
     x=B(lambda n, b, i: {'burn_p_ns': 5}))
case('armed_a_arm_not_clean', dict(failed=['armed'], admission='NOT_ADMITTED'),
     x=A(lambda n, b, i: {'burn_g_ns': 5}))
case('arm_line_missing', dict(failed=['arm_lines'], admission='NOT_ADMITTED'), burn_lines=[SELFTEST])
case('arm_line_wrong_dose', dict(failed=['arm_lines'], admission='NOT_ADMITTED'),
     burn_lines=[SELFTEST, 'Burn: arm code=1 thread=GuestGpu dose_us=1000 q_ns=0'])
case('arm_line_wrong_code', dict(failed=['arm_lines'], admission='NOT_ADMITTED'),
     burn_lines=[SELFTEST, 'Burn: arm code=2 thread=Record dose_us=2000 q_ns=0'])
case('arm_line_wrong_thread', dict(failed=['arm_lines'], admission='NOT_ADMITTED'),
     burn_lines=[SELFTEST, 'Burn: arm code=1 thread=Record dose_us=2000 q_ns=0'])
case('arm_line_second_one_bad', dict(failed=['arm_lines'], admission='NOT_ADMITTED'),
     burn_lines=[SELFTEST, 'Burn: arm code=1 thread=GuestGpu dose_us=2000 q_ns=0',
                 'Burn: arm code=1 thread=GuestGpu dose_us=3000 q_ns=0'])
case('dose_low_6pct', dict(failed=['dose'], admission='NOT_ADMITTED', burn__measure__per_frame_us=1880.0),
     x=B(lambda n, b, i: burnt(1, int(DOSE * 0.94))))
case('dose_low_exactly_5pct', dict(OK, verdict='CRITICAL', burn__measure__per_frame_us=1900.0),
     x=B(lambda n, b, i: burnt(1, int(DOSE * 0.95))))
case('dose_high_6pct', dict(failed=['dose'], admission='NOT_ADMITTED', burn__measure__per_frame_us=2120.0),
     x=B(lambda n, b, i: burnt(1, int(DOSE * 1.06))))
case('coverage_zero', dict(failed=['coverage'], admission='NOT_ADMITTED', burn__coverage__value=0),
     x=B(lambda n, b, i: dict(burnt(1), burn_g_seen=0)))
case('repeat_tag_not_evaluable', dict(admission='NOT_ADMITTED', verdict='NOT_EVALUABLE',
                                      last_has=['NOT_EVALUABLE']),
     tag='sky122r', meta=dict(binary_sha256='ff' * 32))

# ------------------------------------------------------------------ ROADMAP s122 item 17 (c): an outlier drops a PAIR
F = lambda b, i: START + 1 + PERIOD * b + i      # the frame at position i of block b
OUT = lambda *spots: (lambda n, b, arm, i: {'dt_us': spots[[s[:2] for s in spots].index((b, i))][2]}
                      if (b, i) in [s[:2] for s in spots] else {})
case('outlier_exact_500000', dict(OK, verdict='CRITICAL', pairs=3, dropped_pairs=1, dt_us__delta=2000.0,
                                  outliers=[dict(frame=F(1, 20), dt_us=500000, block=1, pair=0)],
                                  lines_has=['OUTLIER frame n=1911 dt_us=500000 (>= 500000): block 1, pair (0, 1) '
                                             'dropped whole', 'outlier pairs dropped 1 (limit 2; more => the run is '
                                             'INVALID)']),
     main=OUT((1, 20, 500000)), min_pairs=3)
case('outlier_499999_kept', dict(admission='ADMITTED', failed=[], ne=[], pairs=4, dropped_pairs=0, outliers=[],
                                 dt_us__delta=2000.0 + (499999 - 35300) / float(WIN) / 4, lines_not=['OUTLIER']),
     main=OUT((1, 20, 499999)))
case('outlier_outside_window_drops_pair', dict(OK, verdict='CRITICAL', pairs=3, dropped_pairs=1, dt_us__delta=2000.0,
                                               outliers=[dict(frame=F(2, 3), dt_us=900000, block=2, pair=2)]),
     main=OUT((2, 3, 900000)), min_pairs=3)
case('outlier_a_block_drops_its_partner', dict(OK, verdict='CRITICAL', pairs=3, dropped_pairs=1, dt_us__delta=2000.0,
                                               dt_us__A=33300.0,
                                               lines_has=['block 3, pair (2, 3) dropped whole']),
     main=OUT((3, 50, 23796476)), min_pairs=3)
case('outlier_same_pair_counts_once', dict(OK, verdict='CRITICAL', pairs=3, dropped_pairs=1),
     main=OUT((0, 40, 600000), (1, 40, 600000)), min_pairs=3)
case('outlier_two_pairs_admitted', dict(OK, verdict='CRITICAL', pairs=2, dropped_pairs=2),
     main=OUT((1, 40, 600000), (4, 40, 600000)), min_pairs=2)
case('outlier_three_pairs_invalid', dict(failed=['outlier_pairs'], admission='NOT_ADMITTED', verdict='NOT_ADMITTED',
                                         dropped_pairs=3,
                                         lines_has=['outlier pairs dropped 3 (limit 2; more => the run is INVALID)',
                                                    'ADMISSION: NOT_ADMITTED failed=outlier_pairs']),
     main=OUT((1, 40, 600000), (2, 40, 600000), (5, 40, 600000)), min_pairs=1)
case('outlier_floor_counted_after_drops', dict(admission='ADMITTED', failed=[], ne=['pairs'], verdict='NOT_EVALUABLE',
                                               pairs=23, dropped_pairs=2),
     blocks=50, main=OUT((1, 40, 600000), (3, 40, 600000)), min_pairs='default')
case('outlier_floor_after_drops_ok', dict(OK, verdict='CRITICAL', pairs=24, dropped_pairs=2),
     blocks=52, main=OUT((1, 40, 600000), (3, 40, 600000)), min_pairs='default')
case('outlier_before_schedule_ignored', dict(OK, verdict='CRITICAL', pairs=4, dropped_pairs=0),
     main=lambda n, b, arm, i: {'dt_us': 10 ** 6} if n == START - 2 else {})
case('outlier_on_incomplete_row', dict(failed_has=['streams'], admission='NOT_ADMITTED', dropped_pairs=1,
                                       outliers=[dict(frame=F(5, 20), dt_us=600000, block=5, pair=4)]),
     main=OUT((5, 20, 600000)), strip=(('main', F(5, 20), 'submits'),))
case('outlier_dup_main_row_keeps_largest', dict(failed_has=['streams'], admission='NOT_ADMITTED', dropped_pairs=1),
     main=OUT((1, 20, 600000)), after=lambda n: ['FrameTrace: n=%d dt_us=33300' % n] if n == F(1, 20) else [])
check('outlier_constants', (mod.OUTLIER_US, mod.MAX_OUTLIER_PAIRS), (500000, 2))
check('dropped_pairs_partner', mod.dropped_pairs([(0, 1, 1), (0, 1, 2), (0, 1, 3), (0, 1, 6)]), [0, 2, 6])

# ------------------------------------------------------------------ ROADMAP s122 item 17 (a): the host-event witness
case('host_missing', dict(failed=['host_clean'], admission='NOT_ADMITTED', host='NOT CHECKED (no hostdev_sky122.txt)',
                          lines_has=['host events (hostdev_sky122.txt): NOT CHECKED (no hostdev_sky122.txt)']),
     hostdev=None)
case('host_run_invalid', dict(failed=['host_clean'], admission='NOT_ADMITTED', host='RUN_INVALID'),
     hostdev=hostdev_text(TAG, 'RUN_INVALID - host device events inside the window: hidbth/2'))
case('host_journal_not_read', dict(failed=['host_clean'], host='NOT CHECKED (the System journal was not read)'),
     hostdev=hostdev_text(TAG, 'NOT EVALUABLE - the Windows System log could not be read for this window'))
case('host_stall_unattributed_ok', dict(OK, verdict='CRITICAL', host='STALL_UNATTRIBUTED'),
     hostdev=hostdev_text(TAG, 'STALL_UNATTRIBUTED - stall present (1 dt outliers, 0 gpu-idle windows) with no host '
                               'device event'))
case('host_window_padded', dict(failed=['host_clean']),
     hostdev=hostdev_text(TAG, launched='2026-09-26T21:59:50', finished='2026-09-26T22:06:11'))
case('host_window_other_run', dict(failed=['host_clean']), meta=dict(launched='2026-09-26T23:00:00'))
case('host_names_other_tag', dict(failed=['host_clean']), hostdev=hostdev_text('skyp122'))
case('host_two_verdicts', dict(failed=['host_clean']), hostdev=hostdev_text(TAG) + 'VERDICT: RUN_CLEAN - again' + NL)
case('host_unknown_verdict', dict(failed=['host_clean'], host='SOMETHING'),
     hostdev=hostdev_text(TAG, 'SOMETHING - else'))
case('host_empty_report', dict(failed=['host_clean']), hostdev='')
_other_tool = BASE / 'hostdev122_other.py'
_other_tool.write_bytes(Path('C:/kyty/s122/hostdev122.py').read_bytes() + b'# edited' + NL.encode())
case('host_tool_other_bytes', dict(failed=['host_tool'], admission='NOT_ADMITTED'), hostdev_py=str(_other_tool))
case('host_tool_missing', dict(failed=['host_tool'], admission='NOT_ADMITTED'),
     hostdev_py=str(BASE / 'no_such_hostdev122.py'))

# ------------------------------------------------------------------ ROADMAP s122 item 14: the skipped-draw marker
SKIP = 'AsyncPipelines: skipped draw'
case('skip_draw_just_before_population', dict(OK, verdict='CRITICAL', skipped_draws=2, skipped_in_window=0,
                                              skipped_before=2, skipped_before_max=1810,
                                              lines_has=['skipped draws: 0 fatal (frame >= 1811), 2 before the '
                                                         'population (largest frame 1810)']),
     after=lambda n: [SKIP] if n in (1797, 1809) else [])
case('skip_draw_first_population_frame', dict(failed=['no_skip_window'], admission='NOT_ADMITTED', skipped_in_window=1,
                                              lines_has=['skipped draws: 1 fatal (frame >= 1811)']),
     after=lambda n: [SKIP] if n == 1810 else [])
case('skip_draw_between_windows', dict(failed=['no_skip_window'], skipped_in_window=1),
     after=lambda n: [SKIP] if n == F(2, 2) else [])
case('skip_draw_after_last_block', dict(failed=['no_skip_window'], skipped_in_window=1),
     after=lambda n: [SKIP] if n == START + PERIOD * BLOCKS else [])
case('skip_draw_unknown_window_fatal', dict(failed_has=['no_skip_window', 'arms'], admission='NOT_ADMITTED'),
     gate_arm=lambda b, arm: [], after=lambda n: [SKIP] if n == START - 3 else [])
case('skip_draw_before_any_frame', dict(OK, verdict='CRITICAL', skipped_before=1, skipped_before_max=None),
     pins=(PIN, SKIP))
check('skip_fatal_edges', (mod.skip_fatal(1810, 1811), mod.skip_fatal(1811, 1811), mod.skip_fatal(None, 1811),
                           mod.skip_fatal(None, None), mod.skip_fatal(5, None)), (False, True, False, True, True))
check('first_population_frame', (mod.first_population_frame({0: 0}), mod.first_population_frame({1: 1}),
                                 mod.first_population_frame({})), (1811, None, None))

# ------------------------------------------------------------------ ROADMAP s122 items 17 (d), 18 (c): headroom by the
# measured share of one-vblank frames (dt_us < 25 000) in the base-arm window, never by the level name
FAST = lambda base, slow=(): (lambda n, b, arm, i: {} if n <= START else
                              {'dt_us': (25000 if (b, i) in slow else base) + (DELTA if arm == 1 else 0)})
A_WIN = [(b, i) for b in range(BLOCKS) if arm_of(b) == 0 for i in range(KEEP[0], KEEP[1])]   # 316 base frames
HR_LINES = ['game speed: NOT QUOTED - on this scene the slope measures HEADROOM', 'pairs=4 bda=NEW reading=HEADROOM']
case('headroom_by_base_arm', dict(OK, verdict='CRITICAL', reading='HEADROOM', level='intro_next',
                                  headroom__share=1.0, headroom__frames=4 * WIN,
                                  lines_has=HR_LINES + ['reading HEADROOM: base-arm window share of dt_us < 25000 = '
                                                        '1.0000 over 316 frames (HEADROOM at >= 0.95; ROADMAP s122 '
                                                        'item 18 (c))'],
                                  lines_not=['game speed (16 667'],
                                  last_has=['HEADROOM: the slope here is the work the frame absorbs before it falls '
                                            'to the next vblank step, never a speed']),
     tag='des122', level='intro_next', main=FAST(16800))
case('headroom_not_by_name_intro_next', dict(OK, verdict='CRITICAL', reading='SPEED', headroom__share=0.0,
                                             lines_has=['game speed (16 667', 'reading=SPEED'],
                                             lines_not=['NOT QUOTED'], last_not=['HEADROOM']),
     tag='des122', level='intro_next')
case('headroom_not_by_name_sky', dict(OK, verdict='CRITICAL', reading='HEADROOM', lines_has=HR_LINES),
     main=FAST(16800))
# 316 base frames: 15 slow => 301/316 = 0.9525 HEADROOM, 16 slow => 300/316 = 0.9494 SPEED; fast = 24 999
case('headroom_edge_15_slow', dict(OK, reading='HEADROOM', headroom__share=301 / 316.0),
     main=FAST(24999, A_WIN[:15]))
case('headroom_edge_16_slow', dict(OK, reading='SPEED', headroom__share=300 / 316.0,
                                   lines_has=['game speed (16 667']),
     main=FAST(24999, A_WIN[:16]))
# base 24 000 (fast), armed 26 000 (every B frame slow): only the base arm classifies
case('headroom_b_arm_slow_ignored', dict(OK, verdict='CRITICAL', reading='HEADROOM', headroom__share=1.0),
     main=FAST(24000))
case('headroom_outside_window_ignored', dict(OK, verdict='CRITICAL', reading='HEADROOM', headroom__share=1.0),
     main=lambda n, b, arm, i: {} if n <= START else
     {'dt_us': (40000 if (arm == 0 and not KEEP[0] <= i < KEEP[1]) else 16800) + (DELTA if arm == 1 else 0)})
case('headroom_dropped_pair_ignored', dict(OK, verdict='CRITICAL', reading='HEADROOM', pairs=3, dropped_pairs=1,
                                           headroom__frames=3 * WIN, headroom__share=1.0),
     main=lambda n, b, arm, i: {} if n <= START else
     {'dt_us': (600000 if (b, i) == (1, 50) else 40000 if b == 0 else 16800) + (DELTA if arm == 1 else 0)},
     min_pairs=3)
case('headroom_no_base_arm', dict(admission='ADMITTED', verdict='NOT_EVALUABLE', reading='NOT_EVALUABLE', pairs=0,
                                  headroom__share=None, headroom__frames=0,
                                  lines_has=['game speed: NOT QUOTED - the reading is NOT EVALUABLE',
                                             'reading=NOT_EVALUABLE', 'reading NOT_EVALUABLE: base-arm window share '
                                             'of dt_us < 25000 = - over 0 frames'],
                                  lines_not=['game speed (16 667', 'reading=HEADROOM']),
     main=FAST(16800), drop=tuple(('main', F(b, 40)) for b in range(BLOCKS) if arm_of(b) == 0))
check('reading_of_edges', tuple(mod.reading_of(d)[:2] for d in (
    [24999] * 950 + [25000] * 50, [24999] * 949 + [25000] * 51, [25000] * 1000, [24999] * 1000, [])),
    (('HEADROOM', 0.95), ('SPEED', 0.949), ('SPEED', 0.0), ('HEADROOM', 1.0), ('NOT_EVALUABLE', None)))
check('reading_of_frames', (mod.reading_of([1, 2, 3])[2], mod.reading_of([])[2]), (3, 0))
check('headroom_constants', (mod.HEADROOM_DT_US, mod.HEADROOM_SHARE), (25000, 0.95))

# ------------------------------------------------------------------ the draw-adjusted estimator (report only)
case('draw_adjusted_differs', dict(OK, verdict='CRITICAL', zone='CRITICAL', draw_adjusted__zone='NOT_CRITICAL',
                                   draw_adjusted__differs=True, draw_adjusted__est__delta=335.0,
                                   draw_adjusted__est__draws_delta=230.0, draw_adjusted__slope__s=335.0 / DOSE,
                                   lines_has=['zone NOT_CRITICAL; Delta draws (B - A) 230.0 +- 0.0  DRAW-ADJUSTED ZONE '
                                              'DIFFERS', 'VERDICT: CRITICAL']),
     main=B(lambda n, b, i: {'draws': 4830}))
ADJ = [35300.0 - 33300.0 * 4830 / 4600, 35300.0 - 33300.0 * 4830 / 4600, 2000.0, 2000.0]
case('draw_adjusted_arithmetic', dict(OK, verdict='CRITICAL', draw_adjusted__est__pair_diffs=ADJ,
                                      draw_adjusted__est__delta=sum(ADJ) / 4,
                                      draw_adjusted__est__two_se=2.0 * statistics.stdev(ADJ) / 2.0,
                                      draw_adjusted__est__draws_delta=115.0),
     main=B(lambda n, b, i: {'draws': 4830} if b in (1, 2) else {}))

# ------------------------------------------------------------------ code 7: the role split is part of coverage
case('code7_role_partial', dict(OK, verdict='CRITICAL', code=7, burn__coverage__value=4 * WIN,
                                burn__coverage__role_value=3 * WIN,
                                lines_has=['coverage burn_s_seen = 316 (role burn_s_main = 237)']),
     tag='sub122', code=7, x=lambda n, b, arm, i: {'burn_s_main': 0} if b == 1 else {})
case('code7_role_zero', dict(failed=['coverage'], admission='NOT_ADMITTED', burn__coverage__role_value=0),
     tag='sub122', code=7, x=B(lambda n, b, i: {'burn_s_main': 0}))

# ------------------------------------------------------------------ edges the first mutant run left unpinned
case('estimator_draws_300_excluded', dict(OK, verdict='CRITICAL', est_frames__B=4 * WIN - 10, dt_us__delta=2000.0),
     main=lambda n, b, arm, i: {'draws': 300, 'dt_us': 400000} if (b == 1 and 20 <= i < 30) else {})
case('idle_exactly_10', dict(OK, verdict='CRITICAL'), meta=dict(pre_run=dict(gpu_util_median=10)))
case('arm_line_trailing_field', dict(failed=['arm_lines'], admission='NOT_ADMITTED'),
     burn_lines=[SELFTEST, 'Burn: arm code=1 thread=GuestGpu dose_us=2000 q_ns=0 extra=1'])
case('repeat_tag_admitted', dict(OK, verdict='CRITICAL', x_tag='sky122r', burn_value=102000), tag='sky122r')
case('gates_duplicate_first_wins', dict(failed=['gates_exact'], admission='NOT_ADMITTED'),
     meta=dict(gates=GATES_TEXT + ' texmemo2=1'))
case('gates_sha_bytes_only', dict(failed=['gates_exact'], admission='NOT_ADMITTED'),
     gates_file='copy', gates_copy=Path(GATES_REAL).read_bytes() + b'  ' + NL.encode())
case('only_block_a', dict(failed=['arm_asserts', 'armed', 'coverage', 'dose'], admission='NOT_ADMITTED'), blocks=1)
STD_ARM = lambda frame_shift=0: (lambda b, arm: ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                 % (arm, b, START + PERIOD * b + frame_shift,
                                                    ('burn=0', 'burn=102000')[arm])])
case('arms_frame_off_by_one', dict(failed_has=['arms'], admission='NOT_ADMITTED'), gate_arm=STD_ARM(1))
case('arms_block_missing', dict(failed_has=['arms'], admission='NOT_ADMITTED'),
     gate_arm=lambda b, arm: [] if b == 5 else STD_ARM()(b, arm))
case('dup_x_row_sums_both', dict(failed=['burn_ok', 'streams'], admission='NOT_ADMITTED', burn__cpu_bad=2),
     x=AT(1, 20, {'burn_cpu_bad': 1}), dup=(F(1, 20),))
case('label_blk_mismatch', dict(OK, verdict='CRITICAL', complete_blocks=7, pairs=3), main=AT(1, 20, {'blk': 7}),
     min_pairs=3)
case('label_arm_mismatch', dict(OK, verdict='CRITICAL', complete_blocks=7, pairs=3), main=AT(1, 20, {'arm': 0}),
     min_pairs=3)
case('block_without_estimator_rows', dict(OK, verdict='CRITICAL', pairs=3, complete_blocks=8),
     main=lambda n, b, arm, i: {'draws': 100} if b == 1 else {}, min_pairs=3)
check('zone_lo_exactly_half', mod.zone(dict(lo=0.5, hi=1.5)), 'NOT_RESOLVED')
check('zone_hi_exactly_flat', mod.zone(dict(lo=0.0, hi=0.3)), 'NOT_RESOLVED')
check('zone_lo_exactly_one', mod.zone(dict(lo=1.0, hi=1.0)), 'CRITICAL')
check('zone_hi_exactly_reach', mod.zone(dict(lo=0.6, hi=1.0)), 'CRITICAL')
check('zone_undefined', mod.zone(dict(lo=None, hi=1.0)), None)
check('vblank_floor_is_1', mod.vblank_shares([{'dt_us': 5000}]), ({1: 1.0}, (1, 1.0)))
check('vblank_top_is_the_largest', mod.vblank_shares([{'dt_us': 16667}] + [{'dt_us': 33334}] * 3),
      ({1: 0.25, 2: 0.75}, (2, 0.75)))

# ------------------------------------------------------------------ the pre-registration branches by direct calls (trap
# of s121: once PRED_SHA / PRED_BYTES are filled, pred=(None, None) no longer reaches the unsealed branch)
_pm = dict(prereg=dict(path=PRED_BACK, sha256=PSHA, bytes=PBYTES))
check('pred_checks_unfilled_direct', (mod.pred_checks(_pm, False, None, None, PRED_FWD),
                                      mod.pred_checks(_pm, False, PSHA, None, PRED_FWD),
                                      mod.pred_checks(_pm, False, None, PBYTES, PRED_FWD)),
      ((True, False), (True, False), (True, False)))
check('pred_checks_filled_direct', (mod.pred_checks(_pm, False, PSHA, PBYTES, PRED_FWD),
                                    mod.pred_checks(_pm, True, None, None, PRED_FWD),
                                    mod.pred_checks(_pm, False, PSHA, PBYTES + 1, PRED_FWD),
                                    mod.pred_checks(_pm, False, PSHA, PBYTES, str(BASE / 'no_such_pred.md'))),
      ((True, True), (True, True), (True, False), (False, False)))
if mod.PRED_SHA is None:
    check('pred_constants_unsealed', (mod.PRED_SHA, mod.PRED_BYTES), (None, None))
else:
    _real = Path(mod.PRED_PATH).read_bytes() if Path(mod.PRED_PATH).is_file() else b''
    _rm = dict(prereg=dict(path=mod.PRED_PATH.replace('/', '\\'), sha256=mod.PRED_SHA, bytes=mod.PRED_BYTES))
    check('pred_constants_sealed', (hashlib.sha256(_real).hexdigest(), len(_real),
                                    mod.pred_checks(_rm, False, mod.PRED_SHA, mod.PRED_BYTES, mod.PRED_PATH)),
          (mod.PRED_SHA, mod.PRED_BYTES, (True, True)))

# ------------------------------------------------------------------ the real logs: a clean NOT_ADMITTED, never a crash
if '--real' in sys.argv:
    for root, tag, log in (('C:/kyty/s122', 'bsky122', 'C:/kyty/s122/log_bsky122.txt'),
                           ('C:/kyty/s121', 'shp121', 'C:/kyty/s121/log_shp121.txt')):
        if not Path(log).is_file():
            RESULTS.append(('real_%s' % tag, False, ['missing %s' % log]))
            continue
        try:
            res = mod.evaluate(root, tag, draft=False, installed_sha='ff' * 32,
                               plan=dict(PLAN, **{tag: PLAN[TAG]}))
            text = NL.join(mod.format_report(res))
            failed = [k for k, v in res['checks'].items() if not v]
            ok = (res['verdict'] == 'NOT_ADMITTED' and not res['admitted'] and failed
                  and not re.search(r'(?i)\bnan\b|\binf\b', text))
            RESULTS.append(('real_%s' % tag, bool(ok),
                            [] if ok else ['verdict %s failed %r' % (res['verdict'], failed)]))
        except Exception as exc:                            # noqa: BLE001 - a crash is the failure this fixture tests
            RESULTS.append(('real_%s' % tag, False, ['crash: %r' % exc]))

bad = [(n, errs) for n, ok, errs in RESULTS if not ok]
for name, errs in bad:
    print('FAIL %s: %s' % (name, '; '.join(errs)))
print('%d fixtures, %d failed' % (len(RESULTS), len(bad)))
if not bad:
    print('ALL OK')
sys.exit(1 if bad else 0)

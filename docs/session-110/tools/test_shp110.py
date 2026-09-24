"""Session 110: fixtures for shp110.py (the SHIP run of knob `cspfree`, ABBA cspfree=0|1) in NON-draft mode, derived
from session 109's test_frf109.py (same coverage, renamed: tag shp110, video vsh110, predictions H1-H6).  Rule
(decision after 107, item 2): every decision term and every admission term gets a fixture where ONLY it fails, plus
every verdict branch.  Each case asserts the exact failing set (failed_controls) AND the exact failing sub-lists: ship
rules, video checks, arming sub-checks (by name, under control:ARMING), area-mirror criteria where relevant, and the
exact protocol error list.  Terms that cannot fail alone by construction are asserted as exact sets, with the scorer
lines that couple them cited at the case.  The seal check is pointed at a throwaway file; everything else is the
scorer's own code.  IDENTITY exists only in main() (shp110.py 830-834): main() is driven in-process with EXE /
PRODUCTION_ROOT pointed at fixtures.

The b3f7a2c9 build: every FrameTrace-x row carries cs_sync_new_us and cs_sync_wait_us after cspfree_moved (the base
fixture writes them, 1 500 us on each cs_sync_new row) and the log carries `CsStall:` lines (the base fixture writes
one per cs_sync_new row plus a load-time `kind=wait` line): SCHEMA_new_us / SCHEMA_wait_us / FIELD_ORIGIN_us put the
two counters under the schema, CSSTALL_not_marker keeps `CsStall:` out of the markers (log and stdout).

New against test_frf109.py - killers of the four session-109 audit survivors (AUDIT109.md MINOR-5):
  KEEP_edge   (KEEP_shift1)       noise-free dt; every arm-1 row at in-block index 59 and 89 (just outside the kept
                                  window 60..88 on either side) is +29 000 us: d mean dt is exactly -150 and the
                                  verdict pending; a window shifted by one row takes one outlier per block (+1 000 us
                                  a block mean, d mean dt +850, S1 fails).
  SE_exact    (SE_pstdev)         noise-free dt, arm-1 blocks +-867 us by quartet: the 110 pair deltas are known
                                  exactly; the pair SE is asserted as the SAMPLE SD / sqrt(n) (1e-9 relative) and not
                                  the population one, and the case sits on the S2 edge: mean + 2 SE = +0.296 us (S2
                                  fails, KEEP by the bar) where the population SD gives -0.461 (S2 would pass).
  LEVEL_median (LEVEL_mean)       noise-free dt, one arm-0 and one arm-1 block +2 900 us, one arm-1 block with
                                  cspfree_hit 5 000: the arm levels are asserted as MEDIANS of the block means
                                  (31 000 / 30 850 / 262 exactly; means would read 31 026.4 / 30 876.4 / 305.1, H1 a
                                  miss).
  FATAL_waitslow_log / _so (FATAL_no_waitslow) a `GpuWaitSlow:` line in the log, then in stdout: NO_FATAL_MARKER
                                  fails; the stdout loop over every marker is a HARD-CODED list (the suite of 109
                                  iterated the scorer's own FATAL tuple, so dropping a marker dropped its case).
Plus CONSTANTS (the sealed identity: root, pred path, unfilled seal, binary, gates file/sha, arms, schedule - these
feed the fixtures themselves, so no behavioural case can see them), full-text refusals / pending verdict, tag
acceptance (shp110b, shp110_entry1, shp110b_entry1 reach evaluate()) and refusal of the dropped tags, and the H1-H6
bands with their exact values (PRED_H6_hit, PRED_misses).
    python test_shp110.py <shp110.py> [<fixture dir>]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
import random
import shutil
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/fx_shp110')
NL = chr(10)
spec = importlib.util.spec_from_file_location('shp110', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ORIG = {k: getattr(mod, k) for k in ('PRODUCTION_ROOT', 'PRED', 'PRED_SHA', 'PRED_BYTES', 'BINARY_SHA', 'GATES_FILE',
                                      'GATES_SHA', 'ARMS', 'SCHEDULE', 'TAG_RE')}
BASE.mkdir(parents=True, exist_ok=True)
seal = BASE / 'seal.md'
seal.write_text('fixture seal 110 shp', encoding='utf-8')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
assert hashlib.sha256(Path(mod.GATES_FILE).read_bytes()).hexdigest() == mod.GATES_SHA, 'gates_base.txt moved'
gates_text = ' '.join(Path(mod.GATES_FILE).read_text(encoding='utf-8').split())
KEPT = range(mod.KEEP_LO, mod.KEEP_HI)      # in-block indices of the kept rows (60..88)
TAG = 'shp110'
STALL_US = 1500


def make(name, d_dt=-150, noise=300, cpu_noise=None, blocks=224, hit1=262, look0=0, hit0=0, sync0=1, sync1=1,
         pins=1, pin_mode=1, recs=2, fatal=None, dt_base=31000, draws1=5000, kpx1=201600, spin1=30, arm_text=None,
         prereg=None, binary=None, extra_env=None, block_noise=0.0, pattern=(0, 1, 1, 0), abba=1, gate=None,
         pre_dt=None, row=None, tail=()):
    """row(n, blk, arm, idx, tok): edit the three token dicts of frame n in place (idx = in-block index from
    frame 1801, None before); set tok[kind] = None to drop that line.  gate(b, fields): edit (or drop, by returning
    None) the GateArm line of block b.  pre_dt: dt_us of the rows before 1800.  cpu_noise: the SD of cpu_gpu_us
    (default noise; the same random draws are taken either way)."""
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(108)
    lines = ['GpuClockPin: mode %d' % pin_mode] * pins + ['RecordThread: started'] * recs
    if fatal:
        lines.append(fatal)
    last = 1800 + 90 * blocks
    sync_left = {0: sync0, 1: sync1}
    for n in range(1700, last + 1):
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < blocks:
            b = (n - 1800) // 90
            arm = pattern[b % 4]
            text = mod.ARMS[arm] if arm_text is None or b != 7 else arm_text
            g = {'arm': arm, 'arms': 2, 'block': b, 'frame': n, 'period': 90, 'abba': abba, 'text': text}
            if gate is not None:
                g = gate(b, g)
            if g is not None:
                lines.append('GateArm: arm=%d arms=%d block=%d frame=%d period=%d abba=%d text=%s'
                             % (g['arm'], g['arms'], g['block'], g['frame'], g['period'], g['abba'], g['text']))
        blk = (n - 1801) // 90 if n >= 1801 else 0
        arm = pattern[blk % 4] if n >= 1801 else 0
        if n >= 1801 and (n - 1801) % 90 == 0:
            # deterministic spread: arm-1 blocks alternate +A / -A by quartet, so the mean keeps d_dt and the
            # pair SD is ~A
            boff = (block_noise if (blk // 4) % 2 == 0 else -block_noise) if arm else 0.0
        elif n < 1801:
            boff = 0.0
        dt = dt_base + d_dt * arm + boff + rnd.gauss(0, noise)
        if pre_dt is not None and n < 1800:
            dt = pre_dt
        cpu = dt_base - 1000 + d_dt * arm + rnd.gauss(0, noise if cpu_noise is None else cpu_noise)
        draws = draws1 if arm else 5000
        kpx = kpx1 if arm else 201600
        sn = 0
        if n >= 2200 and sync_left[arm] > 0 and n % 997 == 0:
            sn = 1
            sync_left[arm] -= 1
        if n == 1720:      # a load-time wait for a pending compile (the b3f7a2c9 build's CsStall line, not a marker)
            lines.append('CsStall: kind=wait us=300 id=41 hash=0x9bc1c45f56b06af1')
        if sn:
            lines.append('CsStall: kind=new us=%d id=77 hash=0x0192b89f529d8bcb' % STALL_US)
        tok = {
            'main': {'n': n, 'dt_us': dt, 'draws': draws, 'dispatches': 268, 'gpu_busy_us': 12700,
                     'cpu_gpu_us': cpu, 'arm': arm, 'blk': blk},
            'draw': {'n': n, 'spin_gpu_us': spin1 if arm else 30, 'rec_n': 10900, 'da_walks': 8, 'da_walk_us': 2000,
                     'da_queue_us': 1100, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300, 'da_late': 6,
                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0},
            'x': {'n': n, 'rt_att': 100, 'rt_kpx': kpx, 'bf_n': 0, 'bf_disp': 0, 'bf_skip': 0, 'bf_clr_skip': 0,
                  'bf_skip_drop': 0, 'gm_ops': 0, 'da_wjobs': 8, 'da_wskip': 8, 'da_wdrop': 0, 'da_wlag_us': 72000,
                  'da_wdepth': 17, 'da_qcall': 1080, 'mw_n': 0, 'a_hold_us': 0, 'a_mut_us': 0, 'pl_em_n': 0,
                  'pl_proc_n': 0, 'sh_jobs': 0, 'cspfam_look': 0, 'cspfam_skip': 0, 'cs_sync_new': sn,
                  'cs_sync_wait': 0, 'cspf_have': (266 - hit1) if arm else 266, 'cspf_new': 0, 'cspfam_clr': 0,
                  'cspfree_look': 266 if arm else look0, 'cspfree_hit': hit1 if arm else hit0,
                  'cspfree_src_miss': 0, 'cspfree_spec_miss': (266 - hit1) if arm else 0, 'cspfree_mat_fail': 0,
                  'cspfree_clr': 0, 'cspfree_store': (266 - hit1) if arm else 0, 'cspfree_bad': 0,
                  'cspfree_moved': 0, 'cs_sync_new_us': STALL_US * sn, 'cs_sync_wait_us': 300 if n == 1720 else 0},
        }
        if row is not None:
            row(n, blk, arm, (n - 1801) % 90 if n >= 1801 else None, tok)
        for kind, prefix in (('main', 'FrameTrace: '), ('draw', 'FrameTrace-draw: '), ('x', 'FrameTrace-x: ')):
            if tok[kind] is not None:
                lines.append(prefix + ' '.join('%s=%d' % kv for kv in tok[kind].items()))
    lines.extend(tail)
    (d / ('log_%s.txt' % TAG)).write_text(NL.join(lines) + NL, encoding='utf-8')
    env = dict(mod.ENV_EXPECTED)
    env.update({'KYTY_GATE_FILE': mod.GATES_FILE, 'KYTY_SAMPLE_GATE': '1', 'KYTY_GATE_SCHEDULE': mod.SCHEDULE})
    if extra_env:
        env.update(extra_env)
    meta = {'binary_sha256': binary or mod.BINARY_SHA, 'env': env, 'schedule': mod.SCHEDULE, 'gates': gates_text,
            'hold_s': mod.HOLD_S, 'prereg': prereg or {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES},
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': mod.HOLD_S}]}
    (d / ('%s.json' % TAG)).write_text(json.dumps(meta), encoding='utf-8')
    return d


def variant(src, name, meta_edit=None, append=(), stdout=None, log=True, meta=True):
    """A copy of fixture `src` (log bytes verbatim) with an edited meta, extra log lines or a stdout file.  A
    verbatim log is a hard link to the source's (the scorer only reads it; size), a copy where links fail."""
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    for f in ('log_%s.txt' % TAG, '%s.json' % TAG, 'stdout_%s.txt' % TAG):
        if (d / f).exists():
            (d / f).unlink()
    if log:
        src_log, dst_log = src / ('log_%s.txt' % TAG), d / ('log_%s.txt' % TAG)
        if append:
            data = src_log.read_bytes() + (os.linesep.join(append) + os.linesep).encode('utf-8')
            dst_log.write_bytes(data)
        else:
            try:
                os.link(src_log, dst_log)
            except OSError:
                shutil.copyfile(src_log, dst_log)
    if meta:
        m = json.loads((src / ('%s.json' % TAG)).read_text(encoding='utf-8'))
        if meta_edit:
            meta_edit(m)
        (d / ('%s.json' % TAG)).write_text(json.dumps(m), encoding='utf-8')
    if stdout is not None:
        (d / ('stdout_%s.txt' % TAG)).write_text(NL.join(stdout) + NL, encoding='utf-8')
    return d


def video(d, frames=3990, glitches=0, gate='cspfree=1', pin='1', binary=None, tag='v', rec=True, env_extra=None,
          attempts=None, gates=None):
    vm = d / ('vsh110_%s.json' % tag)
    vr = d / ('vsh110_%s_glitch.txt' % tag)
    env = {'KYTY_REC': 'x.mp4'} if rec else {}
    if pin:
        env['KYTY_GPU_CLOCK_PIN'] = pin
    if env_extra:
        env.update(env_extra)
    vm.write_text(json.dumps({'binary_sha256': binary or mod.BINARY_SHA,
                              'gates': (gates_text if gates is None else gates) + ' ' + gate, 'env': env,
                              'attempts': [{'outcome': 'ok', 'hold_exit': None}] if attempts is None else attempts}),
                  encoding='utf-8')
    vr.write_text('rec: %d frames 960x540' % frames + NL + 'one-frame glitches: %d' % glitches + NL, encoding='utf-8')
    return str(vm), str(vr)


def setter(**kv):
    """row hook: set tokens {kind: {key: value or callable(n, blk, arm, idx)}} where pick(n, blk, arm, idx)."""
    def hook(pick, edits):
        def row(n, blk, arm, idx, tok):
            if pick(n, blk, arm, idx):
                for kind, fields in edits.items():
                    if fields is None:
                        tok[kind] = None
                        continue
                    for k, v in fields.items():
                        if v is None:
                            tok[kind].pop(k, None)
                        else:
                            tok[kind][k] = v(n, blk, arm, idx) if callable(v) else v
        return row
    return hook(kv['pick'], kv['edits'])


def both(*hooks):
    """row hook: apply several row hooks in order."""
    def row(n, blk, arm, idx, tok):
        for h in hooks:
            h(n, blk, arm, idx, tok)
    return row


def gate_at(which, **fields):
    """gate hook: edit the GateArm line of block `which` (drop it with drop=True)."""
    def edit(b, g):
        if b != which:
            return g
        if fields.get('drop'):
            return None
        g = dict(g)
        for k, v in fields.items():
            g[k] = v(g[k]) if callable(v) else v
        return g
    return edit


def kept(idx):
    return idx is not None and idx in KEPT


def not_kept(idx):
    return idx is not None and idx not in KEPT


def meta_set(**kv):
    def edit(m):
        for k, v in kv.items():
            m[k] = v
    return edit


def env_set(key, value):
    def edit(m):
        if value is None:
            m['env'].pop(key, None)
        else:
            m['env'][key] = value
    return edit


def run_eval(root, vm=None, vr=None, gates_file=None, draft=False):
    return lambda: (None, mod.evaluate(root, TAG, draft, None, gates_file or mod.GATES_FILE, vm, vr), '')


def run_main(argv, **patch):
    """Drive shp110.main() in-process; returns (rc, the result dict evaluate() built and main() finished, stdout)."""
    def go():
        saved = {k: getattr(mod, k) for k in patch}
        captured = {}
        orig = mod.evaluate

        def spy(*a, **k):
            captured['out'] = orig(*a, **k)
            return captured['out']
        buf = io.StringIO()
        try:
            for k, v in patch.items():
                setattr(mod, k, v)
            mod.evaluate = spy
            with contextlib.redirect_stdout(buf):
                rc = mod.main(argv)
        finally:
            mod.evaluate = orig
            for k, v in saved.items():
                setattr(mod, k, v)
        return rc, captured.get('out'), buf.getvalue()
    return go


KEEP_NA = 'KEEP cspfree=0 (run not admitted)'
KEEP_BAR = 'KEEP cspfree=0 (ship rule S1-S2 on mean dt not met)'
KEEP_VID = 'KEEP cspfree=0 (video pass failed)'
SHIP = 'SHIP cspfree=1 as the new default (a new build: its video pass is owed, ROADMAP 6)'
PENDING = 'SHIP_PENDING_VIDEO (S1-S2 met; nothing ships until vsh110 is read)'
ARMING = {'control:ARMING'}
PRED_BANDS = {'H1': [200, 270], 'H2': [None, 30], 'H3': [-300, 0], 'H4': [None, -100.0], 'H5': [-30, 30],
              'H6': [0, 150]}
# the scorer's markers, written out here (not read from mod.FATAL: a dropped marker must still have its case)
FATAL_TEXTS = ('--- Error ---', '--- Fatal Error ---', '--- std::terminate ---', '--- abort() ---', 'ErrorDeviceLost',
               'Unhandled exception:', 'GpuWaitSlow:', 'AsyncPipelines: skipped draw')
WAITSLOW = 'GpuWaitSlow: tick=51234 waited 2000 ms submit_backlog=0 acopy=12/12/12 acopy_pending=0'
TAG_MSG = "tag %r is not a pred/03 tag (shp110, shp110b, optional _entry1)"

good = make('good')
cases = []


def case(name, run, want, fails=(), rules=(), vfail=(), arming=(), errors=(), mirror=None, rc=None, check=None):
    cases.append(dict(name=name, run=run, want=want, fails=set(fails), rules=sorted(rules), vfail=sorted(vfail),
                      arming=sorted(arming), errors=list(errors), mirror=mirror, rc=rc, check=check))


def pred_values(o, **want):
    """the six keys, their sealed bands, the given exact values, and the given hit / miss sets."""
    p = o['predictions']
    hits = want.pop('hits')
    return (sorted(p) == sorted(PRED_BANDS) and all(p[k]['band'] == PRED_BANDS[k] for k in PRED_BANDS)
            and all(p[k]['value'] == v for k, v in want.items())
            and sorted(k for k in p if p[k]['hit']) == sorted(hits))


def pred_good(o):
    """H1-H6 of the good fixture: the six keys, their sealed bands, the fixture's exact values, all HIT; plus the
    scorer's name in the result and in the summary header."""
    dt = o['pair_stats']['dt_us']['mean']
    return (pred_values(o, H1=262, H2=4, H3=dt, H4=dt, H5=0, H6=0, hits=list(PRED_BANDS))
            and o['scorer'] == 'shp110.py'
            and mod.summary(o).split(NL)[0].startswith('shp110.py shp110 status=ADMITTED'))


def const_check():
    want = {'PRODUCTION_ROOT': 'C:/kyty/s110', 'PRED': 'C:/kyty/s110/pred/03_shp110.md', 'PRED_SHA': None,
            'PRED_BYTES': None, 'BINARY_SHA': 'b3f7a2c957dd344bfd140fe6d04eb2b95ac9387d01dabf5b7dde42b6765b6a82',
            'GATES_FILE': 'C:/kyty/s110/gates_base.txt',
            'GATES_SHA': '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf',
            'ARMS': ('dawalk=1 dawalklead=1 cspfree=0', 'dawalk=1 dawalklead=1 cspfree=1'),
            'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 cspfree=0|dawalk=1 dawalklead=1 cspfree=1',
            'TAG_RE': r'shp110b?(?:_entry1)?'}
    bad = sorted(k for k in want if ORIG[k] != want[k])
    return None, None, 'CONSTANTS OK' if not bad else 'CONSTANTS DIFFER %s' % bad


# ---- the sealed identity (feeds the fixtures themselves, so no behavioural case can see it) ----------------------
case('CONSTANTS', const_check, 'CONSTANTS OK')

# ---- verdict branches -------------------------------------------------------------------------------------------
case('SHIP', run_eval(good, *video(good, tag='ok')), SHIP)
case('PENDING', run_eval(good), PENDING, check=pred_good)
case('DRAFT', run_eval(good, draft=True), 'DRAFT (no verdict)', check=lambda o: o['status'] == 'DRAFT')
# KEEP by the bar = S1_only / S2_only / SE_exact; KEEP by a failed video = V_*; KEEP not admitted = every admission case

# ---- decision terms, each alone ---------------------------------------------------------------------------------
case('S1_only', run_eval(make('s1', d_dt=-60, noise=80)), KEEP_BAR, rules=['S1_dt_le_-100'],
     check=lambda o: not o['predictions']['H4']['hit'] and o['predictions']['H3']['hit'])
case('S2_only', run_eval(make('s2', d_dt=-150, noise=300, block_noise=1500)), KEEP_BAR,
     rules=['S2_dt_2se_excludes_0'])

# ---- audit-109 survivor KEEP_shift1: the kept window's edges -----------------------------------------------------
# noise-free: arm 0 31 000, arm 1 30 850; arm-1 rows at in-block index 59 and 89 (outside 60..88, one on each side)
# +29 000 us.  The kept window gives d mean dt -150 exactly; a window shifted by one row either way (59..87 or
# 61..89) takes one outlier per arm-1 block: +29 000 / 29 = +1 000 on its mean, d mean dt +850, S1 fails.
case('KEEP_edge', run_eval(make('keepedge', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i in (59, 89),
    edits={'main': {'dt_us': lambda n, b, a, i: 31000 - 150 + 29000}}))), PENDING,
    check=lambda o: (o['pair_stats']['dt_us']['mean'] == -150.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                     and o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30850.0
                     and o['selection']['pairs'] == 110))

# ---- audit-109 survivor SE_pstdev: the pair SE is the SAMPLE SD / sqrt(n) ------------------------------------------
# noise-free; arm-1 blocks 31 000 - 150 +- 867 (+ when blk // 4 is even).  Paired quartets 1..55 (blocks 0-2 lie
# before frame 2100): 2 pairs each, delta -150 + 867 (even quartet) or -150 - 867 (odd).  mean -165.7636,
# sample SE 83.0298 -> mean + 2 SE = +0.296 (S2 fails: KEEP by the bar); population SE -> -0.461 (S2 would pass).
SE_B = 867
SE_D = [-150 + (SE_B if q % 2 == 0 else -SE_B) for q in range(1, 56) for _ in range(2)]
SE_N = len(SE_D)
SE_MEAN = sum(SE_D) / SE_N
SE_SAMPLE = math.sqrt(sum((x - SE_MEAN) ** 2 for x in SE_D) / (SE_N - 1)) / math.sqrt(SE_N)
SE_POP = math.sqrt(sum((x - SE_MEAN) ** 2 for x in SE_D) / SE_N) / math.sqrt(SE_N)
assert SE_MEAN + 2 * SE_SAMPLE > 0 > SE_MEAN + 2 * SE_POP, 'SE_exact no longer straddles the S2 edge'


def se_exact(o):
    st = o['pair_stats']['dt_us']
    return (st['n'] == SE_N and abs(st['mean'] - SE_MEAN) <= 1e-9 * abs(SE_MEAN)
            and abs(st['se'] - SE_SAMPLE) <= 1e-9 * SE_SAMPLE and abs(st['se'] - SE_POP) > 1e-3 * SE_SAMPLE
            and sorted(p['d']['dt_us'] for p in o['pairs']) == sorted(float(x) for x in SE_D))


case('SE_exact', run_eval(make('seexact', noise=0, block_noise=SE_B)), KEEP_BAR, rules=['S2_dt_2se_excludes_0'],
     check=se_exact)

# ---- audit-109 survivor LEVEL_mean: arm levels are MEDIANS of the block means --------------------------------------
# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 17 (arm 1) cspfree_hit 5 000:
# medians 31 000 / 30 850 / 262 exactly (means: 31 026.4 / 30 876.4 / 305.07 - H1 would miss); the two dt
# outliers sit in different pairs with opposite signs, so d mean dt stays -150 exactly.
case('LEVEL_median', run_eval(make('levmed', noise=0, row=both(
    setter(pick=lambda n, b, a, i: i is not None and b in (9, 12),
           edits={'main': {'dt_us': lambda n, b, a, i: 31000 - 150 * a + 2900}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 17, edits={'x': {'cspfree_hit': 5000}})))), PENDING,
    check=lambda o: (o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30850.0
                     and o['levels']['arm1']['cspfree_hit'] == 262.0 and o['levels']['arm0']['cspfree_hit'] == 0.0
                     and o['pair_stats']['dt_us']['mean'] == -150.0
                     and pred_values(o, H1=262.0, hits=list(PRED_BANDS))))

# ---- the reported, never deciding d cpu_net_us (audit-108 survivor 2) -------------------------------------------
# cpu_gpu_us noise-free, arm-1 spin_gpu_us 80 against 30: d cpu_net = d cpu_gpu - d spin = -150 - 50 = -200 exactly;
# with spin dropped from derived() (shp110.py 278) it would read -150.  The verdict does not move (no term reads it:
# 647 `cpu` is bound and never read; 648-652 S1/S2 read dt only; BANDS 612-613 are dt/rec_n/gpu_busy; its other uses
# are PAIR_KEYS 98, levels and the summary 752/758).
case('CPU_NET_spin', run_eval(make('cpunet', spin1=80, cpu_noise=0)), PENDING,
     check=lambda o: (o['pair_stats']['cpu_net_us']['mean'] == -200.0
                      and o['pair_stats']['spin_gpu_us']['mean'] == 50.0
                      and o['levels']['arm0']['cpu_net_us'] == 29970.0
                      and o['levels']['arm1']['cpu_net_us'] == 29770.0
                      and '  d cpu_net_us   mean -200.0  2SE None  t -inf  n 110' in mod.summary(o).split(NL)))

# ---- predictions H1-H6 (report only: the verdict never reads them) ------------------------------------------------
# arm-1 gpu_busy_us +70: H6 value 70.0, a hit
case('PRED_H6_hit', run_eval(make('predh6', row=setter(pick=lambda n, b, a, i: a == 1,
                                                       edits={'main': {'gpu_busy_us': 12770}}))), PENDING,
     check=lambda o: pred_values(o, H1=262, H2=4, H5=0, H6=70.0, hits=list(PRED_BANDS)))
# arm-1 cspfree_hit 180 (cspf_have 86), da_miss +40, gpu_busy_us -20: H1, H2, H5, H6 miss (H6's old lower bound -50
# would hit), H3 / H4 hit
case('PRED_misses', run_eval(make('predmiss', hit1=180, row=setter(
    pick=lambda n, b, a, i: a == 1, edits={'main': {'gpu_busy_us': 12680}, 'draw': {'da_miss': 340}}))), PENDING,
    check=lambda o: pred_values(o, H1=180, H2=86, H5=40.0, H6=-20.0, hits=['H3', 'H4']))

# ---- video checks, each alone (all nine; sub-conditions of the gate text and of one_ok_attempt too) -------------
case('V_frames', run_eval(good, *video(good, frames=2000, tag='fr')), KEEP_VID, vfail=['frames'])
case('V_glitch', run_eval(good, *video(good, glitches=1, tag='gl')), KEEP_VID, vfail=['no_glitch'])
case('V_gate', run_eval(good, *video(good, gate='cspfree=0', tag='gt')), KEEP_VID, vfail=['cspfree_1_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['cspfree_1_in_gate_text'])
case('V_pin', run_eval(good, *video(good, pin=None, tag='pn')), KEEP_VID, vfail=['pinned'])
case('V_binary', run_eval(good, *video(good, binary='0' * 64, tag='bn')), KEEP_VID, vfail=['binary'])
case('V_recorded', run_eval(good, *video(good, rec=False, tag='rc')), KEEP_VID, vfail=['recorded'])
case('V_no_schedule', run_eval(good, *video(good, env_extra={'KYTY_GATE_SCHEDULE': mod.SCHEDULE}, tag='sc')),
     KEEP_VID, vfail=['no_schedule'])
case('V_no_ckpt', run_eval(good, *video(good, env_extra={'KYTY_GPU_CHECKPOINTS': '0'}, tag='ck')),
     KEEP_VID, vfail=['no_checkpoints'])
case('V_att_outcome', run_eval(good, *video(good, attempts=[{'outcome': 'fatal', 'hold_exit': None}], tag='ao')),
     KEEP_VID, vfail=['one_ok_attempt'])
case('V_att_exit', run_eval(good, *video(good, attempts=[{'outcome': 'ok', 'hold_exit': 1}], tag='ae')),
     KEEP_VID, vfail=['one_ok_attempt'])
case('V_att_two', run_eval(good, *video(good, attempts=[{'outcome': 'ok', 'hold_exit': None}] * 2, tag='a2')),
     KEEP_VID, vfail=['one_ok_attempt'])
# video paths given but the files missing: read_video (shp110.py 489-491) reads ABSENT, not FAIL -> pending
case('V_missing', run_eval(good, str(good / 'no_such_vsh110.json'), str(good / 'no_such_glitch.txt')), PENDING,
     check=lambda o: o['video']['state'] == 'ABSENT')

# ---- integrity terms, each alone --------------------------------------------------------------------------------
# INPUTS is coupled with 'protocol' BY CONSTRUCTION: the missing input is written into out['errors'] (shp110.py
# 531-535) and finish() appends 'protocol' whenever out['errors'] is non-empty (693-694).
case('INPUTS_log', run_eval(variant(good, 'in_log', log=False)), KEEP_NA,
     fails={'integrity:INPUTS', 'protocol'}, errors=['missing input: '])
case('INPUTS_meta', run_eval(variant(good, 'in_meta', meta=False)), KEEP_NA,
     fails={'integrity:INPUTS', 'protocol'}, errors=['missing input: '])
case('PREREG', run_eval(make('prereg', prereg={'sha256': '0' * 64, 'bytes': 1})), KEEP_NA,
     fails={'integrity:PREREG_PINNED'})
case('BINARY', run_eval(make('binary', binary='1' * 64)), KEEP_NA, fails={'integrity:BINARY_SEALED'})
case('SCHEMA', run_eval(make('schema', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                  edits={'x': {'cspf_new': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'})
# the 2f593229 build's counters are in the schema too ...
case('SCHEMA_free', run_eval(make('schemafree', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                           edits={'x': {'cspfree_moved': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'})
# ... and the b3f7a2c9 build's two duration counters, each alone
case('SCHEMA_new_us', run_eval(make('schemanewus', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                              edits={'x': {'cs_sync_new_us': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o: o['schema_missing_fields'] == ['cs_sync_new_us'])
case('SCHEMA_wait_us', run_eval(make('schemawaitus', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                edits={'x': {'cs_sync_wait_us': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o: o['schema_missing_fields'] == ['cs_sync_wait_us'])
case('FIELD_ORIGIN', run_eval(make('origin', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                        edits={'draw': {'mw_n': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'})
case('FIELD_ORIGIN_us', run_eval(make('originus', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                             edits={'draw': {'cs_sync_wait_us': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},
     check=lambda o: o['field_origin_defects'] == {'cs_sync_wait_us': ['draw', 'x']})
case('RAW_CONTIG', run_eval(make('contig', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                      edits={'main': None, 'draw': None, 'x': None}))),
     KEEP_NA, fails={'integrity:RAW_CONTIGUITY'})
# 140 blocks: 68 pairs (PAIRS holds) but 12 701 rows x ~31 ms = ~394 s < hold_s 600
case('DURATION', run_eval(make('duration', blocks=140)), KEEP_NA, fails={'integrity:DURATION'},
     check=lambda o: o['selection']['pairs'] >= mod.MIN_PAIRS)
# GATEARM, every clause of shp110.py 569-571 alone
case('GATEARM', run_eval(make('gatearm', arm_text='dawalk=1 cspfree=9')), KEEP_NA, fails={'integrity:GATEARM'})
case('GATEARM_malformed', run_eval(make('gatemal', tail=['GateArm: arm=x'])), KEEP_NA, fails={'integrity:GATEARM'})
# the ABBA order with abba=1 (audit-108 survivor 1): BAAB keeps both orientations (one pair each per quartet), so
# only the order clause fails
case('GATEARM_order', run_eval(make('gateorder', pattern=(1, 0, 0, 1))), KEEP_NA, fails={'integrity:GATEARM'},
     check=lambda o: o['orientations'][0] == o['orientations'][1] > 0)
case('GATEARM_abba0', run_eval(make('gateabba', gate=gate_at(7, abba=0))), KEEP_NA, fails={'integrity:GATEARM'})
case('GATEARM_arms', run_eval(make('gatearms', gate=gate_at(7, arms=3))), KEEP_NA, fails={'integrity:GATEARM'})
case('GATEARM_period', run_eval(make('gateper', gate=gate_at(7, period=91))), KEEP_NA, fails={'integrity:GATEARM'})
case('GATEARM_frame', run_eval(make('gateframe', gate=gate_at(7, frame=lambda f: f + 1))), KEEP_NA,
     fails={'integrity:GATEARM'})
# block 7's line says block=8: arms[7] is never set, quartet 4-7 leaves the selection (108 pairs), nothing else fails
case('GATEARM_block', run_eval(make('gateblock', gate=gate_at(7, block=8))), KEEP_NA, fails={'integrity:GATEARM'},
     check=lambda o: o['selection']['pairs'] == 108)
# no GateArm line at all: ok_gate = bool([]) (shp110.py 562) cannot fail alone BY CONSTRUCTION - with no arms
# select() pairs nothing, so PAIRS / AB_BA_BALANCED fail and the early return (604-607) fails the rest
case('GATEARM_none', run_eval(make('gatenone', gate=lambda b, g: None)), KEEP_NA,
     fails={'integrity:GATEARM', 'control:PAIRS', 'integrity:AB_BA_BALANCED', 'control:BANDS',
            'control:WORK_SPLIT', 'control:AREA_VERDICT', 'control:AREA_SELECTED', 'control:ARMING'},
     check=lambda o: o['gate_blocks'] == 0 and 'SYNC_COMPILE' not in o['controls'])
for key in mod.FLOOR_KEYS:
    case('NO_FLOOR_%s' % key, run_eval(make('floor_%s' % key, row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                        edits={'x': {key: 1}}))),
         KEEP_NA, fails={'integrity:NO_FLOOR'})
case('MARKERS_OFF', run_eval(make('gmops', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                      edits={'x': {'gm_ops': 1}}))),
     KEEP_NA, fails={'integrity:MARKERS_OFF'})
case('NO_RECORDING', run_eval(variant(good, 'recording', append=['Recording: C:/kyty/s110/rec_shp110.mp4 960x540'])),
     KEEP_NA, fails={'integrity:NO_RECORDING'})
# frame 1850 (> start 1800, block 0 - never paired) lacks its FrameTrace-x line
case('STREAMS', run_eval(make('streams', row=setter(pick=lambda n, b, a, i: n == 1850, edits={'x': None}))),
     KEEP_NA, fails={'integrity:STREAMS_COMPLETE'})
# a kept row of block 5 (arm 1) reports blk=6 (also arm 1): only the row/block agreement breaks
case('ROW_ARMS', run_eval(make('rowarms', row=setter(pick=lambda n, b, a, i: b == 5 and i == 60,
                                                     edits={'main': {'blk': 6}}))),
     KEEP_NA, fails={'integrity:ROW_ARMS'})
# AB_BA_BALANCED cannot fail alone BY CONSTRUCTION: GATEARM (shp110.py 569-571) pins arms[i] = (0,1,1,0)[i%4];
# select() pairs only whole quartets as (b,b+1),(b+2,b+3) (263-266), so each quartet adds one pair of each
# orientation (590) and orient[0] > 0 needs one pair, implied by PAIRS (603, MIN_PAIRS 60).  It fails only with
# GATEARM (here: an ABAB schedule, with abba=0 and with abba=1) or with PAIRS (NO_PAIRS below).
case('AB_BA', run_eval(make('abab', pattern=(0, 1, 0, 1), abba=0)), KEEP_NA,
     fails={'integrity:GATEARM', 'integrity:AB_BA_BALANCED'})
case('AB_BA_abba1', run_eval(make('abab1', pattern=(0, 1, 0, 1), abba=1)), KEEP_NA,
     fails={'integrity:GATEARM', 'integrity:AB_BA_BALANCED'})

# ---- controls, each alone ---------------------------------------------------------------------------------------
case('PIN_ONCE', run_eval(make('pin', pins=2)), KEEP_NA, fails={'control:PIN_ONCE'})
case('PIN_mode2', run_eval(make('pinmode', pin_mode=2)), KEEP_NA, fails={'control:PIN_ONCE'})
case('PIN_none', run_eval(make('pinnone', pins=0)), KEEP_NA, fails={'control:PIN_ONCE'})
case('REC_TWO', run_eval(make('rec', recs=1)), KEEP_NA, fails={'control:RECORD_THREAD_TWO'})
case('CKPT_line', run_eval(variant(good, 'ckline', append=['Vulkan: GPU checkpoints on (NV)'])),
     KEEP_NA, fails={'control:NO_CHECKPOINT_LINE'})
case('CKPT_off', run_eval(variant(good, 'ckoff', append=['Vulkan: GPU checkpoints off (KYTY_GPU_CHECKPOINTS=0)'])),
     KEEP_NA, fails={'control:NO_CHECKPOINT_LINE'})
case('CKPT_diag', run_eval(variant(good, 'ckdiag', append=['CommandRecorder: diagnostic checkpoints enabled'])),
     KEEP_NA, fails={'control:NO_CHECKPOINT_LINE'})
case('HANGABORT', run_eval(variant(good, 'hang', append=['GpuHangAbort: no progress for 8 s acopy=1/1/1 '
                                                         'acopy_pending=0'])),
     KEEP_NA, fails={'control:NO_GPUHANGABORT'})
case('FATAL', run_eval(make('fatal', fatal='AsyncPipelines: skipped draw')), KEEP_NA,
     fails={'control:NO_FATAL_MARKER'})
for i, marker in enumerate(FATAL_TEXTS):     # every marker, read from the stdout file (the second scanned stream)
    case('FATAL_so%d' % i, run_eval(variant(good, 'fatal_so%d' % i, stdout=['x ' + marker + ' y'])),
         KEEP_NA, fails={'control:NO_FATAL_MARKER'}, check=lambda o, m=marker: o['markers']['fatal'] == {m: 1})
# audit-109 survivor FATAL_no_waitslow: a GpuWaitSlow line in the log, then in stdout
case('FATAL_waitslow_log', run_eval(variant(good, 'waitslow_log', append=[WAITSLOW])), KEEP_NA,
     fails={'control:NO_FATAL_MARKER'}, check=lambda o: o['markers']['fatal'] == {'GpuWaitSlow:': 1})
case('FATAL_waitslow_so', run_eval(variant(good, 'waitslow_so', stdout=[WAITSLOW])), KEEP_NA,
     fails={'control:NO_FATAL_MARKER'}, check=lambda o: o['markers']['fatal'] == {'GpuWaitSlow:': 1})
# the b3f7a2c9 build's CsStall lines are not a marker: more of them in the log and in stdout, still pending
STALLS = ['CsStall: kind=new us=12345 id=9 hash=0x5323000000000000', 'CsStall: kind=wait us=800 id=9 hash=0x1']
case('CSSTALL_not_marker', run_eval(variant(good, 'csstall', append=STALLS, stdout=STALLS)), PENDING,
     check=lambda o: o['markers']['fatal'] == {} and o['markers']['hang'] == 0)
# ENV_NO_CHECKPOINTS is coupled with 'protocol' BY CONSTRUCTION: KYTY_GPU_CHECKPOINTS is a KYTY_* variable outside
# ENV_EXPECTED / ENV_PRESENT, so protocol_errors() flags it (shp110.py 417-419) whenever control 602 fails.
case('ENV_CKPT', run_eval(make('envc', extra_env={'KYTY_GPU_CHECKPOINTS': '1'})), KEEP_NA,
     fails={'control:ENV_NO_CHECKPOINTS', 'protocol'}, errors=['env carries KYTY_* variables outside'])
# 100 blocks (48 pairs) with a 100-frame pre-schedule prefix of 3.5 s frames: ~628 s, so DURATION holds
case('PAIRS', run_eval(make('pairs1', blocks=100, pre_dt=3500000)), KEEP_NA, fails={'control:PAIRS'})
# PAIRS and DURATION together (the session-108 first draft's case, kept)
case('PAIRS_DUR', run_eval(make('pairs', blocks=100)), KEEP_NA, fails={'control:PAIRS', 'integrity:DURATION'})
# no pair at all (4 blocks: 0-2 outside the first-frame window, 3 an edge block): the early return of shp110.py
# 604-607 fails BANDS/WORK_SPLIT/AREA_*/ARMING by construction and never evaluates SYNC_COMPILE
case('NO_PAIRS', run_eval(make('nopairs', blocks=4, pre_dt=6500000)), KEEP_NA,
     fails={'control:PAIRS', 'integrity:AB_BA_BALANCED', 'control:BANDS', 'control:WORK_SPLIT',
            'control:AREA_VERDICT', 'control:AREA_SELECTED', 'control:ARMING'},
     check=lambda o: 'SYNC_COMPILE' not in o['controls'])
case('BANDS', run_eval(make('bands', dt_base=45000)), KEEP_NA, fails={'control:BANDS'})
case('BANDS_rec1', run_eval(make('bandsrec', row=setter(pick=lambda n, b, a, i: a == 1,
                                                        edits={'draw': {'rec_n': 14000}}))),
     KEEP_NA, fails={'control:BANDS'})
case('BANDS_gpu0', run_eval(make('bandsgpu', row=setter(pick=lambda n, b, a, i: a == 0,
                                                        edits={'main': {'gpu_busy_us': 17000}}))),
     KEEP_NA, fails={'control:BANDS'})
# work split alone: arm-1 KEPT rows +61 draws, the other 61 rows of each arm-1 block -29 -> selected work +1.22 %,
# the whole-arm mirror work ~0
case('WORK_SPLIT', run_eval(make('workonly', row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None,
    edits={'main': {'draws': lambda n, b, a, i: 5061 if i in KEPT else 4971}}))),
    KEEP_NA, fails={'control:WORK_SPLIT'}, mirror=[])
# area verdict alone, split+match criteria: arm-1 NOT-kept rows +2 % area (mirror split ~1.36 %; kept rows equal)
case('AREA_VERDICT', run_eval(make('avsplit', row=setter(pick=lambda n, b, a, i: a == 1 and not_kept(i),
                                                         edits={'x': {'rt_kpx': 205632}}))),
     KEEP_NA, fails={'control:AREA_VERDICT'}, mirror=['match', 'split'])
# area verdict alone, work criterion: arm-1 NOT-kept rows +1 % draws (mirror work ~0.68 %; selected work 0)
case('AREA_V_work', run_eval(make('avwork', row=setter(pick=lambda n, b, a, i: a == 1 and not_kept(i),
                                                       edits={'main': {'draws': 5050}}))),
     KEEP_NA, fails={'control:AREA_VERDICT'}, mirror=['work'])
# area selected alone: arm-1 KEPT rows +1.2 % area (selected split 1.2 %; mirror split ~0.39 %, pairs match)
case('AREA_SELECTED', run_eval(make('asel', row=setter(pick=lambda n, b, a, i: a == 1 and kept(i),
                                                       edits={'x': {'rt_kpx': 204019}}))),
     KEEP_NA, fails={'control:AREA_SELECTED'}, mirror=[])
# uniform shifts fail both (the session-108 first draft's cases, kept)
case('WORK', run_eval(make('work', draws1=5100)), KEEP_NA, fails={'control:WORK_SPLIT', 'control:AREA_VERDICT'},
     mirror=['work'])
case('AREA', run_eval(make('area', kpx1=206000)), KEEP_NA,
     fails={'control:AREA_SELECTED', 'control:AREA_VERDICT'}, mirror=['match', 'split'])
case('SYNC', run_eval(make('sync', sync0=1, sync1=4)), KEEP_NA, fails={'control:SYNC_COMPILE'},
     check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 4})
case('SYNC_edge', run_eval(make('syncedge', sync0=1, sync1=3)), PENDING,
     check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 3})

# ---- arming sub-checks, each alone (control:ARMING + the exact failing sub-check) --------------------------------
# FREE_DARK_ARM0, each half: arm-0 lookups without hits, then hits without lookups
case('FREE_DARK0', run_eval(make('fdark0', look0=5)), KEEP_NA, fails=ARMING, arming=['FREE_DARK_ARM0'],
     check=lambda o: o['arming']['free_arm0_kept']['cspfree_hit'] == 0
     and o['arming']['free_arm0_kept']['cspfree_look'] > 0)
case('FREE_DARK0_hit', run_eval(make('fdark0h', hit0=3)), KEEP_NA, fails=ARMING, arming=['FREE_DARK_ARM0'],
     check=lambda o: o['arming']['free_arm0_kept']['cspfree_look'] == 0
     and o['arming']['free_arm0_kept']['cspfree_hit'] > 0)
# arm 1 looks up (266 a flip) but never hits
case('FREE_ARMED1', run_eval(make('farmed1', hit1=0)), KEEP_NA, fails=ARMING, arming=['FREE_ARMED_ARM1'],
     check=lambda o: o['levels']['arm1']['cspfree_look'] == 266)
# one knob-2 disagreement on a pre-schedule row (outside every kept block: FREE_NO_BAD reads ALL rows) ...
case('FREE_NO_BAD', run_eval(make('fnobad', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                       edits={'x': {'cspfree_bad': 1}}))),
     KEEP_NA, fails=ARMING, arming=['FREE_NO_BAD'], check=lambda o: o['arming']['cspfree_bad_all_rows'] == 1)
# ... and on a kept arm-1 row
case('FREE_NO_BAD_kept', run_eval(make('fnobadk', row=setter(pick=lambda n, b, a, i: b == 5 and i == 70,
                                                             edits={'x': {'cspfree_bad': 2}}))),
     KEEP_NA, fails=ARMING, arming=['FREE_NO_BAD'], check=lambda o: o['arming']['cspfree_bad_all_rows'] == 2)
for a in (0, 1):
    # walker jobs/skips on every third row only: level ~0.33 < 1, kept totals still equal (identity, drops hold)
    case('WALK_ARMED%d' % a, run_eval(make('warmed%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a,
        edits={'x': {'da_wjobs': lambda n, b, arm, i: 1 if n % 3 == 0 else 0,
                     'da_wskip': lambda n, b, arm, i: 1 if n % 3 == 0 else 0}}))),
        KEEP_NA, fails=ARMING, arming=['WALK_ARMED_ARM%d' % a])
    case('WALK_IDENT%d' % a, run_eval(make('wident%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a, edits={'x': {'da_wskip': 9}}))),
        KEEP_NA, fails=ARMING, arming=['WALK_IDENTITY_ARM%d' % a])
    case('WALK_DROPS%d' % a, run_eval(make('wdrops%d' % a, row=setter(
        pick=lambda n, b, arm, i, a=a: arm == a, edits={'x': {'da_wjobs': 7, 'da_wdrop': 1}}))),
        KEEP_NA, fails=ARMING, arming=['WALK_DROPS_ARM%d' % a])
case('WALKS_SAME', run_eval(make('wsame', row=setter(pick=lambda n, b, a, i: a == 1, edits={'draw': {'da_walks': 9}}))),
     KEEP_NA, fails=ARMING, arming=['WALKS_SAME'])
# INSTRUMENTS_DARK, every key: one kept row, arm 0 (block 4) for even keys, arm 1 (block 5) for odd ones
for j, key in enumerate(mod.DARK_KEYS):
    case('DARK_%s' % key, run_eval(make('dk_%s' % key, row=setter(
        pick=lambda n, b, a, i, blk=4 + j % 2: b == blk and i == 60, edits={'x': {key: 1}}))),
        KEEP_NA, fails=ARMING, arming=['INSTRUMENTS_DARK'])

# ---- protocol errors, each alone (failed = ['protocol'], the exact error list) -----------------------------------
for key in mod.ENV_EXPECTED:
    case('P_env_%s' % key[5:].lower(), run_eval(variant(good, 'p_%s' % key.lower(), env_set(key, 'x'))), KEEP_NA,
         fails={'protocol'}, errors=['env %s=' % key])
case('P_env_sched', run_eval(variant(good, 'p_envsched', env_set('KYTY_GATE_SCHEDULE', '90+1800:%s|%s'
                                                                 % mod.ARMS[::-1]))),
     KEEP_NA, fails={'protocol'}, errors=['env KYTY_GATE_SCHEDULE='])
case('P_meta_sched', run_eval(variant(good, 'p_metasched', meta_set(schedule='90+1800:%s|%s' % mod.ARMS[::-1]))),
     KEEP_NA, fails={'protocol'}, errors=['meta schedule '])
case('P_absent_gatefile', run_eval(variant(good, 'p_nogatefile', env_set('KYTY_GATE_FILE', None))), KEEP_NA,
     fails={'protocol'}, errors=['env KYTY_GATE_FILE absent'])
case('P_absent_samplegate', run_eval(variant(good, 'p_nosample', env_set('KYTY_SAMPLE_GATE', None))), KEEP_NA,
     fails={'protocol'}, errors=['env KYTY_SAMPLE_GATE absent'])
# the schedule variable is both a value check (410-411) and a presence check (414-416): two errors, one term
case('P_absent_schedule', run_eval(variant(good, 'p_nosched', env_set('KYTY_GATE_SCHEDULE', None))), KEEP_NA,
     fails={'protocol'}, errors=['env KYTY_GATE_SCHEDULE=None', 'env KYTY_GATE_SCHEDULE absent'])
case('ENV_EXTRA', run_eval(make('envx', extra_env={'KYTY_SOMETHING_ELSE': '1'})), KEEP_NA, fails={'protocol'},
     errors=['env carries KYTY_* variables outside'])
alt_gates = BASE / 'gates_base_alt.txt'   # same normalised text (a trailing space), different sha256
alt_gates.write_bytes(Path(mod.GATES_FILE).read_bytes() + b' ')
case('P_gates_sha', run_eval(variant(good, 'p_gsha'), gates_file=str(alt_gates)), KEEP_NA, fails={'protocol'},
     errors=['gates_base.txt sha256 '])
case('P_gates_text', run_eval(variant(good, 'p_gtext', meta_set(gates=gates_text + ' cspfree=1'))), KEEP_NA,
     fails={'protocol'}, errors=['meta gates text is not gates_base.txt'])
ATT = {'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': mod.HOLD_S}
case('P_att_label', run_eval(variant(good, 'p_alabel', meta_set(attempts=[dict(ATT, label='attempt 2')]))), KEEP_NA,
     fails={'protocol'}, errors=['attempts are '])
case('P_att_two', run_eval(variant(good, 'p_atwo', meta_set(attempts=[ATT, dict(ATT, label='attempt 2')]))), KEEP_NA,
     fails={'protocol'}, errors=['attempts are '])
case('P_att_outcome', run_eval(variant(good, 'p_aout', meta_set(attempts=[dict(ATT, outcome='fatal')]))), KEEP_NA,
     fails={'protocol'}, errors=['attempt outcome '])
case('P_att_exit', run_eval(variant(good, 'p_aexit', meta_set(attempts=[dict(ATT, hold_exit=3221225477)]))), KEEP_NA,
     fails={'protocol'}, errors=['the game ended inside the hold'])
case('P_att_hold_s', run_eval(variant(good, 'p_ahold', meta_set(attempts=[dict(ATT, hold_s=300)]))), KEEP_NA,
     fails={'protocol'}, errors=['hold_s 300 below'])
# meta hold_s 590 (not 600): DURATION compares with it (559-560) and still holds (~627 s), only protocol fails
case('P_meta_hold_s', run_eval(variant(good, 'p_mhold', meta_set(hold_s=590))), KEEP_NA, fails={'protocol'},
     errors=['meta hold_s 590'])

# ---- IDENTITY and the exits of main() ---------------------------------------------------------------------------
fake_exe = BASE / 'fake_kyty_emulator.exe'
fake_exe.write_bytes(b'not the b3f7a2c9 build')
fake_sha = hashlib.sha256(fake_exe.read_bytes()).hexdigest()
main_ok = variant(good, 'main_ok', meta_set(binary_sha256=fake_sha))
ROOT = {'PRODUCTION_ROOT': good.as_posix()}
# control: installed exe == meta binary == BINARY_SHA (all three the fixture exe) -> admitted through main()
case('MAIN_OK', run_main([TAG, '--root', str(main_ok)], PRODUCTION_ROOT=main_ok.as_posix(),
                         BINARY_SHA=fake_sha, EXE=str(fake_exe)),
     PENDING, rc=0, check=lambda o: o['integrity']['IDENTITY'] is True and o['installed_exe_sha256'] == fake_sha)
# In main() BINARY_SEALED cannot fail alone BY CONSTRUCTION: IDENTITY (shp110.py 833) also requires the meta binary
# to equal BINARY_SHA, which BINARY_SEALED (545) checks.  Here the installed exe and the meta agree on another build.
# (BINARY above fails it alone through evaluate(), which is main() with a matching installed exe - see MAIN_OK.)
case('BINARY_main', run_main([TAG, '--root', str(main_ok)], PRODUCTION_ROOT=main_ok.as_posix(),
                             EXE=str(fake_exe)),
     KEEP_NA, fails={'integrity:BINARY_SEALED', 'integrity:IDENTITY'}, rc=1)
case('IDENTITY', run_main([TAG, '--root', str(good)], EXE=str(fake_exe), **ROOT), KEEP_NA,
     fails={'integrity:IDENTITY'}, rc=1, check=lambda o: o['installed_exe_sha256'] == fake_sha)
case('IDENTITY_noexe', run_main([TAG, '--root', str(good)], EXE=str(BASE / 'no_such.exe'), **ROOT), KEEP_NA,
     fails={'integrity:IDENTITY'}, rc=1, check=lambda o: o['installed_exe_sha256'] is None)
case('REFUSE_seal', run_main([TAG, '--root', str(good)], PRED_SHA='0' * 64, EXE=str(fake_exe), **ROOT),
     'SEALED PRE-REGISTRATION CHANGED', rc=2)
# the generated scorer ships with PRED_SHA = None: it must refuse until the executor pins pred/03 (full message)
case('REFUSE_unsealed', run_main([TAG, '--root', str(good)], PRED_SHA=None, PRED_BYTES=None, EXE=str(fake_exe),
                                 **ROOT),
     'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into shp110.py (only --draft runs '
     'without a seal): refusing to score' % mod.PRED, rc=2)
case('REFUSE_root', run_main([TAG, '--root', str(good)], EXE=str(fake_exe)), 'production root must be', rc=2)
# the tag pattern: shp110 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('shp110b', 'shp110_entry1', 'shp110b_entry1'):
    case('TAG_ok_%s' % t, run_main([t, '--root', str(good)], EXE=str(fake_exe), **ROOT), KEEP_NA,
         fails={'integrity:INPUTS', 'integrity:IDENTITY', 'protocol'}, errors=['missing input: ', 'missing input: '],
         rc=1, check=lambda o, t=t: o['tag'] == t)
# ... and every other tag is refused with the full message, the dropped session-109 tags and the video tag included
for t in ('shp111', 'frf109', 'frf109b', 'frf109_entry1', 'fam108', 'vsh110', 'shp110c', 'xshp110'):
    case('REFUSE_tag_%s' % t, run_main([t, '--root', str(good)], EXE=str(fake_exe), **ROOT), TAG_MSG % t, rc=2)
case('REFUSE_geom', run_main([TAG, '--root', str(good), '--period', '60'], EXE=str(fake_exe), **ROOT),
     '--period/--start/--first/--keep are --draft only', rc=2)
exists = BASE / 'already_there.json'
exists.write_text('{}', encoding='utf-8')
(BASE / 'not_under_root.json').unlink(missing_ok=True)   # a mutant without the root check would have written it
case('REFUSE_out_exists', run_main([TAG, '--root', str(good), '--out', str(exists)], EXE=str(fake_exe), **ROOT),
     'output %s exists' % exists, rc=2)
case('REFUSE_out_root', run_main([TAG, '--root', str(good), '--out', str(BASE / 'not_under_root.json')],
                                 EXE=str(fake_exe), **ROOT),
     'output must live under', rc=2)


def failing(d):
    return sorted(k for k, v in (d or {}).items() if not v)


ok = True
for c in cases:
    try:
        rc, out, printed = c['run']()
        raised = None
    except Exception as exc:             # an exception is this case's failure, never a crash of the whole suite
        rc, out, printed, raised = None, None, '', exc
    problems = []
    if raised is not None:
        problems.append('raised %r' % raised)
    if c['rc'] is not None and rc != c['rc']:
        problems.append('rc %r' % rc)
    if out is None:                      # a refusal of main(): nothing scored, the message is the verdict
        got = printed.strip().splitlines()[0] if printed.strip() else ''
        if not got.startswith(c['want']) and c['want'] not in got:
            problems.append('message')
        fails = []
    else:
        got = out['verdict']
        fails = out.get('failed_controls') or []
        if not got.startswith(c['want']):
            problems.append('verdict')
        if set(fails) != c['fails'] or len(fails) != len(set(fails)):
            problems.append('failed set')
        if failing((out.get('decision') or {}).get('rules')) != c['rules']:
            problems.append('rules %s' % failing((out.get('decision') or {}).get('rules')))
        if failing((out.get('video') or {}).get('checks')) != c['vfail']:
            problems.append('video %s' % failing((out.get('video') or {}).get('checks')))
        if failing((out.get('arming') or {}).get('checks')) != c['arming']:
            problems.append('arming %s' % failing((out.get('arming') or {}).get('checks')))
        errs = out.get('errors') or []
        if len(errs) != len(c['errors']) or not all(e.startswith(p) for e, p in zip(errs, c['errors'])):
            problems.append('errors %s' % errs)
        if c['mirror'] is not None and failing((out.get('area_verdict_mirror') or {}).get('criteria')) != c['mirror']:
            problems.append('mirror %s' % failing((out.get('area_verdict_mirror') or {}).get('criteria')))
        if c['check'] is not None:
            try:
                good_check = c['check'](out)
            except Exception as exc:     # a missing key is a failed check, not a crash of the suite
                good_check = False
                problems.append('check raised %r' % exc)
            if not good_check:
                problems.append('check')
    passed = not problems
    ok &= passed
    extra = []
    if out is not None:
        for label, key in (('rules', 'rules'), ('video', 'vfail'), ('arming', 'arming'), ('mirror', 'mirror')):
            if c[key]:
                extra.append('%s=%s' % (label, c[key]))
        if c['errors']:
            extra.append('errors=%d' % len(out.get('errors') or []))
    if c['rc'] is not None:
        extra.append('rc=%s' % rc)
    if c['name'] in ('S2_only', 'SE_exact', 'KEEP_edge', 'LEVEL_median'):
        st = ((out or {}).get('pair_stats') or {}).get('dt_us') or {}
        print('   %s case: d mean dt %s se %s (sample SE wanted %s, population %s)'
              % (c['name'], st.get('mean'), st.get('se'), SE_SAMPLE if c['name'] == 'SE_exact' else '-',
                 SE_POP if c['name'] == 'SE_exact' else '-'))
    if c['name'] == 'LEVEL_median':
        lv = (out or {}).get('levels') or {}
        print('   LEVEL case: dt arm0 %s arm1 %s, cspfree_hit arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm1') or {}).get('cspfree_hit')))
    if c['name'] == 'CPU_NET_spin':
        st = ((out or {}).get('pair_stats') or {}).get('cpu_net_us') or {}
        print('   CPU_NET case: d cpu_net_us mean %s (d cpu_gpu -150, d spin +50)' % st.get('mean'))
    print('%-26s want %-34s got %-40s %s  failed=%s %s%s' % (c['name'], c['want'][:34], got[:40],
                                                            'OK' if passed else 'FAIL', sorted(fails), ' '.join(extra),
                                                            ('  PROBLEMS ' + '; '.join(problems)) if problems else ''))
print('%d cases' % len(cases))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)

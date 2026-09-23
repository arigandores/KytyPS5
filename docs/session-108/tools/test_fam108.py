"""Session 108: fixtures for fam108.py in NON-draft mode.  Rule (decision after 107, item 2): every decision term
and every admission term gets a fixture where ONLY it fails, plus every verdict branch.  Each case asserts the exact
failing set (failed_controls) AND the exact failing sub-lists: ship rules, video checks, arming sub-checks (by name,
under control:ARMING), area-mirror criteria where relevant, and the exact protocol error list.  Terms that cannot
fail alone by construction are asserted as exact sets, with the scorer lines that couple them cited at the case.
The seal check is pointed at a throwaway file; everything else is the scorer's own code.  IDENTITY exists only in
main() (fam108.py 808-812): main() is driven in-process with EXE / PRODUCTION_ROOT pointed at fixtures.
    python test_fam108.py <fam108.py>
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import random
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_fam108')
NL = chr(10)
spec = importlib.util.spec_from_file_location('fam108', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BASE.mkdir(parents=True, exist_ok=True)
seal = BASE / 'seal.md'
seal.write_text('fixture seal 108', encoding='utf-8')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
if not Path(mod.GATES_FILE).is_file():  # before the s108 port exists: the same pinned file of s107
    mod.GATES_FILE = 'C:/kyty/s107/gates_base.txt'
gates_text = ' '.join(Path(mod.GATES_FILE).read_text(encoding='utf-8').split())
KEPT = range(mod.KEEP_LO, mod.KEEP_HI)      # in-block indices of the kept rows (60..88)


def make(name, d_dt=-150, noise=300, blocks=224, skip1=200, look0=0, sync0=1, sync1=1, pins=1, recs=2,
         fatal=None, dt_base=31000, draws1=5000, kpx1=201600, arm_text=None, prereg=None, binary=None,
         extra_env=None, block_noise=0.0, pattern=(0, 1, 1, 0), abba=1, pre_dt=None, row=None, tail=()):
    """row(n, blk, arm, idx, tok): edit the three token dicts of frame n in place (idx = in-block index from
    frame 1801, None before); set tok[kind] = None to drop that line.  pre_dt: dt_us of the rows before 1800."""
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(108)
    lines = ['GpuClockPin: mode 1'] * pins + ['RecordThread: started'] * recs
    if fatal:
        lines.append(fatal)
    last = 1800 + 90 * blocks
    sync_left = {0: sync0, 1: sync1}
    for n in range(1700, last + 1):
        if n >= 1800 and (n - 1800) % 90 == 0 and (n - 1800) // 90 < blocks:
            b = (n - 1800) // 90
            arm = pattern[b % 4]
            text = mod.ARMS[arm] if arm_text is None or b != 7 else arm_text
            lines.append('GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=%d text=%s' % (arm, b, n, abba, text))
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
        cpu = dt_base - 1000 + d_dt * arm + rnd.gauss(0, noise)
        draws = draws1 if arm else 5000
        kpx = kpx1 if arm else 201600
        sn = 0
        if n >= 2200 and sync_left[arm] > 0 and n % 997 == 0:
            sn = 1
            sync_left[arm] -= 1
        tok = {
            'main': {'n': n, 'dt_us': dt, 'draws': draws, 'dispatches': 268, 'gpu_busy_us': 12700,
                     'cpu_gpu_us': cpu, 'arm': arm, 'blk': blk},
            'draw': {'n': n, 'spin_gpu_us': 30, 'rec_n': 10900, 'da_walks': 8, 'da_walk_us': 2000,
                     'da_queue_us': 1100, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300, 'da_late': 6,
                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0},
            'x': {'n': n, 'rt_att': 100, 'rt_kpx': kpx, 'bf_n': 0, 'bf_disp': 0, 'bf_skip': 0, 'bf_clr_skip': 0,
                  'bf_skip_drop': 0, 'gm_ops': 0, 'da_wjobs': 8, 'da_wskip': 8, 'da_wdrop': 0, 'da_wlag_us': 72000,
                  'da_wdepth': 17, 'da_qcall': 1080, 'mw_n': 0, 'a_hold_us': 0, 'a_mut_us': 0, 'pl_em_n': 0,
                  'pl_proc_n': 0, 'sh_jobs': 0, 'cspfam_look': (266 if arm else look0),
                  'cspfam_skip': (skip1 if arm else 0), 'cs_sync_new': sn, 'cs_sync_wait': 0,
                  'cspf_have': (266 - skip1) if arm else 266, 'cspf_new': 0},
        }
        if row is not None:
            row(n, blk, arm, (n - 1801) % 90 if n >= 1801 else None, tok)
        for kind, prefix in (('main', 'FrameTrace: '), ('draw', 'FrameTrace-draw: '), ('x', 'FrameTrace-x: ')):
            if tok[kind] is not None:
                lines.append(prefix + ' '.join('%s=%d' % kv for kv in tok[kind].items()))
    lines.extend(tail)
    (d / 'log_fam108.txt').write_text(NL.join(lines) + NL, encoding='utf-8')
    env = dict(mod.ENV_EXPECTED)
    env.update({'KYTY_GATE_FILE': mod.GATES_FILE, 'KYTY_SAMPLE_GATE': '1', 'KYTY_GATE_SCHEDULE': mod.SCHEDULE})
    if extra_env:
        env.update(extra_env)
    meta = {'binary_sha256': binary or mod.BINARY_SHA, 'env': env, 'schedule': mod.SCHEDULE, 'gates': gates_text,
            'hold_s': mod.HOLD_S, 'prereg': prereg or {'sha256': mod.PRED_SHA, 'bytes': mod.PRED_BYTES},
            'attempts': [{'label': 'attempt 1', 'outcome': 'ok', 'hold_exit': None, 'hold_s': mod.HOLD_S}]}
    (d / 'fam108.json').write_text(json.dumps(meta), encoding='utf-8')
    return d


def variant(src, name, meta_edit=None, append=(), stdout=None, log=True, meta=True):
    """A copy of fixture `src` (log bytes verbatim) with an edited meta, extra log lines or a stdout file."""
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    for f in ('log_fam108.txt', 'fam108.json', 'stdout_fam108.txt'):
        if (d / f).exists():
            (d / f).unlink()
    if log:
        data = (src / 'log_fam108.txt').read_bytes()
        if append:
            data += (os.linesep.join(append) + os.linesep).encode('utf-8')
        (d / 'log_fam108.txt').write_bytes(data)
    if meta:
        m = json.loads((src / 'fam108.json').read_text(encoding='utf-8'))
        if meta_edit:
            meta_edit(m)
        (d / 'fam108.json').write_text(json.dumps(m), encoding='utf-8')
    if stdout is not None:
        (d / 'stdout_fam108.txt').write_text(NL.join(stdout) + NL, encoding='utf-8')
    return d


def video(d, frames=3990, glitches=0, gate='cspfam=4', pin='1', binary=None, tag='v', rec=True, env_extra=None,
          attempts=None, gates=None):
    vm = d / ('vfm108_%s.json' % tag)
    vr = d / ('vfm108_%s_glitch.txt' % tag)
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
    return lambda: (None, mod.evaluate(root, 'fam108', draft, None, gates_file or mod.GATES_FILE, vm, vr), '')


def run_main(argv, **patch):
    """Drive fam108.main() in-process; returns (rc, the result dict evaluate() built and main() finished, stdout)."""
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


KEEP_NA = 'KEEP cspfam=0 (run not admitted)'
KEEP_BAR = 'KEEP cspfam=0 (ship rule'
KEEP_VID = 'KEEP cspfam=0 (video pass failed)'
PENDING = 'SHIP_PENDING_VIDEO'
ARMING = {'control:ARMING'}

good = make('good')
cases = []


def case(name, run, want, fails=(), rules=(), vfail=(), arming=(), errors=(), mirror=None, rc=None, check=None):
    cases.append(dict(name=name, run=run, want=want, fails=set(fails), rules=sorted(rules), vfail=sorted(vfail),
                      arming=sorted(arming), errors=list(errors), mirror=mirror, rc=rc, check=check))


# ---- verdict branches -------------------------------------------------------------------------------------------
case('SHIP', run_eval(good, *video(good, tag='ok')), 'SHIP cspfam=4')
case('PENDING', run_eval(good), PENDING)
case('DRAFT', run_eval(good, draft=True), 'DRAFT (no verdict)', check=lambda o: o['status'] == 'DRAFT')
# KEEP by the bar = S1_only / S2_only; KEEP by a failed video = V_*; KEEP not admitted = every admission case

# ---- decision terms, each alone ---------------------------------------------------------------------------------
case('S1_only', run_eval(make('s1', d_dt=-60, noise=80)), KEEP_BAR, rules=['S1_dt_le_-100'])
case('S2_only', run_eval(make('s2', d_dt=-150, noise=300, block_noise=1500)), KEEP_BAR,
     rules=['S2_dt_2se_excludes_0'])

# ---- video checks, each alone (all nine; sub-conditions of the gate text and of one_ok_attempt too) -------------
case('V_frames', run_eval(good, *video(good, frames=2000, tag='fr')), KEEP_VID, vfail=['frames'])
case('V_glitch', run_eval(good, *video(good, glitches=1, tag='gl')), KEEP_VID, vfail=['no_glitch'])
case('V_gate', run_eval(good, *video(good, gate='cspfam=0', tag='gt')), KEEP_VID, vfail=['cspfam_4_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['cspfam_4_in_gate_text'])
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
# video paths given but the files missing: read_video (fam108.py 473-475) reads ABSENT, not FAIL -> pending
case('V_missing', run_eval(good, str(good / 'no_such_vfm108.json'), str(good / 'no_such_glitch.txt')), PENDING,
     check=lambda o: o['video']['state'] == 'ABSENT')

# ---- integrity terms, each alone --------------------------------------------------------------------------------
# INPUTS is coupled with 'protocol' BY CONSTRUCTION: the missing input is written into out['errors'] (fam108.py
# 515-519) and finish() appends 'protocol' whenever out['errors'] is non-empty (674-675).
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
case('FIELD_ORIGIN', run_eval(make('origin', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                        edits={'draw': {'mw_n': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'})
case('RAW_CONTIG', run_eval(make('contig', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                      edits={'main': None, 'draw': None, 'x': None}))),
     KEEP_NA, fails={'integrity:RAW_CONTIGUITY'})
# 140 blocks: 68 pairs (PAIRS holds) but 12 701 rows x ~31 ms = ~394 s < hold_s 600
case('DURATION', run_eval(make('duration', blocks=140)), KEEP_NA, fails={'integrity:DURATION'},
     check=lambda o: o['selection']['pairs'] >= mod.MIN_PAIRS)
case('GATEARM', run_eval(make('gatearm', arm_text='dawalk=1 cspfam=9')), KEEP_NA, fails={'integrity:GATEARM'})
case('GATEARM_malformed', run_eval(make('gatemal', tail=['GateArm: arm=x'])), KEEP_NA, fails={'integrity:GATEARM'})
case('NO_FLOOR', run_eval(make('floor', row=setter(pick=lambda n, b, a, i: n == 1750, edits={'x': {'bf_n': 1}}))),
     KEEP_NA, fails={'integrity:NO_FLOOR'})
case('MARKERS_OFF', run_eval(make('gmops', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                      edits={'x': {'gm_ops': 1}}))),
     KEEP_NA, fails={'integrity:MARKERS_OFF'})
case('NO_RECORDING', run_eval(variant(good, 'recording', append=['Recording: C:/kyty/s108/rec_fam108.mp4 960x540'])),
     KEEP_NA, fails={'integrity:NO_RECORDING'})
# frame 1850 (> start 1800, block 0 - never paired) lacks its FrameTrace-x line
case('STREAMS', run_eval(make('streams', row=setter(pick=lambda n, b, a, i: n == 1850, edits={'x': None}))),
     KEEP_NA, fails={'integrity:STREAMS_COMPLETE'})
# a kept row of block 5 (arm 1) reports blk=6 (also arm 1): only the row/block agreement breaks
case('ROW_ARMS', run_eval(make('rowarms', row=setter(pick=lambda n, b, a, i: b == 5 and i == 60,
                                                     edits={'main': {'blk': 6}}))),
     KEEP_NA, fails={'integrity:ROW_ARMS'})
# AB_BA_BALANCED cannot fail alone BY CONSTRUCTION: GATEARM (fam108.py 553-555) pins arms[i] = (0,1,1,0)[i%4];
# select() pairs only whole quartets as (b,b+1),(b+2,b+3) (254-257), so each quartet adds one pair of each
# orientation (574) and orient[0] > 0 needs one pair, implied by PAIRS (587, MIN_PAIRS 60).  It fails only with
# GATEARM (here: an ABAB schedule, abba=0) or with PAIRS (NO_PAIRS below).
case('AB_BA', run_eval(make('abab', pattern=(0, 1, 0, 1), abba=0)), KEEP_NA,
     fails={'integrity:GATEARM', 'integrity:AB_BA_BALANCED'})

# ---- controls, each alone ---------------------------------------------------------------------------------------
case('PIN_ONCE', run_eval(make('pin', pins=2)), KEEP_NA, fails={'control:PIN_ONCE'})
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
for i, marker in enumerate(mod.FATAL):     # every marker, read from the stdout file (the second scanned stream)
    case('FATAL_so%d' % i, run_eval(variant(good, 'fatal_so%d' % i, stdout=['x ' + marker.decode() + ' y'])),
         KEEP_NA, fails={'control:NO_FATAL_MARKER'})
# ENV_NO_CHECKPOINTS is coupled with 'protocol' BY CONSTRUCTION: KYTY_GPU_CHECKPOINTS is a KYTY_* variable outside
# ENV_EXPECTED / ENV_PRESENT, so protocol_errors() flags it (fam108.py 408-410) whenever control 586 fails.
case('ENV_CKPT', run_eval(make('envc', extra_env={'KYTY_GPU_CHECKPOINTS': '1'})), KEEP_NA,
     fails={'control:ENV_NO_CHECKPOINTS', 'protocol'}, errors=['env carries KYTY_* variables outside'])
# 100 blocks (48 pairs) with a 100-frame pre-schedule prefix of 3.5 s frames: ~628 s, so DURATION holds
case('PAIRS', run_eval(make('pairs1', blocks=100, pre_dt=3500000)), KEEP_NA, fails={'control:PAIRS'})
# PAIRS and DURATION together (the session-108 first draft's case, kept)
case('PAIRS_DUR', run_eval(make('pairs', blocks=100)), KEEP_NA, fails={'control:PAIRS', 'integrity:DURATION'})
# no pair at all (4 blocks: 0-2 outside the first-frame window, 3 an edge block): the early return of fam108.py
# 588-591 fails BANDS/WORK_SPLIT/AREA_*/ARMING by construction and never evaluates SYNC_COMPILE
case('NO_PAIRS', run_eval(make('nopairs', blocks=4, pre_dt=6500000)), KEEP_NA,
     fails={'control:PAIRS', 'integrity:AB_BA_BALANCED', 'control:BANDS', 'control:WORK_SPLIT',
            'control:AREA_VERDICT', 'control:AREA_SELECTED', 'control:ARMING'},
     check=lambda o: 'SYNC_COMPILE' not in o['controls'])
case('BANDS', run_eval(make('bands', dt_base=45000)), KEEP_NA, fails={'control:BANDS'})
case('BANDS_rec1', run_eval(make('bandsrec', row=setter(pick=lambda n, b, a, i: a == 1,
                                                        edits={'draw': {'rec_n': 14000}}))),
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
# uniform shifts fail both (the first draft's cases, kept)
case('WORK', run_eval(make('work', draws1=5100)), KEEP_NA, fails={'control:WORK_SPLIT', 'control:AREA_VERDICT'},
     mirror=['work'])
case('AREA', run_eval(make('area', kpx1=206000)), KEEP_NA,
     fails={'control:AREA_SELECTED', 'control:AREA_VERDICT'}, mirror=['match', 'split'])
case('SYNC', run_eval(make('sync', sync0=1, sync1=4)), KEEP_NA, fails={'control:SYNC_COMPILE'},
     check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 4})
case('SYNC_edge', run_eval(make('syncedge', sync0=1, sync1=3)), PENDING,
     check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 3})

# ---- arming sub-checks, each alone (control:ARMING + the exact failing sub-check) --------------------------------
case('FAM_DARK0', run_eval(make('dark0', look0=5)), KEEP_NA, fails=ARMING, arming=['FAMILY_DARK_ARM0'])
case('FAM_ARMED1', run_eval(make('armed1', skip1=0)), KEEP_NA, fails=ARMING, arming=['FAMILY_ARMED_ARM1'])
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
case('DARK_mw_n0', run_eval(make('dkmw', row=setter(pick=lambda n, b, a, i: b == 4 and i == 60,
                                                    edits={'x': {'mw_n': 1}}))),
     KEEP_NA, fails=ARMING, arming=['INSTRUMENTS_DARK'])
case('DARK_sh_jobs1', run_eval(make('dksh', row=setter(pick=lambda n, b, a, i: b == 5 and i == 60,
                                                       edits={'x': {'sh_jobs': 1}}))),
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
# the schedule variable is both a value check (401-402) and a presence check (405-407): two errors, one term
case('P_absent_schedule', run_eval(variant(good, 'p_nosched', env_set('KYTY_GATE_SCHEDULE', None))), KEEP_NA,
     fails={'protocol'}, errors=['env KYTY_GATE_SCHEDULE=None', 'env KYTY_GATE_SCHEDULE absent'])
case('ENV_EXTRA', run_eval(make('envx', extra_env={'KYTY_SOMETHING_ELSE': '1'})), KEEP_NA, fails={'protocol'},
     errors=['env carries KYTY_* variables outside'])
alt_gates = BASE / 'gates_base_alt.txt'   # same normalised text (a trailing space), different sha256
alt_gates.write_bytes(Path(mod.GATES_FILE).read_bytes() + b' ')
case('P_gates_sha', run_eval(variant(good, 'p_gsha'), gates_file=str(alt_gates)), KEEP_NA, fails={'protocol'},
     errors=['gates_base.txt sha256 '])
case('P_gates_text', run_eval(variant(good, 'p_gtext', meta_set(gates=gates_text + ' cspfam=4'))), KEEP_NA,
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
# meta hold_s 590 (not 600): DURATION compares with it (543-544) and still holds (~627 s), only protocol fails
case('P_meta_hold_s', run_eval(variant(good, 'p_mhold', meta_set(hold_s=590))), KEEP_NA, fails={'protocol'},
     errors=['meta hold_s 590'])

# ---- IDENTITY and the exits of main() ---------------------------------------------------------------------------
fake_exe = BASE / 'fake_kyty_emulator.exe'
fake_exe.write_bytes(b'not the fd1d0bd7 build')
fake_sha = hashlib.sha256(fake_exe.read_bytes()).hexdigest()
main_ok = variant(good, 'main_ok', meta_set(binary_sha256=fake_sha))
ROOT = {'PRODUCTION_ROOT': good.as_posix()}
# control: installed exe == meta binary == BINARY_SHA (all three the fixture exe) -> admitted through main()
case('MAIN_OK', run_main(['fam108', '--root', str(main_ok)], PRODUCTION_ROOT=main_ok.as_posix(),
                         BINARY_SHA=fake_sha, EXE=str(fake_exe)),
     PENDING, rc=0, check=lambda o: o['integrity']['IDENTITY'] is True and o['installed_exe_sha256'] == fake_sha)
# In main() BINARY_SEALED cannot fail alone BY CONSTRUCTION: IDENTITY (fam108.py 811) also requires the meta binary
# to equal BINARY_SHA, which BINARY_SEALED (529) checks.  Here the installed exe and the meta agree on another build.
# (BINARY above fails it alone through evaluate(), which is main() with a matching installed exe - see MAIN_OK.)
case('BINARY_main', run_main(['fam108', '--root', str(main_ok)], PRODUCTION_ROOT=main_ok.as_posix(),
                             EXE=str(fake_exe)),
     KEEP_NA, fails={'integrity:BINARY_SEALED', 'integrity:IDENTITY'}, rc=1)
case('IDENTITY', run_main(['fam108', '--root', str(good)], EXE=str(fake_exe), **ROOT), KEEP_NA,
     fails={'integrity:IDENTITY'}, rc=1, check=lambda o: o['installed_exe_sha256'] == fake_sha)
case('IDENTITY_noexe', run_main(['fam108', '--root', str(good)], EXE=str(BASE / 'no_such.exe'), **ROOT), KEEP_NA,
     fails={'integrity:IDENTITY'}, rc=1, check=lambda o: o['installed_exe_sha256'] is None)
case('REFUSE_seal', run_main(['fam108', '--root', str(good)], PRED_SHA='0' * 64, EXE=str(fake_exe), **ROOT),
     'SEALED PRE-REGISTRATION CHANGED', rc=2)
case('REFUSE_root', run_main(['fam108', '--root', str(good)], EXE=str(fake_exe)), 'production root must be', rc=2)
case('REFUSE_tag', run_main(['fam109', '--root', str(good)], EXE=str(fake_exe), **ROOT), "tag 'fam109' is not", rc=2)
case('REFUSE_geom', run_main(['fam108', '--root', str(good), '--period', '60'], EXE=str(fake_exe), **ROOT),
     '--period/--start/--first/--keep are --draft only', rc=2)


def failing(d):
    return sorted(k for k, v in (d or {}).items() if not v)


ok = True
for c in cases:
    rc, out, printed = c['run']()
    problems = []
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
        if c['check'] is not None and not c['check'](out):
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
    if c['name'] == 'S2_only':
        st = (out.get('pair_stats') or {}).get('dt_us') or {}
        print('   S2 case: mean %s se %s' % (st.get('mean'), st.get('se')))
    print('%-19s want %-34s got %-40s %s  failed=%s %s%s' % (c['name'], c['want'][:34], got[:40],
                                                            'OK' if passed else 'FAIL', sorted(fails), ' '.join(extra),
                                                            ('  PROBLEMS ' + '; '.join(problems)) if problems else ''))
print('%d cases' % len(cases))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)

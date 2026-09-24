"""Session 112: fixtures for net112.py (the ABBA of today's default daslot=1 daguard=1 against the pre-session profile
daslot=0 daguard=0) in NON-draft mode, derived from session 111's test_shp111.py by make_net112.py (same coverage,
adapted: tag net112, video vnet112, the arms, the b47b58a9 counters da_q_noguard / da_guard_yield, arming
SLOT_ARMED_ARM0 / SLOT_DARK_ARM1 / NOGUARD_ARMED_ARM1 / NOGUARD_DARK_ARM0, the revert bar SHIP_US = 0, the quoted size
of session 111's gain, predictions N1-N7).  Rule (decision after 107, item 2): every decision term and every admission
term gets a fixture where ONLY it fails, plus every verdict branch.  Each case asserts the exact failing set
(failed_controls) AND the exact failing sub-lists: rules, video checks, arming sub-checks (by name, under
control:ARMING), area-mirror criteria where relevant, and the exact protocol error list.  Terms that cannot fail alone
by construction (now also S1: at the bar 0, S2 implies it) are asserted as exact sets, with the scorer lines that
couple them cited at the case.  The seal check is pointed at a throwaway file and GATES_FILE at a sha-checked copy of
gates_base.txt (C:/kyty/s112 need not hold it yet: the copy comes from it when it does, else from C:/kyty/s111 - the
same bytes, GATES_SHA asserted); everything else is the scorer's own code.  IDENTITY exists only in main(): main() is
driven in-process with EXE / PRODUCTION_ROOT pointed at fixtures.  CONSTANTS compares every sealed constant except
PRED_SHA / PRED_BYTES, which it only requires to be both None (the draft) or a 64-hex sha256 and a positive size (the
sealed copy), so the sealed scorer stays green on this suite (audit111 MINOR-5).

The window rows the fixtures edit are HARD-CODED here (MAIN = 10..89, SEC = 60..88), never read from the scorer, so a
mutant of the scorer's window cannot move its own fixtures.  The estimator cases (all noise-free, exact values):
  KEEP_edge        arm-1 row 9 +29 000, rows 10 and 89 -8 000: main -350 exactly, secondary -150 exactly (kills
                   KEEP_LO 9 / 11, KEEP_HI 89, the slice shifted down one row).
  SEC_edge         arm-1 rows 59 and 89 +29 000, rows 60 and 88 -2 900: secondary -350 exactly, main +502.5 exactly
                   (KEEP by the main estimator; the secondary would pass - it never decides).
  EST_rows0_9      arm-1 rows 0..9 +29 000 (the audit110 hitch shape): main and secondary -150 exactly (a full-block
                   estimator would read +3 072).
  EST_rows10_59    arm-1 rows 10..59 +800: main +350 exactly (KEEP), secondary -150 exactly (would pass).
  EST_rows10_59_rev  d 0, arm-1 rows 10..59 -400: main -250 exactly (REVERT pending), secondary 0 (would fail S2).
  PENDING          the noisy base fixture: main and secondary d mean / SE recounted from the log here, independently
                   of the scorer (1e-9 relative), and they differ; the quoted size is -(main d mean) with 2 x its SE.
Killers of the session-109 survivors kept: SE_exact (sample SD), LEVEL_median (median block levels: dt, da_q_free,
da_q_noguard, da_queue_us), FATAL_waitslow_log / _so.  Plus CONSTANTS (the sealed identity and the two windows),
full-text refusals / pending verdict, tag acceptance (net112b, net112_entry1, net112b_entry1 reach evaluate()) and
refusal of the others (session 111's included), the draft-only --secondary.  Threshold edges (audit111 MINOR-10: a
fixture on each side of every tolerance): the bar (S1_edge 0: S2 alone fails; S1_edge_in -0.5 pending; S1_edge_out
+0.5 both fail), the dark totals (SLOT_DARK1_one / NOGUARD_DARK0_one: a total of 1 fails, the good run's 0 passes),
the arming levels (ARMED_edge: 1 passes; *_sparse 0.33 fails), the attempt hold (595 s passes, 594 fails), the area
mirror's minimum block (8 flips count, 7 do not), the walk identity (0.9 % passes, 1.1 % fails), the video floor
(3 000 frames pass, 2 999 fail), and the N1-N7 bands with exact values at, inside and just outside every edge.
    python test_net112.py <net112.py> [<fixture dir>]
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import math
import os
import random
import re
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SRC = Path(sys.argv[1])
BASE = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('C:/kyty/s106_stage/net112/fx')
NL = chr(10)
spec = importlib.util.spec_from_file_location('net112', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ORIG = {k: getattr(mod, k) for k in ('PRODUCTION_ROOT', 'PRED', 'PRED_SHA', 'PRED_BYTES', 'BINARY_SHA', 'GATES_FILE',
                                      'GATES_SHA', 'ARMS', 'SCHEDULE', 'TAG_RE', 'KEEP_LO', 'KEEP_HI',
                                      'SECONDARY_LO', 'SECONDARY_HI')}
BASE.mkdir(parents=True, exist_ok=True)
seal = BASE / 'seal.md'
seal.write_text('fixture seal 112 net', encoding='utf-8')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size
GATES_SRC = Path(ORIG['GATES_FILE']) if Path(ORIG['GATES_FILE']).is_file() else Path('C:/kyty/s111/gates_base.txt')
gates_copy = BASE / 'gates_base.txt'
gates_copy.write_bytes(GATES_SRC.read_bytes())
assert hashlib.sha256(gates_copy.read_bytes()).hexdigest() == mod.GATES_SHA, 'gates_base.txt moved'
mod.GATES_FILE = str(gates_copy)
gates_text = ' '.join(gates_copy.read_text(encoding='utf-8').split())
MAIN = range(10, 90)      # in-block rows of the MAIN estimator (hard-coded: a scorer mutant must not move them)
SEC = range(60, 89)       # in-block rows of the secondary (session-110) window
TAG = 'net112'
STALL_US = 1500


def make(name, d_dt=-150, noise=300, cpu_noise=None, blocks=224, hit0=262, hit1=262, look0=266, look1=266,
         qfree0=1080, qfree1=0, ng0=0, ng1=1080, qq0=1296, qq1=1080, qcall=1080, gb0=1, gb1=2, sync0=1, sync1=1,
         pins=1, pin_mode=1, recs=2, fatal=None,
         dt_base=31000, draws1=5000, kpx1=201600, spin1=30, arm_text=None, prereg=None, binary=None, extra_env=None,
         block_noise=0.0, pattern=(0, 1, 1, 0), abba=1, gate=None, pre_dt=None, row=None, tail=()):
    """row(n, blk, arm, idx, tok): edit the three token dicts of frame n in place (idx = in-block index from
    frame 1801, None before); set tok[kind] = None to drop that line.  gate(b, fields): edit (or drop, by returning
    None) the GateArm line of block b.  pre_dt: dt_us of the rows before 1800.  cpu_noise: the SD of cpu_gpu_us
    (default noise; the same random draws are taken either way).  The shipping configuration: cspfree on in BOTH
    arms (look/hit per arm).  Arm 0 (today, daslot=1 daguard=1): da_q_free = qfree0 (= da_qcall 1080: every call off
    m_mutex), da_q_noguard = ng0; arm 1 (the candidate, daslot=0 daguard=0): da_q_free = qfree1, da_q_noguard = ng1
    (every call without the guards); the rows before the schedule are arm 0.  da_queue_us qq0 / qq1 and da_qcall
    qcall (both arms): walker us per call 1.2 / 1.0 by default; da_guard_busy gb0 / gb1."""
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
        hit = hit1 if arm else hit0
        sn = 0
        if n >= 2200 and sync_left[arm] > 0 and n % 997 == 0:
            sn = 1
            sync_left[arm] -= 1
        if n == 1720:      # a load-time wait for a pending compile (a CsStall line, not a marker)
            lines.append('CsStall: kind=wait us=300 id=41 hash=0x9bc1c45f56b06af1')
        if sn:
            lines.append('CsStall: kind=new us=%d id=77 hash=0x0192b89f529d8bcb' % STALL_US)
        tok = {
            'main': {'n': n, 'dt_us': dt, 'draws': draws, 'dispatches': 268, 'gpu_busy_us': 12700,
                     'cpu_gpu_us': cpu, 'arm': arm, 'blk': blk},
            'draw': {'n': n, 'spin_gpu_us': spin1 if arm else 30, 'rec_n': 10900, 'da_walks': 8, 'da_walk_us': 2000,
                     'da_queue_us': qq1 if arm else qq0, 'da_take_us': 2800, 'da_hit': 8350, 'da_miss': 300,
                     'da_late': 6,
                     'da_stale': 0, 'da_stale_old': 0, 'da_busy': 0},
            'x': {'n': n, 'rt_att': 100, 'rt_kpx': kpx, 'bf_n': 0, 'bf_disp': 0, 'bf_skip': 0, 'bf_clr_skip': 0,
                  'bf_skip_drop': 0, 'gm_ops': 0, 'da_wjobs': 8, 'da_wskip': 8, 'da_wdrop': 0, 'da_wlag_us': 72000,
                  'da_wdepth': 17, 'da_qcall': qcall, 'mw_n': 0, 'a_hold_us': 0, 'a_mut_us': 0, 'pl_em_n': 0,
                  'pl_proc_n': 0, 'sh_jobs': 0, 'cspfam_look': 0, 'cspfam_skip': 0, 'cs_sync_new': sn,
                  'cs_sync_wait': 0, 'cspf_have': 266 - hit, 'cspf_new': 0, 'cspfam_clr': 0,
                  'cspfree_look': look1 if arm else look0, 'cspfree_hit': hit,
                  'cspfree_src_miss': 0, 'cspfree_spec_miss': 266 - hit, 'cspfree_mat_fail': 0,
                  'cspfree_clr': 0, 'cspfree_store': 266 - hit, 'cspfree_bad': 0,
                  'cspfree_moved': 0, 'cs_sync_new_us': STALL_US * sn, 'cs_sync_wait_us': 300 if n == 1720 else 0,
                  'da_guard_busy': gb1 if arm else gb0, 'da_q_taking': 1, 'da_hint_defer': 0, 'da_hint_torn': 0,
                  'da_slot_bad': 0, 'da_q_free': qfree1 if arm else qfree0, 'da_chk_ok': 0, 'da_chk_bad': 0,
                  'da_q_noguard': ng1 if arm else ng0, 'da_guard_yield': 0},
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


def video(d, frames=3990, glitches=0, gate='daslot=0 daguard=0', pin='1', binary=None, tag='v', rec=True,
          env_extra=None, attempts=None, gates=None):
    vm = d / ('vnet112_%s.json' % tag)
    vr = d / ('vnet112_%s_glitch.txt' % tag)
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


def in_main(idx):
    return idx is not None and idx in MAIN


def out_main(idx):
    return idx is not None and idx not in MAIN


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
    """Drive net112.main() in-process; returns (rc, the result dict evaluate() built and main() finished, stdout)."""
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


def recount(d, rows_in_block, quartets=range(1, 56)):
    """Independent of the scorer: dt_us of every FrameTrace main line of fixture `d`, block means over the given
    in-block rows, the ABBA pairs (4q, 4q+1) and (4q+3, 4q+2) of the given quartets (pattern 0 1 1 0; the first
    block of each pair is arm 0), d = arm 1 - arm 0.  Returns (mean, sample SE, n)."""
    dt = {}
    for line in (d / ('log_%s.txt' % TAG)).read_text(encoding='utf-8').splitlines():
        if line.startswith('FrameTrace: '):
            kv = dict(tok.split('=') for tok in line.split()[1:])
            dt[int(kv['n'])] = int(kv['dt_us'])

    def bm(b):
        vals = [dt[1801 + 90 * b + i] for i in rows_in_block]
        return sum(vals) / len(vals)
    ds = []
    for q in quartets:
        ds.append(bm(4 * q + 1) - bm(4 * q))
        ds.append(bm(4 * q + 2) - bm(4 * q + 3))
    m = sum(ds) / len(ds)
    return m, math.sqrt(sum((x - m) ** 2 for x in ds) / (len(ds) - 1)) / math.sqrt(len(ds)), len(ds)


def close(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(b))


KEEP_NA = 'KEEP daslot=1 (run not admitted)'
KEEP_BAR = 'KEEP daslot=1 (revert rule S1-S2 on mean dt not met)'
KEEP_VID = 'KEEP daslot=1 (video pass failed)'
REVERT = 'REVERT to daslot=0 daguard=0 as the new default (a new build: its video pass is owed)'
PENDING = 'REVERT_PENDING_VIDEO (S1-S2 met; nothing changes until vnet112 is read)'
ARMING = {'control:ARMING'}
BOTH_RULES = ['S1_dt_le_0', 'S2_dt_2se_excludes_0']
PRED_BANDS = {'N1': [0.90, 1.12], 'N2': [1.00, 1.30], 'N3': [0, 300], 'N4': [100, None], 'N5': [800, 1400],
              'N6': [800, 1400], 'N7': [-40, 40]}
# the quoted size's label, written out here (not read from mod.GAIN_LABEL: a changed label must fail)
GAIN_LABEL = ("session 111's gain against the pre-session profile (arm 0 - arm 1 = -(d mean dt_us), main estimator; "
              'negative: daslot=1 faster)')
# the scorer's markers, written out here (not read from mod.FATAL: a dropped marker must still have its case)
FATAL_TEXTS = ('--- Error ---', '--- Fatal Error ---', '--- std::terminate ---', '--- abort() ---', 'ErrorDeviceLost',
               'Unhandled exception:', 'GpuWaitSlow:', 'AsyncPipelines: skipped draw')
WAITSLOW = 'GpuWaitSlow: tick=51234 waited 2000 ms submit_backlog=0 acopy=12/12/12 acopy_pending=0'
TAG_MSG = "tag %r is not a pred/02 tag (net112, net112b, optional _entry1)"
NEW_COUNTERS = ('da_guard_busy', 'da_q_taking', 'da_hint_defer', 'da_hint_torn', 'da_slot_bad', 'da_q_free',
                'da_chk_ok', 'da_chk_bad', 'da_q_noguard', 'da_guard_yield')

good = make('good')
cases = []


def case(name, run, want, fails=(), rules=(), vfail=(), arming=(), errors=(), mirror=None, rc=None, check=None):
    cases.append(dict(name=name, run=run, want=want, fails=set(fails), rules=sorted(rules), vfail=sorted(vfail),
                      arming=sorted(arming), errors=list(errors), mirror=mirror, rc=rc, check=check))


def pred_values(o, **want):
    """the seven keys, their sealed bands, the given exact values, and the given hit / miss sets."""
    p = o['predictions']
    hits = want.pop('hits')
    return (sorted(p) == sorted(PRED_BANDS) and all(p[k]['band'] == PRED_BANDS[k] for k in PRED_BANDS)
            and all(p[k]['value'] == v for k, v in want.items())
            and sorted(k for k in p if p[k]['hit']) == sorted(hits))


def main_dt(o):
    return o['pair_stats']['dt_us']['mean']


def sec_dt(o):
    return o['secondary']['pair_stats']['dt_us']['mean']


def sec_rules(o):
    return sorted(k for k, v in o['secondary']['rules_not_deciding'].items() if not v)


def gain_exact(o, mean, two_se):
    """the quoted size in the result (exact) and its summary line (label and format written out here)."""
    g = o['reported']['s111_gain_vs_pre_session']
    line = '  quoted size: %s = %.1f us a flip, 2SE %.1f, n 110' % (GAIN_LABEL, mean, two_se)
    return (g == {'mean': mean, 'two_se': two_se, 'n': 110, 'label': GAIN_LABEL}
            and line in mod.summary(o).split(NL))


def pred_good(o):
    """N1-N7 of the good fixture: the seven keys, their sealed bands, the fixture's exact values (N1 1.0, N2 1.2, N5 /
    N6 1 080, N7 0; N3 / N4 the main d mean, a REVERT here, so both miss), hits N1, N2, N5-N7; the scorer's name in the
    result and in the summary header; both estimators recounted from the log here (1e-9 relative), the secondary's own
    selection (block 3 excluded as an edge block there, nothing excluded in the main one), and the two summary lines
    naming the windows; the quoted size = -(main d mean) with 2 x its SE (result and summary line); the area mirror's
    110 block pairs; the added must-not-be-claimed item."""
    dt = main_dt(o)
    m_main, se_main, n_main = recount(good, MAIN)
    m_sec, se_sec, n_sec = recount(good, SEC)
    lines = mod.summary(o).split(NL)
    return (pred_values(o, N1=1080 / 1080, N2=1296 / 1080, N3=dt, N4=dt, N5=1080, N6=1080, N7=0,
                        hits=['N1', 'N2', 'N5', 'N6', 'N7'])
            and o['scorer'] == 'net112.py' and lines[0].startswith('net112.py net112 status=ADMITTED')
            and o['pair_stats']['dt_us']['n'] == n_main == 110 and close(dt, m_main)
            and close(o['pair_stats']['dt_us']['se'], se_main)
            and o['secondary']['pair_stats']['dt_us']['n'] == n_sec == 110 and close(sec_dt(o), m_sec)
            and close(o['secondary']['pair_stats']['dt_us']['se'], se_sec) and abs(m_main - m_sec) > 1.0
            and o['secondary']['window'] == [60, 89] and o['secondary']['deciding'] is False
            and o['geometry']['keep'] == [10, 90] and o['geometry']['secondary'] == [60, 89]
            and o['selection']['excluded_edge_blocks'] == [] and o['secondary']['excluded_edge_blocks'] == [3]
            and '  main estimator (decides): rows 10..89 of each block' in lines
            and '  secondary estimator (rows 60..88, never deciding): pairs 110, blocks 220, excluded [3]' in lines
            and gain_exact(o, -dt, 2 * o['pair_stats']['dt_us']['se']) and close(-dt, -m_main) and dt < 0
            and o['area_verdict_mirror']['pairs'] == 110
            and 'a gain against a different build' in o['must_not_be_claimed'])


def const_check():
    want = {'PRODUCTION_ROOT': 'C:/kyty/s112', 'PRED': 'C:/kyty/s112/pred/02_net112.md',
            'BINARY_SHA': 'b47b58a997b441478ab1d278c992949d79795014370d034b747d5fd4e7b9f7f7',
            'GATES_FILE': 'C:/kyty/s112/gates_base.txt',
            'GATES_SHA': '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf',
            'ARMS': ('dawalk=1 dawalklead=1 daslot=1 daguard=1', 'dawalk=1 dawalklead=1 daslot=0 daguard=0'),
            'SCHEDULE': '90+1800:dawalk=1 dawalklead=1 daslot=1 daguard=1|dawalk=1 dawalklead=1 daslot=0 daguard=0',
            'TAG_RE': r'net112b?(?:_entry1)?', 'KEEP_LO': 10, 'KEEP_HI': 90, 'SECONDARY_LO': 60,
            'SECONDARY_HI': 89}
    bad = sorted(k for k in want if ORIG[k] != want[k])
    # PRED_SHA / PRED_BYTES are never compared with a value (audit111 MINOR-5: the executor fills them when pred/02 is
    # sealed, and the sealed copy must stay green here): both None (the draft) or a sha256 and a size (the sealed copy)
    sha, size = ORIG['PRED_SHA'], ORIG['PRED_BYTES']
    sealed = (isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha) is not None and type(size) is int
              and size > 0)
    if not (sealed or (sha is None and size is None)):
        bad.append('PRED_SHA/PRED_BYTES')
    return None, None, 'CONSTANTS OK' if not bad else 'CONSTANTS DIFFER %s' % bad


# ---- the sealed identity (feeds the fixtures themselves, so no behavioural case can see it) ----------------------
case('CONSTANTS', const_check, 'CONSTANTS OK')

# ---- verdict branches -------------------------------------------------------------------------------------------
case('REVERT', run_eval(good, *video(good, tag='ok')), REVERT)
case('PENDING', run_eval(good), PENDING, check=pred_good)
case('DRAFT', run_eval(good, draft=True), 'DRAFT (no verdict)', check=lambda o: o['status'] == 'DRAFT')
# KEEP by the bar = S1_S2_positive / S2_only / S1_edge / S1_edge_out / SE_exact / EST_rows10_59 / PRED_*; KEEP by a
# failed video = V_*; KEEP not admitted = every admission case

# ---- decision terms ---------------------------------------------------------------------------------------------
# S1 (d mean <= SHIP_US = 0) cannot fail alone BY CONSTRUCTION: S2 (d mean + 2 SE < 0, with SE >= 0) implies d mean < 0.
# A positive d mean fails both (ship_rules() returns the two terms of one dict; both listed).
case('S1_S2_positive', run_eval(make('s1', d_dt=60, noise=80)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: 0 < main_dt(o) < 100 and o['predictions']['N3']['hit'] and not o['predictions']['N4']['hit'])
case('S2_only', run_eval(make('s2', d_dt=-150, noise=300, block_noise=1500)), KEEP_BAR,
     rules=['S2_dt_2se_excludes_0'])
# the bar's edge, noise-free (every pair delta equal, SE 0): d mean dt exactly 0 - S1 holds (<= 0), S2 fails alone
# (0 + 2 * 0 is not < 0; kills S1 strict and a bar moved to -1) ...
case('S1_edge', run_eval(make('s1edge', d_dt=0, noise=0)), KEEP_BAR, rules=['S2_dt_2se_excludes_0'],
     check=lambda o: (main_dt(o) == 0.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                      and pred_values(o, N3=0.0, N4=0.0, hits=['N1', 'N2', 'N3', 'N5', 'N6', 'N7'])))
# ... -0.5 (arm-1 frames with an even number -1 us: 40 of the 80 main-window rows of each block): both hold, REVERT
# pending (kills a bar moved to -1) ...
case('S1_edge_in', run_eval(make('s1edgein', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31000 - 1}}))), PENDING,
    check=lambda o: main_dt(o) == -0.5 and o['pair_stats']['dt_us']['sd'] == 0.0)
# ... and +0.5 (+1 us on those rows): S1 fails with S2 (kills a bar moved to +1)
case('S1_edge_out', run_eval(make('s1edgeout', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and n % 2 == 0, edits={'main': {'dt_us': 31000 + 1}}))), KEEP_BAR,
    rules=BOTH_RULES, check=lambda o: main_dt(o) == 0.5 and o['pair_stats']['dt_us']['sd'] == 0.0)

# ---- the estimator: the main window's edges, the secondary window's edges, and where a hitch sits ----------------
# noise-free: arm 0 31 000, arm 1 30 850.  Arm-1 row 9 (just outside the main window 10..89) +29 000 us, arm-1 rows 10
# and 89 (its first and last row) -8 000 each: main d mean dt = -150 - 16 000 / 80 = -350 exactly (row 9 not in it);
# the secondary window 60..88 holds none of the three: -150 exactly.  KEEP_LO 9 or 11, KEEP_HI 89 and a slice shifted
# down by one row all read another mean.
case('KEEP_edge', run_eval(make('keepedge', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i in (9, 10, 89),
    edits={'main': {'dt_us': lambda n, b, a, i: 30850 + (29000 if i == 9 else -8000)}}))), PENDING,
    check=lambda o: (main_dt(o) == -350.0 and o['pair_stats']['dt_us']['sd'] == 0.0
                     and o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30650.0
                     and o['selection']['pairs'] == 110 and sec_dt(o) == -150.0 and o['secondary']['pairs'] == 110
                     and sec_rules(o) == []))
# noise-free; arm-1 rows 59 and 89 (just outside the secondary window 60..88) +29 000 us, rows 60 and 88 (its first
# and last row) -2 900: secondary -150 - 5 800 / 29 = -350 exactly; main (all four rows inside 10..89) -150 +
# (58 000 - 5 800) / 80 = +502.5 exactly - KEEP by the bar, while the secondary alone would pass S1/S2.
case('SEC_edge', run_eval(make('secedge', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i in (59, 60, 88, 89),
    edits={'main': {'dt_us': lambda n, b, a, i: 30850 + (29000 if i in (59, 89) else -2900)}}))), KEEP_BAR,
    rules=BOTH_RULES,
    check=lambda o: (main_dt(o) == 502.5 and sec_dt(o) == -350.0 and o['secondary']['levels']['dt_us'] == [
        31000.0, 30650.0] and o['levels']['arm1']['dt_us'] == 31502.5 and sec_rules(o) == []
        and o['secondary']['pairs'] == 110 and o['secondary']['blocks'] == 220))
# the audit110 MAJOR-1 hitch shape: every arm-1 block's rows 0..9 carry +29 000 us (a ~60 ms flip each).  Main (10..89)
# and secondary (60..88) both read -150 exactly; a full-block estimator (0..89) would read -150 + 290 000 / 90 =
# +3 072.2 (KEEP).
case('EST_rows0_9', run_eval(make('estrows0', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and i < 10,
    edits={'main': {'dt_us': 30850 + 29000}}))), PENDING,
    check=lambda o: (main_dt(o) == -150.0 and o['pair_stats']['dt_us']['sd'] == 0.0 and sec_dt(o) == -150.0
                     and o['levels']['arm1']['dt_us'] == 30850.0 and o['selection']['pairs'] == 110))
# arm-1 rows 10..59 +800 us (noise-free, d -150): main -150 + 800 * 50 / 80 = +350 exactly - KEEP by the bar; the
# secondary (60..88) reads -150 exactly and would pass S1/S2: the verdict follows the main estimator only.
case('EST_rows10_59', run_eval(make('estrows10', noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 30850 + 800}}))), KEEP_BAR, rules=BOTH_RULES,
    check=lambda o: (main_dt(o) == 350.0 and sec_dt(o) == -150.0 and sec_rules(o) == []
                     and pred_values(o, N3=350.0, N4=350.0, hits=['N1', 'N2', 'N4', 'N5', 'N6', 'N7'])))
# the other direction: d 0, arm-1 rows 10..59 -400 us: main -250 exactly (REVERT pending); the secondary reads 0
# exactly: it would pass S1 (0 <= 0) and FAIL S2 (0 + 2 * 0 is not < 0).
case('EST_rows10_59_rev', run_eval(make('estrows10s', d_dt=0, noise=0, row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None and 10 <= i < 60,
    edits={'main': {'dt_us': 31000 - 400}}))), PENDING,
    check=lambda o: (main_dt(o) == -250.0 and sec_dt(o) == 0.0 and sec_rules(o) == ['S2_dt_2se_excludes_0']
                     and '  secondary would FAIL S2_dt_2se_excludes_0 (not deciding)' in mod.summary(o).split(NL)
                     and '  secondary would PASS S1_dt_le_0 (not deciding)' in mod.summary(o).split(NL)))

# ---- audit-109 survivor SE_pstdev: the pair SE is the SAMPLE SD / sqrt(n) ------------------------------------------
# noise-free; arm-1 blocks 31 000 - 150 +- 867 (+ when blk // 4 is even).  Paired quartets 1..55 (blocks 0-3 lie
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
# noise-free; block 12 (arm 0) and block 9 (arm 1) +2 900 us on every row, block 16 (arm 0) da_q_free 50 000, block 17
# (arm 1) da_q_noguard 50 000, block 21 (arm 1) da_queue_us 20 000: medians 31 000 / 30 850 / 1 080 / 1 080 / 1 080
# exactly (means: 31 026.4 / 30 876.4 / 1 524.7 / 1 524.7 / 1 251.6 - N6, N5 and N1 would miss); the two dt outliers
# sit in different pairs with opposite signs, so d mean dt stays -150.
case('LEVEL_median', run_eval(make('levmed', noise=0, row=both(
    setter(pick=lambda n, b, a, i: i is not None and b in (9, 12),
           edits={'main': {'dt_us': lambda n, b, a, i: 31000 - 150 * a + 2900}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 16, edits={'x': {'da_q_free': 50000}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 17, edits={'x': {'da_q_noguard': 50000}}),
    setter(pick=lambda n, b, a, i: i is not None and b == 21, edits={'draw': {'da_queue_us': 20000}})))), PENDING,
    check=lambda o: (o['levels']['arm0']['dt_us'] == 31000.0 and o['levels']['arm1']['dt_us'] == 30850.0
                     and o['levels']['arm0']['da_q_free'] == 1080.0 and o['levels']['arm1']['da_q_noguard'] == 1080.0
                     and o['levels']['arm1']['da_queue_us'] == 1080.0 and main_dt(o) == -150.0
                     and pred_values(o, N1=1080 / 1080, N5=1080.0, N6=1080.0, hits=['N1', 'N2', 'N5', 'N6', 'N7'])))

# ---- the reported, never deciding d cpu_net_us (audit-108 survivor 2) -------------------------------------------
# cpu_gpu_us noise-free, arm-1 spin_gpu_us 80 against 30: d cpu_net = d cpu_gpu - d spin = -150 - 50 = -200 exactly;
# with spin dropped from derived() it would read -150.  The verdict does not move (no term reads it: `cpu` is bound in
# evaluate() and never read; ship_rules() reads dt only; BANDS are dt/rec_n/gpu_busy; its other uses are PAIR_KEYS,
# levels, the secondary's levels and the summary).
case('CPU_NET_spin', run_eval(make('cpunet', spin1=80, cpu_noise=0)), PENDING,
     check=lambda o: (o['pair_stats']['cpu_net_us']['mean'] == -200.0
                      and o['pair_stats']['spin_gpu_us']['mean'] == 50.0
                      and o['levels']['arm0']['cpu_net_us'] == 29970.0
                      and o['levels']['arm1']['cpu_net_us'] == 29770.0
                      and o['secondary']['pair_stats']['cpu_net_us']['mean'] == -200.0
                      and '  d cpu_net_us   mean -200.0  2SE None  t -inf  n 110' in mod.summary(o).split(NL)
                      and '  secondary d cpu_net_us   mean -200.0  2SE None  t -inf  n 110'
                      in mod.summary(o).split(NL)))

# ---- predictions N1-N7 (report only: the verdict never reads them) ------------------------------------------------
# Every band exactly at, inside and just outside each edge, noise-free.  da_qcall is 1 000 in the edge fixtures, so the
# walker ratios land on the band literals exactly (900 / 1 000 is the double nearest 0.9, 1 120 / 1 000 the one nearest
# 1.12).  The good run (a REVERT) is inside N1, N2 and N5-N7; PRED_inside is the predicted run, inside all seven.
case('PRED_inside', run_eval(make('predin', d_dt=150, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: (pred_values(o, N1=1080 / 1080, N2=1296 / 1080, N3=150.0, N4=150.0, N5=1080.0, N6=1080.0,
                                  N7=0.0, hits=list(PRED_BANDS)) and gain_exact(o, -150.0, 0.0)))
# on the lower edges: N1 0.90, N2 1.00, N3 0 (S2 fails alone), N5 800, N6 800, N7 -40 - all hit but N4
case('PRED_edges_lo', run_eval(make('prededgelo', d_dt=0, noise=0, qcall=1000, qq1=900, qq0=1000, ng1=800,
                                    qfree0=800, row=setter(pick=lambda n, b, a, i: a == 1,
                                                           edits={'draw': {'da_miss': 260}}))),
     KEEP_BAR, rules=['S2_dt_2se_excludes_0'],
     check=lambda o: pred_values(o, N1=900 / 1000, N2=1000 / 1000, N3=0.0, N4=0.0, N5=800.0, N6=800.0, N7=-40.0,
                                 hits=['N1', 'N2', 'N3', 'N5', 'N6', 'N7']))
# just below them: 0.89, 0.99, d -1 (a REVERT pending), 799, 799, -41 - all miss
case('PRED_misses_lo', run_eval(make('predmisslo', d_dt=-1, noise=0, qcall=1000, qq1=890, qq0=990, ng1=799,
                                     qfree0=799, row=setter(pick=lambda n, b, a, i: a == 1,
                                                            edits={'draw': {'da_miss': 259}}))),
     PENDING, check=lambda o: pred_values(o, N1=890 / 1000, N2=990 / 1000, N3=-1.0, N4=-1.0, N5=799.0, N6=799.0,
                                          N7=-41.0, hits=[]))
# on the upper edges: N1 1.12, N2 1.30, N3 +300, N5 1 400, N6 1 400, N7 +40 - all hit (N4 too)
case('PRED_edges_hi', run_eval(make('prededgehi', d_dt=300, noise=0, qcall=1000, qq1=1120, qq0=1300, ng1=1400,
                                    qfree0=1400, row=setter(pick=lambda n, b, a, i: a == 1,
                                                            edits={'draw': {'da_miss': 340}}))),
     KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N1=1120 / 1000, N2=1300 / 1000, N3=300.0, N4=300.0, N5=1400.0, N6=1400.0,
                                 N7=40.0, hits=list(PRED_BANDS)))
# just above them: 1.13, 1.31, +301, 1 401, 1 401, +41 - all miss but N4
case('PRED_misses_hi', run_eval(make('predmisshi', d_dt=301, noise=0, qcall=1000, qq1=1130, qq0=1310, ng1=1401,
                                     qfree0=1401, row=setter(pick=lambda n, b, a, i: a == 1,
                                                             edits={'draw': {'da_miss': 341}}))),
     KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N1=1130 / 1000, N2=1310 / 1000, N3=301.0, N4=301.0, N5=1401.0, N6=1401.0,
                                 N7=41.0, hits=['N4']))
# N4's only bound: d mean +100 hits, +99 misses (N3 hits both)
case('PRED_N4_edge', run_eval(make('predn4', d_dt=100, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N3=100.0, N4=100.0, hits=list(PRED_BANDS)))
case('PRED_N4_out', run_eval(make('predn4out', d_dt=99, noise=0)), KEEP_BAR, rules=BOTH_RULES,
     check=lambda o: pred_values(o, N3=99.0, N4=99.0, hits=['N1', 'N2', 'N3', 'N5', 'N6', 'N7']))

# ---- video checks, each alone (all nine; sub-conditions of the gate text and of one_ok_attempt too) -------------
case('V_frames', run_eval(good, *video(good, frames=2000, tag='fr')), KEEP_VID, vfail=['frames'])
# the frame floor's edge: exactly 3 000 frames pass, 2 999 fail
case('V_frames_3000', run_eval(good, *video(good, frames=3000, tag='f3')), REVERT)
case('V_frames_2999', run_eval(good, *video(good, frames=2999, tag='f2')), KEEP_VID, vfail=['frames'])
case('V_glitch', run_eval(good, *video(good, glitches=1, tag='gl')), KEEP_VID, vfail=['no_glitch'])
# the gate text: today's default (the arm-0 text) instead of the candidate, then each of the three names alone missing
case('V_gate', run_eval(good, *video(good, gate='daslot=1 daguard=1', tag='gt')), KEEP_VID,
     vfail=['daguard_0_in_gate_text'])
case('V_gate_daslot', run_eval(good, *video(good, gate='daguard=0', tag='gs')), KEEP_VID,
     vfail=['daguard_0_in_gate_text'])
case('V_gate_daguard', run_eval(good, *video(good, gate='daslot=0', tag='gc')), KEEP_VID,
     vfail=['daguard_0_in_gate_text'])
case('V_gate_dawalk', run_eval(good, *video(good, gates=gates_text.replace('dawalk=1', 'dawalk=0'), tag='gd')),
     KEEP_VID, vfail=['daguard_0_in_gate_text'])
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
# video paths given but the files missing: read_video reads ABSENT, not FAIL -> pending
case('V_missing', run_eval(good, str(good / 'no_such_vnet112.json'), str(good / 'no_such_glitch.txt')), PENDING,
     check=lambda o: o['video']['state'] == 'ABSENT')

# ---- integrity terms, each alone --------------------------------------------------------------------------------
# INPUTS is coupled with 'protocol' BY CONSTRUCTION: the missing input is written into out['errors'] (evaluate()) and
# finish() appends 'protocol' whenever out['errors'] is non-empty.
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
# the session-109 / -110 counters stay in the schema ...
case('SCHEMA_free', run_eval(make('schemafree', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                           edits={'x': {'cspfree_moved': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o: o['schema_missing_fields'] == ['cspfree_moved'])
case('SCHEMA_new_us', run_eval(make('schemanewus', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                              edits={'x': {'cs_sync_new_us': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o: o['schema_missing_fields'] == ['cs_sync_new_us'])
case('SCHEMA_wait_us', run_eval(make('schemawaitus', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                edits={'x': {'cs_sync_wait_us': None}}))),
     KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o: o['schema_missing_fields'] == ['cs_sync_wait_us'])
# ... and the b47b58a9 build's ten daslot / daguard counters (session 111's eight, session 112's two), each alone
for key in NEW_COUNTERS:
    case('SCHEMA_%s' % key, run_eval(make('schema_%s' % key, row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                         edits={'x': {key: None}}))),
         KEEP_NA, fails={'integrity:SCHEMA'}, check=lambda o, key=key: o['schema_missing_fields'] == [key])
case('FIELD_ORIGIN', run_eval(make('origin', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                        edits={'draw': {'mw_n': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'})
case('FIELD_ORIGIN_us', run_eval(make('originus', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                             edits={'draw': {'cs_sync_wait_us': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},
     check=lambda o: o['field_origin_defects'] == {'cs_sync_wait_us': ['draw', 'x']})
case('FIELD_ORIGIN_slot', run_eval(make('originslot', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                 edits={'main': {'da_q_free': 0}}))),
     KEEP_NA, fails={'integrity:FIELD_ORIGIN'},
     check=lambda o: o['field_origin_defects'] == {'da_q_free': ['main', 'x']})
case('RAW_CONTIG', run_eval(make('contig', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                      edits={'main': None, 'draw': None, 'x': None}))),
     KEEP_NA, fails={'integrity:RAW_CONTIGUITY'})
# 140 blocks: 68 pairs (PAIRS holds) but 12 701 rows x ~31 ms = ~394 s < hold_s 600
case('DURATION', run_eval(make('duration', blocks=140)), KEEP_NA, fails={'integrity:DURATION'},
     check=lambda o: o['selection']['pairs'] >= 60)
# GATEARM, every clause of the GateArm check alone
case('GATEARM', run_eval(make('gatearm', arm_text='dawalk=1 daslot=9')), KEEP_NA, fails={'integrity:GATEARM'})
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
# no GateArm line at all: ok_gate = bool([]) cannot fail alone BY CONSTRUCTION - with no arms select() pairs nothing,
# so PAIRS / AB_BA_BALANCED fail and the early return fails the rest
case('GATEARM_none', run_eval(make('gatenone', gate=lambda b, g: None)), KEEP_NA,
     fails={'integrity:GATEARM', 'control:PAIRS', 'integrity:AB_BA_BALANCED', 'control:BANDS',
            'control:WORK_SPLIT', 'control:AREA_VERDICT', 'control:AREA_SELECTED', 'control:ARMING'},
     check=lambda o: o['gate_blocks'] == 0 and 'SYNC_COMPILE' not in o['controls'] and 'secondary' not in o)
for key in ('bf_n', 'bf_disp', 'bf_skip', 'bf_clr_skip', 'bf_skip_drop'):
    case('NO_FLOOR_%s' % key, run_eval(make('floor_%s' % key, row=setter(pick=lambda n, b, a, i: n == 1750,
                                                                        edits={'x': {key: 1}}))),
         KEEP_NA, fails={'integrity:NO_FLOOR'})
case('MARKERS_OFF', run_eval(make('gmops', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                      edits={'x': {'gm_ops': 1}}))),
     KEEP_NA, fails={'integrity:MARKERS_OFF'})
case('NO_RECORDING', run_eval(variant(good, 'recording', append=['Recording: C:/kyty/s112/rec_net112.mp4 960x540'])),
     KEEP_NA, fails={'integrity:NO_RECORDING'})
# frame 1850 (> start 1800, block 0 - never paired) lacks its FrameTrace-x line
case('STREAMS', run_eval(make('streams', row=setter(pick=lambda n, b, a, i: n == 1850, edits={'x': None}))),
     KEEP_NA, fails={'integrity:STREAMS_COMPLETE'})
# a kept row of block 5 (arm 1) reports blk=6 (also arm 1): only the row/block agreement breaks
case('ROW_ARMS', run_eval(make('rowarms', row=setter(pick=lambda n, b, a, i: b == 5 and i == 60,
                                                     edits={'main': {'blk': 6}}))),
     KEEP_NA, fails={'integrity:ROW_ARMS'})
# AB_BA_BALANCED cannot fail alone BY CONSTRUCTION: GATEARM pins arms[i] = (0,1,1,0)[i%4]; select() pairs only whole
# quartets as (b,b+1),(b+2,b+3), so each quartet adds one pair of each orientation and orient[0] > 0 needs one pair,
# implied by PAIRS (MIN_PAIRS 60).  It fails only with GATEARM (here: an ABAB schedule, with abba=0 and with abba=1) or
# with PAIRS (NO_PAIRS below).
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
# CsStall lines (still printed by the build) and DaSlotVerify lines (knob 2 only) are not markers: in the log and in
# stdout, still pending
STALLS = ['CsStall: kind=new us=12345 id=9 hash=0x5323000000000000', 'CsStall: kind=wait us=800 id=9 hash=0x1',
          'DaSlotVerify: MISMATCH slot=12 fingerprint=0x0000000000000001']
case('CSSTALL_not_marker', run_eval(variant(good, 'csstall', append=STALLS, stdout=STALLS)), PENDING,
     check=lambda o: o['markers']['fatal'] == {} and o['markers']['hang'] == 0)
# ENV_NO_CHECKPOINTS is coupled with 'protocol' BY CONSTRUCTION: KYTY_GPU_CHECKPOINTS is a KYTY_* variable outside
# ENV_EXPECTED / ENV_PRESENT, so protocol_errors() flags it whenever the control fails.
case('ENV_CKPT', run_eval(make('envc', extra_env={'KYTY_GPU_CHECKPOINTS': '1'})), KEEP_NA,
     fails={'control:ENV_NO_CHECKPOINTS', 'protocol'}, errors=['env carries KYTY_* variables outside'])
# 100 blocks (48 pairs) with a 100-frame pre-schedule prefix of 3.5 s frames: ~628 s, so DURATION holds
case('PAIRS', run_eval(make('pairs1', blocks=100, pre_dt=3500000)), KEEP_NA, fails={'control:PAIRS'},
     check=lambda o: o['selection']['pairs'] == 48)
# PAIRS and DURATION together (the session-108 first draft's case, kept)
case('PAIRS_DUR', run_eval(make('pairs', blocks=100)), KEEP_NA, fails={'control:PAIRS', 'integrity:DURATION'})
# no pair at all (4 blocks, all before frame 2100 in the main window): the early return fails BANDS/WORK_SPLIT/AREA_*/
# ARMING by construction and never evaluates SYNC_COMPILE or the secondary
case('NO_PAIRS', run_eval(make('nopairs', blocks=4, pre_dt=6500000)), KEEP_NA,
     fails={'control:PAIRS', 'integrity:AB_BA_BALANCED', 'control:BANDS', 'control:WORK_SPLIT',
            'control:AREA_VERDICT', 'control:AREA_SELECTED', 'control:ARMING'},
     check=lambda o: 'SYNC_COMPILE' not in o['controls'] and 'secondary' not in o)
case('BANDS', run_eval(make('bands', dt_base=45000)), KEEP_NA, fails={'control:BANDS'})
case('BANDS_rec1', run_eval(make('bandsrec', row=setter(pick=lambda n, b, a, i: a == 1,
                                                        edits={'draw': {'rec_n': 14000}}))),
     KEEP_NA, fails={'control:BANDS'})
case('BANDS_gpu0', run_eval(make('bandsgpu', row=setter(pick=lambda n, b, a, i: a == 0,
                                                        edits={'main': {'gpu_busy_us': 17000}}))),
     KEEP_NA, fails={'control:BANDS'})
# work split alone: arm-1 rows 10..89 (the main window) +30 draws, rows 0..9 -240 -> selected work +0.6 %, the
# whole-arm mirror work exactly 0 (80 * 30 = 10 * 240)
case('WORK_SPLIT', run_eval(make('workonly', row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None,
    edits={'main': {'draws': lambda n, b, a, i: 5030 if i in MAIN else 4760}}))),
    KEEP_NA, fails={'control:WORK_SPLIT'}, mirror=[],
    check=lambda o: abs(o['work_split']['work'] - 0.006) < 1e-12)
# area verdict alone, split+match criteria: arm-1 rows 0..9 (outside the main window) +12 % area (mirror split and
# every block pair +1.33 %; the main-window rows equal)
case('AREA_VERDICT', run_eval(make('avsplit', row=setter(pick=lambda n, b, a, i: a == 1 and out_main(i),
                                                         edits={'x': {'rt_kpx': 225792}}))),
     KEEP_NA, fails={'control:AREA_VERDICT'}, mirror=['match', 'split'])
# area verdict alone, work criterion: arm-1 rows 0..9 +6 % draws (mirror work +0.67 %; selected work 0)
case('AREA_V_work', run_eval(make('avwork', row=setter(pick=lambda n, b, a, i: a == 1 and out_main(i),
                                                       edits={'main': {'draws': 5300}}))),
     KEEP_NA, fails={'control:AREA_VERDICT'}, mirror=['work'])
# area selected alone: arm-1 main-window rows +1.2 % area, rows 0..9 -9.6 % (selected split 1.2 %; every whole
# block -0.0001 %, so the mirror splits nothing and matches every pair)
case('AREA_SELECTED', run_eval(make('asel', row=setter(
    pick=lambda n, b, a, i: a == 1 and i is not None,
    edits={'x': {'rt_kpx': lambda n, b, a, i: 204019 if i in MAIN else 182246}}))),
    KEEP_NA, fails={'control:AREA_SELECTED'}, mirror=[])
# uniform shifts fail both (the session-108 first draft's cases, kept)
case('WORK', run_eval(make('work', draws1=5100)), KEEP_NA, fails={'control:WORK_SPLIT', 'control:AREA_VERDICT'},
     mirror=['work'])
case('AREA', run_eval(make('area', kpx1=206000)), KEEP_NA,
     fails={'control:AREA_SELECTED', 'control:AREA_VERDICT'}, mirror=['match', 'split'])


def relabel(k):
    """row hook: rows 0..k-1 of block 8 (arm 0) and block 9 (arm 1) - outside every estimator window - report blk 998
    and 999."""
    return setter(pick=lambda n, b, a, i: b in (8, 9) and i is not None and i < k,
                  edits={'main': {'blk': lambda n, b, a, i: 990 + b}})


# the area mirror's minimum block size (AREA_MIN_FLIPS 8): the relabelled rows form one more consecutive two-arm block
# pair (998 arm 0, 999 arm 1); with 8 flips each it counts (111 pairs, all matched) ...
case('AREA_min_flips', run_eval(make('amin8', row=relabel(8))), PENDING,
     check=lambda o: (o['area_verdict_mirror']['pairs'] == 111 and o['area_verdict_mirror']['matched'] == 111
                      and o['area_verdict_mirror']['valid'] is True))
# ... with 7 flips each it does not (110, as in the good run)
case('AREA_min_flips_below', run_eval(make('amin7', row=relabel(7))), PENDING,
     check=lambda o: (o['area_verdict_mirror']['pairs'] == 110 and o['area_verdict_mirror']['matched'] == 110
                      and o['area_verdict_mirror']['valid'] is True))
case('SYNC', run_eval(make('sync', sync0=1, sync1=4)), KEEP_NA, fails={'control:SYNC_COMPILE'},
     check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 4})
case('SYNC_edge', run_eval(make('syncedge', sync0=1, sync1=3)), PENDING,
     check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 3})
# the guard reads ALL rows from frame 2100, not the estimator's: three more arm-1 compiles at row 5 (outside the main
# window) of blocks 21, 22 and 25 -> {0: 1, 1: 4}, fails (the main-window rows alone would read {0: 1, 1: 1})
case('SYNC_unkept', run_eval(make('syncunkept', row=setter(
    pick=lambda n, b, a, i: b in (21, 22, 25) and i == 5,
    edits={'x': {'cs_sync_new': 1, 'cs_sync_new_us': STALL_US}}))), KEEP_NA, fails={'control:SYNC_COMPILE'},
    check=lambda o: o['sync_compile']['cs_sync_new'] == {0: 1, 1: 4})

# ---- arming sub-checks, each alone (control:ARMING + the exact failing sub-check) --------------------------------
# SLOT_ARMED_ARM0: today's default arm queues under m_mutex (da_qcall still 1 080: the knob, not the call count; N6
# misses) ...
case('SLOT_ARMED0', run_eval(make('sarmed0', qfree0=0)), KEEP_NA, fails=ARMING, arming=['SLOT_ARMED_ARM0'],
     check=lambda o: o['levels']['arm0']['da_qcall'] == 1080.0 and o['levels']['arm0']['da_q_free'] == 0.0)
# ... on every third row only: level ~0.33 < 1 ...
case('SLOT_ARMED0_sparse', run_eval(make('sarmed0s', row=setter(
    pick=lambda n, b, a, i: a == 0, edits={'x': {'da_q_free': lambda n, b, a, i: 1 if n % 3 == 0 else 0}}))),
    KEEP_NA, fails=ARMING, arming=['SLOT_ARMED_ARM0'])
# ... only outside the main window (rows 0..9 of the arm-0 blocks): the level reads the main window only
case('SLOT_ARMED0_lag', run_eval(make('sarmed0lag', row=setter(
    pick=lambda n, b, a, i: a == 0 and i is not None,
    edits={'x': {'da_q_free': lambda n, b, a, i: 0 if i in MAIN else 1080}}))),
    KEEP_NA, fails=ARMING, arming=['SLOT_ARMED_ARM0'], check=lambda o: o['levels']['arm0']['da_q_free'] == 0.0)
# SLOT_DARK_ARM1: the candidate arm with calls off m_mutex on every main-window row (5 a flip) ...
case('SLOT_DARK1', run_eval(make('sdark1', qfree1=5)), KEEP_NA, fails=ARMING, arming=['SLOT_DARK_ARM1'],
     check=lambda o: o['arming']['slot_arm1_kept']['da_q_free'] == 5 * 80 * 110)
# ... on ONE main-window row of block 5 (arm 1), value 1: a kept total of 1 fails - no tolerance (the good run's 0
# passes) ...
case('SLOT_DARK1_one', run_eval(make('sdark1one', row=setter(pick=lambda n, b, a, i: b == 5 and i == 50,
                                                             edits={'x': {'da_q_free': 1}}))),
     KEEP_NA, fails=ARMING, arming=['SLOT_DARK_ARM1'],
     check=lambda o: o['arming']['slot_arm1_kept']['da_q_free'] == 1)
# ... but not rows 0..9 of an arm-1 block (the counters of the flips that straddle the arm change): pending
case('SLOT_DARK1_lag', run_eval(make('sdark1lag', row=setter(
    pick=lambda n, b, a, i: a == 1 and out_main(i), edits={'x': {'da_q_free': 400}}))), PENDING,
    check=lambda o: o['arming']['slot_arm1_kept']['da_q_free'] == 0 and o['levels']['arm1']['da_q_free'] == 0.0)
# NOGUARD_ARMED_ARM1: the candidate arm queues with the guards (da_qcall still 1 080; N5 misses) ...
case('NOGUARD_ARMED1', run_eval(make('ngarmed1', ng1=0)), KEEP_NA, fails=ARMING, arming=['NOGUARD_ARMED_ARM1'],
     check=lambda o: o['levels']['arm1']['da_qcall'] == 1080.0 and o['levels']['arm1']['da_q_noguard'] == 0.0)
# ... on every third row only: level ~0.33 < 1 ...
case('NOGUARD_ARMED1_sparse', run_eval(make('ngarmed1s', row=setter(
    pick=lambda n, b, a, i: a == 1, edits={'x': {'da_q_noguard': lambda n, b, a, i: 1 if n % 3 == 0 else 0}}))),
    KEEP_NA, fails=ARMING, arming=['NOGUARD_ARMED_ARM1'])
# ... only outside the main window (rows 0..9 of the arm-1 blocks): the level reads the main window only
case('NOGUARD_ARMED1_lag', run_eval(make('ngarmed1lag', row=setter(
    pick=lambda n, b, a, i: a == 1,
    edits={'x': {'da_q_noguard': lambda n, b, a, i: 0 if i in MAIN else 1080}}))),
    KEEP_NA, fails=ARMING, arming=['NOGUARD_ARMED_ARM1'], check=lambda o: o['levels']['arm1']['da_q_noguard'] == 0.0)
# NOGUARD_DARK_ARM0: today's arm skipping the guards on every main-window row (5 a flip) ...
case('NOGUARD_DARK0', run_eval(make('ngdark0', ng0=5)), KEEP_NA, fails=ARMING, arming=['NOGUARD_DARK_ARM0'],
     check=lambda o: o['arming']['noguard_arm0_kept']['da_q_noguard'] == 5 * 80 * 110)
# ... on ONE main-window row of block 4 (arm 0), value 1: a kept total of 1 fails - no tolerance ...
case('NOGUARD_DARK0_one', run_eval(make('ngdark0one', row=setter(pick=lambda n, b, a, i: b == 4 and i == 50,
                                                                 edits={'x': {'da_q_noguard': 1}}))),
     KEEP_NA, fails=ARMING, arming=['NOGUARD_DARK_ARM0'],
     check=lambda o: o['arming']['noguard_arm0_kept']['da_q_noguard'] == 1)
# ... but not rows 0..9 of an arm-0 block: pending
case('NOGUARD_DARK0_lag', run_eval(make('ngdark0lag', row=setter(
    pick=lambda n, b, a, i: a == 0 and out_main(i), edits={'x': {'da_q_noguard': 400}}))), PENDING,
    check=lambda o: (o['arming']['noguard_arm0_kept']['da_q_noguard'] == 0
                     and o['levels']['arm0']['da_q_noguard'] == 0.0))
# the level edges: arm-0 da_q_free 1, arm-1 da_q_noguard 1, cspfree_hit 1 in both arms - every arming check holds (N5
# and N6 miss)
case('ARMED_edge', run_eval(make('armededge', qfree0=1, ng1=1, hit0=1, hit1=1)), PENDING,
     check=lambda o: (o['levels']['arm0']['da_q_free'] == 1.0 and o['levels']['arm1']['da_q_noguard'] == 1.0
                      and o['arming']['cspfree_hit_levels'] == [1.0, 1.0]
                      and pred_values(o, N5=1.0, N6=1.0, hits=['N1', 'N2', 'N7'])))
# SLOT_NO_BAD: one knob-2 slot-key disagreement on a pre-schedule row (outside every kept block: the check reads ALL
# rows) ...
case('SLOT_NO_BAD', run_eval(make('snobad', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                       edits={'x': {'da_slot_bad': 1}}))),
     KEEP_NA, fails=ARMING, arming=['SLOT_NO_BAD'], check=lambda o: o['arming']['da_slot_bad_all_rows'] == 1)
# ... and on a kept arm-1 row
case('SLOT_NO_BAD_kept', run_eval(make('snobadk', row=setter(pick=lambda n, b, a, i: b == 5 and i == 70,
                                                             edits={'x': {'da_slot_bad': 2}}))),
     KEEP_NA, fails=ARMING, arming=['SLOT_NO_BAD'], check=lambda o: o['arming']['da_slot_bad_all_rows'] == 2)
# DEFAULTS_ON: cspfree off in arm 0 (no lookup, no hit) ...
case('DEFAULTS_arm0', run_eval(make('defarm0', look0=0, hit0=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
     check=lambda o: o['arming']['cspfree_hit_levels'] == [0.0, 262.0])
# ... arm 0 looking up but never hitting (the check reads hits, not lookups) ...
case('DEFAULTS_arm0_look', run_eval(make('defarm0l', hit0=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
     check=lambda o: o['levels']['arm0']['cspfree_look'] == 266.0)
# ... arm 1 looking up but never hitting ...
case('DEFAULTS_arm1', run_eval(make('defarm1', hit1=0)), KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'],
     check=lambda o: o['arming']['cspfree_hit_levels'] == [262.0, 0.0])
# ... a knob-2 cspfree disagreement on a pre-schedule row (ALL rows are read) ...
case('DEFAULTS_bad', run_eval(make('defbad', row=setter(pick=lambda n, b, a, i: n == 1750,
                                                        edits={'x': {'cspfree_bad': 1}}))),
     KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o: o['arming']['cspfree_bad_all_rows'] == 1)
# ... and on a kept arm-0 row
case('DEFAULTS_bad_kept', run_eval(make('defbadk', row=setter(pick=lambda n, b, a, i: b == 4 and i == 70,
                                                              edits={'x': {'cspfree_bad': 3}}))),
     KEEP_NA, fails=ARMING, arming=['DEFAULTS_ON'], check=lambda o: o['arming']['cspfree_bad_all_rows'] == 3)
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
# the walk identity's tolerance (1 %): kept skips 0.9 % above jobs + drops pass (both arms) ...
case('WALK_IDENT_edge_in', run_eval(make('widentin', row=setter(
    pick=lambda n, b, a, i: True, edits={'x': {'da_wjobs': 1000, 'da_wskip': 1009}}))), PENDING,
    check=lambda o: abs(o['arming']['skip_over_posts_rel'] - 0.009) < 1e-12)
# ... 1.1 % above fail (arm 1 alone)
case('WALK_IDENT_edge_out', run_eval(make('widentout', row=setter(
    pick=lambda n, b, a, i: a == 1, edits={'x': {'da_wjobs': 1000, 'da_wskip': 1011}}))),
    KEEP_NA, fails=ARMING, arming=['WALK_IDENTITY_ARM1'],
    check=lambda o: abs(o['arming']['skip_over_posts_rel'] - 0.011) < 1e-12)
# INSTRUMENTS_DARK, every key: one kept row, arm 0 (block 4) for even keys, arm 1 (block 5) for odd ones
for j, key in enumerate(('mw_n', 'a_hold_us', 'a_mut_us', 'pl_em_n', 'pl_proc_n', 'sh_jobs')):
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
# the schedule variable is both a value check and a presence check: two errors, one term
case('P_absent_schedule', run_eval(variant(good, 'p_nosched', env_set('KYTY_GATE_SCHEDULE', None))), KEEP_NA,
     fails={'protocol'}, errors=['env KYTY_GATE_SCHEDULE=None', 'env KYTY_GATE_SCHEDULE absent'])
case('ENV_EXTRA', run_eval(make('envx', extra_env={'KYTY_SOMETHING_ELSE': '1'})), KEEP_NA, fails={'protocol'},
     errors=['env carries KYTY_* variables outside'])
alt_gates = BASE / 'gates_base_alt.txt'   # same normalised text (a trailing space), different sha256
alt_gates.write_bytes(gates_copy.read_bytes() + b' ')
case('P_gates_sha', run_eval(variant(good, 'p_gsha'), gates_file=str(alt_gates)), KEEP_NA, fails={'protocol'},
     errors=['gates_base.txt sha256 '])
case('P_gates_text', run_eval(variant(good, 'p_gtext', meta_set(gates=gates_text + ' daslot=1'))), KEEP_NA,
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
# the attempt's hold tolerance (HOLD_S - 5 = 595 s): 595 passes, 594 fails
case('P_att_hold_edge', run_eval(variant(good, 'p_ahold595', meta_set(attempts=[dict(ATT, hold_s=595)]))), PENDING)
case('P_att_hold_out', run_eval(variant(good, 'p_ahold594', meta_set(attempts=[dict(ATT, hold_s=594)]))), KEEP_NA,
     fails={'protocol'}, errors=['hold_s 594 below 595'])
# meta hold_s 590 (not 600): DURATION compares with it and still holds (~627 s), only protocol fails
case('P_meta_hold_s', run_eval(variant(good, 'p_mhold', meta_set(hold_s=590))), KEEP_NA, fails={'protocol'},
     errors=['meta hold_s 590'])

# ---- IDENTITY and the exits of main() ---------------------------------------------------------------------------
fake_exe = BASE / 'fake_kyty_emulator.exe'
fake_exe.write_bytes(b'not the b47b58a9 build')
fake_sha = hashlib.sha256(fake_exe.read_bytes()).hexdigest()
main_ok = variant(good, 'main_ok', meta_set(binary_sha256=fake_sha))
ROOT = {'PRODUCTION_ROOT': good.as_posix()}
# control: installed exe == meta binary == BINARY_SHA (all three the fixture exe) -> admitted through main()
case('MAIN_OK', run_main([TAG, '--root', str(main_ok)], PRODUCTION_ROOT=main_ok.as_posix(),
                         BINARY_SHA=fake_sha, EXE=str(fake_exe)),
     PENDING, rc=0, check=lambda o: o['integrity']['IDENTITY'] is True and o['installed_exe_sha256'] == fake_sha)
# In main() BINARY_SEALED cannot fail alone BY CONSTRUCTION: IDENTITY also requires the meta binary to equal
# BINARY_SHA, which BINARY_SEALED checks.  Here the installed exe and the meta agree on another build.  (BINARY above
# fails it alone through evaluate(), which is main() with a matching installed exe - see MAIN_OK.)
case('BINARY_main', run_main([TAG, '--root', str(main_ok)], PRODUCTION_ROOT=main_ok.as_posix(),
                             EXE=str(fake_exe)),
     KEEP_NA, fails={'integrity:BINARY_SEALED', 'integrity:IDENTITY'}, rc=1)
case('IDENTITY', run_main([TAG, '--root', str(good)], EXE=str(fake_exe), **ROOT), KEEP_NA,
     fails={'integrity:IDENTITY'}, rc=1, check=lambda o: o['installed_exe_sha256'] == fake_sha)
case('IDENTITY_noexe', run_main([TAG, '--root', str(good)], EXE=str(BASE / 'no_such.exe'), **ROOT), KEEP_NA,
     fails={'integrity:IDENTITY'}, rc=1, check=lambda o: o['installed_exe_sha256'] is None)
case('REFUSE_seal', run_main([TAG, '--root', str(good)], PRED_SHA='0' * 64, EXE=str(fake_exe), **ROOT),
     'SEALED PRE-REGISTRATION CHANGED', rc=2)
# the generated scorer ships with PRED_SHA = None: it must refuse until the executor pins pred/02 (full message)
case('REFUSE_unsealed', run_main([TAG, '--root', str(good)], PRED_SHA=None, PRED_BYTES=None, EXE=str(fake_exe),
                                 **ROOT),
     'PRED_SHA / PRED_BYTES are not filled: seal %s and put its sha256 and size into net112.py (only --draft runs '
     'without a seal): refusing to score' % mod.PRED, rc=2)
case('REFUSE_root', run_main([TAG, '--root', str(good)], EXE=str(fake_exe)), 'production root must be', rc=2)
# the tag pattern: net112 with the optional b and _entry1 reaches evaluate() (no files under that tag here: INPUTS,
# protocol and IDENTITY fail, rc 1 - not the refusal's rc 2) ...
for t in ('net112b', 'net112_entry1', 'net112b_entry1'):
    case('TAG_ok_%s' % t, run_main([t, '--root', str(good)], EXE=str(fake_exe), **ROOT), KEEP_NA,
         fails={'integrity:INPUTS', 'integrity:IDENTITY', 'protocol'}, errors=['missing input: ', 'missing input: '],
         rc=1, check=lambda o, t=t: o['tag'] == t)
# ... and every other tag is refused with the full message, session 111's tags and the video tags included
for t in ('net113', 'net111', 'shp111', 'shp111b', 'shp111_entry1', 'vnet112', 'vss111', 'net112c', 'xnet112'):
    case('REFUSE_tag_%s' % t, run_main([t, '--root', str(good)], EXE=str(fake_exe), **ROOT), TAG_MSG % t, rc=2)
GEOM_MSG = '--period/--start/--first/--keep/--secondary are --draft only'
case('REFUSE_geom', run_main([TAG, '--root', str(good), '--period', '60'], EXE=str(fake_exe), **ROOT), GEOM_MSG, rc=2)
case('REFUSE_geom_keep', run_main([TAG, '--root', str(good), '--keep', '0:90'], EXE=str(fake_exe), **ROOT), GEOM_MSG,
     rc=2)
case('REFUSE_geom_secondary', run_main([TAG, '--root', str(good), '--secondary', '0:90'], EXE=str(fake_exe),
                                       **ROOT), GEOM_MSG, rc=2)
# in --draft the secondary window is a geometry like the others: it reaches evaluate() and the secondary estimator
case('DRAFT_secondary', run_main([TAG, '--root', str(good), '--draft', '--secondary', '50:80'], EXE=str(fake_exe),
                                 **ROOT), 'DRAFT (no verdict)', rc=0,
     check=lambda o: (o['status'] == 'DRAFT' and o['geometry']['secondary'] == [50, 80]
                      and o['secondary']['window'] == [50, 80] and o['secondary']['pairs'] == 110
                      and o['geometry']['keep'] == [10, 90]))
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
    if c['name'] in ('PENDING', 'S2_only', 'S1_edge', 'S1_edge_in', 'S1_edge_out', 'SE_exact', 'KEEP_edge',
                     'SEC_edge', 'EST_rows0_9', 'EST_rows10_59', 'EST_rows10_59_rev', 'LEVEL_median'):
        st = ((out or {}).get('pair_stats') or {}).get('dt_us') or {}
        s2 = (((out or {}).get('secondary') or {}).get('pair_stats') or {}).get('dt_us') or {}
        print('   %s case: main d mean dt %s se %s | secondary d mean dt %s se %s%s'
              % (c['name'], st.get('mean'), st.get('se'), s2.get('mean'), s2.get('se'),
                 (' (sample SE wanted %s, population %s)' % (SE_SAMPLE, SE_POP)) if c['name'] == 'SE_exact' else ''))
    if c['name'] == 'LEVEL_median':
        lv = (out or {}).get('levels') or {}
        print('   LEVEL case: dt arm0 %s arm1 %s, da_q_free arm0 %s, da_q_noguard arm1 %s, da_queue_us arm1 %s'
              % ((lv.get('arm0') or {}).get('dt_us'), (lv.get('arm1') or {}).get('dt_us'),
                 (lv.get('arm0') or {}).get('da_q_free'), (lv.get('arm1') or {}).get('da_q_noguard'),
                 (lv.get('arm1') or {}).get('da_queue_us')))
    if c['name'] == 'CPU_NET_spin':
        st = ((out or {}).get('pair_stats') or {}).get('cpu_net_us') or {}
        print('   CPU_NET case: d cpu_net_us mean %s (d cpu_gpu -150, d spin +50)' % st.get('mean'))
    print('%-26s want %-34s got %-40s %s  failed=%s %s%s' % (c['name'], c['want'][:34], got[:40],
                                                            'OK' if passed else 'FAIL', sorted(fails), ' '.join(extra),
                                                            ('  PROBLEMS ' + '; '.join(problems)) if problems else ''))
print('%d cases' % len(cases))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)

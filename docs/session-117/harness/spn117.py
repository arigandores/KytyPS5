"""Session 117, ROADMAP §0.1 "СЕССИЯ 117 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 4-6 (route A stage 4 part 1; design
docs/session-117/designA4_spine.md) - DRAFT, NOT SEALED (pre-registration pred/01_spn117.md; fixtures test_spn117.py;
mutants mut_spn117.py; chain go117a.sh).

spn117 is an OBSERVATION of the shadow spine (knob "spine", measurement only): one Sky Garden entry on the installed
build BUILD_SHA, 300-s hold, pinned (KYTY_GPU_CLOCK_PIN=1), KYTY_GPU_MARKERS=0, no recording, gates gates_base.txt
(which does not name "spine"), schedule KYTY_GATE_SCHEDULE="90+1800:spine=1|spine=2" with KYTY_GATE_SCHEDULE_ABBA=1:
arm 0 plans every submission (spine=1), arm 1 plans and verifies (spine=2).  Verdicts K5 (the spine reproduces the
register state at every draw/dispatch) and K1 (its price on the GuestGpu thread), then the consequence of item 4.

Admission (every check must hold, else NOT_ADMITTED):
  binary / installed_now  TAG.json binary_sha256 and the installed exe are BUILD_SHA
  pinned                  env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, and it is mode 1
  env_exact               the KYTY_* part of env is exactly ENV_EXPECT (lite, pin, markers 0, the schedule, ABBA, the
                          s117 gate file; hence no KYTY_REC, no checkpoints, no GPU wall, no GC shift, no GPU time ...)
  env_vk                  of the VK_* part of env only VK_ALLOWED (VK_SDK_PATH) may appear
  hold                    TAG.json hold_s == HOLD_S
  one_ok_attempt          exactly one attempt, outcome ok, hold_exit None
  prereg / prereg_sha     TAG.json prereg.path is PRED_PATH and its sha256 (read before the emulator starts) equals the
                          sha256 of PRED_PATH now
  gates_exact             the whitespace-normalised gate text hashes to GATES_SHA (gates_base.txt, which has no
                          `spine=` token: the schedule owns the knob)
  gate_lines              every `Gate:` line of the log is `Gate: spine=V frame=F` with F the start frame of a block
                          (START + PERIOD * b) and V = 1 + the arm of block b (the schedule's own flips; nothing else
                          moves a gate or knob during the run)
  arms                    every `GateArm:` line parses; arms=2, period=PERIOD, abba=1; arm 0 text is exactly
                          ARM_TEXT[0], arm 1 text exactly ARM_TEXT[1]; block b starts at frame START + PERIOD * b; the
                          arm of block b is ABBA[b % 4]; blocks are consecutive from 0
  spine_logged            exactly one `Spine: mode=` line
  no_marker               no failure marker (MARKERS, as obs116) in the log or in stdout_TAG.txt
  blocks                  >= MIN_BLOCKS complete blocks of each arm (every frame of the block has one FrameTrace and
                          one FrameTrace-x line with every field used, the FrameTrace line carries arm = the block's arm
                          and blk = the block); the estimator keeps frames KEEP[0]..KEEP[1]-1 of each block
  armed                   over the kept frames: arm 0 sum spine_n > 0, sum spine_el > 0, 100 * sum spine_cmp <= sum
                          spine_el (a mode-2 submission blocked past a flip may still compare - ROADMAP 117 item 11);
                          arm 1 sum spine_cmp > 0
  el_ops                  over the kept frames of arm 1: spine_el / (draws + dispatches) in [EL_OPS_LO_PCT,
                          EL_OPS_HI_PCT] % (the K5 denominator is not the spine's own count taken blind)
  idle                    pre_run.gpu_util_median <= IDLE_GPU_MAX

K5 (reproduction), over EVERY FrameTrace-x line with n > START (both arms, block edges, duplicated lines and frames
missing other lines included: each submission latches its own mode, so a compare can only come from a mode-2 plan):
  FAIL            sum spine_bad > 0 or sum spine_misal > 0 or sum cram_write > 0 (const RAM is outside the compare), or
                  any `SpineMismatch:` / `SpineMisalign:` line anywhere in the log
  PASS            both 0 and cmp_ratio = sum spine_cmp / sum spine_el over arm-1 kept frames >= CMP_MIN_PCT / 100
  NOT_EVALUABLE   both 0 but cmp_ratio below the bar (aborted plans or lost compares left too little compared)
K1 (price): k1_us = mean over arm-0 kept frames of spine_ns / 1000 (us a frame; spine_ns excludes snapshot time).
  PASS  k1_us <= K1_MAX_US;  FAIL otherwise, and then walker_fit = mean over arm-0 kept frames of
        (da_walk_us + spine_ns / 1000) < mean of (dt_us - spine_ns / 1000) over the same frames: the walker thread
        could carry the spine within the frame the GuestGpu thread would have without it (ROADMAP 117 item 11).
Consequence (item 4): K5 FAIL -> STOP_STAGE4; K5 NOT_EVALUABLE -> NOT_EVALUABLE (one repeat, tag spn117r);
  K5 PASS and K1 PASS -> PART2; K5 PASS and K1 FAIL and walker_fit -> PART2_WALKER; K5 PASS and K1 FAIL and not
  walker_fit -> CLOSE_A.

Report (no verdict): per arm over kept frames the means of dt_us, cpu_gpu_us, draws, dispatches, every spine_* field
(ns fields also in us), da_walk_us; spine_el / (draws + dispatches); spine_pk per spine_n; the sums over all frames of
spine_bad, spine_misal, spine_pad, spine_lost, spine_abort, cram_write (complete frames, and every x line for K5);
the first SpineMismatch / SpineMisalign / SpineAbort lines.  spine_misal = the real element count of a submission
differs from its plan; spine_lost = compares lost because another plan of the same processor replaced the snapshots
(an instrument limit, caught by the cmp ratio, not a failure) - ROADMAP 117 item 11 (3).

    python C:/kyty/s117/spn117.py [--root C:/kyty/s117] [--tag spn117|spn117r] [--out <json>]
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = 'C:/kyty/s117'
TAG = 'spn117'
TAGS = ('spn117', 'spn117r')
BUILD_SHA = '3cde1af8ed1af960a2216957288c6d9f54e606fd7c3e48bd97659b052a9c64b9'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
HOLD_S = 300
PERIOD = 90
START = 1800
KEEP = (10, 90)
ABBA = (0, 1, 1, 0)
ARM_TEXT = ('spine=1', 'spine=2')
MIN_BLOCKS = 20
CMP_MIN_PCT = 90
K1_MAX_US = 1200
EL_OPS_LO_PCT = 95
EL_OPS_HI_PCT = 105
IDLE_GPU_MAX = 10
GATES_SHA = '91da50f6d85b99d09fe4198da1438f5766a0773112268302efa62c0d1ba09c5e'
PRED_PATH = 'C:/kyty/s117/pred/01_spn117.md'
NL = chr(10)
SCHEDULE = '90+1800:spine=1|spine=2'
ENV_EXPECT = {
    'KYTY_FRAME_TRACE': 'lite',
    'KYTY_GPU_HANG_ABORT_S': '8',
    'KYTY_GATE_FILE': 'C:\\kyty\\s117\\gates.req',
    'KYTY_SAMPLE_GATE': 'C:\\kyty\\s117\\sample.req',
    'KYTY_QUEUE_TRACE': '1',
    'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',
    'KYTY_GPU_CLOCK_PIN': '1',
    'KYTY_GPU_MARKERS': '0',
    'KYTY_GATE_SCHEDULE': SCHEDULE,
    'KYTY_GATE_SCHEDULE_ABBA': '1',
}
VK_ALLOWED = ('VK_SDK_PATH',)
MARKERS = (b'gpuhangabort', b'gpuwaitslow', b'gpumarkerhung', b'gpucheckpointhang', b'errordevicelost',
           b'std::terminate', b'abort()', b'fatal', b'unhandled exception', b'--- error ---',
           b'asyncpipelines: skipped draw')

MAIN_FIELDS = ('dt_us', 'cpu_gpu_us', 'draws', 'dispatches', 'arm', 'blk')
DRAW_FIELDS = ('da_walk_us',)
X_FIELDS = ('spine_n', 'spine_ns', 'spine_pk', 'spine_el', 'spine_ib', 'spine_cf_br', 'spine_cf_cond', 'spine_cf_pred',
            'spine_cf_predw', 'spine_cf_ind', 'spine_abort', 'spine_cmp', 'spine_bad', 'spine_misal', 'spine_pad',
            'spine_lost', 'spine_chk_ns', 'cram_write')
REPORT_KEYS = ('dt_us', 'cpu_gpu_us', 'draws', 'dispatches', 'da_walk_us') + X_FIELDS + ('spine_us', 'spine_chk_us')
ALL_SUMS = ('spine_bad', 'spine_misal', 'spine_pad', 'spine_lost', 'spine_abort', 'spine_cmp', 'spine_el', 'spine_n',
            'cram_write')
K5_RAW = ('spine_bad', 'spine_misal', 'cram_write')

LINE_MAIN = re.compile(rb'^FrameTrace: n=(\d+)')
LINE_DRAW = re.compile(rb'^FrameTrace-draw: n=(\d+)')
LINE_X = re.compile(rb'^FrameTrace-x: n=(\d+)')
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
KINDS = ((LINE_MAIN, 'main', MAIN_FIELDS), (LINE_DRAW, 'draw', DRAW_FIELDS), (LINE_X, 'x', X_FIELDS))
DIAG = (b'SpineMismatch:', b'SpineMisalign:', b'SpineAbort:')
K5_LINES = (b'SpineMismatch:', b'SpineMisalign:')


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


def row_values(m, dr, x):
    v = {k: float(m[k]) for k in MAIN_FIELDS}
    v['da_walk_us'] = float(dr['da_walk_us'])
    v.update((k, float(x[k])) for k in X_FIELDS)
    v['spine_us'] = v['spine_ns'] / 1000.0
    v['spine_chk_us'] = v['spine_chk_ns'] / 1000.0
    return v


def mean(col):
    return sum(col) / len(col) if col else None


def arms_ok(gate_arms):
    """(ok, blocks): blocks maps block -> arm when every GateArm line is well-formed and ABBA-ordered."""
    blocks = {}
    for g in gate_arms:
        if g is None:
            return False, {}
        arm, arms, block, frame, period, abba, text = g
        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1) or text != ARM_TEXT[arm]:
            return False, {}
        if frame != START + PERIOD * block or ABBA[block % 4] != arm or block in blocks:
            return False, {}
        blocks[block] = arm
    ok = bool(blocks) and sorted(blocks) == list(range(len(blocks)))
    return ok, blocks


def gate_lines_ok(lines, blocks):
    """Every Gate: line is the schedule's own flip of spine at a block start, with the value of that block's arm."""
    for raw in lines:
        m = GATE.match(raw)
        if m is None or m.group(1) != b'spine':
            return False
        frame = int(m.group(3))
        if (frame - START) % PERIOD != 0 or frame < START:
            return False
        block = (frame - START) // PERIOD
        if block not in blocks or int(m.group(2)) != 1 + blocks[block]:
            return False
    return True


def evaluate(root=ROOT, tag=TAG, installed_sha=None, min_blocks=None, pred_sha=None):
    """ADMITTED checks, then K5/K1 and the consequence; the report is computed either way (a NOT_ADMITTED report is
    not to be quoted).  installed_sha / pred_sha: None = hash the installed exe / PRED_PATH."""
    min_blocks = MIN_BLOCKS if min_blocks is None else min_blocks
    res = dict(scorer_sha256=sha_file(__file__), build_sha256=BUILD_SHA, tag=tag)
    meta = json.loads((Path(root) / (tag + '.json')).read_text(encoding='utf-8'))
    env = meta.get('env') or {}
    kyty_env = {k: v for k, v in env.items() if k.startswith('KYTY_')}
    vk_env = sorted(k for k in env if k.startswith('VK_'))
    atts = meta.get('attempts') or []
    ok_att = [a for a in atts if a.get('outcome') == 'ok' and a.get('hold_exit') is None]
    gates = ' '.join((meta.get('gates') or '').split())
    prereg = meta.get('prereg') or {}
    prereg_path = str(prereg.get('path') or '')
    pins, gate_arms, spine_lines, spine_gate_lines, markers, diag = [], [], [], [], [], []
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    raw_k5 = {k: 0 for k in K5_RAW}
    k5_lines = 0
    with open(Path(root) / ('log_%s.txt' % tag), 'rb') as f:
        for line in f:
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
            if line.startswith(b'GpuClockPin:'):
                mp = PIN.match(line)
                pins.append(int(mp.group(1)) if mp else -1)
            if line.startswith(b'GateArm:'):
                mg = GATE_ARM.match(line.rstrip(b'\r\n'))
                gate_arms.append(None if mg is None else tuple(int(x) for x in mg.groups()[:6])
                                 + (mg.group(7).decode('utf-8', 'replace').strip(),))
            if line.startswith(b'Spine: mode='):
                spine_lines.append(line.rstrip())
            if line.startswith(b'Gate: '):
                spine_gate_lines.append(line.rstrip())
            if line.startswith(DIAG) and len(diag) < 20:
                diag.append(line[:200].decode('utf-8', 'replace').strip())
            if line.startswith(K5_LINES):
                k5_lines += 1
            if not line.startswith(b'FrameTrace'):
                continue
            for regex, kind, names in KINDS:
                m = regex.match(line)
                if m is None:
                    continue
                n = int(m.group(1))
                got = dict(FIELD.findall(line, m.end()))
                rec = {k: int(got[k.encode()]) for k in names if k.encode() in got}
                if kind == 'x' and n > START:
                    for k in K5_RAW:
                        raw_k5[k] += int(got.get(k.encode(), 0))
                if n in seen[kind]:
                    dups.add(n)
                seen[kind][n] = rec if len(rec) == len(names) else None
                break
    so = Path(root) / ('stdout_%s.txt' % tag)
    if so.is_file():
        for line in open(so, 'rb'):
            if is_marker(line):
                markers.append(line[:200].decode('utf-8', 'replace').strip())
    arms_fine, blocks = arms_ok(gate_arms)
    first_frame = START if blocks else None

    def complete(n):
        return n not in dups and all(seen[k].get(n) is not None for k in seen)

    kept = {0: [], 1: []}
    complete_blocks = {0: 0, 1: 0}
    for b, arm in sorted(blocks.items()):
        frames = list(range(START + 1 + PERIOD * b, START + 1 + PERIOD * (b + 1)))
        if not all(complete(n) and seen['main'][n]['arm'] == arm and seen['main'][n]['blk'] == b for n in frames):
            continue
        complete_blocks[arm] += 1
        kept[arm].extend(frames[KEEP[0]:KEEP[1]])
    values = {arm: [row_values(seen['main'][n], seen['draw'][n], seen['x'][n]) for n in kept[arm]] for arm in (0, 1)}
    all_frames = sorted(n for n in seen['x'] if first_frame is not None and n > first_frame and complete(n))
    sums_all = {k: sum(seen['x'][n][k] for n in all_frames) for k in ALL_SUMS}

    def ksum(arm, key):
        return sum(v[key] for v in values[arm])

    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if pred_sha is None:
        pred_sha = sha_file(PRED_PATH) if Path(PRED_PATH).is_file() else None
    ops1 = ksum(1, 'draws') + ksum(1, 'dispatches')
    checks = dict(
        binary=meta.get('binary_sha256') == BUILD_SHA,
        installed_now=installed_sha == BUILD_SHA,
        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and pins == [1],
        env_exact=kyty_env == ENV_EXPECT,
        env_vk=all(k in VK_ALLOWED for k in vk_env),
        hold=meta.get('hold_s') == HOLD_S,
        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,
        prereg=prereg_path.replace('\\', '/') == PRED_PATH,
        prereg_sha=pred_sha is not None and prereg.get('sha256') == pred_sha,
        gates_exact=hashlib.sha256(gates.encode('utf-8')).hexdigest() == GATES_SHA,
        gate_lines=gate_lines_ok(spine_gate_lines, blocks),
        arms=arms_fine,
        spine_logged=len(spine_lines) == 1,
        no_marker=not markers,
        blocks=complete_blocks[0] >= min_blocks and complete_blocks[1] >= min_blocks,
        armed=(ksum(0, 'spine_n') > 0 and ksum(0, 'spine_el') > 0 and 100 * ksum(0, 'spine_cmp') <= ksum(0, 'spine_el')
               and ksum(1, 'spine_cmp') > 0),
        el_ops=(ops1 > 0 and 100 * ksum(1, 'spine_el') >= EL_OPS_LO_PCT * ops1
                and 100 * ksum(1, 'spine_el') <= EL_OPS_HI_PCT * ops1),
        idle=idle_ok(meta))
    admitted = all(checks.values())
    cmp_el = ksum(1, 'spine_el')
    cmp_ratio = ksum(1, 'spine_cmp') / cmp_el if cmp_el else None
    if raw_k5['spine_bad'] > 0 or raw_k5['spine_misal'] > 0 or raw_k5['cram_write'] > 0 or k5_lines > 0:
        k5 = 'FAIL'
    elif cmp_ratio is not None and 100 * ksum(1, 'spine_cmp') >= CMP_MIN_PCT * cmp_el:
        k5 = 'PASS'
    else:
        k5 = 'NOT_EVALUABLE'
    k1_us = mean([v['spine_us'] for v in values[0]])
    k1 = 'PASS' if k1_us is not None and k1_us <= K1_MAX_US else 'FAIL'
    walker_need = mean([v['da_walk_us'] + v['spine_us'] for v in values[0]])
    dt0 = mean([v['dt_us'] for v in values[0]])
    frame_nospine = mean([v['dt_us'] - v['spine_us'] for v in values[0]])
    walker_fit = walker_need is not None and frame_nospine is not None and walker_need < frame_nospine
    if k5 == 'FAIL':
        consequence = 'STOP_STAGE4'
    elif k5 == 'NOT_EVALUABLE':
        consequence = 'NOT_EVALUABLE'
    elif k1 == 'PASS':
        consequence = 'PART2'
    elif walker_fit:
        consequence = 'PART2_WALKER'
    else:
        consequence = 'CLOSE_A'
    report = {}
    for arm in (0, 1):
        report[arm] = {k: mean([v[k] for v in values[arm]]) for k in REPORT_KEYS}
        ops = ksum(arm, 'draws') + ksum(arm, 'dispatches')
        report[arm]['el_over_ops'] = ksum(arm, 'spine_el') / ops if ops else None
        report[arm]['pk_per_plan'] = ksum(arm, 'spine_pk') / ksum(arm, 'spine_n') if ksum(arm, 'spine_n') else None
        report[arm]['kept_frames'] = len(values[arm])
        report[arm]['complete_blocks'] = complete_blocks[arm]
    res.update(checks=checks, verdict='ADMITTED' if admitted else 'NOT_ADMITTED', k5=k5, k1=k1, k1_us=k1_us,
               cmp_ratio=cmp_ratio, walker_need_us=walker_need, dt0_us=dt0, frame_nospine_us=frame_nospine,
               walker_fit=walker_fit, raw_k5=raw_k5, k5_lines=k5_lines,
               consequence=consequence if admitted else 'NOT_ADMITTED', sums_all=sums_all,
               all_frames=len(all_frames), report=report, pins=pins, spine_lines=[s.decode('utf-8', 'replace')
                                                                                   for s in spine_lines],
               gate_arms=len(gate_arms), markers=markers[:10], diag=diag, vk_env=vk_env,
               prereg_sha256=prereg.get('sha256'), pred_sha256_now=pred_sha)
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    if isinstance(x, bool):
        return str(x)
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    out = ['spn117 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16])]
    for k, v in res['checks'].items():
        out.append('  %-16s %s' % (k, 'ok' if v else 'FAIL'))
    if res['verdict'] != 'ADMITTED':
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    out.append('K5 %s: every x line after %d: %s, SpineMismatch/Misalign lines %d; complete frames (%d): %s; '
               'cmp_ratio (arm 1 kept) %s (bar %d %%)'
               % (res['k5'], START, ', '.join('%s=%d' % kv for kv in res['raw_k5'].items()), res['k5_lines'],
                  res['all_frames'], ', '.join('%s=%d' % kv for kv in res['sums_all'].items()),
                  fmt(res['cmp_ratio'], 4), CMP_MIN_PCT))
    out.append('K1 %s: spine %s us a frame (arm 0 kept; bar %d); walker need %s us vs the frame without the spine %s us '
               '(dt %s) -> walker_fit %s'
               % (res['k1'], fmt(res['k1_us']), K1_MAX_US, fmt(res['walker_need_us']), fmt(res['frame_nospine_us']),
                  fmt(res['dt0_us']), res['walker_fit']))
    for arm in (0, 1):
        r = res['report'][arm]
        out.append('  arm %d (%s): %d kept frames in %d blocks; ' % (arm, ARM_TEXT[arm], r['kept_frames'],
                                                                  r['complete_blocks'])
                   + ', '.join('%s=%s' % (k, fmt(r[k], 2)) for k in REPORT_KEYS + ('el_over_ops', 'pk_per_plan')))
    for d in res['diag']:
        out.append('  diag ' + d)
    out.append('VERDICT: %s  CONSEQUENCE: %s' % (res['verdict'], res['consequence']))
    return out


def main():
    root = sys.argv[sys.argv.index('--root') + 1] if '--root' in sys.argv else ROOT
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else TAG
    if tag not in TAGS:
        print('unknown tag %s (expected one of %s)' % (tag, ', '.join(TAGS)))
        return 2
    res = evaluate(root, tag)
    print(NL.join(format_report(res)))
    if '--out' in sys.argv:
        Path(sys.argv[sys.argv.index('--out') + 1]).write_bytes(json.dumps(res, indent=1).encode('utf-8'))
    return 0 if res['verdict'] == 'ADMITTED' else 1


if __name__ == '__main__':
    sys.exit(main())

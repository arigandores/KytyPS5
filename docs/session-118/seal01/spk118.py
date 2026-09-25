"""Session 118, ROADMAP §0.1 "СЕССИЯ 118 — ЗАПИСИ ДО ДЕЙСТВИЙ" items 1-3 (route A stage 4 part 2; design
docs/session-118/designA4_part2.md). Pre-registration pred/01_spk118.md; fixtures test_spk118.py; mutants mut_spk118.py;
chain go118a.sh.

spk118 is an OBSERVATION: one Sky Garden entry on the build BUILD_SHA, 300-s hold, pinned (KYTY_GPU_CLOCK_PIN=1),
KYTY_GPU_MARKERS=0, no recording, gates gates_base.txt, schedule SCHEDULE with KYTY_GATE_SCHEDULE_ABBA=1: arm P (0) runs
the part-2 instruments (spine=2 with the carry and the safe plan, gate slicecen), arm M (1) re-measures the micro-track
candidates (takelap, bindlap, pathlap, mutsite).  Verdicts K5, C, K4 (with K3 as a bound) and the consequence of
ROADMAP 118 item 2; arm M is a report only.

Admission (every check must hold, else NOT_ADMITTED):
  binary / installed_now  TAG.json binary_sha256 and the installed exe are BUILD_SHA
  pinned                  env KYTY_GPU_CLOCK_PIN == '1' and exactly one `GpuClockPin:` line, and it is mode 1
  env_exact               the KYTY_* part of env is exactly ENV_EXPECT
  env_vk                  of the VK_* part of env only VK_ALLOWED may appear
  hold                    TAG.json hold_s == HOLD_S
  one_ok_attempt          exactly one attempt, outcome ok, hold_exit None
  prereg / prereg_sha     TAG.json prereg.path is PRED_PATH and its sha256 equals the sha256 of PRED_PATH now
  gates_exact             the whitespace-normalised gate text hashes to GATES_SHA (gates_base.txt)
  gate_lines              every `Gate:` line is `Gate: NAME=V frame=F` with NAME one of the schedule's names, F the start
                          frame of a block (START + PERIOD * b) and V the value the arm of block b gives NAME
  arms                    every `GateArm:` line parses; arms=2, period=PERIOD, abba=1; arm texts exactly ARM_TEXT; block b
                          at frame START + PERIOD * b; arm of block b = ABBA[b % 4]; blocks consecutive from 0
  spine_logged            exactly one `Spine: mode=` line
  no_marker               no failure marker (MARKERS) in the log or in stdout_TAG.txt
  blocks                  >= MIN_BLOCKS complete blocks of each arm (every frame has one FrameTrace, one FrameTrace-draw
                          and one FrameTrace-x line with every field used, the FrameTrace line carries arm = the block's arm
                          and blk = the block); the estimator keeps frames KEEP[0]..KEEP[1]-1 of each block (10..88)
  armed                   kept frames: arm P sum spine_n, sc_frames, carry_cmp all > 0 and da_t_n == 0; arm M sum
                          da_t_n, bl_stage_n, pl_em_n, mh_draws all > 0, sc_frames == 0, and 100 * its spine_n <= arm P's
  el_ops                  arm P kept frames: spine_el / (draws + dispatches) in [EL_OPS_LO_PCT, EL_OPS_HI_PCT] %
  idle                    pre_run.gpu_util_median <= IDLE_GPU_MAX

Verdicts (arm P):
  K5  over EVERY FrameTrace-x line with n > START: FAIL if sum spine_bad, spine_misal or cram_write > 0, or any
      `SpineMismatch:` / `SpineMisalign:` line; else PASS if spine_cmp >= CMP_MIN_PCT % of spine_el over arm-P kept
      frames; else NOT_EVALUABLE.
  C   (carry) over every x line with n > START: FAIL if sum carry_bad > 0 or any `SpineCarry:` line; else PASS if
      carry_cmp >= CMP_MIN_PCT % of (spine_n - carry_skip) over arm-P kept frames; else NOT_EVALUABLE.
  safe  100 * (spine_unc + spine_abort) <= SAFE_MAX_PCT * spine_n over arm-P kept frames, else K5 and C become
      NOT_EVALUABLE (unless FAIL).
  K3  median over arm-P kept frames with sc_frames == 1 of k3_max / sc_el: >= K3_SHARE_PERMILLE / 1000 => W_MAX 4, else 8
      (a bound, never a closure).
  K4  at W = 2 and at W = 4: median of k4_wW_dep over arm-P kept frames with sc_frames == 1 and k4_wW_n == 1 (at least
      K4_MIN_PCT % of the kept frames must qualify, else NOT_EVALUABLE): <= K4_DEP_MAX_PERMILLE => PASS, else FAIL.
Consequence: K5 or C FAIL => STOP_STAGE4; else K5, C or K4 at W = 2 NOT_EVALUABLE => NOT_EVALUABLE (one repeat,
  spk118r); else K4 W = 2 FAIL => CLOSE_A; K4 W = 2 PASS and W = 4 FAIL or NOT_EVALUABLE => W2_CEILING; all PASS => STAGE3.

K4 is evaluable only when >= K4_MIN_PCT % of the arm-P kept frames carry exactly one finished frame (sc_frames == 1) and
k4_wW_n == 1; FAIL of K5 or C is stronger than the safe-plan condition (ROADMAP 118 item 4, rule m5).

Report: per arm means over kept frames of REPORT_KEYS (ns fields also in us); the K3/K4 medians and p90; arm M's candidate
levels; the diagnostic lines.  Report only (ROADMAP 118 item 4, M1 and m1): at W = 2 and 4 the share of the qualifying
frames whose dep is above the bar and the median per arm-P block; carry_skip as a share of the plans.

    python C:/kyty/s118/spk118.py [--root C:/kyty/s118] [--tag spk118|spk118r] [--out <json>]
"""
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = 'C:/kyty/s118'
TAG = 'spk118'
TAGS = ('spk118', 'spk118r')
BUILD_SHA = '321175ab43ebba1664b03d307cb09e61782505a4f9628196c2f089414babcf76'
INSTALLED = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/kyty_emulator.exe'
HOLD_S = 300
PERIOD = 90
START = 1800
KEEP = (10, 89)
ABBA = (0, 1, 1, 0)
ARM_TEXT = ('spine=2 slicecen=1 takelap=0 bindlap=0 pathlap=0 mutsite=0',
            'spine=0 slicecen=0 takelap=1 bindlap=1 pathlap=1 mutsite=1')
MIN_BLOCKS = 20
CMP_MIN_PCT = 90
SAFE_MAX_PCT = 10
EL_OPS_LO_PCT = 95
EL_OPS_HI_PCT = 105
K3_SHARE_PERMILLE = 250
K4_DEP_MAX_PERMILLE = 300
K4_MIN_PCT = 50
IDLE_GPU_MAX = 10
GATES_SHA = '91da50f6d85b99d09fe4198da1438f5766a0773112268302efa62c0d1ba09c5e'
PRED_PATH = 'C:/kyty/s118/pred/01_spk118.md'
NL = chr(10)
SCHEDULE = '90+1800:' + ARM_TEXT[0] + '|' + ARM_TEXT[1]
ENV_EXPECT = {
    'KYTY_FRAME_TRACE': 'lite',
    'KYTY_GPU_HANG_ABORT_S': '8',
    'KYTY_GATE_FILE': 'C:\\kyty\\s118\\gates.req',
    'KYTY_SAMPLE_GATE': 'C:\\kyty\\s118\\sample.req',
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
DRAW_FIELDS = ('da_take_us', 'bda_scan')
X_FIELDS = ('spine_n', 'spine_ns', 'spine_el', 'spine_abort', 'spine_cmp', 'spine_bad', 'spine_misal', 'spine_unc',
            'carry_cmp', 'carry_bad', 'carry_skip', 'cram_write', 'sc_frames', 'sc_el', 'sc_runs', 'k3_max',
            'k4_w2_n', 'k4_w2_any', 'k4_w2_dep', 'k4_w2_fmax', 'k4_w4_n', 'k4_w4_any', 'k4_w4_dep', 'k4_w4_fmax',
            'k4_nocut', 'sc_ns',
            'da_t_n', 'da_t_key_us', 'da_t_prb_us', 'da_t_pfa_us', 'da_t_pfb_us', 'da_t_ver_us', 'da_t_cpy_us',
            'bl_stage_n', 'bl_prep_us', 'bl_img_us', 'bl_buf_us', 'bl_res_us', 'bl_smp_us', 'bl_sd_us', 'bl_tr_us',
            'bl_wr_us', 'bl_em_us',
            'mh_pro_us', 'mh_rt_us', 'mh_prog_us', 'mh_bind_us', 'mh_emit_us', 'mh_tail_us', 'mh_disp_us', 'mh_draws',
            'pl_em_vtx_ns', 'pl_em_rt_ns', 'pl_em_pipe_ns', 'pl_em_com_ns', 'pl_em_rec_ns', 'pl_em_rest_ns',
            'pl_em_n')
KINDS = ((re.compile(rb'^FrameTrace: n=(\d+)'), 'main', MAIN_FIELDS),
         (re.compile(rb'^FrameTrace-draw: n=(\d+)'), 'draw', DRAW_FIELDS),
         (re.compile(rb'^FrameTrace-x: n=(\d+)'), 'x', X_FIELDS))
FIELD = re.compile(rb' (\w+)=(-?\d+)')
PIN = re.compile(rb'^GpuClockPin: mode (\d+)')
GATE = re.compile(rb'^Gate: (\w+)=(\d+) frame=(\d+)$')
GATE_ARM = re.compile(rb'^GateArm: arm=(\d+) arms=(\d+) block=(\d+) frame=(\d+) period=(\d+) abba=(\d+) text=(.*)$')
K5_RAW = ('spine_bad', 'spine_misal', 'cram_write')
C_RAW = ('carry_bad',)
K5_LINES = (b'SpineMismatch:', b'SpineMisalign:')
C_LINES = (b'SpineCarry:',)
DIAG = (b'SpineMismatch:', b'SpineMisalign:', b'SpineAbort:', b'SpineUncertain:', b'SpineCarry:')
REPORT_KEYS = ('dt_us', 'cpu_gpu_us', 'draws', 'dispatches', 'bda_scan', 'da_take_us') + X_FIELDS


def arm_values(text):
    return dict(pair.split('=') for pair in text.split())


ARM_VALUES = tuple(arm_values(t) for t in ARM_TEXT)


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_marker(line):
    low = line.lower()
    return any(k in low for k in MARKERS)


def idle_ok(meta):
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


def mean(col):
    return sum(col) / len(col) if col else None


def median(col):
    return statistics.median(col) if col else None


def p90(col):
    if not col:
        return None
    s = sorted(col)
    return s[min(len(s) - 1, int(0.9 * len(s)))]


def arms_ok(gate_arms):
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
    for raw in lines:
        m = GATE.match(raw)
        if m is None:
            return False
        name = m.group(1).decode()
        frame = int(m.group(3))
        if name not in ARM_VALUES[0] or (frame - START) % PERIOD != 0 or frame < START:
            return False
        block = (frame - START) // PERIOD
        if block not in blocks or m.group(2).decode() != ARM_VALUES[blocks[block]][name]:
            return False
    return True


def evaluate(root=ROOT, tag=TAG, installed_sha=None, min_blocks=None, pred_sha=None):
    """Admission, the verdicts and the consequence; the report is computed either way (a NOT_ADMITTED report is not
    to be quoted).  installed_sha / pred_sha: None = hash the installed exe / PRED_PATH."""
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
    pins, gate_arms, spine_lines, gate_lines, markers, diag = [], [], [], [], [], []
    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    raw = {k: 0 for k in K5_RAW + C_RAW}
    k5_lines = 0
    c_lines = 0
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
                gate_lines.append(line.rstrip())
            if line.startswith(DIAG) and len(diag) < 20:
                diag.append(line[:200].decode('utf-8', 'replace').strip())
            if line.startswith(K5_LINES):
                k5_lines += 1
            if line.startswith(C_LINES):
                c_lines += 1
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
                    for k in raw:
                        raw[k] += int(got.get(k.encode(), 0))
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
    values = {arm: [dict(seen['main'][n], **seen['draw'][n], **seen['x'][n]) for n in kept[arm]] for arm in (0, 1)}

    def ksum(arm, key):
        return sum(v[key] for v in values[arm])

    if installed_sha is None:
        installed_sha = sha_file(INSTALLED) if Path(INSTALLED).is_file() else None
    if pred_sha is None:
        pred_sha = sha_file(PRED_PATH) if Path(PRED_PATH).is_file() else None
    ops_p = ksum(0, 'draws') + ksum(0, 'dispatches')
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
        gate_lines=gate_lines_ok(gate_lines, blocks),
        arms=arms_fine,
        spine_logged=len(spine_lines) == 1,
        no_marker=not markers,
        blocks=complete_blocks[0] >= min_blocks and complete_blocks[1] >= min_blocks,
        armed=(ksum(0, 'spine_n') > 0 and ksum(0, 'sc_frames') > 0 and ksum(0, 'carry_cmp') > 0
               and ksum(0, 'da_t_n') == 0 and ksum(1, 'da_t_n') > 0 and ksum(1, 'bl_stage_n') > 0
               and ksum(1, 'pl_em_n') > 0 and ksum(1, 'mh_draws') > 0 and ksum(1, 'sc_frames') == 0
               and 100 * ksum(1, 'spine_n') <= ksum(0, 'spine_n')),
        el_ops=(ops_p > 0 and 100 * ksum(0, 'spine_el') >= EL_OPS_LO_PCT * ops_p
                and 100 * ksum(0, 'spine_el') <= EL_OPS_HI_PCT * ops_p),
        idle=idle_ok(meta))
    admitted = all(checks.values())

    plans = ksum(0, 'spine_n')
    safe = plans > 0 and 100 * (ksum(0, 'spine_unc') + ksum(0, 'spine_abort')) <= SAFE_MAX_PCT * plans
    el_p = ksum(0, 'spine_el')
    if raw['spine_bad'] > 0 or raw['spine_misal'] > 0 or raw['cram_write'] > 0 or k5_lines > 0:
        k5 = 'FAIL'
    elif safe and el_p > 0 and 100 * ksum(0, 'spine_cmp') >= CMP_MIN_PCT * el_p:
        k5 = 'PASS'
    else:
        k5 = 'NOT_EVALUABLE'
    with_pred = plans - ksum(0, 'carry_skip')
    if raw['carry_bad'] > 0 or c_lines > 0:
        carry = 'FAIL'
    elif safe and with_pred > 0 and 100 * ksum(0, 'carry_cmp') >= CMP_MIN_PCT * with_pred:
        carry = 'PASS'
    else:
        carry = 'NOT_EVALUABLE'
    one = [v for v in values[0] if v['sc_frames'] == 1 and v['sc_el'] > 0]
    k3_shares = [v['k3_max'] / v['sc_el'] for v in one]
    k3_median = median(k3_shares)
    w_max = None if k3_median is None else (4 if 1000 * k3_median >= K3_SHARE_PERMILLE else 8)
    k4 = {}
    for w in (2, 4):
        col = [v['k4_w%d_dep' % w] for v in one if v['k4_w%d_n' % w] == 1]
        qualified = len(values[0]) > 0 and 100 * len(col) >= K4_MIN_PCT * len(values[0])
        med = median(col)
        by_block = {}
        for v in one:
            if v['k4_w%d_n' % w] == 1:
                by_block.setdefault(v['blk'], []).append(v['k4_w%d_dep' % w])
        above = sum(1 for d in col if d > K4_DEP_MAX_PERMILLE)
        k4[w] = dict(frames=len(col), median=med, p90=p90(col),
                     above_pct=None if not col else 100.0 * above / len(col),
                     block_medians=[[blk, median(ds)] for blk, ds in sorted(by_block.items())],
                     any_median=median([v['k4_w%d_any' % w] for v in one if v['k4_w%d_n' % w] == 1]),
                     fmax_median=median([v['k4_w%d_fmax' % w] for v in one if v['k4_w%d_n' % w] == 1]),
                     verdict='NOT_EVALUABLE' if not qualified or med is None
                     else ('PASS' if med <= K4_DEP_MAX_PERMILLE else 'FAIL'))
    if k5 == 'FAIL' or carry == 'FAIL':
        consequence = 'STOP_STAGE4'
    elif 'NOT_EVALUABLE' in (k5, carry, k4[2]['verdict']):
        consequence = 'NOT_EVALUABLE'
    elif k4[2]['verdict'] == 'FAIL':
        consequence = 'CLOSE_A'
    elif k4[4]['verdict'] != 'PASS':
        consequence = 'W2_CEILING'
    else:
        consequence = 'STAGE3'
    report = {}
    for arm in (0, 1):
        report[arm] = {k: mean([v[k] for v in values[arm]]) for k in REPORT_KEYS}
        report[arm]['kept_frames'] = len(values[arm])
        report[arm]['complete_blocks'] = complete_blocks[arm]
    res.update(checks=checks, verdict='ADMITTED' if admitted else 'NOT_ADMITTED', k5=k5, carry=carry, safe=safe,
               k3_median=k3_median, k3_frames=len(k3_shares), w_max=w_max, k4=k4,
               consequence=consequence if admitted else 'NOT_ADMITTED', raw=raw, k5_lines=k5_lines, c_lines=c_lines,
               plans=plans, with_pred=with_pred, carry_skip_pct=None if not plans else
               100.0 * ksum(0, 'carry_skip') / plans, report=report, pins=pins, gate_arms=len(gate_arms),
               markers=markers[:10], diag=diag, vk_env=vk_env, prereg_sha256=prereg.get('sha256'),
               pred_sha256_now=pred_sha)
    return res


def fmt(x, digits=1):
    if x is None:
        return '-'
    if isinstance(x, bool):
        return str(x)
    return ('%.' + str(digits) + 'f') % x


def format_report(res):
    out = ['spk118 tag %s  scorer %s  build %s' % (res['tag'], res['scorer_sha256'][:16], res['build_sha256'][:16])]
    for k, v in res['checks'].items():
        out.append('  %-16s %s' % (k, 'ok' if v else 'FAIL'))
    if res['verdict'] != 'ADMITTED':
        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')
    out.append('K5 %s  C %s  safe %s: raw %s, mismatch/misalign lines %d, carry lines %d; plans %d, with a predecessor %d'
               % (res['k5'], res['carry'], res['safe'], ', '.join('%s=%d' % kv for kv in res['raw'].items()),
                  res['k5_lines'], res['c_lines'], res['plans'], res['with_pred']))
    out.append('  carry_skip %s %% of plans (report only)' % fmt(res['carry_skip_pct'], 1))
    out.append('K3 median largest-run share %s over %d frames -> W_MAX %s' % (fmt(res['k3_median'], 4),
                                                                          res['k3_frames'], res['w_max']))
    for w in (2, 4):
        e = res['k4'][w]
        out.append('K4 W=%d %s: dep median %s p90 %s permille (bar %d) over %d frames; any median %s; fmax median %s'
                   % (w, e['verdict'], fmt(e['median'], 0), fmt(e['p90'], 0), K4_DEP_MAX_PERMILLE, e['frames'],
                      fmt(e['any_median'], 0), fmt(e['fmax_median'], 0)))
        out.append('  W=%d above the bar %s %% of %d frames; block medians %s (report only)'
                   % (w, fmt(e['above_pct'], 1), e['frames'],
                      ' '.join('%d:%s' % (blk, fmt(m, 0)) for blk, m in e['block_medians'])))
    for arm in (0, 1):
        r = res['report'][arm]
        out.append('  arm %d: %d kept frames in %d blocks; ' % (arm, r['kept_frames'], r['complete_blocks'])
                   + ', '.join('%s=%s' % (k, fmt(r[k], 1)) for k in REPORT_KEYS))
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

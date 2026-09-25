"""Session 117 (DRAFT, not sealed): mutants of spn117.py - each must be killed by test_spn117.py.  At the seal they are
run through the frozen mutlib v4.1 (--control --no-memo, work dir C:/kyty/s117/work*) on the sealed copy; this loop is
the draft check (one fresh `python test_spn117.py <mutant>` per mutant, mutant files in C:/kyty/s117/work_mut117)."""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s117/work_mut117')
SRC = Path('C:/kyty/s117/spn117.py').read_text(encoding='utf-8')
MUTANTS = [
    # constants (the suite uses them at their edges)
    ('hold_s', 'HOLD_S = 300', 'HOLD_S = 299'),
    ('period', 'PERIOD = 90', 'PERIOD = 91'),
    ('start', 'START = 1800', 'START = 1890'),
    ('keep_lo', 'KEEP = (10, 90)', 'KEEP = (5, 90)'),
    ('keep_hi', 'KEEP = (10, 90)', 'KEEP = (10, 85)'),
    ('abba', 'ABBA = (0, 1, 1, 0)', 'ABBA = (0, 1, 0, 1)'),
    ('arm_text0', "ARM_TEXT = ('spine=1', 'spine=2')", "ARM_TEXT = ('spine=0', 'spine=2')"),
    ('arm_text1', "ARM_TEXT = ('spine=1', 'spine=2')", "ARM_TEXT = ('spine=1', 'spine=1')"),
    ('min_blocks', 'MIN_BLOCKS = 20', 'MIN_BLOCKS = 19'),
    ('cmp_pct', 'CMP_MIN_PCT = 90', 'CMP_MIN_PCT = 89'),
    ('k1_max', 'K1_MAX_US = 1200', 'K1_MAX_US = 1201'),
    ('idle_max', 'IDLE_GPU_MAX = 10', 'IDLE_GPU_MAX = 11'),
    ('gates_sha', "GATES_SHA = '91da", "GATES_SHA = '81da"),
    ('pred_path', "PRED_PATH = 'C:/kyty/s117/pred/01_spn117.md'", "PRED_PATH = 'C:/kyty/s117/pred/02_spn117.md'"),
    ('schedule', "SCHEDULE = '90+1800:spine=1|spine=2'", "SCHEDULE = '90+1800:spine=2|spine=1'"),
    ('env_abba', "'KYTY_GATE_SCHEDULE_ABBA': '1',", "'KYTY_GATE_SCHEDULE_ABBAX': '1',"),
    ('env_markers', "'KYTY_GPU_MARKERS': '0',", "'KYTY_GPU_MARKERS': '2',"),
    ('env_lite', "'KYTY_FRAME_TRACE': 'lite',", "'KYTY_FRAME_TRACE': '1',"),
    ('vk_allowed', "VK_ALLOWED = ('VK_SDK_PATH',)", "VK_ALLOWED = ('VK_SDK_PATH', 'VK_LAYER_PATH')"),
    ('marker_fatal', "b'fatal', ", ''),
    ('marker_slow', "b'gpuwaitslow', ", ''),
    ('marker_skipped', "b'asyncpipelines: skipped draw'", "b'asyncpipelines: skipped drawX'"),
    ('draw_field', "DRAW_FIELDS = ('da_walk_us',)", "DRAW_FIELDS = ()"),
    ('main_blk', "'arm', 'blk')", "'arm')"),
    ('x_misal', "'spine_abort', 'spine_cmp', 'spine_bad', 'spine_misal', 'spine_pad',",
     "'spine_abort', 'spine_cmp', 'spine_bad', 'spine_pad',"),
    # admission checks
    ('binary', "binary=meta.get('binary_sha256') == BUILD_SHA,", 'binary=True,'),
    ('installed', 'installed_now=installed_sha == BUILD_SHA,', 'installed_now=True,'),
    ('pin_env', "pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and pins == [1],", 'pinned=pins == [1],'),
    ('pin_list', 'and pins == [1],', 'and 1 in pins,'),
    ('env_exact', 'env_exact=kyty_env == ENV_EXPECT,', 'env_exact=True,'),
    ('env_superset', 'env_exact=kyty_env == ENV_EXPECT,', 'env_exact=kyty_env.items() >= ENV_EXPECT.items(),'),
    ('env_vk', 'env_vk=all(k in VK_ALLOWED for k in vk_env),', 'env_vk=True,'),
    ('hold', "hold=meta.get('hold_s') == HOLD_S,", 'hold=True,'),
    ('att_len', 'one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,', 'one_ok_attempt=len(ok_att) == 1,'),
    ('att_ok', 'one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,', 'one_ok_attempt=len(atts) == 1,'),
    ('hold_exit', "a.get('outcome') == 'ok' and a.get('hold_exit') is None]", "a.get('outcome') == 'ok']"),
    ('prereg', "prereg=prereg_path.replace('\\\\', '/') == PRED_PATH,", 'prereg=True,'),
    ('prereg_sha', "prereg_sha=pred_sha is not None and prereg.get('sha256') == pred_sha,", 'prereg_sha=True,'),
    ('gates_hash', "gates_exact=hashlib.sha256(gates.encode('utf-8')).hexdigest() == GATES_SHA,",
     'gates_exact=True,'),
    ('gates_norm', "gates = ' '.join((meta.get('gates') or '').split())", "gates = meta.get('gates') or ''"),
    ('gate_lines', 'gate_lines=gate_lines_ok(spine_gate_lines, blocks),', 'gate_lines=True,'),
    ('gate_name', "if m is None or m.group(1) != b'spine':", 'if m is None:'),
    ('gate_mod', 'if (frame - START) % PERIOD != 0 or frame < START:', 'if frame < START:'),
    ('gate_value', 'if block not in blocks or int(m.group(2)) != 1 + blocks[block]:', 'if block not in blocks:'),
    ('arms', 'arms=arms_fine,', 'arms=True,'),
    ('arms_count', 'if arms != 2 or period != PERIOD', 'if period != PERIOD'),
    ('arms_period', 'if arms != 2 or period != PERIOD or abba != 1', 'if arms != 2 or abba != 1'),
    ('arms_abba', 'or abba != 1 or arm not in (0, 1)', 'or arm not in (0, 1)'),
    ('arms_text', 'or text != ARM_TEXT[arm]:', ':'),
    ('arms_frame', 'if frame != START + PERIOD * block or ABBA[block % 4] != arm', 'if ABBA[block % 4] != arm'),
    ('arms_order', 'or ABBA[block % 4] != arm or block in blocks:', 'or block in blocks:'),
    ('arms_dup', 'or ABBA[block % 4] != arm or block in blocks:', 'or ABBA[block % 4] != arm:'),
    ('arms_none', '        if g is None:\n            return False, {}\n', '        if g is None:\n            continue\n'),
    ('spine_logged', 'spine_logged=len(spine_lines) == 1,', 'spine_logged=len(spine_lines) >= 1,'),
    ('no_marker', 'no_marker=not markers,', 'no_marker=True,'),
    ('stdout_markers', "    so = Path(root) / ('stdout_%s.txt' % tag)\n", "    so = Path(root) / ('stdout_%s.txtX' % tag)\n"),
    ('blocks_arm1', 'and complete_blocks[1] >= min_blocks,', ','),
    ('blocks_ge', 'blocks=complete_blocks[0] >= min_blocks', 'blocks=complete_blocks[0] > min_blocks'),
    ('block_label_arm', "seen['main'][n]['arm'] == arm and ", ''),
    ('block_label_blk', " and seen['main'][n]['blk'] == b for n in frames", ' for n in frames'),
    ('complete_dups', 'return n not in dups and all(', 'return all('),
    ('armed_arm0_cmp', "and 100 * ksum(0, 'spine_cmp') <= ksum(0, 'spine_el')", ''),
    ('armed_arm0_cmp_lt', "100 * ksum(0, 'spine_cmp') <= ksum(0, 'spine_el')", "100 * ksum(0, 'spine_cmp') < ksum(0, 'spine_el')"),
    ('armed_arm1_cmp', "and ksum(1, 'spine_cmp') > 0),", '),'),
    ('armed_plan', "armed=(ksum(0, 'spine_n') > 0 and ", 'armed=('),
    ('armed_el', "ksum(0, 'spine_el') > 0 and ", ''),
    ('idle', 'idle=idle_ok(meta))', 'idle=True)'),
    ('idle_le', 'return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX', 'return isinstance(v, (int, float)) and v < IDLE_GPU_MAX'),
    # K5 / K1 / consequence
    ('k5_bad', "if raw_k5['spine_bad'] > 0 or ", 'if '),
    ('k5_misal', "raw_k5['spine_misal'] > 0 or raw_k5['cram_write'] > 0", "raw_k5['cram_write'] > 0"),
    ('k5_cram', " or raw_k5['cram_write'] > 0 or k5_lines > 0:", ' or k5_lines > 0:'),
    ('k5_lines', " or k5_lines > 0:\n        k5 = 'FAIL'", ":\n        k5 = 'FAIL'"),
    ('k5_lines_prefix', "K5_LINES = (b'SpineMismatch:', b'SpineMisalign:')", "K5_LINES = (b'SpineMismatch:',)"),
    ('k5_raw_start', '                if kind == \'x\' and n > START:', '                if kind == \'x\' and n > START + PERIOD:'),
    ('k5_raw_ge', "                if kind == 'x' and n > START:", "                if kind == 'x' and n >= START:"),
    ('k5_raw_cram', "K5_RAW = ('spine_bad', 'spine_misal', 'cram_write')", "K5_RAW = ('spine_bad', 'spine_misal')"),
    ('k5_complete_only', "    if raw_k5['spine_bad'] > 0 or raw_k5['spine_misal'] > 0",
     "    if sums_all['spine_bad'] > 0 or raw_k5['spine_misal'] > 0"),
    ('el_ops_off', 'el_ops=(ops1 > 0 and ', 'el_ops=(True or '),
    ('el_ops_lo', 'EL_OPS_LO_PCT = 95', 'EL_OPS_LO_PCT = 94'),
    ('el_ops_hi', 'EL_OPS_HI_PCT = 105', 'EL_OPS_HI_PCT = 106'),
    ('el_ops_ops', "    ops1 = ksum(1, 'draws') + ksum(1, 'dispatches')", "    ops1 = ksum(1, 'draws')"),
    ('arms_consecutive', 'ok = bool(blocks) and sorted(blocks) == list(range(len(blocks)))', 'ok = bool(blocks)'),
    ('rec_full', 'seen[kind][n] = rec if len(rec) == len(names) else None', 'seen[kind][n] = rec'),
    ('pin_parse', 'pins.append(int(mp.group(1)) if mp else -1)', 'pins.append(int(mp.group(1)) if mp else 1)'),
    ('k5_ratio_ge', "100 * ksum(1, 'spine_cmp') >= CMP_MIN_PCT * cmp_el", "100 * ksum(1, 'spine_cmp') > CMP_MIN_PCT * cmp_el"),
    ('k5_ratio_off', "elif cmp_ratio is not None and 100 * ksum(1, 'spine_cmp') >= CMP_MIN_PCT * cmp_el:",
     'elif cmp_ratio is not None:'),
    ('all_frames_start', 'if first_frame is not None and n > first_frame and complete(n))',
     'if first_frame is not None and n >= first_frame - 5 and complete(n))'),
    ('all_frames_kept', "sums_all = {k: sum(seen['x'][n][k] for n in all_frames) for k in ALL_SUMS}",
     "sums_all = {k: sum(seen['x'][n][k] for n in kept[0] + kept[1]) for k in ALL_SUMS}"),
    ('k1_le', 'k1 = \'PASS\' if k1_us is not None and k1_us <= K1_MAX_US else \'FAIL\'',
     'k1 = \'PASS\' if k1_us is not None and k1_us < K1_MAX_US else \'FAIL\''),
    ('k1_arm', "k1_us = mean([v['spine_us'] for v in values[0]])", "k1_us = mean([v['spine_us'] for v in values[1]])"),
    ('walker_lt', 'walker_need is not None and frame_nospine is not None and walker_need < frame_nospine',
     'walker_need is not None and frame_nospine is not None and walker_need <= frame_nospine'),
    ('walker_old_rule', "    frame_nospine = mean([v['dt_us'] - v['spine_us'] for v in values[0]])",
     "    frame_nospine = mean([v['dt_us'] for v in values[0]])"),
    ('walker_walk', "walker_need = mean([v['da_walk_us'] + v['spine_us'] for v in values[0]])",
     "walker_need = mean([v['spine_us'] for v in values[0]])"),
    ('cons_fail', "    consequence = 'STOP_STAGE4'", "    consequence = 'PART2'"),
    ('cons_ne', "        consequence = 'NOT_EVALUABLE'", "        consequence = 'PART2'"),
    ('cons_part2', "        consequence = 'PART2'\n    elif walker_fit:", "        consequence = 'PART2_WALKER'\n    elif walker_fit:"),
    ('cons_walker', "        consequence = 'PART2_WALKER'\n    else:", "        consequence = 'CLOSE_A'\n    else:"),
    ('cons_close', "        consequence = 'CLOSE_A'\n    report", "        consequence = 'PART2_WALKER'\n    report"),
    ('cons_admitted', "consequence=consequence if admitted else 'NOT_ADMITTED'", 'consequence=consequence'),
    ('verdict', "verdict='ADMITTED' if admitted else 'NOT_ADMITTED'", "verdict='ADMITTED'"),
    # report
    ('spine_us_unit', "v['spine_us'] = v['spine_ns'] / 1000.0", "v['spine_us'] = v['spine_ns'] / 1024.0"),
    ('chk_us_unit', "v['spine_chk_us'] = v['spine_chk_ns'] / 1000.0", "v['spine_chk_us'] = v['spine_chk_ns'] / 1e6"),
    ('el_over_ops', "ops = ksum(arm, 'draws') + ksum(arm, 'dispatches')", "ops = ksum(arm, 'draws')"),
    ('pk_per_plan', "ksum(arm, 'spine_pk') / ksum(arm, 'spine_n')", "ksum(arm, 'spine_pk') / ksum(arm, 'spine_el')"),
]
STAGE.mkdir(parents=True, exist_ok=True)
killed = 0
for name, old, new in MUTANTS:
    if SRC.count(old) != 1:
        print('%-18s ANCHOR x%d' % (name, SRC.count(old)))
        continue
    path = STAGE / ('mut_spn117_%s.py' % name)
    path.write_text(SRC.replace(old, new), encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, 'C:/kyty/s117/test_spn117.py', str(path)], capture_output=True, text=True)
    killed += r.returncode != 0
    print('%-18s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
    path.unlink()
print('killed %d of %d' % (killed, len(MUTANTS)))

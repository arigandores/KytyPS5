"""Session 122: mutants of map122.py - each must be killed by test_map122.py.  Run through the frozen mutlib v4.1
FULL (never --changed-from; ROADMAP s121 rule), exactly this command:
    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s122/map122.py
        --test C:/kyty/s122/test_map122.py --mutants C:/kyty/s122/mut_map122.py --control --no-memo
        --work-dir C:/kyty/s122/mutwork --cache-dir C:/kyty/s122/mutcache --out C:/kyty/s122/mut_map122.draft.txt
After the seal fills PRED_SHA / PRED_BYTES the whole run is repeated on the sealed scorer (trap of s121: a filled
pre-registration constant can leave a mutant without its killing fixture).
Every anchor occurs exactly once in map122.py (LF).  One mutant per constant, per threshold comparison, per window
edge, per unit conversion, per admission check, per counter group, per verdict branch, per scene-classification term
and per report line the fixtures read.
LEFT OUT, because the fixtures pass their own value and a mutant of the constant is then unobservable (the chain, not
the suite, checks these): PRED_PATH, PRED_SHA, PRED_BYTES (pred_path / pred_sha / pred_bytes arguments), GATES_FILE
(gates_file argument), INSTALLED (installed_sha argument), ROOT and the argv parsing of main() other than
--plan-check, which has its own fixture.
REMOVED after the unsealed run of 2026-09-26 (46 survivors), as EQUIVALENT - no input can tell them from the scorer:
  rx_gate_arm_loose          the GateArm line is rstripped before the match and `.` matches every byte but LF, so
                             `(.*)$` and `(.*)` capture the same text on every line;
  arm_asserts_names_ignored  the names test sat behind `t != want[arm]`, and an arm text equal to 'burn=0' / 'burn=V'
                             names only burn - the dead clause is removed from the scorer itself;
  estimate_pooled            its replacement added a no-op statement (`rows = None`); replaced by a REAL pooled
                             estimator mutant (estimate_pooled_means);
  skip_window_any_pos / skip_window_never / check_skip_window   the code they mutated was replaced by the item-14 rule
                             (first_population_frame / skip_fatal), which carries its own mutants.
Every other survivor of that run is killed by a fixture added for it (see test_map122.py "edges the first mutant run
left unpinned" and the plan check `plan_default_is_the_seal`, which pins every PLAN level and value).
REPLACED at step 3b (ROADMAP s122 item 13 (b), the skym122 arm left the map after the smoke csky122): plan_skym_code4
  and plan_skym_none - their PLAN line is gone; plan_skym_back (the arm put back) takes their place.
REPLACED at step 3b (ROADMAP s122 item 18 (c), the HEADROOM reading by the run's own base arm, not by the level name):
  headroom_levels_empty      its constant HEADROOM_LEVELS is gone; the reading mutants hr_* and reading_by_name /
                             reading_always_speed / rep_reading_line / rep_speed_on_ne take its place.
"""
import subprocess
import sys
from pathlib import Path

STAGE = Path('C:/kyty/s122/work_mut_map122')
SRC = Path('C:/kyty/s122/map122.py').read_text(encoding='utf-8')
MUTANTS = [
    # ---- constants: run shape, window, thresholds, units
    ('hold_s', 'HOLD_S = 300', 'HOLD_S = 299'),
    ('period', 'PERIOD = 90\n', 'PERIOD = 91\n'),
    ('start', 'START = 1800', 'START = 1710'),
    ('keep_lo9', 'KEEP = (10, 89)', 'KEEP = (9, 89)'),
    ('keep_lo11', 'KEEP = (10, 89)', 'KEEP = (11, 89)'),
    ('keep_hi90', 'KEEP = (10, 89)', 'KEEP = (10, 90)'),
    ('keep_hi88', 'KEEP = (10, 89)', 'KEEP = (10, 88)'),
    ('keep_0_89', 'KEEP = (10, 89)', 'KEEP = (0, 89)'),
    ('keep_60_88', 'KEEP = (10, 89)', 'KEEP = (60, 89)'),
    ('draws_min_299', 'DRAWS_MIN = 300 ', 'DRAWS_MIN = 299 '),
    ('draws_min_4700', 'DRAWS_MIN = 300 ', 'DRAWS_MIN = 4700 '),
    ('abba_abab', 'ABBA = (0, 1, 1, 0)', 'ABBA = (0, 1, 0, 1)'),
    ('arms_swapped', 'ARM_A = 0                # "burn=0", the baseline\nARM_B = 1',
     'ARM_A = 1                # "burn=0", the baseline\nARM_B = 0'),
    ('min_pairs_23', 'MIN_PAIRS = 24           #', 'MIN_PAIRS = 23           #'),
    ('min_pairs_25', 'MIN_PAIRS = 24           #', 'MIN_PAIRS = 25           #'),
    ('idle_9', 'IDLE_GPU_MAX = 10', 'IDLE_GPU_MAX = 9'),
    ('idle_11', 'IDLE_GPU_MAX = 10', 'IDLE_GPU_MAX = 11'),
    ('dose_us_1000', 'DOSE_US = 2000 ', 'DOSE_US = 1000 '),
    ('dose_us_2001', 'DOSE_US = 2000 ', 'DOSE_US = 2001 '),
    ('dose_tol_04', 'DOSE_TOL = 0.05 ', 'DOSE_TOL = 0.04 '),
    ('dose_tol_06', 'DOSE_TOL = 0.05 ', 'DOSE_TOL = 0.06 '),
    ('dose_tol_off', 'DOSE_TOL = 0.05 ', 'DOSE_TOL = 1.0 '),
    ('s_crit_lo_04', 'S_CRIT_LO = 0.5 ', 'S_CRIT_LO = 0.4 '),
    ('s_crit_lo_06', 'S_CRIT_LO = 0.5 ', 'S_CRIT_LO = 0.6 '),
    ('s_reach_09', 'S_REACH = 1.0 ', 'S_REACH = 0.9 '),
    ('s_reach_11', 'S_REACH = 1.0 ', 'S_REACH = 1.1 '),
    ('s_flat_02', 'S_FLAT_HI = 0.3 ', 'S_FLAT_HI = 0.2 '),
    ('s_flat_04', 'S_FLAT_HI = 0.3 ', 'S_FLAT_HI = 0.4 '),
    ('s_super_09', 'S_SUPER = 1.0 ', 'S_SUPER = 0.9 '),
    ('s_super_11', 'S_SUPER = 1.0 ', 'S_SUPER = 1.1 '),
    ('gpu_bound_089', 'GPU_BOUND = 0.9 ', 'GPU_BOUND = 0.89 '),
    ('gpu_bound_091', 'GPU_BOUND = 0.9 ', 'GPU_BOUND = 0.91 '),
    ('pinch_079', 'PINCH = 0.80 ', 'PINCH = 0.79 '),
    ('pinch_081', 'PINCH = 0.80 ', 'PINCH = 0.81 '),
    ('vblank_us', 'VBLANK_US = 16667.0', 'VBLANK_US = 25000.0'),
    ('game_frame_us', 'GAME_FRAME_US = 16667.0', 'GAME_FRAME_US = 16666.0'),
    ('ns_per_us_1', 'NS_PER_US = 1000.0', 'NS_PER_US = 1.0'),
    ('ns_per_us_1e6', 'NS_PER_US = 1000.0', 'NS_PER_US = 1000000.0'),
    ('bda_new_54', 'BDA_NEW_MAX = 300', 'BDA_NEW_MAX = 54'),
    ('bda_new_1200', 'BDA_NEW_MAX = 300', 'BDA_NEW_MAX = 1200'),
    ('bda_old_440', 'BDA_OLD_MIN = 600', 'BDA_OLD_MIN = 440'),
    ('bda_old_1200', 'BDA_OLD_MIN = 600', 'BDA_OLD_MIN = 1200'),
    ('cpu_wall_block', 'CPU_WALL_BLOCK = 1.00 ', 'CPU_WALL_BLOCK = 2.00 '),
    ('cpu_wall_spread', 'CPU_WALL_SPREAD = 1.33', 'CPU_WALL_SPREAD = 1.30'),
    ('build_sha', "BUILD_SHA = '2baf8742676255fefd37c72f727e6c27c024be9b67d3afa987bed7fe334af86b'",
     "BUILD_SHA = '2baf8742676255fefd37c72f727e6c27c024be9b67d3afa987bed7fe334af86c'"),
    ('gates_sha', "GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbf'",
     "GATES_SHA = '303a784911cf0ffed238f581e47f98876a0a5164a72a24ca32a17fc67820cbbe'"),
    # ---- the plan: the scene, the code and the dose of each tag
    ('plan_sky_value', "    'sky122':  dict(level='underwater_aerial_garden', burn=102000),",
     "    'sky122':  dict(level='underwater_aerial_garden', burn=202000),"),
    ('plan_sky_level', "    'sky122':  dict(level='underwater_aerial_garden', burn=102000),",
     "    'sky122':  dict(level='penguin_atlantis', burn=102000),"),
    ('plan_skyp_value', "    'skyp122': dict(level='underwater_aerial_garden', burn=802000),",
     "    'skyp122': dict(level='underwater_aerial_garden', burn=102000),"),
    ('plan_skym_back', "    'skyp122': dict(level='underwater_aerial_garden', burn=802000),\n",
     "    'skyp122': dict(level='underwater_aerial_garden', burn=802000),\n"
     "    'skym122': dict(level='underwater_aerial_garden', burn=702000),\n"),
    ('plan_atl_level', "    'atl122':  dict(level='penguin_atlantis', burn=102000),",
     "    'atl122':  dict(level='underwater_aerial_garden', burn=102000),"),
    ('plan_ght_level', "    'ght122':  dict(level='time_stopper_ghost_world', burn=102000),",
     "    'ght122':  dict(level='time_stopper_ghost_world2', burn=102000),"),
    ('plan_dnn_level', "    'dnn122':  dict(level='rotating_level_day_and_night', burn=102000),",
     "    'dnn122':  dict(level='rotating_level_day_and_night2', burn=102000),"),
    ('plan_des_level', "    'des122':  dict(level='intro_next', burn=102000),",
     "    'des122':  dict(level='intro', burn=102000),"),
    ('plan_mgg_level', "    'mgg122':  dict(level='mini_giants_garden', burn=102000),",
     "    'mgg122':  dict(level='mini_giants_garden2', burn=102000),"),
    ('plan_hub_level', "    'hub122':  dict(level='hub_crashsite', burn=102000),",
     "    'hub122':  dict(level='hub_crashsite2', burn=102000),"),
    ('plan_hov_level', "    'hov122':  dict(level='hoover_beach', burn=102000),",
     "    'hov122':  dict(level='hoover_beach2', burn=102000),"),
    ('plan_ice_level', "    'ice122':  dict(level='ice_iceberg', burn=102000),",
     "    'ice122':  dict(level='ice_iceberg2', burn=102000),"),
    ('plan_dose', "    'sky122':  dict(level='underwater_aerial_garden', burn=102000),",
     "    'sky122':  dict(level='underwater_aerial_garden', burn=101000),"),
    # ---- the counter groups
    ('group_code1_prefix', "CODE_GROUP = {1: ('g', 'block', 'GuestGpu')", "CODE_GROUP = {1: ('p', 'block', 'GuestGpu')"),
    ('group_code1_thread', "CODE_GROUP = {1: ('g', 'block', 'GuestGpu')", "CODE_GROUP = {1: ('g', 'block', 'Main')"),
    ('group_code2_kind', "2: ('r', 'spread', 'Record')", "2: ('r', 'block', 'Record')"),
    ('group_code3_prefix', "3: ('m', 'spread', 'M1')", "3: ('r', 'spread', 'M1')"),
    ('group_code7_thread', "7: ('t', 'block', 'Submit')", "7: ('t', 'block', 'Main')"),
    ('group_code8_prefix', "8: ('p', 'block', 'Placebo')", "8: ('g', 'block', 'Placebo')"),
    ('group_code9_added', "7: ('t', 'block', 'Submit'), 8: ('p', 'block', 'Placebo')}",
     "7: ('t', 'block', 'Submit'), 8: ('p', 'block', 'Placebo'), 9: ('g', 'block', '?')}"),
    ('cover_empty', "COVER = {7: 'burn_s_seen'}", "COVER = {}"),
    ('cover_wrong', "COVER = {7: 'burn_s_seen'}", "COVER = {7: 'burn_t_seen'}"),
    ('role_empty', "ROLE = {7: 'burn_s_main'}", "ROLE = {}"),
    ('prefixes_short', "PREFIXES = ('g', 'r', 'm', 't', 'p')", "PREFIXES = ('g', 'r', 'm', 't')"),
    ('main_fields_no_submits', "'draws', 'dispatches', 'submits', 'arm', 'blk')",
     "'draws', 'dispatches', 'arm', 'blk')"),
    ('main_fields_no_blk', "'draws', 'dispatches', 'submits', 'arm', 'blk')",
     "'draws', 'dispatches', 'submits', 'arm')"),
    ('x_fields_no_spin', "X_FIELDS = ('rec_spin_us',) + BURN_KEYS", "X_FIELDS = BURN_KEYS"),
    ('burn_keys_no_cpu_bad', "'burn_s_seen', 'burn_s_main', 'burn_late', 'burn_cpu_bad')",
     "'burn_s_seen', 'burn_s_main', 'burn_late')"),
    ('base_absent_no_burn', "BASE_ABSENT_OR_0 = ('burn', 'texmemo8'", "BASE_ABSENT_OR_0 = ('texmemo8'"),
    ('base_absent_no_texmemo2', "'texmemo8', 'texmemo2', 'r1cen'", "'texmemo8', 'r1cen'"),
    ('markers_no_error', "b'unhandled exception', b'--- error ---')", "b'unhandled exception')"),
    ('markers_no_hang', "MARKERS = (b'gpuhangabort', ", "MARKERS = ("),
    ('skipped_draw_text', "SKIPPED_DRAW = b'AsyncPipelines: skipped draw'",
     "SKIPPED_DRAW = b'AsyncPipelines: skipped nothing'"),
    ('vk_allowed', "VK_ALLOWED = ('VK_SDK_PATH',)", "VK_ALLOWED = ('VK_SDK_PATH', 'VK_LAYER_PATH')"),
    # ---- the log grammar
    ('rx_burn_arm_thread', "BURN_ARM = re.compile(rb'^Burn: arm code=(\\d+) thread=(\\S+) dose_us=(\\d+) q_ns=(\\d+)$')",
     "BURN_ARM = re.compile(rb'^Burn: arm code=(\\d+) thread=(\\S+) dose_us=(\\d+) q_ns=(\\d+)')"),
    ('rx_selftest', "BURN_SELFTEST = re.compile(rb'^Burn: selftest target_us=(\\d+) ')",
     "BURN_SELFTEST = re.compile(rb'^Burn: selftestX target_us=(\\d+) ')"),
    ('rx_reject', "BURN_REJECT = re.compile(rb'^Burn: value=\\d+ rejected')",
     "BURN_REJECT = re.compile(rb'^Burn: value=\\d+ rejectedX')"),
    ('rx_notsc', "BURN_NOTSC = re.compile(rb'^Burn: no calibrated TSC')",
     "BURN_NOTSC = re.compile(rb'^Burn: no calibrated TSCX')"),
    ('rx_late', "BURN_LATE = re.compile(rb'^BurnLate: code=(\\d+) us=([0-9.]+) target_us=(\\d+)$')",
     "BURN_LATE = re.compile(rb'^BurnLateX: code=(\\d+) us=([0-9.]+) target_us=(\\d+)$')"),
    ('rx_pin', "PIN = re.compile(rb'^GpuClockPin: mode (\\d+)')", "PIN = re.compile(rb'^GpuClockPin: mode 1')"),
    # ---- helpers
    ('base_tag_always', "    return tag[:-1] if tag.endswith('r') else tag", "    return tag"),
    ('code_dose_split', "    return (0, 0) if value == 0 else (value // 100000, value % 100000)",
     "    return (0, 0) if value == 0 else (value // 10000, value % 10000)"),
    ('arm_texts_a', "    return ('burn=0', None if v is None else 'burn=%d' % v)",
     "    return ('burn=1', None if v is None else 'burn=%d' % v)"),
    ('schedule_order', "    return None if texts[1] is None else '%d+%d:%s|%s' % (PERIOD, START, texts[0], texts[1])",
     "    return None if texts[1] is None else '%d+%d:%s|%s' % (PERIOD, START, texts[1], texts[0])"),
    ('env_trace', "        'KYTY_FRAME_TRACE': 'lite',", "        'KYTY_FRAME_TRACE': '1',"),
    ('env_hang', "        'KYTY_GPU_HANG_ABORT_S': '8',", "        'KYTY_GPU_HANG_ABORT_S': '0',"),
    ('env_gate_file', "        'KYTY_GATE_FILE': 'C:\\\\kyty\\\\s122\\\\gates.req',",
     "        'KYTY_GATE_FILE': 'C:\\\\kyty\\\\s121\\\\gates.req',"),
    ('env_sample', "        'KYTY_SAMPLE_GATE': 'C:\\\\kyty\\\\s122\\\\sample.req',",
     "        'KYTY_SAMPLE_GATE': 'C:\\\\kyty\\\\s121\\\\sample.req',"),
    ('env_queue', "        'KYTY_QUEUE_TRACE': '1',", "        'KYTY_QUEUE_TRACE': '2',"),
    ('env_guest_args', "        'KYTY_GUEST_ARGS': '-lvl ' + plan['level'],",
     "        'KYTY_GUEST_ARGS': '-lvl underwater_aerial_garden',"),
    ('env_no_abba', "        'KYTY_GATE_SCHEDULE_ABBA': '1',", ""),
    ('env_pin_2', "        'KYTY_GPU_CLOCK_PIN': '1',", "        'KYTY_GPU_CLOCK_PIN': '2',"),
    ('env_markers_2', "        'KYTY_GPU_MARKERS': '0',", "        'KYTY_GPU_MARKERS': '2',"),
    ('env_allows_rec', "    return {\n        'KYTY_FRAME_TRACE': 'lite',",
     "    return {\n        'KYTY_REC': 'C:\\\\kyty\\\\s122\\\\rec_sky122.mp4',\n        'KYTY_FRAME_TRACE': 'lite',"),
    ('idle_lt', '    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX',
     '    return isinstance(v, (int, float)) and v < IDLE_GPU_MAX'),
    ('idle_any', '    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX', '    return True'),
    ('two_se_three', '    if len(values) < 2:\n        return None\n    return 2.0 * statistics.stdev(values)',
     '    if len(values) < 3:\n        return None\n    return 2.0 * statistics.stdev(values)'),
    ('two_se_one', '    return 2.0 * statistics.stdev(values) / math.sqrt(len(values))',
     '    return 1.0 * statistics.stdev(values) / math.sqrt(len(values))'),
    ('two_se_no_sqrt', '    return 2.0 * statistics.stdev(values) / math.sqrt(len(values))',
     '    return 2.0 * statistics.stdev(values) / len(values)'),
    ('mean_sum', '    return sum(values) / len(values) if values else None', '    return sum(values) if values else None'),
    ('median_first', '    return ordered[len(ordered) // 2]', '    return ordered[0]'),
    ('median_last', '    return ordered[len(ordered) // 2]', '    return ordered[-1]'),
    ('regime_new_ge', '    if v <= BDA_NEW_MAX:', '    if v < BDA_NEW_MAX:'),
    ('regime_old_gt', '    if v >= BDA_OLD_MIN:', '    if v > BDA_OLD_MIN:'),
    ('first_values_last', '            out.setdefault(k, v)', '            out[k] = v'),
    ('arm_asserts_no_gate_loop', "    for name in BASE_ABSENT_OR_0:\n        if g.get(name) not in (None, '0'):\n"
                                 "            return False\n", ''),
    ('arm_asserts_no_text_loop', "    for arm in (ARM_A, ARM_B):\n        for t in texts[arm]:\n"
                                 "            if t != want[arm]:\n"
                                 "                return False\n", ''),
    ('arm_asserts_one_arm', "    if want[1] is None or not texts.get(ARM_A) or not texts.get(ARM_B):",
     "    if want[1] is None or not texts.get(ARM_A):"),
    ('arms_no_arms2', "        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1) or text != want[arm]:",
     "        if period != PERIOD or abba != 1 or arm not in (0, 1) or text != want[arm]:"),
    ('arms_no_abba', "        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1) or text != want[arm]:",
     "        if arms != 2 or period != PERIOD or arm not in (0, 1) or text != want[arm]:"),
    ('arms_no_text', "        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1) or text != want[arm]:",
     "        if arms != 2 or period != PERIOD or abba != 1 or arm not in (0, 1):"),
    ('arms_no_frame', "        if frame != START + PERIOD * block or ABBA[block % 4] != arm or block in blocks:",
     "        if ABBA[block % 4] != arm or block in blocks:"),
    ('arms_no_order', "        if frame != START + PERIOD * block or ABBA[block % 4] != arm or block in blocks:",
     "        if frame != START + PERIOD * block or block in blocks:"),
    ('arms_no_consecutive', "    ok = bool(blocks) and sorted(blocks) == list(range(len(blocks)))",
     "    ok = bool(blocks)"),
    ('gate_lines_any_name', "        if name != 'burn' or frame < START or (frame - START) % PERIOD != 0:",
     "        if frame < START or (frame - START) % PERIOD != 0:"),
    ('gate_lines_any_frame', "        if name != 'burn' or frame < START or (frame - START) % PERIOD != 0:",
     "        if name != 'burn':"),
    ('gate_lines_any_value', "        if block not in blocks or m.group(2).decode() != values[blocks[block]][name]:",
     "        if block not in blocks:"),
    # ---- the parse
    ('parse_x_only_once', "                if kind == 'x':\n                    for k in raw:\n"
                          "                        raw[k] += int(got.get(k.encode(), 0))",
     "                if kind == 'x' and n not in seen['x']:\n                    for k in raw:\n"
     "                        raw[k] += int(got.get(k.encode(), 0))"),
    ('parse_partial_row_ok', "                seen[kind][n] = rec if len(rec) == len(names) else None",
     "                seen[kind][n] = rec"),
    ('parse_no_stdout', "    if stdout_path is not None and Path(stdout_path).is_file():",
     "    if False and Path(stdout_path).is_file():"),
    ('parse_skip_frame', "                skipped.append(None if last_main is None else last_main + 1)",
     "                skipped.append(None)"),
    # ---- the selection
    ('select_whole_block', "        frames = block_frames(b)[KEEP[0]:KEEP[1]]", "        frames = block_frames(b)"),
    ('select_no_labels', "        if all(complete(n) and seen['main'][n]['arm'] == arm and seen['main'][n]['blk'] == b "
                         "for n in frames):", "        if all(complete(n) for n in frames):"),
    ('select_no_blk_label', "seen['main'][n]['arm'] == arm and seen['main'][n]['blk'] == b for n in frames):",
     "seen['main'][n]['arm'] == arm for n in frames):"),
    ('select_pairs_overlap', "    pairs = [(b, b + 1) for b in range(0, top, 2)", "    pairs = [(b, b + 1) for b in range(0, top)"),
    ('select_pairs_no_est', "             if b in done and b + 1 in done and done[b]['est'] and done[b + 1]['est'] and b not in drop]",
     "             if b in done and b + 1 in done and b not in drop]"),
    ('select_ignores_drop', " and done[b + 1]['est'] and b not in drop]", " and done[b + 1]['est']]"),
    ('streams_no_exempt', "            if n not in seen['main'] or n == parsed['last_main']:",
     "            if n not in seen['main']:"),
    ('streams_no_dups', "            if n in dups or any(seen[k].get(n) is None for k in seen):",
     "            if any(seen[k].get(n) is None for k in seen):"),
    # ---- ROADMAP s122 item 14: the skipped-draw marker from the population's first frame on
    ('first_pop_no_keep', '    return START + 1 + KEEP[0] if 0 in blocks else None', '    return START + 1 if 0 in blocks else None'),
    ('first_pop_any_block', '    return START + 1 + KEEP[0] if 0 in blocks else None',
     '    return START + 1 + KEEP[0] if blocks else None'),
    ('skip_unknown_not_fatal', '    if first is None:\n        return True', '    if first is None:\n        return False'),
    ('skip_gt', '    return frame is not None and frame >= first', '    return frame is not None and frame > first'),
    ('skip_none_fatal', '    return frame is not None and frame >= first', '    return frame is None or frame >= first'),
    ('check_skip_all', '        no_skip_window=not skipped_in,', "        no_skip_window=not parsed['skipped'],"),
    ('check_skip_off', '        no_skip_window=not skipped_in,', '        no_skip_window=True,'),
    ('skipped_before_min', "skipped_before_max=max([f for f in skipped_out if f is not None],",
     "skipped_before_max=min([f for f in skipped_out if f is not None],"),
    ('rep_skip_line_max', "                  res['skipped_before_max']))", "                  res['skipped_before']))"),
    # ---- ROADMAP s122 item 17 (c): an outlier frame drops its block's ABBA pair
    ('outlier_us_499999', 'OUTLIER_US = 500000 ', 'OUTLIER_US = 499999 '),
    ('outlier_us_500001', 'OUTLIER_US = 500000 ', 'OUTLIER_US = 500001 '),
    ('max_outlier_1', 'MAX_OUTLIER_PAIRS = 2 ', 'MAX_OUTLIER_PAIRS = 1 '),
    ('max_outlier_3', 'MAX_OUTLIER_PAIRS = 2 ', 'MAX_OUTLIER_PAIRS = 3 '),
    ('outlier_gt', '        if dt >= OUTLIER_US:', '        if dt > OUTLIER_US:'),
    ('outlier_no_block_check', '            if b in blocks:\n                out.append((n, dt, b))',
     '            out.append((n, dt, b))'),
    ('dropped_pairs_self', '    return sorted({b - b % 2 for _n, _dt, b in outs})', '    return sorted({b for _n, _dt, b in outs})'),
    ('dropped_pairs_next', '    return sorted({b - b % 2 for _n, _dt, b in outs})',
     '    return sorted({b + b % 2 for _n, _dt, b in outs})'),
    ('outlier_check_lt', '        outlier_pairs=len(drops) <= MAX_OUTLIER_PAIRS,',
     '        outlier_pairs=len(drops) < MAX_OUTLIER_PAIRS,'),
    ('outlier_check_off', '        outlier_pairs=len(drops) <= MAX_OUTLIER_PAIRS,', '        outlier_pairs=True,'),
    ('dts_complete_rows_only', "                    if b'dt_us' in got:\n",
     "                    if b'dt_us' in got and len(rec) == len(names):\n"),
    ('dts_last_duplicate', "dts[n] = max(dts.get(n, 0), int(got[b'dt_us']))", "dts[n] = int(got[b'dt_us'])"),
    ('res_outlier_pair', "outliers=[dict(frame=n, dt_us=d, block=b, pair=b - b % 2) for n, d, b in outs],",
     "outliers=[dict(frame=n, dt_us=d, block=b, pair=b // 2) for n, d, b in outs],"),
    ('rep_outlier_line', "        out.append('OUTLIER frame n=%d dt_us=%d (>= %d): block %d, pair (%d, %d) dropped whole'",
     "        out.append('OUTLIER frame n=%d dt_us=%d (>= %d): block %d, pair (%d, %d) trimmed'"),
    ('rep_outlier_pair_args', "                   % (o['frame'], o['dt_us'], OUTLIER_US, o['block'], o['pair'], o['pair'] + 1))",
     "                   % (o['frame'], o['dt_us'], OUTLIER_US, o['block'], o['block'], o['block'] + 1))"),
    # ---- ROADMAP s122 item 17 (a): the host-event witness
    ('host_ok_add_invalid', "HOST_OK = ('RUN_CLEAN', 'STALL_UNATTRIBUTED')",
     "HOST_OK = ('RUN_CLEAN', 'STALL_UNATTRIBUTED', 'RUN_INVALID')"),
    ('host_ok_no_stall', "HOST_OK = ('RUN_CLEAN', 'STALL_UNATTRIBUTED')", "HOST_OK = ('RUN_CLEAN',)"),
    ('hostdev_sha', "HOSTDEV_SHA = '8404ff8c309a2cf723c44262c543343fe55a5a3b2e1c21c264831b8cac935a1c'",
     "HOSTDEV_SHA = '8404ff8c309a2cf723c44262c543343fe55a5a3b2e1c21c264831b8cac935a1d'"),
    ('hostdev_py', "HOSTDEV_PY = 'C:/kyty/s122/hostdev122.py'", "HOSTDEV_PY = 'C:/kyty/s121/hostdev122.py'"),
    ('host_missing_ok', "        return False, 'NOT CHECKED (no hostdev_%s.txt)' % tag",
     "        return True, 'NOT CHECKED (no hostdev_%s.txt)' % tag"),
    ('host_tag_unchecked', "    if not lines or lines[0].strip() != 'hostdev122 %s' % tag:", '    if not lines:'),
    ('host_window_unchecked', '    if want_window not in [ln.strip() for ln in lines]:', '    if False:'),
    ('host_verdicts_any', '    if len(verdicts) != 1:', '    if not verdicts:'),
    ('host_not_evaluable_ok', "    if verdicts[0] == 'NOT EVALUABLE':\n        return False,",
     "    if verdicts[0] == 'NOT EVALUABLE':\n        return True,"),
    ('host_check_off', '        host_clean=host_ok,', '        host_clean=True,'),
    ('host_tool_off', '        host_tool=Path(hostdev_py).is_file() and sha_file(hostdev_py) == HOSTDEV_SHA,',
     '        host_tool=True,'),
    ('host_tool_arg_ignored', '    hostdev_py = HOSTDEV_PY if hostdev_py is None else hostdev_py', '    hostdev_py = HOSTDEV_PY'),
    ('rep_host_line', "    out.append('host events (hostdev_%s.txt): %s' % (res['tag'], res['host']))",
     "    out.append('host events (hostdev_%s.txt): %s' % (res['tag'], 'RUN_CLEAN'))"),
    # ---- ROADMAP s122 items 17 (d) / (e), 18 (c): headroom reading by the base arm, the BDA regime on every verdict line
    ('hr_dt_24999', 'HEADROOM_DT_US = 25000 ', 'HEADROOM_DT_US = 24999 '),
    ('hr_dt_25001', 'HEADROOM_DT_US = 25000 ', 'HEADROOM_DT_US = 25001 '),
    ('hr_share_094', 'HEADROOM_SHARE = 0.95 ', 'HEADROOM_SHARE = 0.94 '),
    ('hr_share_096', 'HEADROOM_SHARE = 0.95 ', 'HEADROOM_SHARE = 0.96 '),
    ('hr_lt_le', '    share = sum(1 for d in dts if d < HEADROOM_DT_US) / float(len(dts))',
     '    share = sum(1 for d in dts if d <= HEADROOM_DT_US) / float(len(dts))'),
    ('hr_ge_gt', "    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts)",
     "    return ('HEADROOM' if share > HEADROOM_SHARE else 'SPEED'), share, len(dts)"),
    ('hr_empty_speed', "        return 'NOT_EVALUABLE', None, 0", "        return 'SPEED', None, 0"),
    ('hr_empty_headroom', "        return 'NOT_EVALUABLE', None, 0", "        return 'HEADROOM', None, 0"),
    ('hr_frames_off', "    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts)",
     "    return ('HEADROOM' if share >= HEADROOM_SHARE else 'SPEED'), share, len(dts) - 1"),
    ('hr_arm_b', "for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])",
     "for pr in pairs for b in pr if done[b]['arm'] == ARM_B for r in done[b]['win']])"),
    ('hr_both_arms', "for pr in pairs for b in pr if done[b]['arm'] == ARM_A for r in done[b]['win']])",
     "for pr in pairs for b in pr for r in done[b]['win']])"),
    ('hr_all_blocks', "    return reading_of([r['dt_us'] for pr in pairs for b in pr if done[b]['arm'] == ARM_A "
     "for r in done[b]['win']])",
     "    return reading_of([r['dt_us'] for b in done if done[b]['arm'] == ARM_A for r in done[b]['win']])"),
    ('reading_always_speed', '               reading=reading, headroom=dict(',
     "               reading='SPEED', headroom=dict("),
    ('reading_by_name', '               reading=reading, headroom=dict(',
     "               reading='HEADROOM' if res['level'] == 'intro_next' else reading, headroom=dict("),
    ('rep_reading_line', "               'item 18 (c))' % (res['reading'], hr['dt_us'], fmt(hr['share'], 4), hr['frames'],",
     "               'item 18 (c))' % (res['reading'], hr['dt_us'], fmt(hr['share'], 3), hr['frames'],"),
    ('rep_speed_on_ne', "    elif res['reading'] != 'SPEED':", "    elif False:"),
    ('rep_speed_on_headroom', "    if res['reading'] == 'HEADROOM':\n        out.append('game speed: NOT QUOTED",
     "    if False:\n        out.append('game speed: NOT QUOTED"),
    ('rep_headroom_note_off', "    if res['reading'] == 'HEADROOM':\n        note +=", "    if False:\n        note +="),
    ('rep_bda_old_note_off', "    if res['bda_scan']['A_regime'] == 'OLD':\n        note +=", "    if False:\n        note +="),
    ('rep_verdict_bda_b', "res['pairs'], res['bda_scan']['A_regime'], res['reading'],",
     "res['pairs'], res['bda_scan']['B_regime'], res['reading'],"),
    # ---- the draw-adjusted estimator (report only)
    ('adj_ratio_inverted', "        ratio = div(mean([r['draws'] for r in done[bb]['est']]), mean([r['draws'] for r in done[ab]['est']]))",
     "        ratio = div(mean([r['draws'] for r in done[ab]['est']]), mean([r['draws'] for r in done[bb]['est']]))"),
    ('adj_no_ratio', '        diffs.append(b_dt - a_dt * ratio)', '        diffs.append(b_dt - a_dt)'),
    ('adj_sign', '        diffs.append(b_dt - a_dt * ratio)', '        diffs.append(a_dt * ratio - b_dt)'),
    ('adj_zone_raw', 'draw_adjusted=dict(est=adj, slope=sl_adj, zone=z_adj, differs=z_adj != z),',
     'draw_adjusted=dict(est=adj, slope=sl_adj, zone=z, differs=z_adj != z),'),
    ('adj_differs_off', 'differs=z_adj != z),', 'differs=False),'),
    ('adj_decides_verdict', '    else:\n        verdict = z\n', '    else:\n        verdict = z_adj\n'),
    ('adj_draws_delta', "pair_diffs=diffs, draws_delta=draws['delta'],", "pair_diffs=diffs, draws_delta=draws['two_se'],"),
    ('rep_adj_differs_text', "'  DRAW-ADJUSTED ZONE DIFFERS' if ad['differs'] else ''", "'' if ad['differs'] else ''"),
    # ---- code 7: the role split is part of coverage
    ('coverage_no_role', "    return bool(cover and cover['value'] > 0 and (cover['role'] is None or cover['role_value'] > 0))",
     "    return bool(cover and cover['value'] > 0)"),
    ('coverage_ge0', "    return bool(cover and cover['value'] > 0 and (", "    return bool(cover and cover['value'] >= 0 and ("),
    ('coverage_role_ge0', "cover['role_value'] > 0))", "cover['role_value'] >= 0))"),
    ('coverage_check_off', '        coverage=coverage_ok(cover))', '        coverage=True)'),
    # ---- arming, dose, coverage
    ('armed_no_other_groups', "        if any(sum(r[k] for r in blk['win']) != 0 for k in BURN_NS if k != own):\n"
                              "            return False\n", ''),
    ('armed_no_a_arm', "    for blk in done.values():\n        if blk['arm'] == ARM_A and any(sum(r[k] for r in "
                       "blk['win']) != 0 for k in BURN_NS):\n            return False\n", ''),
    ('armed_zero_ok', "        if sum(r[own] for r in blk['win']) <= 0:", "        if sum(r[own] for r in blk['win']) < 0:"),
    ('armed_no_b_blocks_ok', "    if not b_blocks:\n        return False", "    if not b_blocks:\n        return True"),
    ('arm_lines_empty_ok', "    if not lines:\n        return False", "    if not lines:\n        return True"),
    ('arm_lines_any', "    return all(c == code and d == dose and (thread is None or t == thread) for c, t, d, _q in lines)",
     "    return any(c == code and d == dose and (thread is None or t == thread) for c, t, d, _q in lines)"),
    ('arm_lines_no_dose', "    return all(c == code and d == dose and (thread is None or t == thread) for c, t, d, _q in lines)",
     "    return all(c == code and (thread is None or t == thread) for c, t, d, _q in lines)"),
    ('arm_lines_no_thread', "    return all(c == code and d == dose and (thread is None or t == thread) for c, t, d, _q in lines)",
     "    return all(c == code and d == dose for c, t, d, _q in lines)"),
    ('measure_per_frame_ns', "                per_frame_us=div(s['ns'] / NS_PER_US, len(rows)), "
                             "per_unit_us=div(s['ns'] / NS_PER_US, s['n']),",
     "                per_frame_us=div(float(s['ns']), len(rows)), per_unit_us=div(s['ns'] / NS_PER_US, s['n']),"),
    ('measure_per_unit_frames', "                per_frame_us=div(s['ns'] / NS_PER_US, len(rows)), "
                                "per_unit_us=div(s['ns'] / NS_PER_US, s['n']),",
     "                per_frame_us=div(s['ns'] / NS_PER_US, len(rows)), "
     "per_unit_us=div(s['ns'] / NS_PER_US, len(rows)),"),
    ('measure_cpu_wall_inverted', "                cpu_wall=div(float(s['cpu_ns']), s['cpu_w']), kind=kind,",
     "                cpu_wall=div(float(s['cpu_w']), s['cpu_ns']), kind=kind,"),
    ('measure_a_arm', "    rows = [r for blk in done.values() if blk['arm'] == ARM_B for r in blk['win']]\n"
                      "    keys = ('ns', 'n', 'cpu_ns', 'cpu_w', 'seen')",
     "    rows = [r for blk in done.values() if blk['arm'] == ARM_A for r in blk['win']]\n"
     "    keys = ('ns', 'n', 'cpu_ns', 'cpu_w', 'seen')"),
    ('coverage_no_cover_map', "    name = COVER.get(code, 'burn_%s_seen' % prefix)", "    name = 'burn_%s_seen' % prefix"),
    ('coverage_a_arm', "    s = window_sums(done, ARM_B, keys)", "    s = window_sums(done, ARM_A, keys)"),
    ('dose_check_abs', "                  and abs(measure['per_frame_us'] - DOSE_US) <= DOSE_TOL * DOSE_US),",
     "                  and abs(measure['per_frame_us'] - DOSE_US) < DOSE_TOL * DOSE_US),"),
    ('burn_ok_no_reject', "        burn_ok=raw['burn_cpu_bad'] == 0 and burn['reject'] == 0 and burn['notsc'] == 0 "
                          "and burn['selftest'] > 0,",
     "        burn_ok=raw['burn_cpu_bad'] == 0 and burn['notsc'] == 0 and burn['selftest'] > 0,"),
    ('burn_ok_no_notsc', "        burn_ok=raw['burn_cpu_bad'] == 0 and burn['reject'] == 0 and burn['notsc'] == 0 "
                         "and burn['selftest'] > 0,",
     "        burn_ok=raw['burn_cpu_bad'] == 0 and burn['reject'] == 0 and burn['selftest'] > 0,"),
    ('burn_ok_no_selftest', "        burn_ok=raw['burn_cpu_bad'] == 0 and burn['reject'] == 0 and burn['notsc'] == 0 "
                            "and burn['selftest'] > 0,",
     "        burn_ok=raw['burn_cpu_bad'] == 0 and burn['reject'] == 0 and burn['notsc'] == 0,"),
    ('burn_ok_cpu_bad_le', "        burn_ok=raw['burn_cpu_bad'] == 0 and", "        burn_ok=raw['burn_cpu_bad'] <= 2 and"),
    # ---- pre-registration, admission assembly
    ('pred_draft_refuses', "    if draft:\n        return True, True", "    if draft:\n        return False, False"),
    ('pred_no_bytes', "    sha_ok = (hashlib.sha256(data).hexdigest() == pred_sha and len(data) == pred_bytes\n"
                      "              and prereg.get('sha256') == pred_sha and prereg.get('bytes') == pred_bytes)",
     "    sha_ok = (hashlib.sha256(data).hexdigest() == pred_sha\n"
     "              and prereg.get('sha256') == pred_sha)"),
    ('pred_no_meta_sha', "              and prereg.get('sha256') == pred_sha and prereg.get('bytes') == pred_bytes)",
     "              and prereg.get('bytes') == pred_bytes)"),
    ('pred_path_slashes', "    path_ok = str(prereg.get('path') or '').replace('\\\\', '/') == pred_path",
     "    path_ok = str(prereg.get('path') or '') == pred_path"),
    ('adm_skips_dose', "    admitted = all(checks.values())",
     "    admitted = all(v for k, v in checks.items() if k != 'dose')"),
    ('adm_skips_streams', "    admitted = all(checks.values())",
     "    admitted = all(v for k, v in checks.items() if k != 'streams')"),
    ('check_binary', "        binary=meta.get('binary_sha256') == BUILD_SHA,", "        binary=True,"),
    ('check_installed', "        installed_now=installed_sha == BUILD_SHA,", "        installed_now=True,"),
    ('check_pin_count', "        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and parsed['pins'] == [1],",
     "        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and parsed['pins'][:1] == [1],"),
    ('check_pin_mode', "        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and parsed['pins'] == [1],",
     "        pinned=env.get('KYTY_GPU_CLOCK_PIN') == '1' and len(parsed['pins']) == 1,"),
    ('check_env_schedule_field', "        env_exact=sealed_plan and kyty_env == env_of(tag) and meta.get('schedule') "
                                 "== schedule_of(tag),",
     "        env_exact=sealed_plan and kyty_env == env_of(tag),"),
    ('check_env_exact_subset', "        env_exact=sealed_plan and kyty_env == env_of(tag) and meta.get('schedule') "
                               "== schedule_of(tag),",
     "        env_exact=sealed_plan and all(kyty_env.get(k) == v for k, v in (env_of(tag) or {}).items()) "
     "and meta.get('schedule') == schedule_of(tag),"),
    ('check_hold', "        hold=draft or meta.get('hold_s') == HOLD_S,", "        hold=True,"),
    ('check_attempts_one', "        one_ok_attempt=len(atts) == 1 and len(ok_att) == 1,",
     "        one_ok_attempt=len(ok_att) == 1,"),
    ('check_attempts_hold_exit', "    ok_att = [a for a in atts if a.get('outcome') == 'ok' and "
                                 "a.get('hold_exit') is None]",
     "    ok_att = [a for a in atts if a.get('outcome') == 'ok']"),
    ('check_gates_text', "        gates_exact=(Path(gates_file).is_file() and sha_file(gates_file) == GATES_SHA "
                         "and gates_text == base_text),",
     "        gates_exact=(Path(gates_file).is_file() and sha_file(gates_file) == GATES_SHA),"),
    ('check_gates_sha', "        gates_exact=(Path(gates_file).is_file() and sha_file(gates_file) == GATES_SHA "
                        "and gates_text == base_text),",
     "        gates_exact=(Path(gates_file).is_file() and gates_text == base_text),"),
    ('check_marker', "        no_marker=not parsed['markers'],", "        no_marker=True,"),
    ('check_plan_sealed_value_only', "    sealed_plan = value is not None and code in CODE_GROUP",
     "    sealed_plan = value is not None"),
    # ---- not evaluable and the verdict
    ('ne_pairs_le', "    if not draft and len(pairs) < min_pairs:", "    if not draft and len(pairs) < min_pairs - 1:"),
    ('ne_pairs_draft', "    if not draft and len(pairs) < min_pairs:", "    if len(pairs) < min_pairs:"),
    ('ne_no_two_se', "    if dt['two_se'] is None:\n        ne.append('two_se_undefined')", ''),
    ('ne_regime_same_only', "    if bda['A_regime'] is None or bda['A_regime'] != bda['B_regime'] or "
                            "bda['A_regime'] == 'MIXED':",
     "    if bda['A_regime'] is None or bda['A_regime'] != bda['B_regime']:"),
    ('ne_regime_dropped', "    if bda['A_regime'] is None or bda['A_regime'] != bda['B_regime'] or "
                          "bda['A_regime'] == 'MIXED':\n        ne.append('bda_regime')", ''),
    ('verdict_ne_ignored', "    elif ne or z is None:", "    elif z is None:"),
    ('verdict_repeat_swapped', "        verdict = 'NOT_EVALUABLE' if tag.endswith('r') else 'NOT_ADMITTED'",
     "        verdict = 'NOT_ADMITTED' if tag.endswith('r') else 'NOT_EVALUABLE'"),
    ('zone_super_first', "    if sl['lo'] > S_SUPER:\n        return 'SUPERLINEAR'\n    if sl['lo'] > S_CRIT_LO and "
                         "sl['hi'] >= S_REACH:\n        return 'CRITICAL'",
     "    if sl['lo'] > S_CRIT_LO and sl['hi'] >= S_REACH:\n        return 'CRITICAL'\n    if sl['lo'] > S_SUPER:\n"
     "        return 'SUPERLINEAR'"),
    ('zone_super_ge', "    if sl['lo'] > S_SUPER:", "    if sl['lo'] >= S_SUPER:"),
    ('zone_crit_ge', "    if sl['lo'] > S_CRIT_LO and sl['hi'] >= S_REACH:",
     "    if sl['lo'] >= S_CRIT_LO and sl['hi'] >= S_REACH:"),
    ('zone_crit_no_reach', "    if sl['lo'] > S_CRIT_LO and sl['hi'] >= S_REACH:", "    if sl['lo'] > S_CRIT_LO:"),
    ('zone_crit_reach_gt', "    if sl['lo'] > S_CRIT_LO and sl['hi'] >= S_REACH:",
     "    if sl['lo'] > S_CRIT_LO and sl['hi'] > S_REACH:"),
    ('zone_flat_le', "    if sl['hi'] < S_FLAT_HI:", "    if sl['hi'] <= S_FLAT_HI:"),
    ('zone_flat_lo', "    if sl['hi'] < S_FLAT_HI:", "    if sl['lo'] < S_FLAT_HI:"),
    ('zone_no_none', "    if sl['lo'] is None or sl['hi'] is None:\n        return None",
     "    if sl['lo'] is None or sl['hi'] is None:\n        return 'NOT_RESOLVED'"),
    # ---- the estimator and the slope
    ('estimate_sign', "        diffs.append(a - c)", "        diffs.append(c - a)"),
    ('estimate_window_rows', "        a = mean([r[key] for r in done[bb]['est']])\n"
                             "        c = mean([r[key] for r in done[ab]['est']])",
     "        a = mean([r[key] for r in done[bb]['win']])\n        c = mean([r[key] for r in done[ab]['win']])"),
    ('estimate_pooled_means', "        a = mean([r[key] for r in done[bb]['est']])\n"
                              "        c = mean([r[key] for r in done[ab]['est']])",
     "        a = mean([r[key] for x in pairs for y in x if done[y]['arm'] == ARM_B for r in done[y]['est']])\n"
     "        c = mean([r[key] for x in pairs for y in x if done[y]['arm'] == ARM_A for r in done[y]['est']])"),
    ('slope_uses_two_se', "    s = div(est['delta'], dose)", "    s = div(est['two_se'], dose)"),
    ('slope_no_div', "    s = div(est['delta'], dose)", "    s = est['delta']"),
    ('slope_lo_plus', "    return dict(s=s, two_se=se, lo=None if s is None or se is None else s - se,",
     "    return dict(s=s, two_se=se, lo=None if s is None or se is None else s + se,"),
    ('slope_hi_minus', "                hi=None if s is None or se is None else s + se)",
     "                hi=None if s is None or se is None else s - se)"),
    # ---- the scene
    ('scene_window_rows', "    rows = [r for pr in pairs for b in pr for r in done[b]['est']]",
     "    rows = [r for pr in pairs for b in pr for r in done[b]['win']]"),
    ('scene_gpu_code8', "    if code != 1:\n        gpu_bound = None", "    if code != 8:\n        gpu_bound = None"),
    ('scene_gpu_any_code', "    if code != 1:\n        gpu_bound = None\n    else:\n        gpu_bound = bool(",
     "    if False:\n        gpu_bound = None\n    else:\n        gpu_bound = bool("),
    ('scene_gpu_no_verdict', "        gpu_bound = bool(gpu_ratio is not None and gpu_ratio >= GPU_BOUND and "
                             "verdict == 'NOT_CRITICAL')",
     "        gpu_bound = bool(gpu_ratio is not None and gpu_ratio >= GPU_BOUND)"),
    ('scene_gpu_gt', "        gpu_bound = bool(gpu_ratio is not None and gpu_ratio >= GPU_BOUND and "
                     "verdict == 'NOT_CRITICAL')",
     "        gpu_bound = bool(gpu_ratio is not None and gpu_ratio > GPU_BOUND and verdict == 'NOT_CRITICAL')"),
    ('scene_pinch_gt', "                pinched=None if top[1] is None else bool(top[1] >= PINCH),",
     "                pinched=None if top[1] is None else bool(top[1] > PINCH),"),
    ('vblank_trunc', "        k = max(1, int(round(dt / VBLANK_US)))", "        k = max(1, int(dt / VBLANK_US))"),
    ('vblank_no_floor', "        k = max(1, int(round(dt / VBLANK_US)))", "        k = int(round(dt / VBLANK_US))"),
    ('vblank_top_first', "    top = max(shares.items(), key=lambda kv: kv[1])",
     "    top = sorted(shares.items())[0]"),
    # ---- report lines the fixtures read
    ('rep_delta_se', "    out.append('Delta dt_us (B - A) %s +- %s us (2SE, %d pairs); A %s B %s us'",
     "    out.append('Delta dt_us (B - A) %s +- %s us (SE, %d pairs); A %s B %s us'"),
    ('rep_delta_swap', "               % (fmt(dt['delta']), fmt(dt['two_se']), res['pairs'], fmt(dt['A']), "
                       "fmt(dt['B'])))",
     "               % (fmt(dt['delta']), fmt(dt['two_se']), res['pairs'], fmt(dt['B']), fmt(dt['A'])))"),
    ('rep_slope_zones', "                  fmt(S_CRIT_LO, 1), fmt(S_REACH, 1), fmt(S_FLAT_HI, 1)))",
     "                  fmt(S_REACH, 1), fmt(S_CRIT_LO, 1), fmt(S_FLAT_HI, 1)))"),
    ('rep_dose_line', "        out.append('dose measured: %s us a frame (want %s +-%s %%), %s us an armed unit over "
                      "%d armings on %d B '", "        out.append('dose measured: %s us a frame (want %s +-%s %%), "
                      "%s us an armed unit over %d armings on %d C '"),
    ('rep_dose_args', "                   % (fmt(m['per_frame_us']), fmt(DOSE_US, 0), fmt(100 * DOSE_TOL, 0), "
                      "fmt(m['per_unit_us']),",
     "                   % (fmt(m['per_unit_us']), fmt(DOSE_US, 0), fmt(100 * DOSE_TOL, 0), fmt(m['per_frame_us']),"),
    ('rep_coverage_role', "        out.append('coverage %s = %d%s' % (c['counter'], c['value'],",
     "        out.append('coverage %s = %d%s' % (c['counter'], c['role_value'] or c['value'],"),
    ('rep_pinched_text', "                  'PINCHED (>= %.0f %%: a saving smaller than the distance to the next step "
                         "does not move FPS)'", "                  'pinched-ish'"),
    ('rep_gpu_bound_na', "    out.append('GPU-bound: %s' % ('n/a (not the GuestGpu arm - only code 1 can answer it)' "
                         "if s['gpu_bound'] is None", "    out.append('GPU-bound: %s' % ('unknown' "
                         "if s['gpu_bound'] is None"),
    ('rep_bda_regimes', "    out.append('bda_scan A %s (%s) B %s (%s)' % (fmt(res['bda_scan']['A']), "
                        "res['bda_scan']['A_regime'],",
     "    out.append('bda_scan A %s (%s) B %s (%s)' % (fmt(res['bda_scan']['A']), res['bda_scan']['B_regime'],"),
    ('rep_not_admitted', "        out.append('REPORT OF A NOT_ADMITTED RUN - NOT TO BE QUOTED')", '        pass'),
    ('rep_draft', "        out.append('DRAFT: unsealed scoring (pre-registration, hold and the pair floor not "
                  "checked) - not a verdict')", '        pass'),
    ('rep_ne_line', "    out.append('not evaluable: %s' % (', '.join(res['not_evaluable']) or '-'))",
     "    out.append('not evaluable: -')"),
    ('rep_admission', "    out.append('ADMISSION: %s%s' % (res['admission'], ' failed=' + ','.join(failed) if failed "
                      "else ''))", "    out.append('ADMISSION: ADMITTED')"),
    ('rep_verdict_line', "    out.append('VERDICT: %s slope=%s 2se=%s interval=%s..%s pairs=%d bda=%s reading=%s%s'",
     "    out.append('VERDICT: %s slope=%s 2SE=%s interval=%s..%s pairs=%d bda=%s reading=%s%s'"),
    ('rep_consequence', "    out.append('CONSEQUENCE: %s%s' % (CONSEQUENCE[res['verdict']], note))",
     "    out.append('CONSEQUENCE: %s%s' % (CONSEQUENCE['NOT_RESOLVED'], note))"),
    ('rep_scene_line', "    out.append('  scene %s; arm B burn=%s (code %s %s, dose %s us), arm A burn=0'",
     "    out.append('  scene %s; arm A burn=%s (code %s %s, dose %s us), arm B burn=0'"),
    ('rep_blocks_line', "    out.append('  blocks %d complete %d pairs %d (floor %d); estimator frames A %d B %d'",
     "    out.append('  blocks %d complete %d pairs %d (floor %d); estimator frames B %d A %d'"),
    # ---- the chain gate --plan-check
    ('plan_check_unknown_ok', "        return 2, 'map122: no PLAN entry for tag %s' % tag",
     "        return 0, 'map122: no PLAN entry for tag %s' % tag"),
    ('plan_check_unsealed_ok', "        return 1, ('map122: the arm of tag %s is NOT sealed",
     "        return 0, ('map122: the arm of tag %s is NOT sealed"),
    ('plan_check_value_only', "    if v is None or code_dose(v)[0] not in CODE_GROUP:\n        return 1,",
     "    if v is None:\n        return 1,"),
    ('plan_check_main_plan', "        rc, text = plan_check(sys.argv[sys.argv.index('--plan-check') + 1], PLAN_DEFAULT)",
     "        rc, text = plan_check(sys.argv[sys.argv.index('--plan-check') + 1], {})"),
]
if __name__ == '__main__':
    STAGE.mkdir(parents=True, exist_ok=True)
    killed = 0
    for name, old, new in MUTANTS:
        if SRC.count(old) != 1:
            print('%-28s ANCHOR x%d' % (name, SRC.count(old)))
            continue
        path = STAGE / ('mut_map122_%s.py' % name)
        path.write_bytes(SRC.replace(old, new).encode('utf-8'))
        r = subprocess.run([sys.executable, 'C:/kyty/s122/test_map122.py', str(path)], capture_output=True, text=True)
        killed += r.returncode != 0
        print('%-28s %s' % (name, 'killed' if r.returncode != 0 else 'SURVIVED'))
        path.unlink()
    print('killed %d of %d' % (killed, len(MUTANTS)))

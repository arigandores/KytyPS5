"""Session 117, ROADMAP item 11: mutants for the pre-seal fixes of spn117.py."""
from pathlib import Path

p = Path('C:/kyty/s117/mut_spn117.py')
s = p.read_text(encoding='utf-8')


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


rep("""    ('armed_arm0_cmp', "and ksum(0, 'spine_cmp') == 0", ''),""",
    """    ('armed_arm0_cmp', "and 100 * ksum(0, 'spine_cmp') <= ksum(0, 'spine_el')", ''),
    ('armed_arm0_cmp_lt', "100 * ksum(0, 'spine_cmp') <= ksum(0, 'spine_el')", "100 * ksum(0, 'spine_cmp') < ksum(0, 'spine_el')"),""")
rep("""    ('k5_bad', "if sums_all['spine_bad'] > 0 or sums_all['spine_misal'] > 0:", "if sums_all['spine_misal'] > 0:"),
    ('k5_misal', "if sums_all['spine_bad'] > 0 or sums_all['spine_misal'] > 0:", "if sums_all['spine_bad'] > 0:"),""",
    """    ('k5_bad', "if raw_k5['spine_bad'] > 0 or ", 'if '),
    ('k5_misal', "raw_k5['spine_misal'] > 0 or raw_k5['cram_write'] > 0", "raw_k5['cram_write'] > 0"),
    ('k5_cram', " or raw_k5['cram_write'] > 0 or k5_lines > 0:", ' or k5_lines > 0:'),
    ('k5_lines', " or k5_lines > 0:\\n        k5 = 'FAIL'", ":\\n        k5 = 'FAIL'"),
    ('k5_lines_prefix', "K5_LINES = (b'SpineMismatch:', b'SpineMisalign:')", "K5_LINES = (b'SpineMismatch:',)"),
    ('k5_raw_start', '                if kind == \\'x\\' and n > START:', '                if kind == \\'x\\' and n > START + PERIOD:'),
    ('k5_raw_cram', "K5_RAW = ('spine_bad', 'spine_misal', 'cram_write')", "K5_RAW = ('spine_bad', 'spine_misal')"),
    ('k5_complete_only', "    if raw_k5['spine_bad'] > 0 or raw_k5['spine_misal'] > 0",
     "    if sums_all['spine_bad'] > 0 or raw_k5['spine_misal'] > 0"),
    ('el_ops_off', 'el_ops=(ops1 > 0 and ', 'el_ops=(True or '),
    ('el_ops_lo', 'EL_OPS_LO_PCT = 95', 'EL_OPS_LO_PCT = 94'),
    ('el_ops_hi', 'EL_OPS_HI_PCT = 105', 'EL_OPS_HI_PCT = 106'),
    ('el_ops_ops', "    ops1 = ksum(1, 'draws') + ksum(1, 'dispatches')", "    ops1 = ksum(1, 'draws')"),
    ('arms_consecutive', 'ok = bool(blocks) and sorted(blocks) == list(range(len(blocks)))', 'ok = bool(blocks)'),
    ('rec_full', 'seen[kind][n] = rec if len(rec) == len(names) else None', 'seen[kind][n] = rec'),
    ('pin_parse', 'pins.append(int(mp.group(1)) if mp else -1)', 'pins.append(int(mp.group(1)) if mp else 1)'),""")
rep("""    ('walker_lt', 'walker_fit = walker_need is not None and dt0 is not None and walker_need < dt0',
     'walker_fit = walker_need is not None and dt0 is not None and walker_need <= dt0'),""",
    """    ('walker_lt', 'walker_need is not None and frame_nospine is not None and walker_need < frame_nospine',
     'walker_need is not None and frame_nospine is not None and walker_need <= frame_nospine'),
    ('walker_old_rule', "    frame_nospine = mean([v['dt_us'] - v['spine_us'] for v in values[0]])",
     "    frame_nospine = mean([v['dt_us'] for v in values[0]])"),""")
p.write_text(s, encoding='utf-8')
print('mut ok')

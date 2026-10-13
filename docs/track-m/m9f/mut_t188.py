"""Track M link M9f (HPP-871): mutants of the T188 rules t188_rules.py - each must be killed by test_t188.py (the mutlib suite).
One or more mutants per stop member, per edge of a relation and per row rule: the field tuples and constants (share 0.8, at most 2
classes, cover 0.5, plan mode), the parser (the prefix test, unparsable counts, key=other, the class field offset, the mode tuple),
N (mode line and unparsable mode), E (exit counts, key=other, periodic rows, each unparsable count), Z (the invariant list and the
zero test), N (I7), I1, I2a-d, I3 (the tint_skip sum), I4 (each relation at its edge), I6 (each equation, each bound, the K x classes
bound and key=other), I8, I5 (the exit total, part, the condition and its direction), I9 (each chain at its edge), the class choice
(share edge, the limit, the zero row, the tie order, key=other), the class rows (the global zeros, rb0_ok, the cover edge), open, the
T109 rows of 791 (v) and 789 (g)(3).
Not mutated, EQUIVALENT or not reachable by the suite (proofs):
 (1) t109_rows "w == 'periodic' and" removed, or "and i + 1 <= len(d) - 1" removed: with whens[-1] == 'exit' required, the exit
     line is the last line, so "the line i is periodic" and "the line i has a later line" say the same (the exit line is the only
     line without a later line, and the only exit line) - each conjunct is redundant given the other;
 (2) checks "and len(img) >= 1" of I3 removed: with no row every class sum is 0 and the fixture globals are non-zero, so I3 fails by
     the sums; a state with all 27 globals 0 and no row is also caught by E (rows >= 1);
 (3) scan(): file I/O and the FrameTrace skip are not in the in-process suite; scan() runs in test_m9f.py on the real M6c log;
 (4) the text of the member names and the docstring.
Run through the frozen mutlib v4.1 FULL (never --changed-from), ONE counted run:
    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/m657/m9f/t188_rules.py
        --test C:/kyty/m657/m9f/test_t188.py --mutants C:/kyty/m657/m9f/mut_t188.py --control --no-memo --workers 8
        --work-dir C:/kyty/m657/m9f/mutwork --cache-dir C:/kyty/m657/m9f/mutcache --out C:/kyty/m657/m9f/mut_t188.txt
Every anchor occurs exactly once in t188_rules.py (LF).  ASCII only."""

MUTANTS = [
    # constants and tuples
    ('inv_no_lock', "INVARIANTS = ('part_unk', 'ep_bad', 'lock_bad', 'tint_bad', 'tint_rb0_bad', 'tint_rb1_bad')",
     "INVARIANTS = ('part_unk', 'ep_bad', 'tint_bad', 'tint_rb0_bad', 'tint_rb1_bad')"),
    ('inv_no_rb0bad', "INVARIANTS = ('part_unk', 'ep_bad', 'lock_bad', 'tint_bad', 'tint_rb0_bad', 'tint_rb1_bad')",
     "INVARIANTS = ('part_unk', 'ep_bad', 'lock_bad', 'tint_bad', 'tint_rb1_bad')"),
    ('clall_no_dt', "CL_ALL = ('cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt',", "CL_ALL = ('cl_smp', 'cl_rt', 'cl_rtclr',"),
    ('clall_with_none', "'cl_commit', 'cl_copydst', 'cl_skip')\nCL_S3", "'cl_commit', 'cl_copydst', 'cl_skip', 'cl_none')\nCL_S3"),
    ('cls3_no_vo', "CL_S3 = ('cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt', 'cl_sto', 'cl_clrop', 'cl_oth', 'cl_vo')",
     "CL_S3 = ('cl_smp', 'cl_rt', 'cl_rtclr', 'cl_dt', 'cl_sto', 'cl_clrop', 'cl_oth')"),
    ('skips_no_ovf', "SKIPS = ('tint_skip_fmt', 'tint_skip_vol', 'tint_skip_cls', 'tint_skip_cpu', 'tint_skip_ovf')",
     "SKIPS = ('tint_skip_fmt', 'tint_skip_vol', 'tint_skip_cls', 'tint_skip_cpu')"),
    ('i3_ev_off', "('ev_off', ('part_off',))", "('ev_off', ('part_synced',))"),
    ('plan_k3', "PLAN_MODE = (2, 'all', 4)", "PLAN_MODE = (2, 'all', 3)"),
    ('share_079', "SHARE = 0.8 ", "SHARE = 0.79 "),
    ('max_3', "MAX_CLASSES = 2 ", "MAX_CLASSES = 3 "),
    ('cover_049', "COVER_MIN = 0.5 ", "COVER_MIN = 0.49 "),
    ('stat_swap', "'part', 'part_st', 'part_fill',", "'part', 'part_fill', 'part_st',"),
    ('t109_swap', "T109 = ('d32', 'zx_d32', 'zx_narrow',", "T109 = ('d32', 'zx_narrow', 'zx_d32',"),
    # parser
    ('rx_mode_digits', "cls=([0-9a-z]+) k=", "cls=([0-9]+) k="),
    ('pfx_or', "if b'T188' not in line and b'T109Stat:' not in line:", "if b'T188' not in line or b'T109Stat:' not in line:"),
    ('stat_bad_2', "            r['stat_bad'] += 1\n        return True\n    if b'T188Img:'",
     "            r['stat_bad'] += 2\n        return True\n    if b'T188Img:'"),
    ('img_other_flip', "if g[12] is not None:", "if g[12] is None:"),
    ('img_cls_off', "for k, v in zip(CLS, g[13:]):", "for k, v in zip(CLS, g[12:]):"),
    ('img_bad_no', "            r['img_bad'] += 1", "            r['img_bad'] += 0"),
    ('t109_no_append', "            r['t109'].append(d)", "            pass"),
    ('t109_bad_no', "            r['t109_bad'] += 1", "            r['t109_bad'] += 0"),
    ('mode_k_swap', "r['mode'].append((int(m.group(1)), m.group(2).decode(), int(m.group(3))))",
     "r['mode'].append((int(m.group(3)), m.group(2).decode(), int(m.group(1))))"),
    ('mode_bad_no', "            r['mode_bad'] += 1", "            r['mode_bad'] += 0"),
    # N, E, Z
    ('n_no_modebad', "r['mode'] == [PLAN_MODE] and r['mode_bad'] == 0)", "r['mode'] == [PLAN_MODE])"),
    ('e_ge1', "nex == 1 and nex9 == 1)", "nex >= 1 and nex9 == 1)"),
    ('e_no_t109', "nex == 1 and nex9 == 1)", "nex == 1)"),
    ('e_other_2', "len(img_ex) >= 1 and n_other <= 1 and", "len(img_ex) >= 1 and n_other <= 2 and"),
    ('e_rows_0', "len(img_ex) >= 1 and n_other <= 1 and", "len(img_ex) >= 0 and n_other <= 1 and"),
    ('e_periodic_ok', "and len(img_ex) == len(r['img']))", ")"),
    ('e_no_statbad', "r['stat_bad'] == 0 and r['img_bad'] == 0", "r['img_bad'] == 0"),
    ('e_no_t109bad', "and r['t109_bad'] == 0 and r['mode_bad'] == 0)", "and r['mode_bad'] == 0)"),
    ('z_gt1', "for k in INVARIANTS if s[k] != 0]", "for k in INVARIANTS if s[k] > 1]"),
    ('z_exit_only', "for i, s in enumerate(r['stat']) for k in INVARIANTS", "for i, s in enumerate(r['stat'][-1:]) for k in INVARIANTS"),
    ('i7_no', "e['tint_skip_cls'], e['tint_skip_cls'] == 0)", "e['tint_skip_cls'], True)"),
    # I1, I2, I4
    ('i1_no_unk0', "e['part'] == ssum(e, ('part_st', 'part_fill', 'part_copy', 'part_unk')) and e['part_unk'] == 0)",
     "e['part'] == ssum(e, ('part_st', 'part_fill', 'part_copy', 'part_unk')))"),
    ('i1_no_copy', "e['part'] == ssum(e, ('part_st', 'part_fill', 'part_copy', 'part_unk')) and",
     "e['part'] == ssum(e, ('part_st', 'part_fill', 'part_unk')) + e['part_copy'] * 0 + 10 and"),
    ('i2a_no_reopen', "a = ssum(e, ('part_synced', 'part_dlmem', 'reopen', 'ep_new'))", "a = ssum(e, ('part_synced', 'part_dlmem', 'ep_new')) + 15"),
    ('i2b_no_open', "ssum(e, CL_ALL) + e['open']", "ssum(e, CL_ALL) + 8"),
    ('i2c_no_open', "p = ssum(e, ('pend_done', 'pend_drop', 'pend_free', 'pend_open'))", "p = ssum(e, ('pend_done', 'pend_drop', 'pend_free')) + 1"),
    ('i2d_lt', "e['ep_pend'] <= ssum(e, CL_S3))", "e['ep_pend'] < ssum(e, CL_S3))"),
    ('i4_w', "w = ssum(e, ('w_mipal', 'w_inmip', 'w_other'))", "w = ssum(e, ('w_mipal', 'w_inmip')) + 20"),
    ('i4_off_lt', "e['part_off'] <= e['part'] and e['w_bytes']", "e['part_off'] < e['part'] and e['w_bytes']"),
    ('i4_wb_lt', "e['w_bytes'] <= e['img_bytes'] and e['img_bytes_unsync']", "e['w_bytes'] < e['img_bytes'] and e['img_bytes_unsync']"),
    ('i4_ub_lt', "e['img_bytes_unsync'] <= e['img_bytes'])", "e['img_bytes_unsync'] < e['img_bytes'])"),
    ('i4_ip_lt', "e['in_pass_unsync'] <= e['in_pass'] <= e['part'])", "e['in_pass_unsync'] < e['in_pass'] <= e['part'])"),
    ('i4_ip2_lt', "e['in_pass_unsync'] <= e['in_pass'] <= e['part'])", "e['in_pass_unsync'] <= e['in_pass'] < e['part'])"),
    ('i4_ip_nopart', "e['in_pass_unsync'] <= e['in_pass'] <= e['part'])", "e['in_pass_unsync'] <= e['in_pass'])"),
    # I3
    ('i3_ne_gt', "            if sc != sg:", "            if sc > sg:"),
    ('i3_no_other', "        img = [g for g in r['img'] if g['when'] == 'exit']\n        i3 = []",
     "        img = [g for g in r['img'] if g['when'] == 'exit' and g['key'] != 'other']\n        i3 = []"),
    # I6, I8
    ('i6_no_pend', "tint_s3 = ssum(e, CL_S3) + e['pend_done']", "tint_s3 = ssum(e, CL_S3)"),
    ('i6_no_bad', "e['tint_ep'] <= tint_s3 and e['tint_bad'] == 0)", "e['tint_ep'] <= tint_s3)"),
    ('i6_cls_ge', "if g['tint_bytes'] > g['lost_bytes'] + g['lost_pend_bytes']]", "if g['tint_bytes'] >= g['lost_bytes'] + g['lost_pend_bytes']]"),
    ('i6_cls_nopend', "if g['tint_bytes'] > g['lost_bytes'] + g['lost_pend_bytes']]", "if g['tint_bytes'] > g['lost_bytes'] + 50]"),
    ('i6_req_nofmt', "rb0 = ssum(e, ('tint_rb0_ok', 'tint_rb0_bad', 'tint_rb0_none', 'tint_rb0_nofmt'))",
     "rb0 = ssum(e, ('tint_rb0_ok', 'tint_rb0_bad', 'tint_rb0_none'))"),
    ('i6_rb1_none', "rb1 = ssum(e, ('tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad', 'tint_rb1_none'))",
     "rb1 = ssum(e, ('tint_rb1_ok', 'tint_rb1_over', 'tint_rb1_bad')) + 1"),
    ('i6_no_rb0bad', "e['tint_rb0_ok'] == rb1 and e['tint_rb0_bad'] == 0 and e['tint_rb1_bad'] == 0)",
     "e['tint_rb0_ok'] == rb1 and e['tint_rb1_bad'] == 0)"),
    ('i6_no_rb1bad', "e['tint_rb0_ok'] == rb1 and e['tint_rb0_bad'] == 0 and e['tint_rb1_bad'] == 0)",
     "e['tint_rb0_ok'] == rb1 and e['tint_rb0_bad'] == 0)"),
    ('i6_k_plus', "e['tint_rb_req'] <= k * ncls)", "e['tint_rb_req'] <= (k + 1) * ncls)"),
    ('i6_other_0', "sum(g['tint_ep'] for g in img if g['key'] == 'other')", "0"),
    ('i8_no_lock', "e['ep_bad'] == 0 and e['lock_bad'] == 0)", "e['ep_bad'] == 0)"),
    # I5
    ('i5_any_when', "if m5_total is None or m5_total.get('when') != 'exit':", "if m5_total is None:"),
    ('i5_no_part', "ok1 = e['part'] == m5_total['inv_part_src']", "ok1 = True"),
    ('i5_cond_flip', "cond = m5_total['inv_part'] == m5_total['inv_part_src']", "cond = m5_total['inv_part'] != m5_total['inv_part_src']"),
    ('i5_always', "ok2 = (not cond) or e['part_off'] == m5_total['inv_off']", "ok2 = e['part_off'] == m5_total['inv_off']"),
    # I9
    ('i9_zx_lt', "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out",
     "t['zx_narrow'] < t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out"),
    ('i9_zxd_nod', "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out",
     "t['zx_narrow'] <= t['zx_d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out"),
    ('i9_bias_lt', "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out",
     "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] < t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out"),
    ('i9_bn_nob', "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out",
     "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out"),
    ('i9_vpc_lt', "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out",
     "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] < t['ovr_w'])\n    return out"),
    ('i9_novpc', "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'] and t['ovr_vpc'] <= t['ovr_w'])\n    return out",
     "t['zx_narrow'] <= t['zx_d32'] <= t['d32'] and t['bias_narrow'] <= t['bias_d32'] <= t['d32'])\n    return out"),
    # class choice / rows / open
    ('ch_gt', "if acc >= SHARE * total or len(chosen) >= MAX_CLASSES:", "if acc > SHARE * total or len(chosen) >= MAX_CLASSES:"),
    ('ch_lim_gt', "if acc >= SHARE * total or len(chosen) >= MAX_CLASSES:", "if acc >= SHARE * total or len(chosen) > MAX_CLASSES:"),
    ('ch_zero_go', "            if v == 0:\n                break", "            if v < 0:\n                break"),
    ('ch_tie', "key=lambda g: (-(g['lost_bytes'] + g['lost_pend_bytes']), -g['ev'], g['key']))",
     "key=lambda g: (-(g['lost_bytes'] + g['lost_pend_bytes']), g['ev'], g['key']))"),
    ('ch_other', "img = [g for g in r['img'] if g['when'] == 'exit' and g['key'] != 'other']\n    total =",
     "img = [g for g in r['img'] if g['when'] == 'exit']\n    total ="),
    ('ch_reached_gt', "reached = bool(total) and acc >= SHARE * total", "reached = bool(total) and acc > SHARE * total"),
    ('ch_nopend', "v = g['lost_bytes'] + g['lost_pend_bytes']\n            if v == 0:", "v = g['lost_bytes']\n            if v == 0:"),
    ('cr_glob', "glob_ok = e is not None and e['tint_rb0_bad'] == 0 and e['tint_rb1_bad'] == 0",
     "glob_ok = e is not None and e['tint_rb0_bad'] == 0"),
    ('cr_rb0', "g['tint_rb0_ok'] >= 1 and glob_ok", "g['tint_rb0_ok'] >= 0 and glob_ok"),
    ('cr_other', "readback_alive=(g['key'] != 'other' and", "readback_alive=("),
    ('cr_cov_gt', "cover_ge_05=(cov is not None and cov >= COVER_MIN)", "cover_ge_05=(cov is not None and cov > COVER_MIN)"),
    ('open_any', "if e is None or e['ep_bad'] != 0:\n        return None", "if e is None:\n        return None"),
    # T109 rows
    ('t109_any', "dv >= 1 and all(x >= 1 for x in d[i + 1:])", "dv >= 1 and any(x >= 1 for x in d[i + 1:])"),
    ('t109_dv0', "dv >= 1 and all(x >= 1 for x in d[i + 1:])", "dv >= 0 and all(x >= 1 for x in d[i + 1:])"),
    ('t109_noexit', "and i + 1 <= len(d) - 1 and whens[-1] == 'exit':", "and i + 1 <= len(d) - 1:"),
    ('t109_bias_zx', "db, bc = part('bias_narrow', 'bias_narrow_vi')", "db, bc = part('zx_narrow', 'zx_narrow_vi')"),
    ('t109_eq_no1', "zx_eq_all=(t['zx_narrow'] >= 1 and t['zx_narrow'] == t['zx_narrow_vi'])",
     "zx_eq_all=(t['zx_narrow'] == t['zx_narrow_vi'])"),
]

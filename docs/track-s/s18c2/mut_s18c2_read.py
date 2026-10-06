"""Track S link S18c2 (HPP-654; ROADMAP s122 item 586 (g)-(d)): mutants of the S18c2 reader s18c2_read.py - every function and constant of
the module (the S18c reader it loads is sealed and unchanged, mutated in S18c: 118 of 118): the constants of the seal (BASE_SHA, KNOWN, HOLD,
SPEC of s18_w2), the paths of the two roots, the catalogue admission (known_rows), the members of item 586 (g)(1)-(4) (rebuild_line,
validation_stop, w2_rows), the dispatch of the group W2, the outputs (main, table).  Each must be killed by test_s18c2_read.py.
Run through the frozen mutlib v4.1 FULL (never --changed-from), ONE counted run on the final text:
    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s288/s18c2/s18c2_read.py
        --test C:/kyty/s288/s18c2/test_s18c2_read.py --mutants C:/kyty/s288/s18c2/mut_s18c2_read.py --control --no-memo --workers 12
        --work-dir C:/kyty/s288/s18c2/mutwork --cache-dir C:/kyty/s288/s18c2/mutcache --out C:/kyty/s288/s18c2/mut_s18c2_read.txt
The cheap failures (constants) stand before the full paths (item 112 (a)).
"""
MUTANTS = [
    # constants of the seal
    ('base_sha', "BASE_SHA = '16570bed3667", "BASE_SHA = '16570bed3668"),
    ('known_45', "('replay.45.bin', 6250527, '12cb3787", "('replay.45.bin', 6250528, '12cb3787"),
    ('known_46', "'332a2f2d6aef0e8b64ccfe366d87df3476117abaf3b6aaf736ffbec2befc7c9a'", "'332a2f2d6aef0e8b64ccfe366d87df3476117abaf3b6aaf736ffbec2befc7c9b'"),
    ('known_cur', "('replay.cur', 3, 'a5331f18", "('replay.cur', 2, 'a5331f18"),
    ('known_dir', "KNOWN_DIR = 'replay_known'", "KNOWN_DIR = 'replay'"),
    ('hold', 'HOLD = 310\n', 'HOLD = 300\n'),
    ('spec_env', "env={'KYTY_SHADER_SEED': '0'}, group='W2')", "env={}, group='W2')"),
    ('spec_state', "form='w', hold=HOLD, state='cat_full',", "form='w', hold=HOLD, state='inst_cat',"),
    ('spec_form', "R.SPEC[TAG] = dict(level=R.SKY, form='w',", "R.SPEC[TAG] = dict(level=R.SKY, form='v',"),
    ('spec_level', "R.SPEC[TAG] = dict(level=R.SKY,", "R.SPEC[TAG] = dict(level=R.MGG,"),
    # paths and dispatch
    ('paths_all', '    if tag != TAG:\n        return _paths(tag)\n', '    if False:\n        return _paths(tag)\n'),
    ('paths_root', '    R.ROOT = ROOT2\n', '    R.ROOT = SRC_ROOT\n'),
    ('paths_restore', '        R.ROOT = old\n', '        pass\n'),
    ('dispatch_all', "    if R.SPEC[tag]['group'] == 'W2':\n", "    if True:\n"),
    ('dispatch_none', "    if R.SPEC[tag]['group'] == 'W2':\n", "    if False:\n"),
    ('install_paths', 'R.paths = paths\n', 'pass\n'),
    ('install_w', 'R.w_rows = w_rows\n', 'pass\n'),
    ('base_root', 'R.ROOT = SRC_ROOT\n', 'R.ROOT = ROOT2\n'),
    # catalogue admission
    ('files_isfile', '            if os.path.isfile(fp):\n', '            if True:\n'),
    ('known_base', "rows.a('S18c reader s18c_read.py = the S18c seal (sha256 %s)' % BASE_SHA[:16], bs == BASE_SHA, bs)",
     "rows.a('S18c reader s18c_read.py = the S18c seal (sha256 %s)' % BASE_SHA[:16], True, bs)"),
    ('known_manifest', "(3 files, size, sha256)' % KNOWN_DIR, got == want,", "(3 files, size, sha256)' % KNOWN_DIR, len(got) == len(want),"),
    ('known_c19', 'got == c19 and len(got) > 0,', 'len(got) > 0,'),
    ('known_c19_empty', 'got == c19 and len(got) > 0,', 'got == c19,'),
    # member (1)
    ('rbl_records', "    rb = [d for _, d in r['rebuild'] if 'records' in d]\n", "    rb = [d for _, d in r['rebuild']]\n"),
    ('rbl_last', '    return rb[-1] if rb else None\n', '    return rb[0] if rb else None\n'),
    ('m1_line', "rows.m('W2 (1) a line ShaderReplay: rebuild records=', rb is not None,", "rows.m('W2 (1) a line ShaderReplay: rebuild records=', True,"),
    ('m1_skipped', "rows.m('W2 (1) no line rebuild skipped', not r['skipped'],", "rows.m('W2 (1) no line rebuild skipped', True,"),
    ('m1_seed_log', "r['seed'] == 0 and so['seed'] == 0, '%d / %d'", "so['seed'] == 0, '%d / %d'"),
    ('m1_seed_out', "r['seed'] == 0 and so['seed'] == 0, '%d / %d'", "r['seed'] == 0, '%d / %d'"),
    # member (2)
    ('m2_share_gt', 'None if share is None else share >= R.SHARE_MIN,', 'None if share is None else share > R.SHARE_MIN,'),
    ('m2_share_none', 'None if share is None else share >= R.SHARE_MIN,', 'share is not None and share >= R.SHARE_MIN,'),
    ('m2_recs0', '    share = None if (prep is None or not recs) else prep / float(recs)\n',
     '    share = None if (prep is None or recs is None) else prep / float(recs or 1)\n'),
    ('m2_ident_pend', 'else prep + rej + pend == recs\n', 'else prep + rej == recs\n'),
    ('m2_ident_none', '    ident = None if None in (recs, prep, rej, pend) else', '    ident = False if None in (recs, prep, rej, pend) else'),
    ('m2_written', "rows.m('W2 (2) pipelines_bin=written', rb.get('pipelines_bin') == 'written',",
     "rows.m('W2 (2) pipelines_bin=written', rb.get('pipelines_bin') != 'stopped',"),
    # member (3)
    ('m3_vke', "rows.m('W2 (3) 0 [Vulkan][E]', r['vke'] == 0, r['vke'])", "rows.m('W2 (3) 0 [Vulkan][E]', True, r['vke'])"),
    ('m3_limit', "rows.m('W2 (3) 0 limit lines of the layer', r['vk_limit'] == 0,", "rows.m('W2 (3) 0 limit lines of the layer', True,"),
    ('m3_vkw', "           r['vkw'] > 0 and len(dual_before) >= 1,", "           len(dual_before) >= 1,"),
    ('m3_dual_any', "           r['vkw'] > 0 and len(dual_before) >= 1,", "           r['vkw'] > 0 and len(r['dual']) >= 1,"),
    ('m3_dual_before', "x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]", "x[1] == 1 and x[2] == 1]"),
    ('m3_dual_sup', "x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]", "x[0] < r['first_guest'] and x[2] == 1]"),
    ('m3_dual_en', "x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]", "x[0] < r['first_guest'] and x[1] == 1]"),
    ('m3_vs_member', "    rows.m('W2 (3) no VALIDATION_STOP (the process ended before the end of the hold with a [Vulkan][E] line)', not vs,",
     "    rows.m('W2 (3) no VALIDATION_STOP (the process ended before the end of the hold with a [Vulkan][E] line)', True,"),
    ('vs_e', "    return r['vke'] > 0 and not R.lived(att, HOLD)\n", "    return r['vke'] >= 0 and not R.lived(att, HOLD)\n"),
    ('vs_lived', "    return r['vke'] > 0 and not R.lived(att, HOLD)\n", "    return r['vke'] > 0\n"),
    ('vs_hold', "    return r['vke'] > 0 and not R.lived(att, HOLD)\n", "    return r['vke'] > 0 and not R.lived(att, 300)\n"),
    # member (4)
    ('m4_entered', "rows.m('W2 (4) entered (Level has started: %s, outcome ok)' % spec['level'], R.entered(r, att),",
     "rows.m('W2 (4) entered (Level has started: %s, outcome ok)' % spec['level'], r['entry_line'] is not None,"),
    ('m4_lived', "rows.m('W2 (4) the process lived to the end of the hold (%d s)' % spec['hold'], R.lived(att, spec['hold']),",
     "rows.m('W2 (4) the process lived to the end of the hold (%d s)' % spec['hold'], R.lived(att, 300),"),
    ('m4_deaths', "rows.m('W2 (4) 0 death markers (log, stdout)', R.deaths(r, so) == 0,", "rows.m('W2 (4) 0 death markers (log, stdout)', len(r['death']) == 0,"),
    # outputs
    ('extra_records', "    extra['rebuild'] = dict((k, rb.get(k)) for k in ('records', 'prepared',", "    extra['rebuild'] = dict((k, rb.get(k)) for k in ('prepared',"),
    ('main_tag', '    if argv[0] != TAG:\n', '    if False:\n'),
    ('main_json', '            json.dump(R.to_json(TAG, rows, meta), f, indent=1)\n', '            json.dump({}, f, indent=1)\n'),
    ('table_row', "    print('  %-8s W2   %-28s READING %s' % (TAG, R.SKY, d['reading']))\n", "    print('  %-8s W2   %-28s' % (TAG, R.SKY))\n"),
    ('table_members', "    for name, ok, det in d['members']:\n        print('      %-15s %s | %s' % (R.yn(ok), R.asc(name), R.asc(det)[:200]))\n    return 0\n",
     "    return 0\n"),
]

"""Session 145 link 1b (HPP-379; ROADMAP s122 item 295 (v), (e), (z)): mutants of the changed and new lines of
step2/gate145.py - each must be killed by step2/test_gate145.py (the suite loads the gate under test from argv[1]).
Run through the frozen mutlib v4.1 with --control --no-memo --only over every mutant of this list (item 295 (z)):
    python C:/kyty/KytyPS5/docs/session-116/mutlib_v41/mutlib.py --scorer C:/kyty/s145/step2/gate145.py
        --test C:/kyty/s145/step2/test_gate145.py --mutants C:/kyty/s145/step2/mut_gate145.py --control --no-memo
        --workers 12 --work-dir C:/kyty/s145/mutwork_1bg --cache-dir C:/kyty/s145/mutcache_1bg
Not mutated (the unchanged lines of step 0 / 0b; no mutant run of the gate existed before link 1b).  Every anchor
occurs exactly once in gate145.py (LF).
"""
MUTANTS = [
    ('g_pred', "PRED = ROOT + '/pred/03_sc145.md'", "PRED = ROOT + '/pred/02_sc145.md'"),
    ('g_refseal', "REF_SEAL = 'C:/kyty/s144/runs144/cache_w144_20.after.json'", "REF_SEAL = 'C:/kyty/s144/runs144/cache_w144_19.after.json'"),
    ('g_minfree', 'MIN_FREE = 60 * 2 ** 30', 'MIN_FREE = 60 * 10 ** 9'),
    ('g_disk', "DISK = 'C:/'", "DISK = 'D:/'"),
    ('g_rx', "re.findall(r'W 295(\\(b\\)\\(\\d\\))', s)", "re.findall(r'W 295(\\(b\\)\\(1\\))', s)"),
    ('g_wab_none', "    if not os.path.isfile(score):\n        return None\n    with open(score, 'r', encoding='utf-8', errors='replace') as f:\n        for line in f:\n            s = line.strip()\n            if s.startswith('admission:'):\n                return re.findall", "    if not os.path.isfile(score):\n        return []\n    with open(score, 'r', encoding='utf-8', errors='replace') as f:\n        for line in f:\n            s = line.strip()\n            if s.startswith('admission:'):\n                return re.findall"),
    ('g_wab_noline', "    return ['no admission line']\n\n\ndef made", '    return []\n\n\ndef made'),
    ('g_f4', '            if not f4[0]:\n', '            if False:\n'),
    ('g_f4_nojson', "                False, 'NO JSON')", "                True, 'NO JSON')"),
    ('g_wb_none', "            if wb is None:\n                bad.append('(v) W", "            if False:\n                bad.append('(v) W"),
    ('g_wb', "            elif wb:\n                bad.append('(v) W", "            elif False:\n                bad.append('(v) W"),
    ('g_ref_cmp', "    if got is None or got != want:\n        bad.append('(r)", "    if got is None:\n        bad.append('(r)"),
    ('g_ref_none', "    if got is None or got != want:\n        bad.append('(r)", "    if got != want:\n        bad.append('(r)"),
    ('g_free_cmp', '    if fr < MIN_FREE:\n', '    if fr <= MIN_FREE:\n'),
    ('g_early', "    if got is None:\n        det.append('(c)(1) not evaluable", "    if False:\n        det.append('(c)(1) not evaluable"),
]

"""Session 109: derive ent109b.py and test_ent109b.py (the powered guard of knob "cspfree" as an ABBA of entries)
from the unpinned session-109 ent109.py / test_ent109.py by anchored substitutions.  Byte-reproducible."""
from pathlib import Path

STAGE = Path('C:/kyty/s106_stage')


def derive(src, dst, pairs, count_ok=None):
    s = (STAGE / src).read_bytes().decode('utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        n = s.count(a)
        want = (count_ok or {}).get(a, 1)
        assert n == want, (src, a[:70], n)
        s = s.replace(a, b)
    (STAGE / dst).write_bytes(s.encode('utf-8'))
    print('wrote', dst)


derive('ent109.py', 'ent109b.py', [
    ('"""Session 109, pred/01_ent109.md: the powered guard of `cspfam` v2 as an ABBA of ENTRIES.',
     '"""Session 109, pred/02_ent109b.md: the powered guard of knob `cspfree` as an ABBA of ENTRIES (derived from\nent109.py by make_ent109b.py).'),
    ('(A = gates_fam0.txt, cspfam=0; B = gates_fam4.txt, cspfam=4 = v2 at K=4), 150 s each, pinned.',
     '(A = gates_free0.txt, cspfree=0; B = gates_free1.txt, cspfree=1), 150 s each, pinned.'),
    ('NO_POWER  admitted and S_A == 0 (nothing to catch: v2 is not shipped on this run)',
     'NO_POWER  admitted and S_A == 0 (nothing to catch: cspfree is not taken further on this run)'),
    ("python C:/kyty/s109/ent109.py", "python C:/kyty/s109/ent109b.py"),
    ("PRED = 'C:/kyty/s109/pred/01_ent109.md'", "PRED = 'C:/kyty/s109/pred/02_ent109b.md'"),
    ("BINARY_SHA = 'e90f55438d95b3b673cde11275965f9ec8a342db40dd4063c4ea8d6836443d40'",
     "BINARY_SHA = '2f5932296d564b1098831b75a7fc6c8796d3a9ac7e871ea0c3a1c6b0610a4b77'"),
    ("TAGS = ['ent109_%d' % (i + 1) for i in range(len(ORDER))]",
     "TAGS = ['ent109b_%d' % (i + 1) for i in range(len(ORDER))]"),
    ("TOKEN = {'A': 'cspfam=0', 'B': 'cspfam=4'}", "TOKEN = {'A': 'cspfree=0', 'B': 'cspfree=1'}"),
    ("FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspfam_clr', 'cspf_new')",
     "FIELDS = ('cs_sync_new', 'cs_sync_wait', 'cspfam_look', 'cspfam_skip', 'cspfam_clr', 'cspf_new', 'cspfree_look',\n          'cspfree_hit', 'cspfree_bad')"),
    ("    if arm == 'A' and (tot['cspfam_skip'] or tot['cspfam_look']):",
     "    if arm == 'A' and (tot['cspfree_hit'] or tot['cspfree_look']):"),
    ("    if arm == 'B' and tot['cspfam_skip'] <= 0:", "    if arm == 'B' and (tot['cspfree_hit'] <= 0 or tot['cspfree_bad']):"),
    ("""        print('  %-10s %s rows %6s  sync_new %4s  sync_wait %4s  S %4s  cspf_new %4s  skip %9s  clr %6s  %s'
              % (e['tag'], e['arm'], e.get('rows'), e.get('cs_sync_new'), e.get('cs_sync_wait'), e.get('s'),
                 e.get('cspf_new'), e.get('cspfam_skip'), e.get('cspfam_clr'), ','.join(e['fails']) or 'ok'))""",
     """        print('  %-11s %s rows %6s  sync_new %4s  sync_wait %4s  S %4s  cspf_new %4s  free_look %8s  hit %8s  %s'
              % (e['tag'], e['arm'], e.get('rows'), e.get('cs_sync_new'), e.get('cs_sync_wait'), e.get('s'),
                 e.get('cspf_new'), e.get('cspfree_look'), e.get('cspfree_hit'), ','.join(e['fails']) or 'ok'))"""),
])

test_pairs = [
    ('"""Session 109: fixtures for ent109.py.', '"""Session 109: fixtures for ent109b.py (derived by make_ent109b.py).'),
    ("BASE = Path('C:/kyty/s106_stage/fx_ent109')", "BASE = Path('C:/kyty/s106_stage/fx_ent109b')"),
    ("spec = importlib.util.spec_from_file_location('ent109', SRC)",
     "spec = importlib.util.spec_from_file_location('ent109b', SRC)"),
    ("seal.write_bytes(b'fixture seal 109 ent')", "seal.write_bytes(b'fixture seal 109 entb')"),
    ("""        fields = 'cs_sync_new=%d cs_sync_wait=%d cspfam_look=%d cspfam_skip=%d cspfam_clr=%d cspf_new=0' % (
            sn, sw, look, skip, 1 if arm == 'B' else 0)""",
     """        fields = ('cs_sync_new=%d cs_sync_wait=%d cspfam_look=0 cspfam_skip=0 cspfam_clr=%d cspf_new=0 '
                  'cspfree_look=%d cspfree_hit=%d cspfree_bad=%d') % (sn, sw, 1 if arm == 'B' else 0, look, skip,
                                                                     bad.get('free_bad', 0) if n == 700 else 0)"""),
    ("'ent109_", "'ent109b_"),
    ("GATES + ' cspfam=4'", "GATES + ' cspfree=1'"),
    ("GATES + ' cspfam=0 cspfam=4'", "GATES + ' cspfree=0 cspfree=1'"),
    ("    ('ARM_B_dark', dict(per={B0: {'b_skip': 0}}), 'NOT_ADMITTED', ['ent109b_2:ARM_B_ARMED']),\n",
     "    ('ARM_B_dark', dict(per={B0: {'b_skip': 0}}), 'NOT_ADMITTED', ['ent109b_2:ARM_B_ARMED']),\n"
     "    ('ARM_B_bad', dict(per={B0: {'free_bad': 1}}), 'NOT_ADMITTED', ['ent109b_2:ARM_B_ARMED']),\n"),
]
s = (STAGE / 'test_ent109.py').read_bytes().decode('utf-8').replace('\r\n', '\n')
n_tag = s.count("'ent109_")
for a, b in test_pairs:
    n = s.count(a)
    assert n == (n_tag if a == "'ent109_" else 1), (a[:60], n)
    s = s.replace(a, b)
(STAGE / 'test_ent109b.py').write_bytes(s.encode('utf-8'))
print('wrote test_ent109b.py')

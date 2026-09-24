"""Audit 113 final (protocol lens): ROADMAP item 15(b) trigger scan on the derived sealed suites (read-only; a copy of
mutlib/review3/scan_six.py pointed at vbn113d/e/f, shn113 (sealed and draft mutants) and check113).  Run with -B."""
import ast, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s106_stage/mutlib/review3')
sys.path.insert(0, 'C:/kyty/s106_stage/mutlib')
import scan_six as S  # noqa: E402
import mutlib  # noqa: E402
R = Path('C:/kyty/s113')
SUITES = [
    ('vbn113d', R / 'vbn113d.py', R / 'test_vbn113d.py', R / 'mut_vbn113d.py'),
    ('vbn113e', R / 'vbn113e.py', R / 'test_vbn113e.py', R / 'mut_vbn113e.py'),
    ('vbn113f', R / 'vbn113f.py', R / 'test_vbn113f.py', R / 'mut_vbn113f.py'),
    ('shn113 sealed', R / 'shn113.py', R / 'test_shn113.py', R / 'mut_shn113_sealed.py'),
    ('shn113 draft', Path('C:/kyty/s106_stage/shn113b/shn113.py'), R / 'test_shn113.py', R / 'mut_shn113.py'),
    ('check113', R / 'check113.py', R / 'test_check113.py', R / 'mut_check113.py'),
]
for name, scorer, test, mutf in SUITES:
    print('== %s' % name)
    s = S.suite_scan(test)
    print('   exit expression: %s (names %s)' % (s['exit_expr'], s['exit_names']))
    print('   ok &= operands: %s' % s['ok_updates'])
    print('   ok &= inside a try: %s' % (s['ok_updates_in_try'] or 'none'))
    print('   raw sys.stdout.write calls: %s; sys.argv[2] uses: %s' % (s['raw_stdout_writes'] or 'none', s['argv2'] or 'none'))
    fmt, muts, _, coll = mutlib.extract_mutants(mutf)
    other, loops, skips = S.mut_scan(mutf, coll)
    print('   mutants: %s format, %d extracted; other tuple lists %s; loop iterables %s; continue at %s'
          % (fmt, len(muts), other or 'none', loops, skips or 'none'))
    rec, plan, leak = S.scorer_scan(scorer)
    print('   scorer: recursive functions %s; memo plan %s; path-leak candidates %s' % (rec or 'none', plan, leak or 'none'))

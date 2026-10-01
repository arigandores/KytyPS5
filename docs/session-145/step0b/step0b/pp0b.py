"""s145 step 0b (HPP-350, ROADMAP s122 item 288 (d)): the seal path pred/01_sc145.md -> pred/02_sc145.md - only the path, in
the scorer, the chain, the wrapper comment, the fixtures and the anchor of the mutant e_pred (LF, every anchor exactly once)."""
R = 'C:/kyty/s145/'
EDITS = [
    ('sc145.py', "PRED_PATH = 'C:/kyty/s145/pred/01_sc145.md'", "PRED_PATH = 'C:/kyty/s145/pred/02_sc145.md'"),
    ('go145a.sh', 'PRED="pred/01_sc145.md"', 'PRED="pred/02_sc145.md"'),
    ('step2/call_one.sh', '(pred/01_sc145.md)', '(pred/02_sc145.md)'),
    ('test_go145a.py', "(root / 'pred' / '01_sc145.md')", "(root / 'pred' / '02_sc145.md')"),
    ('test_go145a.py', "'--pred %s/pred/01_sc145.md' % rp", "'--pred %s/pred/02_sc145.md' % rp"),
    ('test_go145a.py', 'the seal 01_sc145, no checkpoints', 'the seal 02_sc145, no checkpoints'),
    ('test_go145a.py', "'g25 the chain reads the seal pred/01_sc145.md and the scorer sc145.py', 'PRED=\"pred/01_sc145.md\"'",
     "'g25 the chain reads the seal pred/02_sc145.md and the scorer sc145.py', 'PRED=\"pred/02_sc145.md\"'"),
    ('test_sc145.py', "S.PRED_PATH == 'C:/kyty/s145/pred/01_sc145.md'", "S.PRED_PATH == 'C:/kyty/s145/pred/02_sc145.md'"),
    ('mut_sc145.py', """('e_pred', "PRED_PATH = 'C:/kyty/s145/pred/01_sc145.md'", "PRED_PATH = 'C:/kyty/s145/pred/01_sc144.md'"),""",
     """('e_pred', "PRED_PATH = 'C:/kyty/s145/pred/02_sc145.md'", "PRED_PATH = 'C:/kyty/s145/pred/01_sc145.md'"),"""),
]
for f, old, new in EDITS:
    p = R + f
    t = open(p, 'rb').read().decode('utf-8')
    assert '\r' not in t, f
    assert t.count(old) == 1, (f, old)
    t = t.replace(old, new)
    open(p, 'wb').write(t.encode('utf-8'))
    print('edited %s' % f)
for f in ('sc145.py', 'go145a.sh', 'step2/call_one.sh', 'test_go145a.py', 'test_sc145.py', 'step2/gate145.py',
          'step2/next_one.sh', 'step2/pre_one.sh', 'step2/wait_one.sh', 'step2/apichk145.py', 'step2/table145.py'):
    t = open(R + f, 'rb').read().decode('utf-8')
    assert '01_sc145' not in t, f
print('no 01_sc145 left in the scorer, chain, wrappers, gate and fixtures')

"""F33c2 (HPP-748): fixtures of run_stand_f33c2.parse on the F33d stderr samples (docs/track-f/f33d/runs/samples,
5e79c4f9): probe CN at =1 (code F33c), probe CN with m4b, C with m4b. Last line 'ALL OK'.
    python test_driver_f33c2.py <samples dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_stand_f33c2 as D  # noqa: E402

S = sys.argv[1]
CASES = [
    ('probe_CN_1001.err', 'CN', dict(walks=1, nested=0, reenter=2, expired=0, expired_seen=0, done_seen=0,
                                     nested_fatal=1)),
    ('probe_m4b_CN_1001.err', 'CN', dict(walks=1, nested=0, reenter=2, expired=1, expired_seen=1, nested_fatal=1)),
    ('m4b_C_1001.err', 'C', dict(walks=1, nested=0, done_seen=1, nested_fatal=0)),
]
ok = True
for name, arm, exp in CASES:
    r = D.parse(arm, open(os.path.join(S, name), encoding='utf-8', errors='replace').read())
    bad = {k: (r[k], v) for k, v in exp.items() if r[k] != v}
    ok = ok and not bad
    print('%-4s %-24s %s' % ('ok' if not bad else 'FAIL', name, bad or {k: r[k] for k in exp}))
print('ALL OK' if ok else 'FIXTURES FAILED')
sys.exit(0 if ok else 1)

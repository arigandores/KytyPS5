"""S13a4: s13/mkseal_s13.py from s13/mkseal_s12.py (the seal 13 replaces 12).  Each replacement exactly once.  LF, ASCII."""
S13 = 'C:/kyty/s288/s13'
src = open(S13 + '/mkseal_s12.py', 'rb').read().decode('ascii')
R = [
    ('mkseal_s12.py - track S, link S13a3 (HPP-537; ROADMAP "SESSION 122" item 408 (l), item 436 (v)(2)): writes the seal',
     'mkseal_s13.py - track S, link S13a4 (HPP-553; ROADMAP "SESSION 122" item 408 (l), item 452 (d)(2)): writes the seal'),
    ('C:/kyty/s288/pred/12_s.md (it replaces pred/11_s.md, not in force) from s13/seal12_body.md and s13/seal12_tail.md',
     'C:/kyty/s288/pred/13_s.md (it replaces pred/12_s.md, not in force) from s13/seal13_body.md and s13/seal13_tail.md'),
    ('    python mkseal_s12.py', '    python mkseal_s13.py'),
    ("SEAL = ROOT + '/pred/12_s.md'", "SEAL = ROOT + '/pred/13_s.md'"),
    ("OLD = ROOT + '/pred/11_s.md'", "OLD = ROOT + '/pred/12_s.md'"),
    ("'# Seal 12_s - track S", "'# Seal 13_s - track S"),
    ("item 428, item 434 (b), item 436)', ''", "item 428, item 434 (b), item 436, item 446, item 452)', ''"),
    ("by link S13a3 (HPP-537, the rework of item 436 (v)), '", "by link S13a4 (HPP-553, the rework of item 452 (d)), '"),
    ("It replaces pred/11_s.md (sha256 %s), which is not in force (item 436 (v)(2)).",
     "It replaces pred/12_s.md (sha256 %s), which is not in force (item 452 (d)(2))."),
    ('the only later document is the edition pred/12b_s.md of section 1', 'the only later document is the edition pred/13b_s.md of section 1'),
    ("'pred/12_s.md sha256 <sha>\").  S13b runs only after the review S13r2 and the lead line accepting this seal, and after '",
     "'pred/13_s.md sha256 <sha>\").  S13b runs only after the review S13r3 and the lead line accepting this seal, and after '"),
    ("'/seal12_body.md'", "'/seal13_body.md'"),
    ("'/seal12_tail.md'", "'/seal13_tail.md'"),
]
for a, b in R:
    n = src.count(a)
    if n != 1:
        raise SystemExit('mk_mkseal13: the target occurs %d times: %r' % (n, a[:90]))
    src = src.replace(a, b)
src.encode('ascii')
open(S13 + '/mkseal_s13.py', 'wb').write(src.encode('ascii'))
print('mkseal_s13.py written, %d replacements; lines naming 12: %s' % (len(R), [i + 1 for i, x in enumerate(src.split(chr(10)))
                                                                         if '12' in x]))

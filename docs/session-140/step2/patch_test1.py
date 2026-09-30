"""Step 2 (HPP-268): fixtures that kill the survivors of the pre-screen; se_blocks_min declared equivalent (LF, write_bytes;
each anchor exactly once; refuses under the lock)."""
import sys
from pathlib import Path

if Path('C:/kyty/SEALED_RUN.lock').exists():
    sys.exit('lock held - not editing')
p = Path('C:/kyty/s140/test_pm4c140.py')
t = p.read_bytes().decode('utf-8')
assert '\r' not in t
R = [
# generator: drop the draw or the x line of a row
("""        lines += row_lines(n, idx, on, s, xo, dict(m_over or {}, **h.get('m_over', {})), g_ns, fpk, d0_off,
                           h.get('drop_pm4', False), cmd_n, h.get('pm4_line_first', False), h.get('sub', SUB_SITES))
""", """        rl = row_lines(n, idx, on, s, xo, dict(m_over or {}, **h.get('m_over', {})), g_ns, fpk, d0_off,
                       h.get('drop_pm4', False), cmd_n, h.get('pm4_line_first', False), h.get('sub', SUB_SITES))
        drop = tuple({'d': 'FrameTrace-draw:', 'x': 'FrameTrace-x:'}[k] for k in h.get('drop_lines', ()))
        lines += [l for l in rl if not (drop and l.startswith(drop))]
"""),
# the real minimum captured before the override
("""ok = True
SMALL = 200
""", """ok = True
SMALL = 200
REAL_MIN = S.MIN_NEW_ROWS
"""),
("""S.MIN_NEW_ROWS = 4000
ok &= case('D0 the real minimum is 4000 NEW window rows', S.MIN_NEW_ROWS == 4000)
""", """S.MIN_NEW_ROWS = REAL_MIN
ok &= case('D0 the real minimum is 4000 NEW window rows (the scorer constant, read before any override)', REAL_MIN == 4000)
"""),
("""S.MIN_NEW_ROWS = 4000
rc, txt = run_main(['--tag', 'pm4c140c', '--dir', str(Rk)])
S.MIN_NEW_ROWS = SMALL
ok &= case('M6 a call below 4000 NEW rows -> RUN_DEBT rc 1', rc == 1 and 'VERDICT pm4c140c: RUN_DEBT' in txt)
""", """S.MIN_NEW_ROWS = REAL_MIN
rc, txt = run_main(['--tag', 'pm4c140c', '--dir', str(Rk)])
S.MIN_NEW_ROWS = SMALL
ok &= case('M6 a call below 4000 NEW rows -> RUN_DEBT rc 1, the masked line says DEBT', rc == 1
           and 'VERDICT pm4c140c: RUN_DEBT' in txt and 'NEW window rows (item 212 (v)) 200 -> DEBT' in txt)
rc, txt = run_main(['--tag', 'pm4c140b', '--dir', str(census(runs={t: dict(sites=on_sites(op2a=([99, 99, 100, 100, 100], 1000)))
                                                                     for t in S.ON}))])
ok &= case('M6b c_k 100.1 ns: the masked line says c_k in the band NO, RUN_FAIL', rc == 1 and 'c_k in [3, 100] ns: NO' in txt
           and 'IF5b FAIL' in txt)
"""),
("""           and '450' not in re.sub(r'[0-9a-f]{16,}', '', json.dumps(jb)))
""", """           and '450' not in re.sub(r'[0-9a-f]{16,}', '', json.dumps(jb))
           and '19.5' not in re.sub(r'[0-9a-f]{16,}', '', json.dumps(jb)) and jb['c_cands'] == ['op2a', 'E'])
"""),
# parser survivors
("""write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(skip=True) if n == 1810 else {})
""", """write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(after=['FrameTrace-x: n=1806 bda_scan=1']) if n == 1806 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('W3b a duplicate FrameTrace-x: line of one n drops the row whole', 1806 not in [r['n'] for r in w] and p['dups'] == 1)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_lines=('x',)) if n == 1804 else {})
p = S.parse_log(str(R0 / 'log_pm4c140b.txt'))
w, rng, last = S.window(p)
ok &= case('W3c a frame without its FrameTrace-x: line: not full, its pm4 line is an orphan (the x line opens the place of '
           'the pm4 line, not the draw line)', 1804 not in [r['n'] for r in w] and p['orphans'] == 1 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_lines=('d',)) if n == 1804 else {})
w, rng, last = S.window(S.parse_log(str(R0 / 'log_pm4c140b.txt')))
ok &= case('W3d a frame without its FrameTrace-draw: line is not full', 1804 not in [r['n'] for r in w] and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(drop_pm4=True) if n == 1810 else {})
w, rng, last = S.window(S.parse_log(str(R0 / 'log_pm4c140b.txt')))
ok &= case('W6 the last FULL row sets the end: the last frame without its pm4 line is not the last full row (1809 is, and '
           'is excluded)', last == 1809 and len(w) == 9)
write_run(R0, 'pm4c140b', rows=10, row_hook=lambda i, n: dict(skip=True) if n == 1810 else {})
"""),
# IF0 rows
("""for name, kw in IF0_CASES:
    o = decide(census(runs={'pm4c140b': kw}))
    ok &= case('IF0 %s -> INSTRUMENT_FAIL (pm4c140b IF0)' % name, o['outcome'] == 'INSTRUMENT_FAIL'
               and 'pm4c140b IF0' in o['if_fails'])
""", """for name, kw in IF0_CASES:
    o = decide(census(runs={'pm4c140b': kw}))
    ok &= case('IF0 %s -> INSTRUMENT_FAIL (pm4c140b IF0)' % name, o['outcome'] == 'INSTRUMENT_FAIL'
               and 'pm4c140b IF0' in o['if_fails'])
    rows0 = dict(o['runs']['pm4c140b']['if']['IF0'])
    if name == 'json missing':
        ok &= case('IF0 json missing names the row json readable NO', rows0.get('json readable') is False)
    if name == 'log missing':
        ok &= case('IF0 log missing names the row log present NO and still carries the json rows',
                   rows0.get('log present') is False and rows0.get('json readable') is True)
Rg = census()
(Rg / 'gates_base.txt').write_bytes((GATES_TEXT + ' extra=1' + chr(10)).encode('ascii'))
for tg in S.SEQ:
    jp = Rg / ('%s.json' % tg)
    mt = json.loads(jp.read_text(encoding='utf-8'))
    mt['gates'] = GATES_TEXT + ' extra=1'
    jp.write_text(json.dumps(mt), encoding='utf-8')
o = decide(Rg)
ok &= case('IF0e a base file other than the sealed sha (the json gates equal to it) -> IF0 in every run',
           sorted(o['if_fails']) == ['pm4c140a IF0', 'pm4c140b IF0', 'pm4c140c IF0', 'pm4c140d IF0'])
"""),
# the 2SE by blocks, the break-even with a deduction and asymmetric, c-SENSITIVE by the minimum
("""ok &= case('A7 the 2SE of a constant level is 0 by blocks of 90 rows (200 rows -> 2 blocks)', close(tb['REG']['se2b'], 0.0))
""", """ok &= case('A7 the 2SE of a constant level is 0 by blocks of 90 rows (200 rows -> 2 blocks)', close(tb['REG']['se2b'], 0.0))
ok &= case('A6b the break-even of MM_out uses B = mean(sum raw* - A): (251 - 400) / 5.268 and (251 - 325) / 5.268',
           close(tb['MM_out']['cstar_mean'], 1000 * (251.0 - 400) / 5268) and close(tb['MM_out']['cstar_min'],
                                                                                   1000 * (251.0 - 325) / 5268))
o = decide(census(runs={t: dict(rows=180, sites=on_sites(op69=([300] * 90 + [310] * 91, 0))) for t in S.ON}))
ok &= case('A7b 2SE by blocks of 90: block means 300.5 and 310.5 -> SE 5.0 -> 2SE 10.0',
           close(o['table']['REG']['se2b'], 10.0) and close(o['table']['REG']['se2c'], 10.0))
o = decide(census(runs={'pm4c140b': dict(sites=on_sites(op69=([418, 419], 2000))),
                        'pm4c140c': dict(sites=on_sites(op69=([428, 429], 2000)))}))
ok &= case('A6c the break-even of the minimum is the smaller of b and c: min(1000 (419 - 325) / 2000, 1000 (429 - 325) / 2000) = 47',
           close(o['table']['REG']['cstar_min'], 47.0))
o = decide(census(runs={t: dict(sites=on_sites(op69=([349, 350], 2000))) for t in S.ON}))
ok &= case('A6d c-SENSITIVE by the minimum alone: REG raw 350 at 2000 packets - c*min 12.5 in (3, 19.5), c*mean < 0',
           o['sensitive'] == ['REG'] and close(o['table']['REG']['cstar_min'], 12.5) and o['table']['REG']['cstar_mean'] < 0)
"""),
]
for a, b in R:
    assert t.count(a) == 1, a[:70]
    t = t.replace(a, b)
p.write_bytes(t.encode('utf-8'))

m = Path('C:/kyty/s140/mut_pm4c140.py')
u = m.read_bytes().decode('utf-8')
a = ("    ('se_blocks_min', \"    if nb < 2:\\n        return float('nan')\\n    bm\", "
     "\"    if nb < 1:\\n        return float('nan')\\n    bm\"),\n")
assert u.count(a) == 1, 'se_blocks_min anchor'
u = u.replace(a, '')
a2 = "nan/inf ('n/a'); the SystemExit(2)"
assert u.count(a2) == 1
u = u.replace(a2, "nan/inf ('n/a'); se_blocks `nb < 2` -> `nb < 1` (sd of one block mean is nan either way); the SystemExit(2)")
m.write_bytes(u.encode('utf-8'))
print('patched')

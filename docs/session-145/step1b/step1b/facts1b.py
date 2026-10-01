"""Session 145 link 1b (HPP-379): append the section "Step 1b" to C:/kyty/s145/FACTS.md from step1b/facts1b_tpl.md, the
lines of step1b/times.txt and the sha256 of the last outputs; mark the seal 02 replaced in the section Step 0b.  usage:
facts1b.py <commit text>"""
import hashlib
import re
import sys

R = 'C:/kyty/s145/'
B = R + 'step1b/'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


T = open(B + 'facts1b_tpl.md', encoding='utf-8').read()
rows = []
for line in open(B + 'times.txt', encoding='utf-8', errors='replace'):
    line = line.rstrip('\n')
    if not line.strip():
        continue
    t, _, ev = line.partition(' ')
    ev = ev.replace('|', '/')
    rows.append('| %s | %s |' % (t.replace('2026-10-01T', '').rstrip('Z'), ev if len(ev) <= 220 else ev[:217] + '...'))
b3 = []
for l in open(B + 'regress144.out.txt', encoding='ascii'):
    m = re.match(r'^NEW295 (w144_\d\d) W: held; \(b\)\(1\) 0 -> PASS; \(b\)\(2\) \d+ -> PASS; \(b\)\(3\) (\d+) us -> PASS', l)
    if m:
        b3.append((m.group(1), int(m.group(2))))
b3txt = 'у %d удержанных W без лимита (%s) последняя строка слоя %s мкс до последней строки удержания' % (
    len(b3), ', '.join(t for t, _ in b3), ', '.join('%d' % v for _, v in b3))
val = dict(TIMES_SHA=sha(B + 'times.txt')[:16] + '…', TIMES='\n'.join(rows), SHA_GO=sha(R + 'go145a.sh'), DRY=sha(B + 'dry145.out.txt')[:16] + '…',
           T_GO=sha(B + 'test_go145a.out.txt'), SHA_SC=sha(R + 'sc145.py'), SHA_GT=sha(R + 'step2/gate145.py'),
           START_DRY=sha(B + 'start_dry1b.out.txt'), T_GT=sha(B + 'test_gate145.out.txt'),
           T_GTC=sha(B + 'test_gate145_copyarg.out.txt'), T_SC=sha(B + 'test_sc145.out.txt'), REG144=sha(B + 'regress144.out.txt'),
           DIFF=sha(B + 'regress144_diff.out.txt'), B3RANGE=b3txt, REG143=sha(B + 'regress143.out.txt')[:16] + '…',
           REG142=sha(B + 'regress142.out.txt')[:16] + '…', CALIB=sha(B + 'calib145.out.txt')[:16] + '…',
           CHECK1B=sha(B + 'check1b145.out.txt')[:16] + '…', VQ=sha(B + 'vq_rt.out.txt'), MUT1=sha(B + 'mut_only1b_sc.txt'),
           MUT2=sha(B + 'mut_only1b_sc2.txt'), MUTG=sha(B + 'mut_only1b_gate.log'), SEAL=sha(R + 'pred/03_sc145.md'),
           CHECKSEAL=sha(B + 'checkseal145.out.txt'), COMMIT=sys.argv[1])
for k, v in val.items():
    assert T.count('{%s}' % k) == 1, k
    T = T.replace('{%s}' % k, v)
assert not re.findall(r'\{[A-Z_0-9]+\}', T)
F = open(R + 'FACTS.md', encoding='utf-8').read()
assert '## Step 1b' not in F
old = '- печать **`C:/kyty/s145/pred/02_sc145.md` sha256 `493c237d25da415f7287f6d53e1e40e9833b29a071118bcc77f9d3c38f448e4d`**'
assert F.count(old) == 1
F = F.replace(old, old + ' (**заменена** печатью `pred/03_sc145.md`, звено 1б, п. 295)')
F = F.rstrip('\n') + '\n' + T
open(R + 'FACTS.md', 'w', encoding='utf-8', newline='\n').write(F)
print('FACTS.md sha256 %s; rows %d; b3 %s' % (sha(R + 'FACTS.md'), len(rows), b3txt))

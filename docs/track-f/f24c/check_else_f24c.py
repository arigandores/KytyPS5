"""Track F link F24c (HPP-662, ROADMAP s122 item 595(e)(2)): the KYTY_FIX_B13=0 branch of
RegionManager::ChangeState<Cpu, true> is the text before F24c verbatim. Reads the block of the site from the parent file
(the body of `if constexpr (source == DirtySource::Cpu && enable) {` after the bits, up to its closing line) and the
`else` branch of the patched file; the patched branch, minus its two F24c comment lines and with one leading tab removed
from every line that is not a preprocessor line, must equal the parent body line for line. Also checks that the =1 branch
holds the three publications in the order region epoch, bit, global epoch, each once.

    python check_else_f24c.py <parent regionManager.h> <patched regionManager.h>
"""
import sys

T2, T3 = '\t' * 2, '\t' * 3


def lines(path):
    return open(path, 'rb').read().decode('utf-8').replace('\r\n', '\n').split('\n')


def site(L):
    hits = [i for i, l in enumerate(L) if l == T2 + 'if constexpr (source == DirtySource::Cpu && enable) {'
            and i + 1 < len(L) and ('Called with the region lock held' in L[i + 1] or L[i + 1] == T3 + 'if (FixB13Enabled()) {')]
    if len(hits) != 1:
        sys.exit('site: %d hits' % len(hits))
    s = hits[0]
    e = s + 1
    while L[e] != T2 + '}':
        e += 1
    return L[s + 1:e]


old = site(lines(sys.argv[1]))
new = site(lines(sys.argv[2]))
ok = True
if new[0] != T3 + 'if (FixB13Enabled()) {':
    sys.exit('patched site does not start with the knob test')
k = new.index(T3 + '} else {')
fix, rest = new[1:k], new[k + 1:]
if rest[-1] != T3 + '}':
    sys.exit('else branch not closed')
rest = rest[:-1]
marks = [l for l in rest[:2] if 'Track F, F24c' in l or 'B13, ROADMAP s122 item 595' in l]
if len(marks) != 2:
    ok = False
    print('FAIL the two F24c comment lines of the else branch not found')
body = [l if l.startswith('#') else (l[1:] if l.startswith('\t') else 'NO-TAB:' + l) for l in rest[2:]]
same = body == old
ok &= same
print('else branch: %d lines, parent body: %d lines, equal after one tab: %s' % (len(body), len(old), same))
if not same:
    for i, (a, b) in enumerate(zip(old, body)):
        if a != b:
            print('  first difference at body line %d:\n    parent: %r\n    else:   %r' % (i + 1, a, b))
            break
order = [i for i, l in enumerate(fix) for key in ('m_epoch.fetch_add(1, std::memory_order_release);',
                                                  'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);',
                                                  'm_cpu_epoch.fetch_add(1, std::memory_order_release);')
         if l.strip() == key]
names = [fix[i].strip().split('(')[0] for i in order]
good = names == ['m_epoch.fetch_add', 'BdaNoteRegionWrite', 'm_cpu_epoch.fetch_add'] and order == sorted(order)
ok &= good
print('=1 branch publications in order: %s: %s' % (' -> '.join(names), 'ok' if good else 'FAIL'))
reset = [i for i, l in enumerate(fix) if 'B2Reuse::ResetCpu' in l]
good = len(reset) == 1 and order and reset[0] > order[-1]
ok &= good
print('=1 branch B2Reuse reset after the global epoch: %s' % ('ok' if good else 'FAIL'))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

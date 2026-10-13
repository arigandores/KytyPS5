"""M5b: T200 77076965 - memory ops reachable after the vscnt sites, including through back edges (loops). Read-only."""
import os, sys
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc_tr_m5b.py'), encoding='utf-8').read()
src = src[:src.index('progs = sorted(')]
ns = {}
exec(compile(src, 'rc_tr_m5b', 'exec'), ns)
D = 'C:/kyty/f287/f23a/eboot_text/'
h = '77076965e0344358'
b = open(D + h + '.bin', 'rb').read()
words = [int.from_bytes(b[i:i + 4], 'little') for i in range(0, len(b) // 4 * 4, 4)]
ins = ns['walk'](words)
by = {t[0]: t for t in ins}
order = [t[0] for t in ins]
nxt = {order[i]: order[i + 1] for i in range(len(order) - 1)}
def succ(pc):
    t = by[pc]; fam, info = t[1], t[5]
    out = []
    if fam == 'SOPP':
        op = info['op']
        if op in ns['ENDS']:
            return []
        simm = info['imm'] - 0x10000 if info['imm'] & 0x8000 else info['imm']
        if op == 2:
            return [pc + 1 + simm]
        if op in ns['BR_COND']:
            out.append(pc + 1 + simm)
    if pc + t[4] in by:
        out.append(pc + t[4])
    return out
backedges = [(pc, s) for pc in order for s in succ(pc) if s <= pc]
print('back edges', backedges)
for site in (1148, 1257):
    seen = set(); work = [site]
    while work:
        p = work.pop()
        for s in succ(p):
            if s not in seen:
                seen.add(s); work.append(s)
    mem = []
    for p in sorted(seen):
        fam = by[p][1]
        if fam in ('MUBUF', 'MTBUF', 'FLAT', 'MIMG', 'SMEM', 'DS'):
            w = by[p][2]
            if fam == 'MUBUF':
                op = ((w >> 18) & 0x7f) | (((w >> 25) & 1) << 7)
            elif fam == 'SMEM':
                op = (w >> 18) & 0xff
            elif fam == 'DS':
                op = (w >> 18) & 0xff
            else:
                op = None
            mem.append((p, fam, op))
    print('site', site, 'reachable instr', len(seen), 'reaches itself', site in seen)
    import collections
    print('  mem ops reachable', collections.Counter((f, o) for _, f, o in mem))
    print('  first 12', mem[:12])
print('ALL DONE')

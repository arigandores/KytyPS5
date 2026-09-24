# Per-arm means of EVERY FrameTrace field over the main-window rows (audit 111). Two runs compared:
#   python allfields.py <tagA> <armA> <tagB> <armB>   (logs from C:/kyty/s111 or s110)
import sys, re, pickle
sys.path.insert(0, 'C:/kyty/s111/audit111')
from abba import load, blocks
tok = re.compile(rb'([A-Za-z_][A-Za-z_0-9]*)=(-?\d+)')
LOGS = {'shp111': 'C:/kyty/s111/log_shp111.txt', 'shp110': 'C:/kyty/s110/log_shp110.txt'}


def arm_rows(tag, arm):
    P = load(tag); garm, elig, pairs, mism, rej = blocks(P, 10, 90, 2100)
    used = sorted({b for p in pairs for b in p})
    return {n for b in used if garm[b] == arm for n in elig[b]}


def sums(tag, want):
    acc = {0: {}, 1: {}}; cnt = {0: 0, 1: 0}
    arm_of = {}
    for a in (0, 1):
        for n in want[a]: arm_of[n] = a
    seen = {0: set(), 1: set()}
    with open(LOGS[tag], 'rb') as f:
        for raw in f:
            if not raw.startswith(b'FrameTrace'): continue
            sp = raw.find(b' ')
            kind = raw[:sp]
            if kind not in (b'FrameTrace:', b'FrameTrace-draw:', b'FrameTrace-x:'): continue
            d = tok.findall(raw)
            if not d or d[0][0] != b'n': continue
            n = int(d[0][1])
            a = arm_of.get(n)
            if a is None: continue
            if kind == b'FrameTrace:': seen[a].add(n)
            pre = kind[10:-1].decode() or 'main'
            A = acc[a]
            for k, v in d[1:]:
                key = pre + ':' + k.decode()
                A[key] = A.get(key, 0) + int(v)
    return {a: {k: v / len(seen[a]) for k, v in acc[a].items()} for a in (0, 1)}, {a: len(seen[a]) for a in (0, 1)}


if __name__ == '__main__':
    tA, aA, tB, aB = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    res = {}
    for t in {tA, tB}:
        res[t] = sums(t, {0: arm_rows(t, 0), 1: arm_rows(t, 1)})
    pickle.dump(res, open('C:/kyty/s111/audit111/allfields_%s_%s.pkl' % (tA, tB), 'wb'))
    A = res[tA][0][aA]; B = res[tB][0][aB]
    print('rows', tA, res[tA][1], tB, res[tB][1])
    keys = sorted(set(A) | set(B), key=lambda k: -abs(B.get(k, 0) - A.get(k, 0)))
    print('%-34s %14s %14s %12s' % ('field', '%s a%d' % (tA, aA), '%s a%d' % (tB, aB), 'B-A'))
    for k in keys[:150]:
        print('%-34s %14.1f %14.1f %12.1f' % (k, A.get(k, 0), B.get(k, 0), B.get(k, 0) - A.get(k, 0)))

"""sg_s15.py - S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)(ii)): the data line of the slow Sky Garden in form U - frames
>= 100 ms by class (sc_s.classify: PCW / SHADER / PRIO / GPUTHR / WAIT; the attribution only on a class T arm) and frames per
second after the first scene frame (the first 120 s of presented time and the whole domain) of Sky Garden arms of form U, V, W and
class T without the catalogue; and the k / u pair of every level of S13b (the same binary adb0c82f).  Data, no game, no decision.
Streaming, binary.  ASCII.
    python sg_s15.py sky <out> | ku <out> <NN> [<NN> ...]
"""
import importlib.util
import json
import os
import sys

spec = importlib.util.spec_from_file_location('sc15_sg', 'C:/kyty/s288/s15/sc_s15.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
A = S.A
SKY = 'underwater_aerial_garden'
SG = [('u_06', 'C:/kyty/s288/s13', 'T', 'form U (S13b, adb0c82f, catalogue s13/seeds)'),
      ('w13', 'C:/kyty/s288/s13', 'M', 'W in form U (S13b, adb0c82f)'),
      ('s12_v', 'C:/kyty/s288/s12', 'M', 'V (S12c, adb0c82f)'),
      ('fs6_v', 'C:/kyty/f287/fs6c', 'M', 'V (FS6c, FS6 9325446c)'),
      ('fs6_w', 'C:/kyty/f287/fs6c', 'M', 'W (FS6c, FS6 9325446c)'),
      ('k_06', 'C:/kyty/s288/s13', 'M', 'collection, no catalogue, no video (S13b, adb0c82f)'),
      ('u_1', 'C:/kyty/s288/s10', 'T', 'form U (S10, 4aa62e95, catalogue s10)'),
      ('pi_r0', 'C:/kyty/s288/s10', 'T', 'class T, no catalogue (S10)'),
      ('pi_r1', 'C:/kyty/s288/s10', 'T', 'class T, no catalogue (S10)'),
      ('pi_w0', 'C:/kyty/s288/s10', 'M', 'class M, no catalogue (S10)'),
      ('pi_w1', 'C:/kyty/s288/s10', 'M', 'class M, no catalogue (S10)')]


def stats(s, prep, attr_ok, lo, hi):
    rows = s['rows']
    rr = range(lo, hi)
    shown = sum(rows[i][1] for i in rr)
    cc = {}
    for i in rr:
        if rows[i][1] >= 100000:
            c = A.classify(s, i, prep, attr_ok)[0]
            cc[c] = cc.get(c, 0) + 1
    dts = sorted(rows[i][1] for i in rr)
    cgs = sorted(rows[i][3] for i in rr)
    n = len(dts)
    return 'rows %d presented %.1f s frames/s %.2f; dt median %s us; cpu_gpu median %s us; >= 100 ms %d %s; >= 1 s %d' % (
        n, shown / 1e6, n / (shown / 1e6) if shown else 0, dts[n // 2] if n else '-', cgs[n // 2] if n else '-',
        sum(cc.values()), json.dumps(cc, sort_keys=True), sum(1 for i in rr if rows[i][1] >= 1000000))


def one(tag, root, cls, level):
    lp = '%s/log_%s.txt' % (root, tag)
    s = A.scan_s(lp)
    eg, end, fi = A.locate(s, level)
    if fi is None:
        return 'log sha256 %s; no first scene frame' % s['sha256'], None
    prep = A.assign_prep(s)
    rows = s['rows']
    acc, j = 0, fi + 1
    while j < len(rows) and acc < 120000000:
        acc += rows[j][1]
        j += 1
    return 'log sha256 %s; first 120 s: %s | domain: %s' % (s['sha256'], stats(s, prep, cls == 'T', fi + 1, j),
                                                            stats(s, prep, cls == 'T', fi + 1, len(rows))), (j - fi - 1) / (acc / 1e6)


def main():
    kind, out = sys.argv[1], sys.argv[2]
    lines = []
    if kind == 'sky':
        for tag, root, cls, what in SG:
            txt, _ = one(tag, root, cls, SKY)
            lines.append('SKY %-6s %s class %s: %s' % (tag, what, cls, txt))
    else:
        for nn in sys.argv[3:]:
            k, u = 'k_%s' % nn, 'u_%s' % nn
            lv = S.SPEC[k]['level']
            tk, fk = one(k, 'C:/kyty/s288/s13', 'M', lv)
            tu, fu = one(u, 'C:/kyty/s288/s13', 'T', lv)
            rel = '-' if not fk or not fu else '%+.1f %%' % (100.0 * (fu - fk) / fk)
            lines.append('KU %s %-30s u against k frames/s (first 120 s): %s | k: %s | u: %s' % (nn, lv, rel, tk, tu))
    txt = '\n'.join(lines) + '\n'
    txt.encode('ascii')
    open(out, 'w', encoding='ascii', newline='\n').write(txt)
    print(txt)
    return 0


if __name__ == '__main__':
    sys.exit(main())

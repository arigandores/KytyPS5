"""F14e (HPP-505, ROADMAP s122 item 409(g)(1)): reading of the GPU gate runs gpu/<g1|g0|gu|c1|c0>/run.log of gpu_f14e.sh.
Members: g1, g0, gu - 96 '[f19] fmt=' lines each and 'ALL OK' (the test itself requires NEAREST == reference, native
LINEAR |out - PCF| <= 2^-6, manual LINEAR in {0, 1}, the =0 negative control and the cache key); here again: g1
k16UNorm LINEAR native and |out - PCF| <= 2^-6 everywhere, NEAREST out == reference everywhere; g0 k16UNorm LINEAR
manual with >= 1 midpoint |out - PCF| >= 0.25; k32Float and k8UNorm output bits equal at =0 and =1 (64 of 64);
gu == g0 in every field; cache dir with _fixf19 last only in g1; c1 'ALL OK'; c0 fails with the text of the build
without the fix (F14a sampled_depth.log). Usage: python gate_read_f14e.py <gpu dir>. Prints 'ALL OK' / 'FAILED'.
"""
import re
import sys

D = sys.argv[1].rstrip('/\\')
OLD = 'ComparisonDepthTexture failed at SPIR-V disassembly: missing required text: OpImageSampleDrefExplicitLod'
RX = re.compile(r'\[f19\] fmt=(\S+) filter=(\S+) ref=(\S+) s=(\S+) t=(\S+) mid=(\d) out=(\S+) \((0x[0-9a-f]+)\) '
                r'pcf=(\S+) nearest=(\S+) step=(\S+) path=(\S+)')


def text(n):
    return open('%s/%s/run.log' % (D, n), 'rb').read().decode('latin1').replace('\r', '')


def rd(n):
    out = {}
    for line in text(n).split('\n'):
        m = RX.match(line)
        if m:
            out[m.group(1, 2, 3, 4, 5)] = m.groups()
    return out


def main():
    ok = True
    g1, g0, gu = rd('g1'), rd('g0'), rd('gu')
    print('lines g1 %d g0 %d gu %d (96 each)' % (len(g1), len(g0), len(gu)))
    ok &= len(g1) == len(g0) == len(gu) == 96
    for n in ('g1', 'g0', 'gu', 'c1'):
        good = '\nALL OK' in text(n)
        print('%s ALL OK: %s' % (n, good))
        ok &= good
    bad = []
    for k, v in g1.items():
        if k[0] == 'k16UNorm' and k[1] == 'LINEAR' and not (abs(float(v[6]) - float(v[8])) <= 1 / 64 and v[11] == 'native'):
            bad.append(k)
        if k[1] == 'NEAREST' and float(v[6]) != float(v[9]):
            bad.append(k)
    for k, v in g0.items():
        if k[1] == 'NEAREST' and float(v[6]) != float(v[9]):
            bad.append(k)
    print('g1 k16UNorm LINEAR native within 2^-6 of PCF, NEAREST == reference (g1, g0): violations %d' % len(bad))
    ok &= not bad
    mids = [k for k, v in g0.items() if k[0] == 'k16UNorm' and k[1] == 'LINEAR' and v[5] == '1' and v[11] == 'manual'
            and abs(float(v[6]) - float(v[8])) >= 0.25]
    print('g0 k16UNorm LINEAR manual midpoints with |out - PCF| >= 0.25: %d' % len(mids))
    for k in mids:
        print('   ref=%s s=%s t=%s out=%s pcf=%s' % (k[2], k[3], k[4], g0[k][6], g0[k][8]))
    ok &= len(mids) >= 1
    other = [k for k in g1 if k[0] in ('k32Float', 'k8UNorm')]
    same = [k for k in other if g1[k][7] == g0.get(k, ('',) * 12)[7]]
    print('k32Float / k8UNorm output bits =0 vs =1 equal: %d of %d' % (len(same), len(other)))
    ok &= len(other) == 64 and len(same) == 64
    print('gu == g0 in every field: %s' % (gu == g0))
    ok &= gu == g0
    for n in ('g1', 'g0', 'gu'):
        m = re.search(r'cache dir=(\S+)', text(n))
        print('%s cache dir %s' % (n, m.group(1) if m else None))
        ok &= bool(m) and (m.group(1).endswith('_fixf19') == (n == 'g1')) and 'fixf19' not in m.group(1)[:-7]
    c0 = OLD in text('c0') and '\nALL OK' not in text('c0')
    print('c0 fails with the text of the build without the fix: %s' % c0)
    ok &= c0
    print('ALL OK' if ok else 'FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

"""read_probe_f7b.py - F7b (HPP-398): reads rd/rd_f7b_probe.txt (replay phase 'probe' of rd_f7b.py) by the criterion
of docs/track-f/f7b-b39.md sec.2a, written before the replay:
  RT0 (tex 6683) shaderOut of the fragment of the PREDICTED (occluded) primitive at a point Q950_k
    every channel < 0.1                       -> hypothesis (a): UV interpolated from VS 588 out_param_1 reach PS 508
    flat colour (0.6055 0.6094 0.6797) +-0.01 -> hypothesis (b): UV collapsed to a constant
    fragment absent                           -> not determined (3)
Verdict over all points: (a) only if every point reads (a); (b) if any point reads (b); else (3).
Prints a table and 'ALL OK' when the fixtures pass.
"""
import json
import os
import re
import sys

D = os.path.dirname(os.path.abspath(__file__))
FLAT = (0.6055, 0.6094, 0.6797)
RT0 = '6683'
RX_HEAD = re.compile(r'-- PROBE (\S+) \((\d+),(\d+)\) on tex (\d+)')
RX_MOD = re.compile(r'\s+eid (\d+) .*passed=(\w+) prim=(\d+) frag=(\d+) .*out=\(([^)]*)\) post=\(([^)]*)\).*flags:(.*)')


def classify(out):
    if out is None:
        return '3'
    if all(c < 0.1 for c in out[:3]):
        return 'a'
    if all(abs(out[i] - FLAT[i]) <= 0.01 for i in range(3)):
        return 'b'
    return '3'


def verdict(cls):
    if cls and all(c == 'a' for c in cls):
        return 'a'
    if any(c == 'b' for c in cls):
        return 'b'
    return '3'


def parse(lines, pts):
    res = {}
    cur = tex = None
    for l in lines:
        m = RX_HEAD.match(l)
        if m:
            cur, tex = m.group(1), m.group(4)
            continue
        m = RX_MOD.match(l)
        if m and cur and tex == RT0 and m.group(1) == str(pts[cur]['eid']):
            prim = int(m.group(3))
            out = tuple(float(v) for v in m.group(5).split())
            r = res.setdefault(cur, {'pred': None, 'front': None, 'pred_flags': ''})
            if prim == pts[cur]['prim']:
                r['pred'] = out
                r['pred_flags'] = m.group(7).strip()
            elif prim == pts[cur]['front_prim']:
                r['front'] = out
    return res


def selftest():
    ok = True
    ok &= classify((0.0177, 0.0212, 0.0273, 0.0)) == 'a'
    ok &= classify((0.0999, 0.0, 0.0, 0.0)) == 'a'
    ok &= classify((0.1, 0.0, 0.0, 0.0)) == '3'
    ok &= classify((0.6055, 0.6094, 0.6797, 0.0)) == 'b'
    ok &= classify((0.6150, 0.6094, 0.6797, 0.0)) == 'b'
    ok &= classify((0.6160, 0.6094, 0.6797, 0.0)) == '3'
    ok &= classify(None) == '3'
    ok &= verdict(['a'] * 8) == 'a'
    ok &= verdict(['a'] * 7 + ['b']) == 'b'
    ok &= verdict(['a'] * 7 + ['3']) == '3'
    ok &= verdict([]) == '3'
    pts = {'Q': {'eid': 950, 'prim': 2, 'front_prim': 1}}
    ln = ['-- PROBE Q (1,1) on tex 6683 x',
          '   eid 950 d() passed=True prim=1 frag=0 pre=(0 0 0 0) out=(0.6055 0.6094 0.6797 0.0000) post=(0 0 0 0) depth flags:',
          '   eid 950 d() passed=False prim=2 frag=1 pre=(0 0 0 0) out=(0.0177 0.0212 0.0273 0.0000) post=(0 0 0 0) depth flags: depthFail',
          '-- PROBE Q (1,1) on tex 6657 x',
          '   eid 950 d() passed=False prim=2 frag=1 pre=(0 0 0 0) out=(0.9 0.9 0.9 0.0000) post=(0 0 0 0) depth flags: depthFail']
    r = parse(ln, pts)
    ok &= r['Q']['pred'] == (0.0177, 0.0212, 0.0273, 0.0) and r['Q']['front'] == (0.6055, 0.6094, 0.6797, 0.0)
    ok &= r['Q']['pred_flags'] == 'depthFail'
    return ok


def main():
    ok = selftest()
    print('selftest', 'ok' if ok else 'FAIL')
    pts = {p['name']: p for p in json.load(open(os.path.join(D, 'rd', 'probe_pts.json')))}
    res = parse(open(os.path.join(D, 'rd', 'rd_f7b_probe.txt'), encoding='utf-8').read().splitlines(), pts)
    cls = []
    for name in sorted(pts):
        p = pts[name]
        r = res.get(name, {})
        pred = r.get('pred')
        c = classify(pred)
        cls.append(c)
        print('%s (%d,%d) prim %d: RT0 out %s flags [%s] expected %s -> %s; front prim %d out %s' % (
            name, p['x'], p['y'], p['prim'], pred, r.get('pred_flags', ''),
            tuple(round(v, 4) for v in p['expected']), c, p['front_prim'], r.get('front')))
        if c == 'a':
            dev = max(abs(pred[i] - p['expected'][i]) for i in range(3))
            print('   max |out - expected texel| = %.4f' % dev)
    v = verdict(cls)
    print('points %d, (a) %d, (b) %d, (3) %d -> verdict %s' % (len(cls), cls.count('a'), cls.count('b'), cls.count('3'), v))
    print('ALL OK' if ok else 'FIXTURES FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

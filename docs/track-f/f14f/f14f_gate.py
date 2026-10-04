"""F14f (HPP-506, ROADMAP s122 items 409(g)(1), 409(d), 415(g)): Red Team's own run of the GPU gate of KYTY_FIX_F19 and an
independent reader.

Runs (each in <out>/<name>, all KYTY_* removed, one process each):
  g1  KYTY_FIX_F19=1   --fix-f19-only
  g0  KYTY_FIX_F19=0   --fix-f19-only
  gu  (unset)          --fix-f19-only
  c1  KYTY_FIX_F19=1   --fix-f19-comparison-depth
  c0  KYTY_FIX_F19=0   --fix-f19-comparison-depth
Reader (own arithmetic, does NOT use the pcf= / nearest= numbers the test prints): the texels are rebuilt from the
formula of the test, (x < 2 ? 0.20 : 0.80) + 0.01*y, quantized per format (k16UNorm round(v*65535)/65535, k32Float
float32, k8UNorm round(v*255)/255); PCF = compare 4 texels (ref <= texel), then bilinear weights (u = 4s - 0.5,
clamp to edge); NEAREST = compare texel floor(4s), floor(4t).
Checks, item 409(g)(1) by letter:
  A1 g1 k16UNorm LINEAR |out - PCF| <= 2^-6 at all 16 points; path=native
  A2 g0 k16UNorm LINEAR: at least one midpoint with |out - PCF| >= 0.25; path=manual
  A3 NEAREST out == own NEAREST exactly (all formats, g1 and g0)
  A4 k32Float and k8UNorm: out bits g0 == g1 at 32 + 32 points
  A5 gu == g0 in every [f19] fmt line
  A6 cache dir: g1 ends with _fixf19, g0/gu without fixf19; signature g1 ends with :fixf19
  A7 c1 'ComparisonDepthTexture ok' and no failure; c0 fails with 'missing required text: OpImageSampleDrefExplicitLod'
  A8 each --fix-f19-only run: 96 fmt lines, 'ALL OK' line present, rc 0 (c0: rc != 0)
Usage: python f14f_gate.py run <compute_tests.exe> <out> [names]   |   python f14f_gate.py read <out> [--expect-fail]
Rule 27: lock and STOP are checked before every process (exit 5 / 4).
"""
import hashlib
import math
import os
import re
import struct
import subprocess
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
RUNS = {
    'g1': ('1', '--fix-f19-only'),
    'g0': ('0', '--fix-f19-only'),
    'gu': (None, '--fix-f19-only'),
    'c1': ('1', '--fix-f19-comparison-depth'),
    'c0': ('0', '--fix-f19-comparison-depth'),
}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(exe, out, names):
    for n in names:
        if os.path.exists(LOCK):
            print('HALT lock')
            sys.exit(5)
        if os.path.exists(STOP):
            print('HALT stop')
            sys.exit(4)
        f19, arg = RUNS[n]
        d = os.path.join(out, n)
        os.makedirs(d, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
        if f19 is not None:
            env['KYTY_FIX_F19'] = f19
        p = subprocess.run([exe, arg], cwd=d, env=env, capture_output=True, timeout=300)
        open(os.path.join(d, 'run.log'), 'wb').write(p.stdout + b'\n==== stderr ====\n' + p.stderr)
        open(os.path.join(d, 'rc.txt'), 'w').write(str(p.returncode) + '\n')
        print('%s KYTY_FIX_F19=%s %s rc=%d exe=%s' % (n, f19 if f19 is not None else 'unset', arg, p.returncode,
                                                    sha(exe)[:8]))


def q(fmt, v):
    if fmt == 'k16UNorm':
        return round(v * 65535.0) / 65535.0
    if fmt == 'k32Float':
        return struct.unpack('<f', struct.pack('<f', v))[0]
    return round(v * 255.0) / 255.0


def own(fmt, ref, s, t):
    ref = struct.unpack('<f', struct.pack('<f', ref))[0]
    tex = lambda x, y: q(fmt, (0.20 if min(max(x, 0), 3) < 2 else 0.80) + 0.01 * min(max(y, 0), 3))
    p = lambda x, y: 1.0 if ref <= tex(x, y) else 0.0
    u, v = 4.0 * s - 0.5, 4.0 * t - 0.5
    i0, j0 = math.floor(u), math.floor(v)
    a, b = u - i0, v - j0
    pcf = (1 - a) * (1 - b) * p(i0, j0) + a * (1 - b) * p(i0 + 1, j0) + (1 - a) * b * p(i0, j0 + 1) + a * b * p(i0 + 1, j0 + 1)
    return pcf, p(math.floor(4.0 * s), math.floor(4.0 * t))


RX = re.compile(r'^\[f19\] fmt=(\S+) filter=(\S+) ref=(\S+) s=(\S+) t=(\S+) mid=(\d) out=(\S+) \(0x([0-9a-f]{8})\) '
                r'pcf=\S+ nearest=\S+ step=\S+ path=(\S+)$')
REFS = {'0.500': 0.5, '0.213': 0.213}


def lines(out, n):
    text = open(os.path.join(out, n, 'run.log'), 'rb').read().decode('latin1').replace('\r', '')
    rows = []
    for line in text.split('\n'):
        m = RX.match(line)
        if m:
            rows.append(m.groups())
    return text, rows


def read(out, expect_fail=False):
    res = {}
    ok = True

    def chk(name, cond, detail=''):
        nonlocal ok
        res[name] = bool(cond)
        ok &= bool(cond)
        print('%s %s %s' % (name, 'ok' if cond else 'FAIL', detail))

    t = {}
    for n in ('g1', 'g0', 'gu'):
        text, rows = lines(out, n)
        rc = open(os.path.join(out, n, 'rc.txt')).read().strip()
        t[n] = (text, rows)
        chk('A8.' + n, len(rows) == 96 and '\nALL OK' in text and rc == '0', 'fmt lines %d rc %s' % (len(rows), rc))
    # A1 / A2 / A3
    a1, a2, a3 = [], [], []
    for n in ('g1', 'g0'):
        for fmt, flt, ref, s, tt, mid, out_s, bits, path in t[n][1]:
            pcf, near = own(fmt, REFS[ref], float(s), float(tt))
            outv = struct.unpack('<f', bytes.fromhex(bits)[::-1])[0]
            if flt == 'NEAREST':
                a3.append(outv == near)
            elif fmt == 'k16UNorm' and n == 'g1':
                a1.append(abs(outv - pcf) <= 1.0 / 64 and path == 'native')
            elif fmt == 'k16UNorm' and n == 'g0':
                a2.append((mid == '1' and abs(outv - pcf) >= 0.25 and path == 'manual', path))
    chk('A1', len(a1) == 16 and all(a1), 'k16 LINEAR native within 2^-6 of own PCF: %d of %d' % (sum(a1), len(a1)))
    chk('A2', sum(1 for x, _ in a2) and sum(1 for x, _ in a2 if x) >= 1 and all(p == 'manual' for _, p in a2),
        'k16 LINEAR =0 midpoints off own PCF by >= 0.25: %d' % sum(1 for x, _ in a2 if x))
    chk('A3', len(a3) == 2 * 48 and all(a3), 'NEAREST == own reference: %d of %d' % (sum(a3), len(a3)))
    key = lambda r: r[:6]
    g1 = {key(r): r for r in t['g1'][1]}
    g0 = {key(r): r for r in t['g0'][1]}
    a4 = [k in g1 and g1[k][7] == g0[k][7] for k in g0 if k[0] in ('k32Float', 'k8UNorm')]
    chk('A4', len(a4) == 64 and all(a4), 'k32Float/k8UNorm bits =0 == =1: %d of %d' % (sum(a4), len(a4)))
    chk('A5', t['gu'][1] == t['g0'][1], 'gu fmt lines == g0')
    d = {}
    for n in ('g1', 'g0', 'gu'):
        m = re.search(r'cache dir=(\S+)', t[n][0])
        sg = re.search(r'cache signature=(\S+)', t[n][0])
        d[n] = (m.group(1) if m else '', sg.group(1) if sg else '')
    chk('A6', d['g1'][0].endswith('_fixf19') and d['g1'][1].endswith(':fixf19') and 'fixf19' not in d['g0'][0] + d['g0'][1]
        and 'fixf19' not in d['gu'][0] + d['gu'][1], 'dirs g1 %s g0 %s gu %s' % (d['g1'][0], d['g0'][0], d['gu'][0]))
    c1 = open(os.path.join(out, 'c1', 'run.log'), 'rb').read().decode('latin1')
    c0 = open(os.path.join(out, 'c0', 'run.log'), 'rb').read().decode('latin1')
    rc1 = open(os.path.join(out, 'c1', 'rc.txt')).read().strip()
    rc0 = open(os.path.join(out, 'c0', 'rc.txt')).read().strip()
    chk('A7', 'ComparisonDepthTexture' in c1 and ' ok' in c1 and rc1 == '0' and 'failed' not in c1 and rc0 != '0'
        and 'missing required text: OpImageSampleDrefExplicitLod' in c0, 'c1 rc %s, c0 rc %s' % (rc1, rc0))
    print('ALL OK' if ok else 'NOT OK: ' + ' '.join(k for k, v in res.items() if not v))
    return ok


if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run(sys.argv[2], sys.argv[3], sys.argv[4:] or list(RUNS))
    else:
        sys.exit(0 if read(sys.argv[2]) else 1)

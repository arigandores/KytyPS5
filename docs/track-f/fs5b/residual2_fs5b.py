# FS5b (HPP-510, Red Team): residual_fs5b.py with one more class. On FS5 the MSVC-style anonymous-namespace hash ?A0x<hex>
# has no leading zeros (A ?A0x4858C598 vs B ?A0xBCD93A9 - 8 vs 7 digits), so the rest of the decorated name shifts by one
# byte inside its fixed slot and residual_fs5b.py prints those runs as 'other'. New class 'anon-ns-str': the run lies inside a
# NUL-terminated string that starts at the same offset in A and B (or in its NUL padding up to the longer end), and the two
# strings are equal after masking every ?A0x<1-8 hex> to ?A0x#. Everything else stays 'other'. ALL OK only if 'other' == 0.
import re, collections, runpy, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path('C:/kyty/f287/fs5/fs5b/residual_fs5b.py')
A2, B2, runs, dbg_ranges, region = g['A2'], g['B2'], g['runs'], g['dbg_ranges'], g['region']
anon = re.compile(rb'\?A0x[0-9A-F]{1,8}')
PR = set(range(0x20, 0x7f))


def strat(x, s):
    # start of the printable run containing offset s (scan back over printable bytes), end at the first NUL
    a = s
    while a > 0 and x[a - 1] in PR:
        a -= 1
    e = s
    while e < len(x) and x[e] != 0:
        e += 1
    return a, e


cls = collections.Counter()
other = []
for s, l in runs:
    if any(a <= s < b for a, b in dbg_ranges):
        c = 'debug-dir'
    else:
        c = 'other'
        for m in anon.finditer(bytes(A2[max(0, s - 12):s + l + 12])):
            ms = max(0, s - 12) + m.start()
            if ms <= s and s + l <= ms + 12:
                c = 'anon-ns'
                break
        if c == 'other':
            # the run may start in the NUL padding of the shorter string: step back over NULs of one side
            p = s
            while p > 0 and (A2[p] == 0 or B2[p] == 0) and not (A2[p] in PR and B2[p] in PR):
                p -= 1
            a1, e1 = strat(A2, p)
            a2, e2 = strat(B2, p)
            sa_, sb_ = bytes(A2[a1:e1]), bytes(B2[a2:e2])
            if a1 == a2 and b'?A0x' in sa_ and anon.sub(b'?A0x#', sa_) == anon.sub(b'?A0x#', sb_) and s + l <= max(e1, e2) + 1:
                c = 'anon-ns-str'
    cls[(c, region(s))] += 1
    if c == 'other':
        other.append((s, l, region(s), bytes(A2[max(0, s - 24):s + l + 8]), bytes(B2[max(0, s - 24):s + l + 8])))
print('residual runs', len(runs))
for k, v in sorted(cls.items()):
    print('  class', k[0], 'region', k[1], 'runs', v)
for s, l, r, a, b in other[:20]:
    print('  OTHER off 0x%x len %d %s A %r B %r' % (s, l, r, a, b))
print('RESIDUAL2', 'ALL OK' if not other else 'OTHER %d' % len(other))

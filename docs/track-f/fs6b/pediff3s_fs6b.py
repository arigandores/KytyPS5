# FS6b (HPP-556, Red Team): pediff3.py of F15d (unchanged, run as is) + one more class for its OTHER bytes, the form of my FS5b
# residual2_fs5b.py: clang-cl writes the anonymous-namespace hash ?A0x<hex> without leading zeros (A ?A0x9831C33 vs B ?A0xE6E97...,
# 7 vs 8 digits), so the rest of a decorated name inside a fixed slot shifts by one byte and pediff3 (8 hex digits only) leaves
# it OTHER. Class '(2b) anon-namespace string': the byte lies inside a NUL-terminated printable string that starts at the same
# offset in A and B (or in its NUL padding up to the longer end), both strings contain ?A0x and are equal after masking every
# ?A0x<1-8 hex> to ?A0x#. Everything else stays OTHER; the verdict is EXPLAINED only if OTHER == 0. .text differences are never
# reclassified (printed separately).
# Usage: python pediff3s_fs6b.py <A.exe> <B.exe> <dir tag A> <dir tag B>
import collections, contextlib, io, re, runpy, sys

HERE = 'C:/kyty/f287/fs6b/pediff3.py'
args = sys.argv[1:5]
buf = io.StringIO()
sys.argv = [HERE] + args
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(HERE)
first = buf.getvalue().splitlines()[0]
print('pediff3:', first)
A, B, other, sec_of = g['a'], g['b'], g['other'], g['sec_of']
anon = re.compile(rb'\?A0x[0-9A-F]{1,8}')
PR = set(range(0x20, 0x7f))


def bounds(x, p):
    s = p
    while s > 0 and x[s - 1] in PR:
        s -= 1
    e = p
    while e < len(x) and x[e] != 0:
        e += 1
    return s, e


cls = collections.Counter()
left = []
for i in other:
    sec = sec_of(i)
    if sec == '.text':
        left.append(i)
        continue
    p = i
    while p > 0 and (A[p] == 0 or B[p] == 0) and not (A[p] in PR and B[p] in PR):
        p -= 1
    s1, e1 = bounds(A, p)
    s2, e2 = bounds(B, p)
    sa, sb = A[s1:e1], B[s2:e2]
    if s1 == s2 and b'?A0x' in sa and b'?A0x' in sb and anon.sub(b'?A0x#', sa) == anon.sub(b'?A0x#', sb) and i <= max(e1, e2):
        cls[('(2b) anon-namespace string', sec)] += 1
    else:
        left.append(i)
print('pediff3 OTHER bytes', len(other), 'by section', dict(collections.Counter(sec_of(i) for i in other)))
for k, v in sorted(cls.items()):
    print('  reclassified', k[0], 'section', k[1], 'bytes', v)
print('.text differing bytes (never reclassified):', sum(1 for i in other if sec_of(i) == '.text'))
print('left OTHER', len(left), dict(collections.Counter(sec_of(i) for i in left)))
for i in left[:20]:
    print('  0x%08x %s a=%02x b=%02x ctx_a=%r ctx_b=%r' % (i, sec_of(i), A[i], B[i], A[max(0, i - 24):i + 8], B[max(0, i - 24):i + 8]))
print('VERDICT', 'EXPLAINED' if not left else 'UNEXPLAINED')

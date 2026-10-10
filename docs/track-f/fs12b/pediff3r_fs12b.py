# FS12b (HPP-751, Red Team, ROADMAP s122 item 683(g)(2)): copy of the FS11b file with fs11b->fs12b, fs11n->fs12n, FS11b->FS12b in ALL lines (older header lines below that say FS12b mean FS11b HPP-715); default commits 730ed40a (FS12) / 9aaea58c (FS12 without FS12a).
# FS12b (HPP-715, Red Team, ROADMAP s122 item 647(d)(2)): copy of the FS10b file; fs10b -> fs12b, fs10n -> fs12n (paths, names, times label), default commits ee9632be / eded064e.
# FS10b (HPP-685, Red Team, ROADMAP s122 item 624(e)(2)): copy of the FS9b file; fs9b -> fs10b in code lines only (paths, names, times label).
# FS9b (HPP-672, Red Team, ROADMAP s122 item 604(d)(2)): copy of pediff3r_fs8b.py, only the path of pediff3.py changed (fs8b -> fs9b).
# FS8b (HPP-572, Red Team, ROADMAP s122 items 471(g)(2), 527(d)(3)): pediff3 (F15d copy, unchanged) + class 2b of my
# pediff3s_fs8b.py (unchanged logic) + one new class, named here before reading the negative control:
#   (2c) SDL_REVISION: the byte lies inside a NUL-terminated string that starts at the same offset in A and B, both
#        strings match ^SDL-KytyPS5-<date>-<sha7>-<n>-g<hex>$ (SDL2 CMakeLists.txt:3127-3145 - git describe of the source
#        tree at CMake CONFIGURE time, so a build configured at another HEAD carries another describe), and the two strings
#        are equal after masking '-<n>-g<hex>' at the end. Only outside .text.
# Everything else stays OTHER; VERDICT EXPLAINED only if OTHER == 0. .text differences are never reclassified.
# Usage: python pediff3r_fs8b.py <A.exe> <B.exe> <dir tag A> <dir tag B>
import collections
import contextlib
import io
import re
import runpy
import sys

HERE = 'C:/kyty/f287/fs12b/pediff3.py'
args = sys.argv[1:5]
buf = io.StringIO()
sys.argv = [HERE] + args
with contextlib.redirect_stdout(buf):
    g = runpy.run_path(HERE)
print('pediff3:', buf.getvalue().splitlines()[0])
A, B, other, sec_of = g['a'], g['b'], g['other'], g['sec_of']
anon = re.compile(rb'\?A0x[0-9A-F]{1,8}')
sdl = re.compile(rb'^SDL-KytyPS5-\d{4}-\d{2}-\d{2}-[0-9a-f]{7}-(\d+)-g([0-9a-f]+)$')
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
text = 0
sdl_seen = set()
for i in other:
    sec = sec_of(i)
    if sec == '.text':
        text += 1
        left.append(i)
        continue
    sa, ea = bounds(A, i)
    sb, eb = bounds(B, i)
    stra, strb = A[sa:ea], B[sb:eb]
    if sa == sb and b'?A0x' in stra and b'?A0x' in strb and anon.sub(b'?A0x#', stra) == anon.sub(b'?A0x#', strb):
        cls['(2b) anon-namespace string ' + sec] += 1
        continue
    ma, mb = sdl.match(stra), sdl.match(strb)
    if sa == sb and ma and mb and stra[:ma.start(1)] == strb[:mb.start(1)]:
        cls['(2c) SDL_REVISION ' + sec] += 1
        sdl_seen.add((sa, stra.decode(), strb.decode()))
        continue
    left.append(i)
print('pediff3 OTHER bytes', len(other))
for k, v in sorted(cls.items()):
    print('  reclassified %s bytes %d' % (k, v))
for s_, a_, b_ in sorted(sdl_seen):
    print('  SDL_REVISION at 0x%08x: A %s | B %s' % (s_, a_, b_))
print('.text differing bytes (never reclassified):', text)
bysec = collections.Counter(sec_of(i) for i in left)
print('left OTHER', len(left), dict(bysec))
for i in left[:8]:
    print('  0x%08x %s a=%02x b=%02x ctx_a=%r ctx_b=%r' % (i, sec_of(i), A[i], B[i], A[max(0, i - 24):i + 8], B[max(0, i - 24):i + 8]))
print('VERDICT', 'EXPLAINED' if not left else 'UNEXPLAINED')

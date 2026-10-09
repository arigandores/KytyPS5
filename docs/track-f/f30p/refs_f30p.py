# F30p (HPP-726): the <commit>:<path>:<line> links of docs/track-f/f30p-review.md - whole-line anchor and the +1 line;
# negative controls N1 (line + 1) and N2 (anchor with a changed character).  Prints ALL OK or FAILED; exit 0 / 1.
import subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
IM = 'src/graphics/host_gpu/renderer/image/image.cpp'
CX = 'src/graphics/host_gpu/renderer/context.cpp'
C = 'd25a78bc'
REFS = [
    (C, RD, 1601, 'if (t_rts_race && (bits & kRtsBitsA) == 0) {', 'FS::Add(FS::Counter::RtsRace, 1);'),
    (C, RD, 1685, 'if ((g_rts_inj_n.fetch_add(1, std::memory_order_relaxed) + 1) % kRtsInjEvery != 0) {', 'return;'),
    (C, RD, 1692, 'if (image.binding.is_bound || !RtsInjAttachLayout(image, range)) {', 'continue;'),
    (C, RD, 2261, 'const auto  layout = image.binding.is_bound ? vk::ImageLayout::eGeneral',
     ': vk::ImageLayout::eColorAttachmentOptimal;'),
    (C, RD, 3842, 'FS::Add(C::RtsPb, 1);', 'FS::Add(C::RtsChkB, 1);'),
    (C, RD, 3845, 'if (t_rts == 6) [[unlikely]] {', 'RtsInject(cc, state.color_info, img.data());'),
    (C, RD, 3854, 't_rts_ser0   = ImageStateSerial();', 't_rts_open0  = buffer.IsRendering();'),
    (C, RD, 3909, 'if (t_rts_ser1 != t_rts_ser0) {', 'bits |= 0x040u; // S'),
    (C, RD, 3926, 'if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {', 'FS::Add(C::RtsInjRace, 1);'),
    (C, IM, 140, 'subresource_states.resize(info.resources.levels * info.resources.layers, state);', 'representation_moved = true;'),
    (C, IM, 243, 'state = next;', 'return barriers;'),
    (C, CX, 482, 'm_rendering = false;', 'Common::DrawStat::Cut(Common::DrawStat::EdgePass);'),
]

def show(c, p):
    return subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout.decode('utf-8').split(chr(10))

ok = True
def member(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and cond

def ref_ok(c, p, n, a, a1):
    s = show(c, p)
    return 0 < n < len(s) and s[n - 1].strip() == a and s[n].strip() == a1

for r in REFS:
    member('R %s:%s:%d' % r[:3], ref_ok(*r))
r = REFS[0]
member('N1 negative control (line + 1) fails', not ref_ok(r[0], r[1], r[2] + 1, r[3], r[4]))
member('N2 negative control (anchor with a changed character) fails', not ref_ok(r[0], r[1], r[2], r[3] + 'x', r[4]))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

# F30h (HPP-718, Probe Designer): rule 24(1) - every <commit>:<path>:<line> of f30h.md, anchor = the whole line (stripped),
# control +1 = the next line (stripped); two negative controls (shifted line) must be rejected.
# Usage: python refs_f30h.py <repo>
import subprocess
import sys

REPO = sys.argv[1]
C = 'a1d1d863'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
REFS = [
    (C, RD, 1304, 'inline constexpr uint32_t kRtsBitsA = 0x001u | 0x002u | 0x004u | 0x008u | 0x400u;', ''),
    (C, RD, 1569, 'if (!t_rts_reg) {', 'FS::Add(FS::Counter::RtsBadNoreg, 1);'),
    (C, RD, 1576, 'if ((bits & 0x030u) != 0) {', 'FS::Add(FS::Counter::RtsBadRx, 1);'),
    (C, RD, 3470, '} else if (t_rts != 3 && t_rts_reg) {', 'why = C::RtsXaReg;'),
    (C, RD, 3493, 'if (t_rts == 1 && t_rts_pa) {', None),
    (C, RD, 3545, 'if (t_rts >= 2 && t_rts_pa) {', '// The resolution half of the self-check (s.5.1 step 2, s.5.2).'),
    (C, RD, 3654, 'if (t_rts != 4) {', '// 3 (N2, N4): the metadata epoch the record\'s fast records were taken at.'),
    (C, RD, 3661, 'if (img[i]->backing.state_serial != rec->t[i].state_serial) {', 'return C::RtsXbSer;'),
    (C, RD, 3677, 'if (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial) {', 'return C::RtsXbPass;'),
    (C, RD, 3690, 'if (t_rts == 1 && pb_ok) {', None),
    (C, RD, 3704, 'image.binding.attachment_layout = t.att_layout;', 'image.binding.attachment_access = t.att_access;'),
    (C, RD, 3719, 'if (t_rts >= 2 && pb_ok) {', 't_rts_pb = true;'),
    (C, RD, 3758, 'if (t_rts >= 2 && t_rts_pa) {', 'uint32_t bits = t_rts_bits;'),
    (C, RD, 3760, 'if (t_rts_pb) {', 'if (!(rendering == rec->state)) {'),
    (C, RD, 3780, 'if (t_rts_ser1 != t_rts_ser0) {', 'bits |= 0x040u; // S'),
    (C, RD, 3801, 'if (t_rts_pb) {', None),
    (C, 'src/graphics/host_gpu/renderer/renderTarget.h', 57, 'bool operator==(const RenderState&) const = default;', '};'),
    (C, 'src/graphics/host_gpu/graphicContext.h', 202, None, None),
    (C, 'src/common/gates.cpp', 438, '{"KYTY_RT_SKIP", "rtskip", 1, 4},', None),
]


def show(c, p):
    return subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout.decode(
        'utf-8').split('\n')


cache = {}
ok = True
for c, p, n, a, plus in REFS:
    if (c, p) not in cache:
        cache[(c, p)] = show(c, p)
    L = cache[(c, p)]
    line = L[n - 1].strip()
    nxt = L[n].strip()
    good = (a is None or line == a) and (plus is None or nxt == plus)
    ok &= good
    print('%s %s:%s:%d | %s | +1 %s' % ('OK ' if good else 'BAD', c, p, n, line, nxt))
# negative controls: the same anchor one line off must fail
for c, p, n, a, plus in (REFS[2], REFS[7]):
    L = cache[(c, p)]
    bad = L[n].strip() == a
    ok &= not bad
    print('NEG %s:%d shifted -> %s' % (p, n + 1, 'accepted (BAD)' if bad else 'rejected'))
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

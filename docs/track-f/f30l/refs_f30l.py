# F30l (HPP-722): the <commit>:<path>:<line> links of docs/track-f/f30l-review.md - whole-line anchor and the +1 line.
# Usage: python refs_f30l.py   -> PASS/FAIL per link, negative controls N1 (line + 1) and N2 (changed anchor); ALL OK / FAILED.
import subprocess, sys

G = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
REFS = [
    ('6fbdcf67', RD, 1564, 'void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth, uint32_t xsrc) {', 'namespace FS = Common::FrameStats;'),
    ('6fbdcf67', RD, 1566, 'if (t_rts_race && (bits & kRtsBitsA) == 0) {', 'FS::Add(FS::Counter::RtsRace, 1);'),
    ('6fbdcf67', RD, 1582, 'if ((bits & 0x010u) != 0) {', 'FS::Add(FS::Counter::RtsBadR, 1);'),
    ('6fbdcf67', RD, 2169, 'const auto  layout = image.binding.is_bound ? vk::ImageLayout::eGeneral', ': vk::ImageLayout::eColorAttachmentOptimal;'),
    ('6fbdcf67', RD, 2230, 'depth.depth_load_clear_enable = depth.depth_clear_enable || meta_clear;', 'skc3_depth_mat                = meta_clear;'),
    ('6fbdcf67', RD, 3497, '} else if (t_rts != 3 && t_rts_reg) {', 'why = C::RtsXaReg;'),
    ('6fbdcf67', RD, 3681, 'if (t_rts != 4) {', "// 3 (N2, N4): the metadata epoch the record's fast records were taken at."),
    ('6fbdcf67', RD, 3705, 'if (t_rts != 5 && (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial)) {', 'return C::RtsXbPass;'),
    ('6fbdcf67', RD, 3718, 'if (t_rts == 1 && pb_ok) {', "// The skip (s.3.2): the stores the fast path and the capture make on unchanged images, in the capture's order."),
    ('6fbdcf67', RD, 3757, 't_rts_ser0   = ImageStateSerial();', 't_rts_open0  = buffer.IsRendering();'),
    ('6fbdcf67', RD, 3789, 'if (t_rts_pb) {', 'if (!(rendering == rec->state)) {'),
    ('6fbdcf67', RD, 3799, 'xsrc |= 1u;', '}'),
    ('6fbdcf67', RD, 3804, 'xsrc |= 2u;', '}'),
    ('6fbdcf67', RD, 3810, 'xsrc |= 4u;', '}'),
    ('6fbdcf67', RD, 3833, 'if (t_rts_pb) {', '// PA and PB (the skip at 1): the record is not refreshed, only re-pinned at BeginRendering ([RC1]).'),
    ('6fbdcf67', RD, 3854, 'ok = !state.depth_info.depth_clear_enable && !state.depth_info.depth_load_clear_enable;', '}'),
    ('6fbdcf67', 'src/graphics/host_gpu/graphicContext.h', 177, 'inline std::atomic<uint64_t> g_image_state_serial {0};', '[[nodiscard]] inline uint64_t ImageStateSerial() noexcept {'),
    ('6fbdcf67', 'src/graphics/presentation/window/swapchain.cpp', 827, 'Common::LockGuard render_lock(m_impl->renderer.GetMutex());', 'if (present_wait_t0 != 0) {'),
    ('6fbdcf67', 'src/graphics/presentation/window/swapchain.cpp', 858, 'frame->CopyFrom(buffer, image);', 'return *frame;'),
    ('6fbdcf67', 'src/graphics/host_gpu/renderer/context.cpp', 325, 'if (m_rendering && m_render_state == state) {', 'return;'),
    ('6fbdcf67', 'src/graphics/host_gpu/renderer/context.cpp', 417, 'attachment.is_clear ? vk::AttachmentLoadOp::eClear : vk::AttachmentLoadOp::eLoad;', 'colors[i].storeOp                 = vk::AttachmentStoreOp::eStore;'),
    ('6fbdcf67', 'src/common/gates.cpp', 438, '{"KYTY_RT_SKIP", "rtskip", 1, 5},', '// Session 128, MEASUREMENT ONLY: skip the read-only arming of a buffer synchronization on GuestGpu (1)'),
]

cache = {}
def show(c, p):
    if (c, p) not in cache:
        cache[(c, p)] = subprocess.run([G, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True, check=True).stdout.decode('utf-8').split(chr(10))
    return cache[(c, p)]

def ref_ok(c, p, n, a, a1):
    s = show(c, p)
    return 0 < n < len(s) and s[n - 1].strip() == a and s[n].strip() == a1

ok = True
for r in REFS:
    v = ref_ok(*r)
    print(('PASS' if v else 'FAIL') + ' R %s:%s:%d' % r[:3])
    ok = ok and v
r = REFS[0]
n1 = not ref_ok(r[0], r[1], r[2] + 1, r[3], r[4])
n2 = not ref_ok(r[0], r[1], r[2], r[3] + 'x', r[4])
print(('PASS' if n1 else 'FAIL') + ' N1 negative control (line + 1) fails')
print(('PASS' if n2 else 'FAIL') + ' N2 negative control (anchor with a changed character) fails')
ok = ok and n1 and n2
print('%d links' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)

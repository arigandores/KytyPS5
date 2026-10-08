# F30a (HPP-706): check of the <commit>:<path>:<line> references of f30a.md (general rule 24(1)), the form of refs_f28a.py:
# each anchor is a WHOLE line (stripped) that occurs exactly once in the file at the commit, the +1 control is the next
# line (stripped); the script prints the reference with the line number found.  Exit 0 and ALL OK when every reference
# holds.  usage: python refs_f30a.py
import subprocess, sys

REPO = 'C:/kyty/KytyPS5'
FS10 = 'dc5d4712'
S127 = 'defd2c91'
D = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
G = 'src/common/gates.cpp'
T = 'src/graphics/host_gpu/renderer/cache/textureCache.cpp'
X = 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp'
S = 'src/common/frameStats.h'
V = 'src/graphics/presentation/videoOut.cpp'
REFS = [
    ('R1', FS10, G, '{"KYTY_RT_SKIP", "rtskip", 1, 3},',
     '// Session 128, MEASUREMENT ONLY: skip the read-only arming of a buffer synchronization on GuestGpu (1)'),
    ('R2', FS10, G, '{"KYTY_RT_FAST", "rtfast", true},', '// Session 60, B3.'),
    ('R3', FS10, D, '[[gnu::noinline]] void RenderExecutor::RtsLatchSlow(CommandBuffer& buffer, uint32_t value) {',
     'namespace FS = Common::FrameStats;'),
    ('R4', FS10, D, 'reason = "rk3cen";', 'bit    = 1;'),
    ('R5', FS10, D, 'reason = "readback_linear_images";', 'bit    = 11;'),
    ('R6', FS10, D, 'LOGF("RtSkip: refused reason=%s\\n", reason);', '}'),
    ('R7', FS10, D, 'LOGF("RtSkip: mode %u ctx_slots=%u groups=%u rec_bytes=%u\\n", armed,',
     'static_cast<uint32_t>(t_rts_table->e.size()), Rk3::GroupCount, static_cast<uint32_t>(sizeof(RtsRecord)));'),
    ('R8', FS10, D, 'if (t_rts == 1 && t_rts_pa) {',
     "// The skip (s.3.2): the record's outputs, then the stores of the resolution's memo hits in its order - the LRU"),
    ('R9', FS10, D, 'if (t_rts == 1 && pb_ok) {',
     "// The skip (s.3.2): the stores the fast path and the capture make on unchanged images, in the capture's order."),
    ('R10', FS10, D, 'if (t_rts >= 2 && pb_ok) {', 't_rts_pb = true;'),
    ('R11', FS10, D, 'const bool expect = !(rec->color_count == 0 && !rec->pre_depth.image_id && !DrawHasActivePixelShader(buffer));',
     'if (prepared != expect) {'),
    ('R12', FS10, D, 'bits |= 0x010u; // R', '}'),
    ('R13', FS10, D, 'bits |= 0x200u; // L', '}'),
    ('R14', FS10, D, 'inline constexpr uint32_t kRtsBitsA = 0x001u | 0x002u | 0x004u | 0x008u | 0x400u;', ''),
    ('R15', FS10, D, 'if (t_rts_race && (bits & kRtsBitsA) == 0) {', 'FS::Add(FS::Counter::RtsRace, 1);'),
    ('R16', FS10, D, 'if (t_rts_lines < 40) {', 't_rts_lines++;'),
    ('R17', FS10, D, 'LOGF("RtSkipVerify: MISMATCH frame=%d bits=0x%03x reg=%u chain=%u colors=%u depth=%u pa=1 pb=%u mode=%u\\n", frame,',
     'bits, t_rts_reg ? 1u : 0u, age, colors, depth ? 1u : 0u, t_rts_pb ? 1u : 0u, t_rts);'),
    ('R18', FS10, D, 'const auto view  = depth_target ? cache.FindDepthTarget(id, desc) : cache.FindRenderTarget(id, desc);',
     'fast.valid       = false;'),
    ('R19', FS10, D, 'state.ps_active       = DrawHasActivePixelShader(buffer);',
     'if (state.color_count == 0 && !state.depth_info.image_id && !state.ps_active) {'),
    ('R20', FS10, D, 'RtsPost(buffer, state, rendering); // Session 127, knob "rtskip": the record; the self-check at 2/3', '}'),
    ('R21', FS10, D, 'if ((t_rts_logged & (1u << (16u + armed))) == 0) {', 't_rts_logged |= 1u << (16u + armed);'),
    ('R22', FS10, T, 'if (!fce_materialize) {', 'm_b42_draw_seq[id] = ++m_b42_seq;'),
    ('R23', FS10, T, 'm_readback_linear_images(Config::ReadbackLinearImagesEnabled()) {',
     'if (m_graphics.CanReportMemoryUsage()) {'),
    ('R24', FS10, X, 'if (fill.b42_draw_seq > fill.b42_fill_seq) {', 'probe.kind = FixB42Kind::Drawn;'),
    ('R25', FS10, X, 'void RenderExecutor::MaterializeBoundTargetDccClears(CommandBuffer& buffer) {',
     'auto&       cache = m_context.GetTextureCache();'),
    ('R26', FS10, 'src/graphics/host_gpu/renderer/renderMemo.h', "return value == nullptr || value[0] != '0';", '}();'),
    ('R27', FS10, 'src/graphics/host_gpu/renderer/debug.cpp', 'bool graphics_debug_dump_enabled() {',
     'return Config::GraphicsDebugDumpEnabled() &&'),
    ('R28', FS10, S, 'RtsBad,                  // rts_bad: values 2/3 - mismatches (must be 0 at 2; > 0 at 3)',
     'RtsBadNoreg,             // rts_bad_noreg: values 2/3 - mismatches with reg=0 (must be 0 at 2 and 3)'),
    ('R29', FS10, S, 'RtsRace,                 // rts_race: values 2/3 - bind_stamp races (must be 0 on the self-check runs)',
     'RtsRec,                  // rts_rec: values 2/3 - records taken (full update or the capture half)'),
    ('R30', FS10, V, '{"rts_n", FS::Counter::RtsN, false},', '{"rts_skip", FS::Counter::RtsSkip, false},'),
    ('R31', FS10, V, '" bda_scan=%llu bda_skip=%llu bda_bskip=%llu bda_bit_bad=%llu"', '" bpage_hit=%llu bpage_miss=%llu"'),
    ('R32', S127, D, 'constinit thread_local bool        t_rts_a        = false;   // value 1: place A was skipped',
     'constinit thread_local bool        t_rts_pb       = false;   // PA and PB held'),
]


def main():
    ok = True
    for rid, commit, path, anchor, plus1 in REFS:
        text = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        lines = [l.strip() for l in text.decode('utf-8').splitlines()]
        hits = [i for i, l in enumerate(lines) if l == anchor]
        good = len(hits) == 1
        nxt = lines[hits[0] + 1] if good and hits[0] + 1 < len(lines) else None
        if good and plus1 is not None:
            good = nxt == plus1
        ok &= good
        print('%-4s %s %s:%s:%s  anchor x%d  +1 %s' % (rid, 'OK ' if good else 'BAD', commit, path,
                                                    hits[0] + 1 if hits else '?', len(hits),
                                                    'ok' if plus1 is None or nxt == plus1 else repr(nxt)))
    # negative control: a changed +1 and a non-unique anchor must fail
    neg = 0
    for rid, commit, path, anchor, plus1 in [('N1', FS10, D, 'if (t_rts == 1 && pb_ok) {', 't_rts_pb = true;'),
                                             ('N2', FS10, D, '[[unlikely]] {', None)]:
        text = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True, check=True).stdout
        lines = [l.strip() for l in text.decode('utf-8').splitlines()]
        hits = [i for i, l in enumerate(lines) if l == anchor]
        good = len(hits) == 1 and (plus1 is None or lines[hits[0] + 1] == plus1)
        neg += not good
    print('NEG rejected %d/2' % neg)
    ok &= neg == 2
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

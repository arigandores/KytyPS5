# F30k (HPP-721), ROADMAP s122 item 655(g)(1)-(3): KYTY_RT_SKIP=5 (= 2 without PB item 6, RtsXbPass) and the eight
# per-bit counters of place B (rts_bad_r, rts_bad_xr, rts_bad_xc, rts_bad_xe, rts_bad_s, rts_bad_p, rts_bad_m, rts_bad_l).
# Usage: python patch_f30k.py <repo root>.  Whole-line anchors (each must hit exactly once); CRLF-safe; writes LF back
# (or CRLF if the file had it).  A copy of docs/track-f/f30d/patch_f30d.py with the edits replaced.
import sys, pathlib

root = pathlib.Path(sys.argv[1])

def patch(rel, edits):
    p = root / rel
    raw = p.read_bytes()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r\n', '\n')
    lines = text.split('\n')
    for old, new in edits:
        old_l = old.split('\n')
        hits = [i for i in range(len(lines) - len(old_l) + 1) if lines[i:i + len(old_l)] == old_l]
        if len(hits) != 1:
            raise SystemExit('%s: anchor hits=%d: %r' % (rel, len(hits), old_l[0]))
        i = hits[0]
        lines[i:i + len(old_l)] = new.split('\n')
    out = '\n'.join(lines)
    if crlf:
        out = out.replace('\n', '\r\n')
    p.write_bytes(out.encode('utf-8'))
    print('patched', rel, len(edits))

T = '\t'

patch('src/common/gates.cpp', [
    ('    // Track F, F30d (ROADMAP s122 item 643(v)): 4 = the self-check with PB items 3 and 4 not applied (positive control\n'
     '    // of place B).\n'
     '    {"KYTY_RT_SKIP", "rtskip", 1, 4},',
     '    // Track F, F30d (ROADMAP s122 item 643(v)): 4 = the self-check with PB items 3 and 4 not applied (positive control\n'
     '    // of place B).  Track F, F30k (ROADMAP s122 item 655(g)(1)): 5 = the self-check with PB item 6 not applied.\n'
     '    {"KYTY_RT_SKIP", "rtskip", 1, 5},'),
])

patch('src/common/gates.h', [
    (T + 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check, 3 self-check + positive control; default 1 since session 128; 4 self-check + positive control of place B, F30d)',
     T + 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check, 3 self-check + positive control; default 1 since session 128; 4 self-check + positive control of place B, F30d; 5 self-check without PB item 6, F30k)'),
])

patch('src/common/frameStats.h', [
    (T + 'RtsBadB,                 // rts_bad_b\n'
     + T + 'RtsBadRx,                // rts_bad_rx',
     T + 'RtsBadB,                 // rts_bad_b\n'
     + T + 'RtsBadRx,                // rts_bad_rx\n'
     + T + '// Track F, F30k (ROADMAP s122 item 655(g)(2)): of rts_bad (values >= 2), the mismatches by place B bit; X split by\n'
     + T + '// its source in the post.  Raw counts; one mismatch may add to several.\n'
     + T + 'RtsBadR,                 // rts_bad_r:  bit R (0x010), the RenderState against the record\n'
     + T + 'RtsBadXr,                // rts_bad_xr: bit X, attachment layout / access of a target against the record\n'
     + T + 'RtsBadXc,                // rts_bad_xc: bit X, depth_load_clear_enable set after the capture\n'
     + T + 'RtsBadXe,                // rts_bad_xe: bit X, the pass extents against the record\n'
     + T + 'RtsBadS,                 // rts_bad_s:  bit S (0x040), ImageStateSerial() moved over the capture\n'
     + T + 'RtsBadP,                 // rts_bad_p:  bit P (0x080), the capture closed an open pass\n'
     + T + 'RtsBadM,                 // rts_bad_m:  bit M (0x100), MetaEpoch() moved over the capture\n'
     + T + 'RtsBadL,                 // rts_bad_l:  bit L (0x200), the slow path or the re-find ran in the capture'),
])

patch('src/graphics/presentation/videoOut.cpp', [
    (T * 4 + '    {"rts_bad_b", FS::Counter::RtsBadB, false},\n'
     + T * 4 + '    {"rts_bad_rx", FS::Counter::RtsBadRx, false},',
     T * 4 + '    {"rts_bad_b", FS::Counter::RtsBadB, false},\n'
     + T * 4 + '    {"rts_bad_rx", FS::Counter::RtsBadRx, false},\n'
     + T * 4 + '    // Track F, F30k (ROADMAP s122 item 655(g)(2)).\n'
     + T * 4 + '    {"rts_bad_r", FS::Counter::RtsBadR, false},\n'
     + T * 4 + '    {"rts_bad_xr", FS::Counter::RtsBadXr, false},\n'
     + T * 4 + '    {"rts_bad_xc", FS::Counter::RtsBadXc, false},\n'
     + T * 4 + '    {"rts_bad_xe", FS::Counter::RtsBadXe, false},\n'
     + T * 4 + '    {"rts_bad_s", FS::Counter::RtsBadS, false},\n'
     + T * 4 + '    {"rts_bad_p", FS::Counter::RtsBadP, false},\n'
     + T * 4 + '    {"rts_bad_m", FS::Counter::RtsBadM, false},\n'
     + T * 4 + '    {"rts_bad_l", FS::Counter::RtsBadL, false},'),
])

patch('src/graphics/host_gpu/renderer/renderDraw.cpp', [
    # the header comment
    ('// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..4, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items',
     '// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..5, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items'),
    ('//   4 = 2 with PB items 3 (metadata epoch) and 4 (state_serial) not applied (positive control of place B; track F, F30d,\n'
     '//   ROADMAP s122 item 643(v)).',
     '//   4 = 2 with PB items 3 (metadata epoch) and 4 (state_serial) not applied (positive control of place B; track F, F30d,\n'
     '//   ROADMAP s122 item 643(v)); 5 = 2 with PB item 6 (the pinned pass, RtsXbPass) not applied (track F, F30k, ROADMAP\n'
     '//   s122 item 655(g)(1)).'),
    ('constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..20: mode line printed',
     'constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..21: mode line printed'),
    # RtsReport: the X source argument and the per-bit counters, after the race filter, next to rts_bad
    ('// Values 2/3: one draw\'s self-check result (s.5.2).  A race suppresses only the capture bits.\n'
     'void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth) {',
     '// Values 2/3: one draw\'s self-check result (s.5.2).  A race suppresses only the capture bits.  xsrc (track F, F30k):\n'
     '// the sources of bit X the post found - 1 attachment layout / access, 2 depth_load_clear_enable, 4 pass extents.\n'
     'void RtsReport(uint32_t bits, int frame, uint32_t age, uint32_t colors, bool depth, uint32_t xsrc) {'),
    (T + 'if ((bits & 0x030u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadRx, 1);\n'
     + T + '}',
     T + 'if ((bits & 0x030u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadRx, 1);\n'
     + T + '}\n'
     + T + '// Track F, F30k (ROADMAP s122 item 655(g)(2)): one counter per place B bit, X by its source.\n'
     + T + 'if ((bits & 0x010u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadR, 1);\n'
     + T + '}\n'
     + T + 'if ((xsrc & 1u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadXr, 1);\n'
     + T + '}\n'
     + T + 'if ((xsrc & 2u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadXc, 1);\n'
     + T + '}\n'
     + T + 'if ((xsrc & 4u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadXe, 1);\n'
     + T + '}\n'
     + T + 'if ((bits & 0x040u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadS, 1);\n'
     + T + '}\n'
     + T + 'if ((bits & 0x080u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadP, 1);\n'
     + T + '}\n'
     + T + 'if ((bits & 0x100u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadM, 1);\n'
     + T + '}\n'
     + T + 'if ((bits & 0x200u) != 0) {\n'
     + T + T + 'FS::Add(FS::Counter::RtsBadL, 1);\n'
     + T + '}'),
    # place A report: no X source there
    (T + T + T + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, state.color_count,\n'
     + T + T + T + '          static_cast<bool>(state.depth_info.image_id));',
     T + T + T + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, state.color_count,\n'
     + T + T + T + '          static_cast<bool>(state.depth_info.image_id), 0);'),
    # PB item 6 not applied at 5
    (T + T + '// 6 (N10, N11 - a narrowing of the set, [RC4]): inside the pass the record is pinned to.\n'
     + T + T + 'if (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial) {\n'
     + T + T + T + 'return C::RtsXbPass;\n'
     + T + T + '}',
     T + T + '// 6 (N10, N11 - a narrowing of the set, [RC4]): inside the pass the record is pinned to.  Not applied at value 5\n'
     + T + T + '// (track F, F30k, ROADMAP s122 item 655(g)(1)): the full capture then runs against a record this item would refuse.\n'
     + T + T + 'if (t_rts != 5 && (!buffer.IsRendering() || CommandBuffer::PassBeginSerial() != rec->pass_serial)) {\n'
     + T + T + T + 'return C::RtsXbPass;\n'
     + T + T + '}'),
    # the post: X by source
    (T + 'if (t_rts >= 2 && t_rts_pa) {\n'
     + T + T + 'uint32_t bits = t_rts_bits;\n'
     + T + T + 'if (t_rts_pb) {',
     T + 'if (t_rts >= 2 && t_rts_pa) {\n'
     + T + T + 'uint32_t bits = t_rts_bits;\n'
     + T + T + 'uint32_t xsrc = 0; // track F, F30k: the sources of bit X (RtsReport)\n'
     + T + T + 'if (t_rts_pb) {'),
    (T + T + T + T + '    image->binding.attachment_access != rec->t[i].att_access) {\n'
     + T + T + T + T + T + 'bits |= 0x020u; // X\n'
     + T + T + T + T + '}\n'
     + T + T + T + '}\n'
     + T + T + T + 'if (hd && state.depth_info.depth_load_clear_enable) {\n'
     + T + T + T + T + 'bits |= 0x020u;\n'
     + T + T + T + '}\n'
     + T + T + T + 'if (g_pass_extents.max_width != rec->extents.max_width ||\n'
     + T + T + T + '    g_pass_extents.max_height != rec->extents.max_height ||\n'
     + T + T + T + '    g_pass_extents.true_kpx != rec->extents.true_kpx) {\n'
     + T + T + T + T + 'bits |= 0x020u;\n'
     + T + T + T + '}',
     T + T + T + T + '    image->binding.attachment_access != rec->t[i].att_access) {\n'
     + T + T + T + T + T + 'bits |= 0x020u; // X\n'
     + T + T + T + T + T + 'xsrc |= 1u;\n'
     + T + T + T + T + '}\n'
     + T + T + T + '}\n'
     + T + T + T + 'if (hd && state.depth_info.depth_load_clear_enable) {\n'
     + T + T + T + T + 'bits |= 0x020u;\n'
     + T + T + T + T + 'xsrc |= 2u;\n'
     + T + T + T + '}\n'
     + T + T + T + 'if (g_pass_extents.max_width != rec->extents.max_width ||\n'
     + T + T + T + '    g_pass_extents.max_height != rec->extents.max_height ||\n'
     + T + T + T + '    g_pass_extents.true_kpx != rec->extents.true_kpx) {\n'
     + T + T + T + T + 'bits |= 0x020u;\n'
     + T + T + T + T + 'xsrc |= 4u;\n'
     + T + T + T + '}'),
    (T + T + 'if (bits != 0) {\n'
     + T + T + T + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd);\n'
     + T + T + '}',
     T + T + 'if (bits != 0) {\n'
     + T + T + T + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);\n'
     + T + T + '}'),
])
print('ALL OK')

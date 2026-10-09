# F30o (HPP-725), ROADMAP s122 item 664(e)(1)-(3): KYTY_RT_SKIP=6 (= 2 + the (a2) perturbation - a synthetic control of
# the bit S chain) and the counters rts_inj, rts_inj_s, rts_inj_race, rts_inj_nos, rts_inj_none.
# Usage: python patch_f30o.py <repo root>.  Whole-line anchors (each must hit exactly once); CRLF-safe; writes LF back
# (or CRLF if the file had it).  A copy of docs/track-f/f30k/patch_f30k.py with the edits replaced.
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
    ('    // of place B).  Track F, F30k (ROADMAP s122 item 655(g)(1)): 5 = the self-check with PB item 6 not applied.\n'
     '    {"KYTY_RT_SKIP", "rtskip", 1, 5},',
     '    // of place B).  Track F, F30k (ROADMAP s122 item 655(g)(1)): 5 = the self-check with PB item 6 not applied.\n'
     '    // Track F, F30o (ROADMAP s122 item 664(e)(1)): 6 = the self-check with the (a2) perturbation (control of bit S).\n'
     '    {"KYTY_RT_SKIP", "rtskip", 1, 6},'),
])

patch('src/common/gates.h', [
    (T + 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check, 3 self-check + positive control; default 1 since session 128; 4 self-check + positive control of place B, F30d; 5 self-check without PB item 6, F30k)',
     T + 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check, 3 self-check + positive control; default 1 since session 128; 4 self-check + positive control of place B, F30d; 5 self-check without PB item 6, F30k; 6 self-check + (a2) perturbation, F30o)'),
])

patch('src/common/frameStats.h', [
    (T + 'RtsBadL,                 // rts_bad_l:  bit L (0x200), the slow path or the re-find ran in the capture',
     T + 'RtsBadL,                 // rts_bad_l:  bit L (0x200), the slow path or the re-find ran in the capture\n'
     + T + '// Track F, F30o (ROADMAP s122 item 664(e)(2)): value 6 only - the (a2) perturbation and the outcome of the perturbed\n'
     + T + '// draw\'s self-check.  rts_inj_s + rts_inj_race + rts_inj_nos = rts_inj by construction (one of the three per\n'
     + T + '// perturbed draw, in its post); the perturbed reports are in rts_bad / rts_bad_s too.\n'
     + T + 'RtsInj,                  // rts_inj:      perturbations done (one tracked Transit of a colour target to eGeneral)\n'
     + T + 'RtsInjS,                 // rts_inj_s:    the perturbed draw\'s report carries S and the race filter kept it\n'
     + T + 'RtsInjRace,              // rts_inj_race: the perturbed draw\'s report was suppressed by the race filter\n'
     + T + 'RtsInjNos,               // rts_inj_nos:  the perturbed draw - no suppressed report and no S\n'
     + T + 'RtsInjNone,              // rts_inj_none: the N-th PA and PB draw had no eligible colour target (no perturbation)'),
])

patch('src/graphics/presentation/videoOut.cpp', [
    (T * 4 + '    {"rts_bad_l", FS::Counter::RtsBadL, false},',
     T * 4 + '    {"rts_bad_l", FS::Counter::RtsBadL, false},\n'
     + T * 4 + '    // Track F, F30o (ROADMAP s122 item 664(e)(2)).\n'
     + T * 4 + '    {"rts_inj", FS::Counter::RtsInj, false},\n'
     + T * 4 + '    {"rts_inj_s", FS::Counter::RtsInjS, false},\n'
     + T * 4 + '    {"rts_inj_race", FS::Counter::RtsInjRace, false},\n'
     + T * 4 + '    {"rts_inj_nos", FS::Counter::RtsInjNos, false},\n'
     + T * 4 + '    {"rts_inj_none", FS::Counter::RtsInjNone, false},'),
])

patch('src/graphics/host_gpu/renderer/renderDraw.cpp', [
    # the header comment
    ('// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..5, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items',
     '// Session 127, knob "rtskip" (KYTY_RT_SKIP, 0..6, default 0; docs/session-127/design127.md rev 2 with ROADMAP s122 items'),
    ('//   s122 item 655(g)(1)).',
     '//   s122 item 655(g)(1)); 6 = 2 with the (a2) perturbation on every 4 096th PA and PB draw (a synthetic control of\n'
     '//   the bit S chain; track F, F30o, ROADMAP s122 item 664(e)(1)).'),
    ('constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..21: mode line printed',
     'constinit thread_local uint32_t    t_rts_logged   = 0;       // bits 1..15: refusal printed; 17..22: mode line printed'),
    ('constinit thread_local uint32_t    t_rts_lines    = 0;       // RtSkipVerify lines printed (at most 40)',
     'constinit thread_local uint32_t    t_rts_lines    = 0;       // RtSkipVerify lines printed (at most 40)\n'
     'constinit thread_local bool        t_rts_inj      = false;   // value 6: this draw was perturbed (F30o), cleared by the post\n'
     '// Track F, F30o (ROADMAP s122 item 664(e)(1)): value 6 - PA and PB draws of the process counted at place B; every\n'
     '// kRtsInjEvery-th one is perturbed.  Touched at value 6 only.\n'
     'inline constexpr uint64_t   kRtsInjEvery = 4096;\n'
     'std::atomic<uint64_t>       g_rts_inj_n {0};'),
    # the perturbation helper, before the pin
    ('// The pin (s.4.3): after BeginRendering the record the post left is pinned to the pass this draw renders in.',
     '// Track F, F30o (ROADMAP s122 item 664(e)(1)), value 6: the tracked layout of every subresource of the view range is\n'
     '// eColorAttachmentOptimal - read exactly as Image::GetBarriers will (the whole state while there are no subresource\n'
     '// states, else the states of the range; a volume has one layer).  A range outside the image is not eligible.\n'
     'bool RtsInjAttachLayout(const Image& image, ImageSubresourceRange r) noexcept {\n'
     + T + 'const uint32_t levels = image.info.resources.levels;\n'
     + T + 'const uint32_t layers = image.info.resources.layers;\n'
     + T + 'if (image.info.IsVolume()) {\n'
     + T + T + 'r.base_layer  = 0;\n'
     + T + T + 'r.layer_count = 1;\n'
     + T + '}\n'
     + T + 'if (r.level_count == 0 || r.layer_count == 0 || r.base_level + r.level_count > levels ||\n'
     + T + '    r.base_layer + r.layer_count > layers) {\n'
     + T + T + 'return false;\n'
     + T + '}\n'
     + T + 'const auto& b = image.backing;\n'
     + T + 'if (b.subresource_states.empty()) {\n'
     + T + T + 'return b.state.layout == vk::ImageLayout::eColorAttachmentOptimal;\n'
     + T + '}\n'
     + T + 'for (uint32_t level = r.base_level; level < r.base_level + r.level_count; level++) {\n'
     + T + T + 'for (uint32_t layer = r.base_layer; layer < r.base_layer + r.layer_count; layer++) {\n'
     + T + T + T + 'const size_t index = static_cast<size_t>(level) * layers + layer;\n'
     + T + T + T + 'if (index >= b.subresource_states.size() ||\n'
     + T + T + T + '    b.subresource_states[index].layout != vk::ImageLayout::eColorAttachmentOptimal) {\n'
     + T + T + T + T + 'return false;\n'
     + T + T + T + '}\n'
     + T + T + '}\n'
     + T + '}\n'
     + T + 'return true;\n'
     '}\n'
     '\n'
     '// Track F, F30o (ROADMAP s122 item 664(e)(1)), value 6, at place B after PB held and before the snapshots: on every\n'
     '// kRtsInjEvery-th PA and PB draw, one Transit of the first colour target whose tracked layout is the attachment layout\n'
     '// and which this draw does not sample, to eGeneral with the capture\'s access and view range (AcquireRenderTargets) -\n'
     '// the same tracker path (GetBarriers, NoteStateChange, the pass end) under the same lock.  The capture then transits it\n'
     '// back to eColorAttachmentOptimal between the snapshots: bit S.  Never the depth target, never a sampled target.\n'
     'void RtsInject(uint32_t cc, const RenderColorInfo* colors, Image* const* img) {\n'
     + T + 'namespace FS = Common::FrameStats;\n'
     + T + 'if ((g_rts_inj_n.fetch_add(1, std::memory_order_relaxed) + 1) % kRtsInjEvery != 0) {\n'
     + T + T + 'return;\n'
     + T + '}\n'
     + T + 'for (uint32_t i = 0; i < cc; i++) {\n'
     + T + T + 'Image&      image = *img[i];\n'
     + T + T + 'const auto& view = colors[i].desc.view_info;\n'
     + T + T + 'const ImageSubresourceRange range {view.base_level, view.level_count, view.base_layer, view.layer_count};\n'
     + T + T + 'if (image.binding.is_bound || !RtsInjAttachLayout(image, range)) {\n'
     + T + T + T + 'continue;\n'
     + T + T + '}\n'
     + T + T + 'image.Transit(vk::ImageLayout::eGeneral,\n'
     + T + T + '              vk::AccessFlagBits2::eColorAttachmentRead | vk::AccessFlagBits2::eColorAttachmentWrite, range,\n'
     + T + T + '              vk::CommandBuffer {}, RenderPassEnd::TargetTransit);\n'
     + T + T + 't_rts_inj = true;\n'
     + T + T + 'FS::Add(FS::Counter::RtsInj, 1);\n'
     + T + T + 'return;\n'
     + T + '}\n'
     + T + 'FS::Add(FS::Counter::RtsInjNone, 1);\n'
     '}\n'
     '\n'
     '// The pin (s.4.3): after BeginRendering the record the post left is pinned to the pass this draw renders in.'),
    # the latch clears the flag with the rest of the draw state
    (T + 't_rts_refind = false;\n'
     + T + 't_rts_bits   = 0;\n'
     + T + 't_rts_take   = nullptr;',
     T + 't_rts_refind = false;\n'
     + T + 't_rts_bits   = 0;\n'
     + T + 't_rts_inj    = false; // track F, F30o: a perturbed draw that never reached its post\n'
     + T + 't_rts_take   = nullptr;'),
    # place B: the perturbation at 6, after PB and before the snapshots
    (T + 'if (t_rts >= 2 && pb_ok) {\n'
     + T + T + 't_rts_pb = true;\n'
     + T + T + 'FS::Add(C::RtsPb, 1);\n'
     + T + T + 'FS::Add(C::RtsChkB, 1);\n'
     + T + '}',
     T + 'if (t_rts >= 2 && pb_ok) {\n'
     + T + T + 't_rts_pb = true;\n'
     + T + T + 'FS::Add(C::RtsPb, 1);\n'
     + T + T + 'FS::Add(C::RtsChkB, 1);\n'
     + T + T + '// Track F, F30o (ROADMAP s122 item 664(e)(1)): value 6 - the (a2) perturbation, after PB, before the snapshots.\n'
     + T + T + 'if (t_rts == 6) [[unlikely]] {\n'
     + T + T + T + 'RtsInject(cc, state.color_info, img.data());\n'
     + T + T + '}\n'
     + T + '}'),
    # the post: the outcome of the perturbed draw, with the race filter's own predicate (RtsReport)
    (T + T + 'if (bits != 0) {\n'
     + T + T + T + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);\n'
     + T + T + '}',
     T + T + '// Track F, F30o (ROADMAP s122 item 664(e)(2)): the outcome of the perturbed draw - suppressed by the race filter\n'
     + T + T + '// (the predicate of RtsReport, which runs iff bits != 0), else S, else neither.\n'
     + T + T + 'if (t_rts_inj) {\n'
     + T + T + T + 't_rts_inj = false;\n'
     + T + T + T + 'if (bits != 0 && t_rts_race && (bits & kRtsBitsA) == 0) {\n'
     + T + T + T + T + 'FS::Add(C::RtsInjRace, 1);\n'
     + T + T + T + '} else if ((bits & 0x040u) != 0) {\n'
     + T + T + T + T + 'FS::Add(C::RtsInjS, 1);\n'
     + T + T + T + '} else {\n'
     + T + T + T + T + 'FS::Add(C::RtsInjNos, 1);\n'
     + T + T + T + '}\n'
     + T + T + '}\n'
     + T + T + 'if (bits != 0) {\n'
     + T + T + T + 'RtsReport(bits, m_context.GetGpu().GetFrameNum(), rec->age, cc, hd, xsrc);\n'
     + T + T + '}'),
])
print('ALL OK')

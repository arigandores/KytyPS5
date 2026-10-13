"""M9d3 (HPP-876): copy of m657/m9d2/mut_m9d2.py (out m9d3/mut, driver run_stand_m9d3.py, t4 re-anchored, + t7,
t8, t9; built by mk_m9d3.py). Was:
M9d2 (HPP-874): copy of m657/m9d/mut_m9d.py (out m9d2/mut, driver run_stand_m9d2.py, t1/t2 re-anchored, + t5, t6;
built by mk_mut_m9d2.py). Was:
M9d (HPP-869, ROADMAP s122 item 785(d)): mutants of KYTY_DIAG_T188 stage 1. One exact substitution set per mutant in
the worktree, the build of the stand target, the driver arms; the file is restored byte for byte after every mutant and
checked by sha256 at the end; then a control build of both stand targets and every arm (ALL OK).
A mutant is CAUGHT when an arm it names FAILs (for m14 - gpu1 FAILs while gpu0 passes: the fused branch alone). A mutant
whose build fails is BUILD_FAIL (not caught). Usage: python mut_m9d.py [name ...] (a batch, no control) | control (the control alone) | (nothing: all + control). Lock and STOP: exit 3 between mutants.
Output: one line per mutant and ALL OK (every mutant CAUGHT and the control ALL OK)."""
import hashlib
import os
import subprocess
import sys

WT = 'C:/kyty/m657/m9d/wt'
BUILD_CMD = 'C:\\kyty\\m657\\m9d\\build_m9d.cmd'
OUT = 'C:/kyty/m657/m9d3/mut'
LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
IDLE = 0x40
DIAG = 'src/libs/diagT188.cpp'
DIAGH = 'src/libs/diagT188.h'
TC = 'src/graphics/host_gpu/renderer/cache/textureCache.cpp'
IMGH = 'src/graphics/host_gpu/renderer/image/image.h'
PM4 = 'src/graphics/guest_gpu/command_processor/pm4Handlers.cpp'
PURE = ('t188_stand', ['pure'])
GPU = ('shader_recompiler_compute_tests', ['gpu1'])

MUTANTS = [
    # name, file, [(old, new)], (target, arms)
    ('m1_cover_data', DIAG, [('return address <= g.address && address + size >= g.address + g.source_size;',
                              'return address <= g.address && address + size >= g.address + g.data_size;')], PURE),
    ('m2_reopen_new', DIAG, [('\tif (s.open) {\n\t\tev  = Ev::Reopen;', '\tif (false) {\n\t\tev  = Ev::Reopen;')], PURE),
    ('m3_close_unchecked', DIAG, [('\tif (s.open) {\n\t\tCloseEpisode(s, site);\n\t} else {\n\t\tAdd(C::cl_none);\n\t}\n}\n\nvoid NoteFree',
                                   '\tCloseEpisode(s, site);\n}\n\nvoid NoteFree')], PURE),
    ('m4_tint_w', DIAG, [('\t\tmask = lost_mask;\n\t\tAdd(C::tint_part_mips, Popcount(part_mask));\n\t}\n\tmask = VerifyTintPlan(g, mask, first, end, s.w, s.n);',
                          '\t\tmask = lost_mask | part_mask;\n\t\tAdd(C::tint_part_mips, Popcount(part_mask));\n\t}\n\tmask = VerifyTintPlan(g, mask, first, end, s.w, s.n);')], PURE),
    ('m5_tint_deferred', DIAG, [('\tmask = VerifyTintPlan(g, mask, first, end, s.w, s.n);',
                                 '\tmask = VerifyTintPlan(g, mask | (pend_end > pend_first ? ((1u << pend_end) - 1u) & ~((1u << pend_first) - 1u) : 0u), first, end, s.w, s.n);')], PURE),
    ('m6_sync_partial', DIAG, [('\tif (full) {\n\t\ts.sseq.store(', '\tif (true) {\n\t\ts.sseq.store(')], PURE),
    ('m7_wseq_frozen', DIAGH, [('\ts.wseq.fetch_add(1, std::memory_order_acq_rel);\n', '')], PURE),
    ('m8_commit_noop', DIAG, [('void CloseNoUpload(ImageState& s, Close site, bool locked) {\n',
                               'void CloseNoUpload(ImageState& s, Close site, bool locked) {\n\tif (site == Close::Commit) {\n\t\treturn;\n\t}\n')], PURE),
    ('m8s_no_s7_site', TC, [('\t\tT188Close(image, DiagT188::Close::Commit); // Track M, M9d: S7\n', '')], GPU),
    ('m9_propagate_noop', DIAG, [('\tif (!src.open) {\n\t\treturn;\n\t}', '\tif (true) {\n\t\treturn;\n\t}')], PURE),
    ('m10_lock_unchecked', DIAG, [('\tif (!locked) {\n\t\tAdd(C::lock_bad);\n\t\treturn Ev::None;\n\t}\n', '')], PURE),
    ('m11_vol_mipal', DIAG, [('\tif (g.volume) {\n\t\treturn Shape::Other;\n\t}\n', '')], PURE),
    ('m12_class_at_close', DIAG, [('\tconst uint64_t key = s.key;\n\tCloseEpisode(s, site);',
                                   '\ts.key = ClassKey(cf_now);\n\tconst uint64_t key = s.key;\n\tCloseEpisode(s, site);')], PURE),
    ('m13_sw_in_branch', IMGH, [('\t\tif (DiagT188::Mode() != 0) [[unlikely]] {\n\t\t\tDiagT188::NoteGpuWrite(t188);\n\t\t}\n', ''),
                                ('\t\tif (!m_gpu_modified) {\n\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::GpuDirtyGenImage, 1);\n',
                                 '\t\tif (!m_gpu_modified) {\n\t\t\tif (DiagT188::Mode() != 0) {\n\t\t\t\tDiagT188::NoteGpuWrite(t188);\n\t\t\t}\n\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::GpuDirtyGenImage, 1);\n')], GPU),
    ('m14_flag_upload_only', TC, [('\t\tDiagT188::NoteImageWrite(image.t188);\n\t}\n\tconst auto& info    = image.info;',
                                   '\t}\n\tconst auto& info    = image.info;')], ('shader_recompiler_compute_tests', ['gpu1', 'gpu0'])),
    ('m15_ovr_first_reg', PM4, [('\t\tif (DiagT188::Mode() >= 1) [[unlikely]] {\n\t\t\t// Track M, M9d (T109, RC14): the one place every write of the register reaches (direct packet, range from\n\t\t\t// DB_COUNT_CONTROL, indirect paths).\n\t\t\tDiagT109::NoteRenderOverride(value);\n\t\t}\n', ''),
                                ('\tfor (uint32_t i = 0; i < num_values; i++) {\n\t\tHwCtxSetDepthMetadataRegister(cp, cmd_offset + i, buffer[i]);\n\t}\n',
                                 '\tif (cmd_offset == Pm4::DB_RENDER_OVERRIDE && DiagT188::Mode() >= 1) {\n\t\tDiagT109::NoteRenderOverride(buffer[0]);\n\t}\n\tfor (uint32_t i = 0; i < num_values; i++) {\n\t\tHwCtxSetDepthMetadataRegister(cp, cmd_offset + i, buffer[i]);\n\t}\n')], GPU),
    ('g1_base_plus1', TC, [('const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, l, 1, 0, layers};',
                            'const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, l + 1, 1, 0, layers};')], GPU),
    ('g2_layer1', TC, [('const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, l, 1, 0, layers};',
                        'const vk::ImageSubresourceRange range {vk::ImageAspectFlagBits::eColor, l, 1, 0, 1};')], GPU),
    ('g3_rb_before_clear', TC, [('\tconst uint32_t            layers = image.backing.layers;\n\tfor (uint32_t l = 0; l < DiagT188::kLevels; l++) {\n\t\tif ((mask & (1u << l)) == 0) {',
                                 '\tconst uint32_t            layers = image.backing.layers;\n\tconst auto clear_all = [&] {\n\tfor (uint32_t l = 0; l < DiagT188::kLevels; l++) {\n\t\tif ((mask & (1u << l)) == 0) {'),
                                ('\t\t                                 &range);\n\t}\n\tif (rb_mask == 0) {\n\t\treturn;\n\t}',
                                 '\t\t                                 &range);\n\t}\n\t};\n\tif (rb_mask == 0) {\n\t\tclear_all();\n\t\treturn;\n\t}'),
                                ('\tReadTexels(command, image, infos.data(), n, rb_buffer, rb_offset);\n}',
                                 '\tReadTexels(command, image, infos.data(), n, rb_buffer, rb_offset);\n\timage.Transit(vk::ImageLayout::eTransferDstOptimal, vk::AccessFlagBits2::eTransferWrite, {}, command.Handle());\n\tclear_all();\n}')], GPU),
    ('g4_no_transit', TC, [('\timage.Transit(vk::ImageLayout::eTransferDstOptimal, vk::AccessFlagBits2::eTransferWrite, {}, command.Handle());\n\tconst vk::ClearColorValue',
                            '\tconst vk::ClearColorValue')], ('shader_recompiler_compute_tests', ['gpuv'])),
    ('t1_vp0_only', DIAG, [('\tfor (uint32_t i = 0; i < count; i++) {\n\t\tif (scissors[i].extent',
                            '\tfor (uint32_t i = 0; i < 1 && i < count; i++) {\n\t\tif (scissors[i].extent')], PURE),
    ('t2_nonstrict', DIAG, [('\t\tif (lo > 0.0f || hi < 1.0f) {',
                             '\t\tif (lo >= 0.0f || hi <= 1.0f) {')], PURE),
    ('t3_bias_any', DIAG, [('\tif (depth_format != VK_FORMAT_D32_SFLOAT && depth_format != VK_FORMAT_D32_SFLOAT_S8_UINT) {\n',
                            '\tif (bias) {\n\t\tBump(g_bias_d32);\n\t}\n\tif (depth_format != VK_FORMAT_D32_SFLOAT && depth_format != VK_FORMAT_D32_SFLOAT_S8_UINT) {\n')], PURE),
    ('t4_zx_narrow_any', DIAG, [('\tif (z_export) {\n\t\tBump(g_zx_d32);\n\t\tif (narrow) {\n\t\t\tBump(g_zx_narrow);\n',
                                 '\tif (z_export) {\n\t\tBump(g_zx_d32);\n\t}\n\t{\n\t\tif (narrow) {\n\t\t\tBump(g_zx_narrow);\n')], PURE),
    # M9d2 (item 788(b)(4)): t5 - every slot counts (the scissor-area test removed); t6 - raw minDepth / maxDepth.
    ('t5_all_slots', DIAG, [('\t\tif (scissors[i].extent.width == 0 || scissors[i].extent.height == 0) {\n\t\t\tcontinue; // M9d2: the slot does not rasterize (empty ViewportIndex slot, zero-area scissor)\n\t\t}\n', '')], PURE),
    ('t6_raw_range', DIAG, [('\t\tconst float lo = std::min(viewports[i].minDepth, viewports[i].maxDepth);\n\t\tconst float hi = std::max(viewports[i].minDepth, viewports[i].maxDepth);\n',
                             '\t\tconst float lo = viewports[i].minDepth;\n\t\tconst float hi = viewports[i].maxDepth;\n')], PURE),
    # M9d3 (item 789(v)(3)): t7 - the _vi counters are not counted; t8 - _vi counted at count = 1; t9 - narrow_cd
    # without the clip_disable condition.
    ('t7_vi_none', DIAG, [('\t\t\t\tBump(g_zx_narrow_vi); // M9d3: the narrow slot may be one the VS never writes\n', ''),
                          ('\t\t\t\tBump(g_bias_narrow_vi); // M9d3\n', '')], PURE),
    ('t8_vi_count1', DIAG, [('\t\t\tif (count > 1) {\n\t\t\t\tBump(g_zx_narrow_vi);',
                             '\t\t\tif (count >= 1) {\n\t\t\t\tBump(g_zx_narrow_vi);'),
                            ('\t\t\tif (count > 1) {\n\t\t\t\tBump(g_bias_narrow_vi);',
                             '\t\t\tif (count >= 1) {\n\t\t\t\tBump(g_bias_narrow_vi);')], PURE),
    ('t9_cd_any', DIAG, [('\tif (narrow && (z_export || bias) && count > 1 && clip_disable) {\n',
                          '\tif (narrow && (z_export || bias) && count > 1) {\n')], PURE),
]

FILES = sorted({m[1] for m in MUTANTS})


def sha(rel):
    return hashlib.sha256(open(os.path.join(WT, rel), 'rb').read()).hexdigest()


def blocked():
    return os.path.exists(LOCK) or os.path.exists(STOP)


def build(target, log):
    with open(log, 'wb') as f:
        return subprocess.run(['cmd', '/c', BUILD_CMD, 'target', target], stdout=f, stderr=subprocess.STDOUT,
                              creationflags=IDLE).returncode


def arms(names, tag):
    out = os.path.join(OUT, tag)
    r = subprocess.run([sys.executable, 'C:/kyty/m657/m9d3/run_stand_m9d3.py', 'C:/kyty/m657/m9d/build', out] + names,
                       capture_output=True, text=True, creationflags=IDLE)
    res = {}
    for line in r.stdout.splitlines():
        head = line.split(' ', 1)[0]
        if head in names:
            res[head] = line.endswith('-> OK')
    return res, r.stdout


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[1:])
    check = '--check' in only
    only.discard('--check')
    before = {f: sha(f) for f in FILES}
    results = []
    for name, rel, subs, (target, arm_names) in MUTANTS:
        if (only and name not in only) or 'control' in only:
            continue
        if check:
            text = open(os.path.join(WT, rel), 'rb').read().decode('utf-8')
            print(name, 'anchors', [text.count(o) for o, _ in subs])
            continue
        if blocked():
            print('LOCK or STOP before', name)
            return 3
        path = os.path.join(WT, rel)
        raw = open(path, 'rb').read()
        text = raw.decode('utf-8')
        bad = [o for o, _ in subs if text.count(o) != 1]
        if bad:
            print('%s ANCHOR %r' % (name, bad[0][:60]))
            results.append(False)
            continue
        for o, n in subs:
            text = text.replace(o, n)
        open(path, 'wb').write(text.encode('utf-8'))
        try:
            rc = build(target, os.path.join(OUT, name + '_build.log'))
            if rc != 0:
                print('%s BUILD_FAIL rc=%d' % (name, rc))
                results.append(False)
                continue
            res, stdout = arms(arm_names, name)
            open(os.path.join(OUT, name + '_arms.txt'), 'w').write(stdout)
            if name.startswith('m14'):
                caught = res.get('gpu1') is False and res.get('gpu0') is True
            else:
                caught = any(v is False for v in res.values()) and len(res) == len(arm_names)
            print('%s %s %s' % (name, 'CAUGHT' if caught else 'SURVIVED', res))
            results.append(caught)
        finally:
            open(path, 'wb').write(raw)
    after = {f: sha(f) for f in FILES}
    restored = after == before
    print('sources restored (sha256 of %d files): %s' % (len(FILES), restored))
    if check:
        return 0
    if only - {'control'}:
        print('mutants %d of %d CAUGHT (batch, no control)' % (sum(results), len(results)))
        print('BATCH OK' if all(results) and restored else 'BATCH FAIL')
        return 0
    if blocked():
        print('LOCK or STOP before control')
        return 3
    ok_build = build('t188_stand', os.path.join(OUT, 'control_stand_build.log')) == 0 and \
        build('shader_recompiler_compute_tests', os.path.join(OUT, 'control_gpu_build.log')) == 0
    res, stdout = arms(['pure', 'cls', 'gpu1', 'gpu0', 'gpuv'], 'control')
    open(os.path.join(OUT, 'control_arms.txt'), 'w').write(stdout)
    control = ok_build and len(res) == 5 and all(res.values())
    print('CONTROL build=%d arms=%s' % (1 if ok_build else 0, res))
    print('mutants %d of %d CAUGHT' % (sum(results), len(results)))
    print('ALL OK' if all(results) and restored and control else 'FAIL')
    return 0


if __name__ == '__main__':
    sys.exit(main())

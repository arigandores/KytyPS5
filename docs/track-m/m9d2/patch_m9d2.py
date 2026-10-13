"""M9d2 (HPP-874, ROADMAP s122 item 788(b)): RC1 of M9e in DiagT109::NoteDraw - only rasterized slots (scissor area > 0,
the array setScissorWithCount takes) and the [min, max] clamp range; the stand cases t109_vi16, t109_inv, t109_inv_n,
t109_vi16n. Exact whole-line anchors, each found exactly once; CRLF is stripped before the search and restored; LF out.
Usage: python patch_m9d2.py <worktree root>. Lock: exit 3."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
ROOT = sys.argv[1]

EDITS = {
    'src/libs/diagT188.h': [
        ("// db_shader_control.shader_z_export_enable, bias - depth_bias_enable, viewports / count - the computed VkViewport array\n"
         "// passed to vkCmdSetViewportWithCount (after minDepth / maxDepth).\n"
         "void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,\n"
         "              uint32_t count);\n",
         "// db_shader_control.shader_z_export_enable, bias - depth_bias_enable, viewports / scissors / count - the computed\n"
         "// VkViewport and VkRect2D arrays passed to vkCmdSetViewportWithCount / vkCmdSetScissorWithCount (after minDepth /\n"
         "// maxDepth and the empty-slot rule). Track M, M9d2 (RC1 of M9e, ROADMAP s122 item 788(b)): a slot counts only when\n"
         "// its scissor has area > 0 (it rasterizes); its clamp range is [min(minDepth, maxDepth), max(minDepth, maxDepth)].\n"
         "void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,\n"
         "              const VkRect2D* scissors, uint32_t count);\n"),
    ],
    'src/libs/diagT188.cpp': [
        ("void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,\n"
         "              uint32_t count) {\n",
         "void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,\n"
         "              const VkRect2D* scissors, uint32_t count) {\n"),
        ("\tfor (uint32_t i = 0; i < count; i++) {\n"
         "\t\tif (viewports[i].minDepth > 0.0f || viewports[i].maxDepth < 1.0f) {\n"
         "\t\t\tnarrow = true;\n"
         "\t\t}\n"
         "\t}\n",
         "\tfor (uint32_t i = 0; i < count; i++) {\n"
         "\t\tif (scissors[i].extent.width == 0 || scissors[i].extent.height == 0) {\n"
         "\t\t\tcontinue; // M9d2: the slot does not rasterize (empty ViewportIndex slot, zero-area scissor)\n"
         "\t\t}\n"
         "\t\tconst float lo = std::min(viewports[i].minDepth, viewports[i].maxDepth);\n"
         "\t\tconst float hi = std::max(viewports[i].minDepth, viewports[i].maxDepth);\n"
         "\t\tif (lo > 0.0f || hi < 1.0f) {\n"
         "\t\t\tnarrow = true;\n"
         "\t\t}\n"
         "\t}\n"),
    ],
    'src/graphics/host_gpu/renderer/renderDraw.cpp': [
        ("\t\t// Track M, M9d (T109, ROADMAP s122 item 785(b)(4)): the draw with its computed viewports - the array\n"
         "\t\t// setViewportWithCount took above, after minDepth / maxDepth.\n",
         "\t\t// Track M, M9d (T109, ROADMAP s122 item 785(b)(4)): the draw with its computed viewports - the array\n"
         "\t\t// setViewportWithCount took above, after minDepth / maxDepth; M9d2 (item 788(b)(3)): and the computed scissors -\n"
         "\t\t// the array setScissorWithCount took above (a slot counts only when it rasterizes).\n"),
        ("\t\t                   reinterpret_cast<const VkViewport*>(viewports.data()), viewport_count);\n",
         "\t\t                   reinterpret_cast<const VkViewport*>(viewports.data()),\n"
         "\t\t                   reinterpret_cast<const VkRect2D*>(scissors.data()), viewport_count);\n"),
    ],
    'tests/T188Stand.cpp': [
        ("\t\tVkViewport vp[2] = {};\n"
         "\t\tvp[0].minDepth   = d.min0;\n"
         "\t\tvp[0].maxDepth   = d.max0;\n"
         "\t\tvp[1].minDepth   = d.min1;\n"
         "\t\tvp[1].maxDepth   = d.max1;\n"
         "\t\tT109::NoteDraw(d.fmt, d.test, d.write, d.zx, d.bias, vp, d.count);\n",
         "\t\tVkViewport vp[2] = {};\n"
         "\t\tvp[0].minDepth   = d.min0;\n"
         "\t\tvp[0].maxDepth   = d.max0;\n"
         "\t\tvp[1].minDepth   = d.min1;\n"
         "\t\tvp[1].maxDepth   = d.max1;\n"
         "\t\tVkRect2D sc[2]   = {};\n"
         "\t\tsc[0].extent     = {64, 64}; // M9d2: both slots rasterize\n"
         "\t\tsc[1].extent     = {64, 64};\n"
         "\t\tT109::NoteDraw(d.fmt, d.test, d.write, d.zx, d.bias, vp, sc, d.count);\n"),
        ("\t{\n"
         "\t\tReset(1);\n"
         "\t\tT109::NoteRenderOverride(0x20000000u);\n",
         "\t// M9d2 (RC1 of M9e, ROADMAP s122 item 788(b)(4)): rasterized slots only (scissor area > 0) and the [min, max] range.\n"
         "\t// D32, test, write, Z export and bias on; an empty slot is minDepth = maxDepth = 0, width 1, scissor {0, 0} (as\n"
         "\t// SetGraphicsDynamicParams leaves it); the active slot has a 64x64 scissor. want = zx_narrow = bias_narrow.\n"
         "\tstruct Slots {\n"
         "\t\tconst char* name;\n"
         "\t\tuint32_t    count;\n"
         "\t\tuint32_t    active;\n"
         "\t\tfloat       min_a, max_a;\n"
         "\t\tuint64_t    want;\n"
         "\t};\n"
         "\tconst Slots slots[] = {\n"
         "\t    // 16 slots, slot 0 full, slots 1-15 empty 0/0 (t5: every slot without the scissor test)\n"
         "\t    {\"t109_vi16\", 16, 0, 0.0f, 1.0f, 0},\n"
         "\t    // inverted full range [1, 0] (t6: raw minDepth / maxDepth without min/max)\n"
         "\t    {\"t109_inv\", 1, 0, 1.0f, 0.0f, 0},\n"
         "\t    // inverted narrow range [1, 0.5] - positive control of min/max\n"
         "\t    {\"t109_inv_n\", 1, 0, 1.0f, 0.5f, 1},\n"
         "\t    // 16 slots, active slot 3 [0, 0.5], the rest empty (t1: only slot 0)\n"
         "\t    {\"t109_vi16n\", 16, 3, 0.0f, 0.5f, 1},\n"
         "\t};\n"
         "\tfor (const auto& s: slots) {\n"
         "\t\tReset(1);\n"
         "\t\tVkViewport vp[16] = {};\n"
         "\t\tVkRect2D   sc[16] = {};\n"
         "\t\tfor (auto& v: vp) {\n"
         "\t\t\tv.width  = 1.0f;\n"
         "\t\t\tv.height = 1.0f;\n"
         "\t\t}\n"
         "\t\tvp[s.active].width    = 64.0f;\n"
         "\t\tvp[s.active].height   = 64.0f;\n"
         "\t\tvp[s.active].minDepth = s.min_a;\n"
         "\t\tvp[s.active].maxDepth = s.max_a;\n"
         "\t\tsc[s.active].extent   = {64, 64};\n"
         "\t\tT109::NoteDraw(VK_FORMAT_D32_SFLOAT, true, true, true, true, vp, sc, s.count);\n"
         "\t\tconst auto t = T109::Read();\n"
         "\t\tCheck(s.name,\n"
         "\t\t      {{\"x:d32\", 1}, {\"x:zx_d32\", 1}, {\"x:zx_narrow\", s.want}, {\"x:bias_d32\", 1}, {\"x:bias_narrow\", s.want}},\n"
         "\t\t      {{\"x:d32\", t.d32}, {\"x:zx_d32\", t.zx_d32}, {\"x:zx_narrow\", t.zx_narrow}, {\"x:bias_d32\", t.bias_d32},\n"
         "\t\t       {\"x:bias_narrow\", t.bias_narrow}});\n"
         "\t}\n"
         "\t{\n"
         "\t\tReset(1);\n"
         "\t\tT109::NoteRenderOverride(0x20000000u);\n"),
    ],
}

ok = True
for rel, edits in EDITS.items():
    p = os.path.join(ROOT, rel)
    raw = open(p, 'rb').read().decode('utf-8')
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    for old, new in edits:
        n = s.count(old)
        if n != 1:
            print('ANCHOR %s count=%d: %r' % (rel, n, old[:80]))
            ok = False
            continue
        s = s.replace(old, new)
    if crlf:
        s = s.replace('\n', '\r\n')
    if ok:
        open(p, 'wb').write(s.encode('utf-8'))
        print('patched', rel, 'crlf' if crlf else 'lf')
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

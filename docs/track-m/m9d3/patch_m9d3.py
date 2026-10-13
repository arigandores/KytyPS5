"""M9d3 (HPP-876, ROADMAP s122 item 789(v)(1)-(3)): RC1 of M9e2 - witness of multi-slot narrow draws in
DiagT109::NoteDraw: the bool clip_disable argument, the T109Stat fields zx_narrow_vi, bias_narrow_vi, narrow_cd (last),
the stand cases t109_cd16, t109_cd1 and the new fields in the expectations of the previous T109 cases.
Exact whole-line anchors, each found exactly once; CRLF is stripped before the search and restored; LF out.
Usage: python patch_m9d3.py <worktree root>. Lock: exit 3."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
ROOT = sys.argv[1]

EDITS = {
    'src/libs/diagT188.h': [
        ("// its scissor has area > 0 (it rasterizes); its clamp range is [min(minDepth, maxDepth), max(minDepth, maxDepth)].\n"
         "void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,\n"
         "              const VkRect2D* scissors, uint32_t count);\n",
         "// its scissor has area > 0 (it rasterizes); its clamp range is [min(minDepth, maxDepth), max(minDepth, maxDepth)].\n"
         "// M9d3 (RC1 of M9e2, item 789(v)): clip_disable - PA_CL_CLIP_CNTL.CLIP_DISABLE of the same draw; zx_narrow_vi /\n"
         "// bias_narrow_vi - the draws counted in zx_narrow / bias_narrow with count > 1 (which slot the VS writes is not seen\n"
         "// on the CPU); narrow_cd - the draws counted in zx_narrow or bias_narrow with count > 1 and clip_disable (reference).\n"
         "void NoteDraw(uint32_t depth_format, bool test, bool write, bool z_export, bool bias, const VkViewport* viewports,\n"
         "              const VkRect2D* scissors, uint32_t count, bool clip_disable);\n"),
        ("\tuint64_t ovr_w;\n"
         "\tuint64_t ovr_vpc;\n"
         "};\n",
         "\tuint64_t ovr_w;\n"
         "\tuint64_t ovr_vpc;\n"
         "\tuint64_t zx_narrow_vi;   // M9d3\n"
         "\tuint64_t bias_narrow_vi; // M9d3\n"
         "\tuint64_t narrow_cd;      // M9d3\n"
         "};\n"),
    ],
    'src/libs/diagT188.cpp': [
        ("std::atomic<uint64_t> g_ovr_vpc {0};\n",
         "std::atomic<uint64_t> g_ovr_vpc {0};\n"
         "std::atomic<uint64_t> g_zx_narrow_vi {0};   // M9d3 (item 789(v)(2))\n"
         "std::atomic<uint64_t> g_bias_narrow_vi {0}; // M9d3\n"
         "std::atomic<uint64_t> g_narrow_cd {0};      // M9d3\n"),
        ("              const VkRect2D* scissors, uint32_t count) {\n",
         "              const VkRect2D* scissors, uint32_t count, bool clip_disable) {\n"),
        ("\tif (z_export) {\n"
         "\t\tBump(g_zx_d32);\n"
         "\t\tif (narrow) {\n"
         "\t\t\tBump(g_zx_narrow);\n"
         "\t\t}\n"
         "\t}\n"
         "\tif (bias) {\n"
         "\t\tBump(g_bias_d32);\n"
         "\t\tif (narrow) {\n"
         "\t\t\tBump(g_bias_narrow);\n"
         "\t\t}\n"
         "\t}\n"
         "}\n",
         "\tif (z_export) {\n"
         "\t\tBump(g_zx_d32);\n"
         "\t\tif (narrow) {\n"
         "\t\t\tBump(g_zx_narrow);\n"
         "\t\t\tif (count > 1) {\n"
         "\t\t\t\tBump(g_zx_narrow_vi); // M9d3: the narrow slot may be one the VS never writes\n"
         "\t\t\t}\n"
         "\t\t}\n"
         "\t}\n"
         "\tif (bias) {\n"
         "\t\tBump(g_bias_d32);\n"
         "\t\tif (narrow) {\n"
         "\t\t\tBump(g_bias_narrow);\n"
         "\t\t\tif (count > 1) {\n"
         "\t\t\t\tBump(g_bias_narrow_vi); // M9d3\n"
         "\t\t\t}\n"
         "\t\t}\n"
         "\t}\n"
         "\tif (narrow && (z_export || bias) && count > 1 && clip_disable) {\n"
         "\t\tBump(g_narrow_cd); // M9d3: once per draw (reference)\n"
         "\t}\n"
         "}\n"),
        ("\treturn {load(g_d32),       load(g_zx_d32), load(g_zx_narrow), load(g_bias_d32),\n"
         "\t        load(g_bias_narrow), load(g_ovr_w),  load(g_ovr_vpc)};\n",
         "\treturn {load(g_d32),       load(g_zx_d32), load(g_zx_narrow), load(g_bias_d32),\n"
         "\t        load(g_bias_narrow), load(g_ovr_w),  load(g_ovr_vpc), load(g_zx_narrow_vi),\n"
         "\t        load(g_bias_narrow_vi), load(g_narrow_cd)};\n"),
        ("\t     \" bias_narrow=%\" PRIu64 \" ovr_w=%\" PRIu64 \" ovr_vpc=%\" PRIu64 \"\\n\",\n"
         "\t     when, t.d32, t.zx_d32, t.zx_narrow, t.bias_d32, t.bias_narrow, t.ovr_w, t.ovr_vpc);\n",
         "\t     \" bias_narrow=%\" PRIu64 \" ovr_w=%\" PRIu64 \" ovr_vpc=%\" PRIu64 \" zx_narrow_vi=%\" PRIu64\n"
         "\t     \" bias_narrow_vi=%\" PRIu64 \" narrow_cd=%\" PRIu64 \"\\n\",\n"
         "\t     when, t.d32, t.zx_d32, t.zx_narrow, t.bias_d32, t.bias_narrow, t.ovr_w, t.ovr_vpc, t.zx_narrow_vi,\n"
         "\t     t.bias_narrow_vi, t.narrow_cd);\n"),
        ("\tfor (auto* a: {&g_d32, &g_zx_d32, &g_zx_narrow, &g_bias_d32, &g_bias_narrow, &g_ovr_w, &g_ovr_vpc}) {\n",
         "\tfor (auto* a: {&g_d32, &g_zx_d32, &g_zx_narrow, &g_bias_d32, &g_bias_narrow, &g_ovr_w, &g_ovr_vpc, &g_zx_narrow_vi,\n"
         "\t               &g_bias_narrow_vi, &g_narrow_cd}) {\n"),
    ],
    'src/graphics/host_gpu/renderer/renderDraw.cpp': [
        ("\t\t// the array setScissorWithCount took above (a slot counts only when it rasterizes).\n",
         "\t\t// the array setScissorWithCount took above (a slot counts only when it rasterizes); M9d3 (item 789(v)(1)): and\n"
         "\t\t// clip_disable of the same draw (the witness narrow_cd).\n"),
        ("\t\t                   reinterpret_cast<const VkRect2D*>(scissors.data()), viewport_count);\n",
         "\t\t                   reinterpret_cast<const VkRect2D*>(scissors.data()), viewport_count,\n"
         "\t\t                   ctx.GetClipControl().clip_disable);\n"),
    ],
    'tests/T188Stand.cpp': [
        # the previous draws: clip_disable false, want with the three new fields (item 789(v)(3))
        ("\t    {\"t109_d24\", VK_FORMAT_D24_UNORM_S8_UINT, true, true, true, true, 0.0f, 0.5f, 0.0f, 1.0f, 1, {0, 0, 0, 0, 0, 0, 0}},\n",
         "\t    {\"t109_d24\", VK_FORMAT_D24_UNORM_S8_UINT, true, true, true, true, 0.0f, 0.5f, 0.0f, 1.0f, 1, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}},\n"),
        ("\t    {\"t109_off\", VK_FORMAT_D32_SFLOAT, false, false, true, true, 0.0f, 0.5f, 0.0f, 1.0f, 1, {0, 0, 0, 0, 0, 0, 0}},\n",
         "\t    {\"t109_off\", VK_FORMAT_D32_SFLOAT, false, false, true, true, 0.0f, 0.5f, 0.0f, 1.0f, 1, {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}},\n"),
        ("\t    {\"t109_full\", VK_FORMAT_D32_SFLOAT, true, false, true, true, 0.0f, 1.0f, 0.0f, 1.0f, 2, {1, 1, 0, 1, 0, 0, 0}},\n",
         "\t    {\"t109_full\", VK_FORMAT_D32_SFLOAT, true, false, true, true, 0.0f, 1.0f, 0.0f, 1.0f, 2, {1, 1, 0, 1, 0, 0, 0, 0, 0, 0}},\n"),
        ("\t    {\"t109_max\", VK_FORMAT_D32_SFLOAT_S8_UINT, false, true, true, false, 0.0f, 0.5f, 0.0f, 1.0f, 1, {1, 1, 1, 0, 0, 0, 0}},\n",
         "\t    {\"t109_max\", VK_FORMAT_D32_SFLOAT_S8_UINT, false, true, true, false, 0.0f, 0.5f, 0.0f, 1.0f, 1, {1, 1, 1, 0, 0, 0, 0, 0, 0, 0}},\n"),
        ("\t    // D32, minDepth > 0 only on viewport 1 of 2 (t1: only viewport 0)\n"
         "\t    {\"t109_vp1\", VK_FORMAT_D32_SFLOAT, true, true, false, true, 0.0f, 1.0f, 0.25f, 1.0f, 2, {1, 0, 0, 1, 1, 0, 0}},\n",
         "\t    // D32, minDepth > 0 only on viewport 1 of 2 (t1: only viewport 0); M9d3: count 2 - bias_narrow_vi (t7, t9)\n"
         "\t    {\"t109_vp1\", VK_FORMAT_D32_SFLOAT, true, true, false, true, 0.0f, 1.0f, 0.25f, 1.0f, 2, {1, 0, 0, 1, 1, 0, 0, 0, 1, 0}},\n"),
        ("\t    {\"t109_nozx\", VK_FORMAT_D32_SFLOAT, true, true, false, false, 0.0f, 0.5f, 0.0f, 1.0f, 1, {1, 0, 0, 0, 0, 0, 0}},\n",
         "\t    {\"t109_nozx\", VK_FORMAT_D32_SFLOAT, true, true, false, false, 0.0f, 0.5f, 0.0f, 1.0f, 1, {1, 0, 0, 0, 0, 0, 0, 0, 0, 0}},\n"),
        ("\t\tT109::NoteDraw(d.fmt, d.test, d.write, d.zx, d.bias, vp, sc, d.count);\n"
         "\t\tconst auto t = T109::Read();\n"
         "\t\tCheck(d.name,\n"
         "\t\t      {{\"x:d32\", d.want.d32}, {\"x:zx_d32\", d.want.zx_d32}, {\"x:zx_narrow\", d.want.zx_narrow},\n"
         "\t\t       {\"x:bias_d32\", d.want.bias_d32}, {\"x:bias_narrow\", d.want.bias_narrow}},\n"
         "\t\t      {{\"x:d32\", t.d32}, {\"x:zx_d32\", t.zx_d32}, {\"x:zx_narrow\", t.zx_narrow}, {\"x:bias_d32\", t.bias_d32},\n"
         "\t\t       {\"x:bias_narrow\", t.bias_narrow}});\n",
         "\t\tT109::NoteDraw(d.fmt, d.test, d.write, d.zx, d.bias, vp, sc, d.count, false);\n"
         "\t\tconst auto t = T109::Read();\n"
         "\t\tCheck(d.name,\n"
         "\t\t      {{\"x:d32\", d.want.d32}, {\"x:zx_d32\", d.want.zx_d32}, {\"x:zx_narrow\", d.want.zx_narrow},\n"
         "\t\t       {\"x:bias_d32\", d.want.bias_d32}, {\"x:bias_narrow\", d.want.bias_narrow},\n"
         "\t\t       {\"x:zx_narrow_vi\", d.want.zx_narrow_vi}, {\"x:bias_narrow_vi\", d.want.bias_narrow_vi},\n"
         "\t\t       {\"x:narrow_cd\", d.want.narrow_cd}},\n"
         "\t\t      {{\"x:d32\", t.d32}, {\"x:zx_d32\", t.zx_d32}, {\"x:zx_narrow\", t.zx_narrow}, {\"x:bias_d32\", t.bias_d32},\n"
         "\t\t       {\"x:bias_narrow\", t.bias_narrow}, {\"x:zx_narrow_vi\", t.zx_narrow_vi},\n"
         "\t\t       {\"x:bias_narrow_vi\", t.bias_narrow_vi}, {\"x:narrow_cd\", t.narrow_cd}});\n"),
        ("\t// SetGraphicsDynamicParams leaves it); the active slot has a 64x64 scissor. want = zx_narrow = bias_narrow.\n"
         "\tstruct Slots {\n"
         "\t\tconst char* name;\n"
         "\t\tuint32_t    count;\n"
         "\t\tuint32_t    active;\n"
         "\t\tfloat       min_a, max_a;\n"
         "\t\tuint64_t    want;\n"
         "\t};\n",
         "\t// SetGraphicsDynamicParams leaves it); the active slot has a 64x64 scissor. want = zx_narrow = bias_narrow.\n"
         "\t// M9d3 (RC1 of M9e2, item 789(v)(3)): want_vi = zx_narrow_vi = bias_narrow_vi, want_cd = narrow_cd; with cd\n"
         "\t// (clip_disable) every slot is 16384 x 16384 and has the 64x64 scissor (vport_scissor_enable 0), the slots other\n"
         "\t// than the active one keep minDepth = maxDepth = 0.\n"
         "\tstruct Slots {\n"
         "\t\tconst char* name;\n"
         "\t\tuint32_t    count;\n"
         "\t\tuint32_t    active;\n"
         "\t\tfloat       min_a, max_a;\n"
         "\t\tuint64_t    want;\n"
         "\t\tuint64_t    want_vi;\n"
         "\t\tuint64_t    want_cd;\n"
         "\t\tbool        cd;\n"
         "\t};\n"),
        ("\t    {\"t109_vi16\", 16, 0, 0.0f, 1.0f, 0},\n",
         "\t    {\"t109_vi16\", 16, 0, 0.0f, 1.0f, 0, 0, 0, false},\n"),
        ("\t    {\"t109_inv\", 1, 0, 1.0f, 0.0f, 0},\n",
         "\t    {\"t109_inv\", 1, 0, 1.0f, 0.0f, 0, 0, 0, false},\n"),
        ("\t    {\"t109_inv_n\", 1, 0, 1.0f, 0.5f, 1},\n",
         "\t    {\"t109_inv_n\", 1, 0, 1.0f, 0.5f, 1, 0, 0, false},\n"),
        ("\t    // 16 slots, active slot 3 [0, 0.5], the rest empty (t1: only slot 0)\n"
         "\t    {\"t109_vi16n\", 16, 3, 0.0f, 0.5f, 1},\n"
         "\t};\n",
         "\t    // 16 slots, active slot 3 [0, 0.5], the rest empty (t1: only slot 0); M9d3: multi-slot narrow (t7, t9)\n"
         "\t    {\"t109_vi16n\", 16, 3, 0.0f, 0.5f, 1, 1, 0, false},\n"
         "\t    // M9d3: 16 slots, clip_disable, slot 0 [0, 1], slots 1-15 0/0 with 64x64 scissors - the false narrow of RC1 of\n"
         "\t    // M9e2 is seen in zx_narrow_vi / bias_narrow_vi and narrow_cd (once per draw) (t7, t9)\n"
         "\t    {\"t109_cd16\", 16, 0, 0.0f, 1.0f, 1, 1, 1, true},\n"
         "\t    // M9d3: 1 slot [0, 0.5], clip_disable - positive control of the split by count (t8)\n"
         "\t    {\"t109_cd1\", 1, 0, 0.0f, 0.5f, 1, 0, 0, true},\n"
         "\t};\n"),
        ("\t\tfor (auto& v: vp) {\n"
         "\t\t\tv.width  = 1.0f;\n"
         "\t\t\tv.height = 1.0f;\n"
         "\t\t}\n",
         "\t\tfor (uint32_t i = 0; i < 16; i++) {\n"
         "\t\t\tvp[i].width  = s.cd ? 16384.0f : 1.0f;\n"
         "\t\t\tvp[i].height = s.cd ? 16384.0f : 1.0f;\n"
         "\t\t\tif (s.cd) {\n"
         "\t\t\t\tsc[i].extent = {64, 64};\n"
         "\t\t\t}\n"
         "\t\t}\n"),
        ("\t\tvp[s.active].width    = 64.0f;\n"
         "\t\tvp[s.active].height   = 64.0f;\n",
         "\t\tif (!s.cd) {\n"
         "\t\t\tvp[s.active].width  = 64.0f;\n"
         "\t\t\tvp[s.active].height = 64.0f;\n"
         "\t\t}\n"),
        ("\t\tT109::NoteDraw(VK_FORMAT_D32_SFLOAT, true, true, true, true, vp, sc, s.count);\n"
         "\t\tconst auto t = T109::Read();\n"
         "\t\tCheck(s.name,\n"
         "\t\t      {{\"x:d32\", 1}, {\"x:zx_d32\", 1}, {\"x:zx_narrow\", s.want}, {\"x:bias_d32\", 1}, {\"x:bias_narrow\", s.want}},\n"
         "\t\t      {{\"x:d32\", t.d32}, {\"x:zx_d32\", t.zx_d32}, {\"x:zx_narrow\", t.zx_narrow}, {\"x:bias_d32\", t.bias_d32},\n"
         "\t\t       {\"x:bias_narrow\", t.bias_narrow}});\n",
         "\t\tT109::NoteDraw(VK_FORMAT_D32_SFLOAT, true, true, true, true, vp, sc, s.count, s.cd);\n"
         "\t\tconst auto t = T109::Read();\n"
         "\t\tCheck(s.name,\n"
         "\t\t      {{\"x:d32\", 1}, {\"x:zx_d32\", 1}, {\"x:zx_narrow\", s.want}, {\"x:bias_d32\", 1}, {\"x:bias_narrow\", s.want},\n"
         "\t\t       {\"x:zx_narrow_vi\", s.want_vi}, {\"x:bias_narrow_vi\", s.want_vi}, {\"x:narrow_cd\", s.want_cd}},\n"
         "\t\t      {{\"x:d32\", t.d32}, {\"x:zx_d32\", t.zx_d32}, {\"x:zx_narrow\", t.zx_narrow}, {\"x:bias_d32\", t.bias_d32},\n"
         "\t\t       {\"x:bias_narrow\", t.bias_narrow}, {\"x:zx_narrow_vi\", t.zx_narrow_vi},\n"
         "\t\t       {\"x:bias_narrow_vi\", t.bias_narrow_vi}, {\"x:narrow_cd\", t.narrow_cd}});\n"),
        ("\t\tCheck(\"t109_ovr\", {{\"x:ovr_w\", 2}, {\"x:ovr_vpc\", 1}}, {{\"x:ovr_w\", t.ovr_w}, {\"x:ovr_vpc\", t.ovr_vpc}});\n",
         "\t\tCheck(\"t109_ovr\",\n"
         "\t\t      {{\"x:ovr_w\", 2}, {\"x:ovr_vpc\", 1}, {\"x:zx_narrow_vi\", 0}, {\"x:bias_narrow_vi\", 0}, {\"x:narrow_cd\", 0}},\n"
         "\t\t      {{\"x:ovr_w\", t.ovr_w}, {\"x:ovr_vpc\", t.ovr_vpc}, {\"x:zx_narrow_vi\", t.zx_narrow_vi},\n"
         "\t\t       {\"x:bias_narrow_vi\", t.bias_narrow_vi}, {\"x:narrow_cd\", t.narrow_cd}});\n"),
    ],
}

ok = True
out = {}
for rel, edits in EDITS.items():
    path = os.path.join(ROOT, rel)
    raw = open(path, 'rb').read().decode('utf-8')
    crlf = '\r\n' in raw
    s = raw.replace('\r\n', '\n')
    for old, new in edits:
        c = s.count(old)
        if c != 1:
            print('ANCHOR %s count=%d %r' % (rel, c, old[:80]))
            ok = False
            continue
        s = s.replace(old, new)
    out[rel] = s.replace('\n', '\r\n') if crlf else s
if not ok:
    print('FAIL')
    sys.exit(1)
for rel, s in out.items():
    open(os.path.join(ROOT, rel), 'wb').write(s.encode('utf-8'))
print('ALL OK')

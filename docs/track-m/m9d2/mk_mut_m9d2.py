"""M9d2 (HPP-874): build mut_m9d2.py from m657/m9d/mut_m9d.py - output dir m9d2/mut, stand driver run_stand_m9d2.py
(WANT_PURE 49); t1 and t2 re-anchored on the M9d2 loop of DiagT109::NoteDraw; new t5 (every slot without the scissor
test) and t6 (raw minDepth / maxDepth without min/max), ROADMAP s122 item 788(b)(4). Exact anchors, each once; LF out."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)
s = open('C:/kyty/m657/m9d/mut_m9d.py', 'rb').read().decode('utf-8').replace('\r\n', '\n')

T1_OLD = ("    ('t1_vp0_only', DIAG, [('\\tfor (uint32_t i = 0; i < count; i++) {\\n\\t\\tif (viewports[i].minDepth',\n"
          "                            '\\tfor (uint32_t i = 0; i < 1 && i < count; i++) {\\n\\t\\tif (viewports[i].minDepth')], PURE),\n"
          "    ('t2_nonstrict', DIAG, [('viewports[i].minDepth > 0.0f || viewports[i].maxDepth < 1.0f',\n"
          "                             'viewports[i].minDepth >= 0.0f || viewports[i].maxDepth <= 1.0f')], PURE),\n")
T1_NEW = ("    ('t1_vp0_only', DIAG, [('\\tfor (uint32_t i = 0; i < count; i++) {\\n\\t\\tif (scissors[i].extent',\n"
          "                            '\\tfor (uint32_t i = 0; i < 1 && i < count; i++) {\\n\\t\\tif (scissors[i].extent')], PURE),\n"
          "    ('t2_nonstrict', DIAG, [('\\t\\tif (lo > 0.0f || hi < 1.0f) {',\n"
          "                             '\\t\\tif (lo >= 0.0f || hi <= 1.0f) {')], PURE),\n")
T4_END = ("                                 '\\tif (z_export) {\\n\\t\\tBump(g_zx_d32);\\n\\t}\\n\\tif (narrow) {\\n\\t\\tBump(g_zx_narrow);\\n\\t}')], PURE),\n"
          "]\n")
T56 = ("                                 '\\tif (z_export) {\\n\\t\\tBump(g_zx_d32);\\n\\t}\\n\\tif (narrow) {\\n\\t\\tBump(g_zx_narrow);\\n\\t}')], PURE),\n"
       "    # M9d2 (item 788(b)(4)): t5 - every slot counts (the scissor-area test removed); t6 - raw minDepth / maxDepth.\n"
       "    ('t5_all_slots', DIAG, [('\\t\\tif (scissors[i].extent.width == 0 || scissors[i].extent.height == 0) {\\n\\t\\t\\tcontinue; // M9d2: the slot does not rasterize (empty ViewportIndex slot, zero-area scissor)\\n\\t\\t}\\n', '')], PURE),\n"
       "    ('t6_raw_range', DIAG, [('\\t\\tconst float lo = std::min(viewports[i].minDepth, viewports[i].maxDepth);\\n\\t\\tconst float hi = std::max(viewports[i].minDepth, viewports[i].maxDepth);\\n',\n"
       "                             '\\t\\tconst float lo = viewports[i].minDepth;\\n\\t\\tconst float hi = viewports[i].maxDepth;\\n')], PURE),\n"
       "]\n")
REPL = [
    (T1_OLD, T1_NEW),
    (T4_END, T56),
    ("OUT = 'C:/kyty/m657/m9d/mut'\n", "OUT = 'C:/kyty/m657/m9d2/mut'\n"),
    ("[sys.executable, 'C:/kyty/m657/m9d/run_stand_m9d.py', 'C:/kyty/m657/m9d/build', out]",
     "[sys.executable, 'C:/kyty/m657/m9d2/run_stand_m9d2.py', 'C:/kyty/m657/m9d/build', out]"),
]
ok = True
for o, n in REPL:
    c = s.count(o)
    if c != 1:
        print('ANCHOR count=%d %r' % (c, o[:70]))
        ok = False
        continue
    s = s.replace(o, n)
if not ok:
    print('FAIL')
    sys.exit(1)
s = ('"""M9d2 (HPP-874): copy of m657/m9d/mut_m9d.py (out m9d2/mut, driver run_stand_m9d2.py, t1/t2 re-anchored, + t5, t6;\n'
     'built by mk_mut_m9d2.py). Was:\n' + s[3:])
open('C:/kyty/m657/m9d2/mut_m9d2.py', 'wb').write(s.encode('utf-8'))
print('ALL OK')

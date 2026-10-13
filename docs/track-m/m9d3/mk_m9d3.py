"""M9d3 (HPP-876): build run_stand_m9d3.py from m9d2/run_stand_m9d2.py (WANT_PURE 51, T109Stat names + zx_narrow_vi
bias_narrow_vi narrow_cd) and mut_m9d3.py from m9d2/mut_m9d2.py (out m9d3/mut, driver run_stand_m9d3.py, t4 re-anchored
on the M9d3 form of the z_export branch, new t7 - the _vi counters not counted, t8 - _vi counted at count = 1, t9 -
narrow_cd without the clip_disable condition; ROADMAP s122 item 789(v)(3)). Exact anchors, each once; LF out."""
import os
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    sys.exit(3)


def apply(src, dst, repl, head):
    s = open(src, 'rb').read().decode('utf-8').replace('\r\n', '\n')
    ok = True
    for o, n in repl:
        c = s.count(o)
        if c != 1:
            print('ANCHOR %s count=%d %r' % (os.path.basename(dst), c, o[:70]))
            ok = False
            continue
        s = s.replace(o, n)
    if not ok:
        return False
    s = '"""' + head + ' Was:\n' + s[3:]
    open(dst, 'wb').write(s.encode('utf-8'))
    return True


RUN = [
    ("WANT_PURE = 49  # M9d2: + t109_vi16, t109_inv, t109_inv_n, t109_vi16n (ROADMAP s122 item 788(b)(4))\n",
     "WANT_PURE = 51  # M9d3: + t109_cd16, t109_cd1 (ROADMAP s122 item 789(v)(3)); M9d2: 49\n"),
    ("T109 = 'd32 zx_d32 zx_narrow bias_d32 bias_narrow ovr_w ovr_vpc'.split()\n",
     "T109 = 'd32 zx_d32 zx_narrow bias_d32 bias_narrow ovr_w ovr_vpc zx_narrow_vi bias_narrow_vi narrow_cd'.split()\n"),
]

T4_OLD = ("    ('t4_zx_narrow_any', DIAG, [('\\tif (z_export) {\\n\\t\\tBump(g_zx_d32);\\n\\t\\tif (narrow) {\\n\\t\\t\\tBump(g_zx_narrow);\\n\\t\\t}\\n\\t}',\n"
          "                                 '\\tif (z_export) {\\n\\t\\tBump(g_zx_d32);\\n\\t}\\n\\tif (narrow) {\\n\\t\\tBump(g_zx_narrow);\\n\\t}')], PURE),\n")
T4_NEW = ("    ('t4_zx_narrow_any', DIAG, [('\\tif (z_export) {\\n\\t\\tBump(g_zx_d32);\\n\\t\\tif (narrow) {\\n\\t\\t\\tBump(g_zx_narrow);\\n',\n"
          "                                 '\\tif (z_export) {\\n\\t\\tBump(g_zx_d32);\\n\\t}\\n\\t{\\n\\t\\tif (narrow) {\\n\\t\\t\\tBump(g_zx_narrow);\\n')], PURE),\n")
T6_END = ("                             '\\t\\tconst float lo = viewports[i].minDepth;\\n\\t\\tconst float hi = viewports[i].maxDepth;\\n')], PURE),\n"
          "]\n")
T789 = ("                             '\\t\\tconst float lo = viewports[i].minDepth;\\n\\t\\tconst float hi = viewports[i].maxDepth;\\n')], PURE),\n"
        "    # M9d3 (item 789(v)(3)): t7 - the _vi counters are not counted; t8 - _vi counted at count = 1; t9 - narrow_cd\n"
        "    # without the clip_disable condition.\n"
        "    ('t7_vi_none', DIAG, [('\\t\\t\\t\\tBump(g_zx_narrow_vi); // M9d3: the narrow slot may be one the VS never writes\\n', ''),\n"
        "                          ('\\t\\t\\t\\tBump(g_bias_narrow_vi); // M9d3\\n', '')], PURE),\n"
        "    ('t8_vi_count1', DIAG, [('\\t\\t\\tif (count > 1) {\\n\\t\\t\\t\\tBump(g_zx_narrow_vi);',\n"
        "                             '\\t\\t\\tif (count >= 1) {\\n\\t\\t\\t\\tBump(g_zx_narrow_vi);'),\n"
        "                            ('\\t\\t\\tif (count > 1) {\\n\\t\\t\\t\\tBump(g_bias_narrow_vi);',\n"
        "                             '\\t\\t\\tif (count >= 1) {\\n\\t\\t\\t\\tBump(g_bias_narrow_vi);')], PURE),\n"
        "    ('t9_cd_any', DIAG, [('\\tif (narrow && (z_export || bias) && count > 1 && clip_disable) {\\n',\n"
        "                          '\\tif (narrow && (z_export || bias) && count > 1) {\\n')], PURE),\n"
        "]\n")
MUT = [
    (T4_OLD, T4_NEW),
    (T6_END, T789),
    ("OUT = 'C:/kyty/m657/m9d2/mut'\n", "OUT = 'C:/kyty/m657/m9d3/mut'\n"),
    ("[sys.executable, 'C:/kyty/m657/m9d2/run_stand_m9d2.py', 'C:/kyty/m657/m9d/build', out]",
     "[sys.executable, 'C:/kyty/m657/m9d3/run_stand_m9d3.py', 'C:/kyty/m657/m9d/build', out]"),
]

ok = apply('C:/kyty/m657/m9d2/run_stand_m9d2.py', 'C:/kyty/m657/m9d3/run_stand_m9d3.py', RUN,
           'M9d3 (HPP-876): copy of m657/m9d2/run_stand_m9d2.py with WANT_PURE 51 and the T109Stat names + zx_narrow_vi\n'
           'bias_narrow_vi narrow_cd (built by mk_m9d3.py).')
ok &= apply('C:/kyty/m657/m9d2/mut_m9d2.py', 'C:/kyty/m657/m9d3/mut_m9d3.py', MUT,
            'M9d3 (HPP-876): copy of m657/m9d2/mut_m9d2.py (out m9d3/mut, driver run_stand_m9d3.py, t4 re-anchored, + t7,\n'
            't8, t9; built by mk_m9d3.py).')
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)

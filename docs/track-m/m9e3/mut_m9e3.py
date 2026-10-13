"""M9e3 (HPP-877, Red Team): own run of the M9d3 mutants (mut_m9d3.py, unchanged list m1-m15, m8s, g1-g4, t1-t9) plus
the reviewer's extra mutants z1-z9 of the M9d3 change, on the M9d worktree C:/kyty/m657/m9d/wt (HPP-876 done) and its
build dir; output to C:/kyty/m657/m9e3/mut. Every file is restored byte for byte after each mutant (mut_m9d3.main),
sha256 checked at the end. z1, z6 SURVIVED means "the form is not distinguished by the stand" (coverage probe of the
reference field narrow_cd), not a failure.
Usage: python mut_m9e3.py [name ...] | control | --check | (nothing: all + control)."""
import sys

sys.path.insert(0, 'C:/kyty/m657/m9d3')
import mut_m9d3 as M  # noqa: E402

M.OUT = 'C:/kyty/m657/m9e3/mut'
PURE = M.PURE
DIAG = M.DIAG

CD = '\tif (narrow && (z_export || bias) && count > 1 && clip_disable) {\n'
ZVI = '\t\t\t\tBump(g_zx_narrow_vi); // M9d3: the narrow slot may be one the VS never writes\n'
ZIF = '\t\t\tif (count > 1) {\n\t\t\t\tBump(g_zx_narrow_vi);'
RST = '&g_bias_narrow_vi, &g_narrow_cd}'
PRN = '" bias_narrow_vi=%" PRIu64 " narrow_cd=%" PRIu64'

EXTRA = [
    # narrow_cd without narrow (probe: no stand case with clip_disable, count > 1 and no narrow)
    ('z1_cd_no_narrow', DIAG, [(CD, '\tif ((z_export || bias) && count > 1 && clip_disable) {\n')], PURE),
    # narrow_cd without count > 1 (t109_cd1 must catch)
    ('z2_cd_no_count', DIAG, [(CD, '\tif (narrow && (z_export || bias) && clip_disable) {\n')], PURE),
    # narrow_cd bumped once more in the z_export branch (twice per draw; t109_cd16 must catch)
    ('z3_cd_twice', DIAG, [(ZVI, ZVI + '\t\t\t\tif (clip_disable) {\n\t\t\t\t\tBump(g_narrow_cd);\n\t\t\t\t}\n')], PURE),
    # zx_narrow_vi also at count 1 when clip_disable (t109_cd1 must catch)
    ('z4_vi_or_cd', DIAG, [(ZIF, '\t\t\tif (count > 1 || clip_disable) {\n\t\t\t\tBump(g_zx_narrow_vi);')], PURE),
    # the z_export branch bumps bias_narrow_vi (t109_vi16n, t109_cd16 must catch)
    ('z5_vi_swap', DIAG, [(ZVI, '\t\t\t\tBump(g_bias_narrow_vi);\n')], PURE),
    # narrow_cd without (z_export || bias) (probe: no stand case with both off at count > 1)
    ('z6_cd_no_zxbias', DIAG, [(CD, '\tif (narrow && count > 1 && clip_disable) {\n')], PURE),
    # ResetForStand forgets narrow_cd (t109_cd1 after t109_cd16 must catch)
    ('z8_reset_cd', DIAG, [(RST, '&g_bias_narrow_vi}')], PURE),
    # names of the last two fields swapped in T109Stat (pure arm name order must catch)
    ('z9_print_swap', DIAG, [(PRN, '" narrow_cd=%" PRIu64 " bias_narrow_vi=%" PRIu64')], PURE),
]

M.MUTANTS = M.MUTANTS + EXTRA
M.FILES = sorted({m[1] for m in M.MUTANTS})

if __name__ == '__main__':
    sys.exit(M.main())

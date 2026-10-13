"""M9e2 (HPP-875, Red Team): own run of the M9d2 mutants (mut_m9d2.py, unchanged list m1-m15, m8s, g1-g4, t1-t6) plus
the reviewer's extra mutants y1-y5 of the M9d2 change, on the M9d worktree C:/kyty/m657/m9d/wt (HPP-874 done) and its
build dir; output to C:/kyty/m657/m9e2/mut. Every file is restored byte for byte after each mutant (mut_m9d2.main),
sha256 checked at the end. y* SURVIVED means "the form is not distinguished by the stand" (coverage probe), not a failure.
Usage: python mut_m9e2.py [name ...] | control | (nothing: all + control)."""
import sys

sys.path.insert(0, 'C:/kyty/m657/m9d2')
import mut_m9d2 as M  # noqa: E402

M.OUT = 'C:/kyty/m657/m9e2/mut'
PURE = M.PURE
DIAG = M.DIAG

SC = '\t\tif (scissors[i].extent.width == 0 || scissors[i].extent.height == 0) {\n\t\t\tcontinue;'
LO = '\t\tconst float lo = std::min(viewports[i].minDepth, viewports[i].maxDepth);\n'
HI = '\t\tconst float hi = std::max(viewports[i].minDepth, viewports[i].maxDepth);\n'

EXTRA = [
    # height test dropped (stand empty slots are {0, 0}: expected SURVIVED - probe)
    ('y1_width_only', DIAG, [(SC, '\t\tif (scissors[i].extent.width == 0) {\n\t\t\tcontinue;')], PURE),
    # || -> && (expected SURVIVED - probe: no stand case with one zero side)
    ('y2_and', DIAG, [(SC, '\t\tif (scissors[i].extent.width == 0 && scissors[i].extent.height == 0) {\n\t\t\tcontinue;')], PURE),
    # lo raw, hi max
    ('y3_lo_raw', DIAG, [(LO, '\t\tconst float lo = viewports[i].minDepth;\n')], PURE),
    # hi raw, lo min
    ('y4_hi_raw', DIAG, [(HI, '\t\tconst float hi = viewports[i].maxDepth;\n')], PURE),
    # continue -> break (stop at the first empty slot)
    ('y5_break', DIAG, [(SC, '\t\tif (scissors[i].extent.width == 0 || scissors[i].extent.height == 0) {\n\t\t\tbreak;')], PURE),
]

M.MUTANTS = M.MUTANTS + EXTRA
M.FILES = sorted({m[1] for m in M.MUTANTS})

if __name__ == '__main__':
    sys.exit(M.main())

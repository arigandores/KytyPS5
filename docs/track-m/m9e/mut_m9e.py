"""M9e (HPP-870, Red Team): own run of the M9d mutants (mut_m9d.py, unchanged list m1-m15, m8s, g1-g4, t1-t4) plus the
reviewer's extra mutants x1-x9, on the M9d worktree C:/kyty/m657/m9d/wt (HPP-869 done) and its build dir; output to
C:/kyty/m657/m9e/mut. Every file is restored byte for byte after each mutant (mut_m9d.main), sha256 checked at the end.
x* are probes of coverage: SURVIVED there means "the place is proven by reading the code only", not a failure of M9d.
Usage: python mut_m9e.py [name ...] | (nothing: all + control)."""
import sys

sys.path.insert(0, 'C:/kyty/m657/m9d')
import mut_m9d as M  # noqa: E402

M.OUT = 'C:/kyty/m657/m9e/mut'
PURE = M.PURE
TC = M.TC
DIAG = M.DIAG

EXTRA = [
    ('x1_clear_noflag', TC, [('\t\tDiagT188::NoteImageWrite(image.t188); // Track M, M9d (RC12): the clear writes the image\n',
                              '')], PURE),
    ('x2_copydst_noflag', TC, [('\t\tDiagT188::NoteImageWrite(destination.t188);       // Track M, M9d (RC12): the copy wrote the destination\n',
                                '')], PURE),
    ('x3_join_dropped', DIAG, [('\t\t\tJoin(s, g, address, size); // executor decision 1 (names_before_code.md s.4)\n',
                                '')], PURE),
    ('x4_synced_ignored', DIAG, [('\t} else if (s.sseq.load(std::memory_order_acquire) == s.wseq.load(std::memory_order_acquire)) {\n',
                                  '\t} else if (false) {\n')], PURE),
    ('x7_vo_flag_never', TC, [('\t\tm_t188_vo = true;\n', '')], PURE),
    ('x8_download_noop', DIAG, [('\ts.dseq.store(s.wseq.load(std::memory_order_acquire), std::memory_order_release);\n\tAdd(C::dl_mem);',
                                 '\tAdd(C::dl_mem);')], PURE),
    ('x9_s3c_site_gone', TC, [('\t\t\tDiagT188::PendDrop(image.t188, m_lock.HeldByCurrentThread()); // Track M, M9d: S3c\n',
                               '')], PURE),
]

M.MUTANTS = M.MUTANTS + EXTRA
M.FILES = sorted({m[1] for m in M.MUTANTS})

if __name__ == '__main__':
    sys.exit(M.main())

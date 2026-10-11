"""Track F, F46b (HPP-799, Red Team; ROADMAP s122 item 702(e)(6), 706(v)): mutants m1-m3 of the F46a code 1398d44d, applied
to the mutant worktree C:/kyty/f287/f46b/mwt (HEAD 7e8481e5 = cherry-pick of 1398d44d). Whole-line anchors, each anchor
must match exactly once; files are read and written as bytes (CR removed before the search and put back if present).

    python mut_f46b.py <worktree> <mutant>      # applies one mutant (the worktree must be clean - the caller resets it)
    python mut_f46b.py <worktree> --list

m1a  the mark M1 is taken only by the image that set it (the F16o2 keying by image): F26ExecLocked finds the mark of
     the address only when mark.image == the executing image.
m1b  the mark M1 keyed by the image data address (m_line.image) instead of the metadata address (m_line.dcc).
m2a  F26TintAt ignores the key (address != key dropped) - the pure decision.
m2b  F26TintKey ignores the key (the sites' cheap gate) - expected EQUIVALENT (F26TintAt still compares the key).
m2c  both m2a and m2b - the key ignored end to end (the behaviour mutant of item 702(e)(6) m2).
m2d  m2b plus F26Tint passes the address as the key - the key ignored at the sites, the pure F26TintAt intact (tests the
     f26_tint_applied deltas of the arms, not the pure case).
m3a  f26_first_exec printed on the event itself (Report prints the line instead of arming it).
m3b  f26_first_exec fired by the in-call clear of a kept_applied event (armed, then executed in Report).
m3c  m3b only for the events n >= 13 (the T4 event of the test site; D1-D5 keep their lines) - shows that T4 itself
     catches m3.
"""
import sys

TC = "src/graphics/host_gpu/renderer/cache/textureCache.cpp"
DC = "src/graphics/host_gpu/renderer/diagF5.cpp"

M2A = (DC,
       "\tif ((mode != 1 && mode != 2) || address != key || (mode == 1 && !removes_mark)) {",
       "\tif ((mode != 1 && mode != 2) || (mode == 1 && !removes_mark)) { // F46b m2a")
M2B = (DC,
       "\treturn F26TintMode() != 0 && address == F26TintDcc();",
       "\treturn F26TintMode() != 0 && (address == F26TintDcc() || true); // F46b m2b")

M2D = (DC,
       "	const auto result = F26TintAt(F26TintMode(), F26TintDcc(), address, removes_mark, format, clear);",
       "	const auto result = F26TintAt(F26TintMode(), address, address, removes_mark, format, clear); // F46b m2d")

MUTANTS = {
    "m1a": [(TC,
             "\t\tif (const auto found = m_f26_marks.find(address); found != m_f26_marks.end()) {",
             "\t\tif (const auto found = m_f26_marks.find(address); found != m_f26_marks.end() && "
             "found->second.image == image_address) { // F46b m1a")],
    "m1b": [(TC,
             "\t\t\tm_cache->F26MarkLocked(m_line.dcc, {.n = n, .image = m_line.image, .dcc = m_line.dcc});",
             "\t\t\tm_cache->F26MarkLocked(m_line.image, {.n = n, .image = m_line.image, .dcc = m_line.dcc}); // F46b m1b")],
    "m2a": [M2A],
    "m2b": [M2B],
    "m2c": [M2A, M2B],
    "m2d": [M2B, M2D],
    "m3a": [(TC,
             "\t\t\tm_cache->F26ArmFirstExecLocked(m_line.dcc, n);",
             "\t\t\t(void)DiagF5::NoteFirstExec({.n = n, .present = DiagF5::Present(), .dcc = m_line.dcc, "
             ".image = m_line.image, .site = DiagF5::F26Site::Prepare}); // F46b m3a")],
    "m3b": [(TC,
             "\t\t\tm_cache->F26ArmFirstExecLocked(m_line.dcc, n);",
             "\t\t\tm_cache->F26ArmFirstExecLocked(m_line.dcc, n);\n"
             "\t\t\tif (m_applied) { m_cache->F26ExecLocked(m_line.dcc, m_line.image, DiagF5::F26Site::Prepare, 1u); } "
             "// F46b m3b")],
    "m3c": [(TC,
             "\t\t\tm_cache->F26ArmFirstExecLocked(m_line.dcc, n);",
             "\t\t\tm_cache->F26ArmFirstExecLocked(m_line.dcc, n);\n"
             "\t\t\tif (m_applied && n >= 13) { m_cache->F26ExecLocked(m_line.dcc, m_line.image, DiagF5::F26Site::Prepare, 1u); } "
             "// F46b m3c")],
}


def apply(root, name):
    for path, old, new in MUTANTS[name]:
        full = root.rstrip("/") + "/" + path
        raw = open(full, "rb").read()
        crlf = b"\r\n" in raw
        text = raw.replace(b"\r\n", b"\n").decode("utf-8")
        lines = text.split("\n")
        hits = [i for i, l in enumerate(lines) if l == old]
        if len(hits) != 1:
            print("ANCHOR %s: %d matches in %s" % (name, len(hits), path))
            return 1
        lines[hits[0]] = new
        out = "\n".join(lines).encode("utf-8")
        if crlf:
            out = out.replace(b"\n", b"\r\n")
        open(full, "wb").write(out)
        print("applied %s: %s line %d" % (name, path, hits[0] + 1))
    return 0


if __name__ == "__main__":
    if sys.argv[2] == "--list":
        for k in MUTANTS:
            print(k)
        sys.exit(0)
    sys.exit(apply(sys.argv[1], sys.argv[2]))

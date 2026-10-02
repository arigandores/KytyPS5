# P23 (HPP-404, ROADMAP s122 p.333(e)): port of the P-var commit 4b7665e5 onto the FS2 tree without edits of its lines.
# The diff of 4b7665e5 is taken as is; only the 3 leading context lines of two hunks are replaced, because on the FS2 tree
# the counter enum (src/common/frameStats.h) and the named counter list (src/graphics/presentation/videoOut.cpp) no longer
# end with RtsEarly / rts_early: the same "+" lines go at the end of the same two lists (before "Count" / before "};"),
# as P14 put them on 4fc501f4. Writes pvar_ported.diff (LF), applied by "git apply" in the worktree.
import sys

SRC = "C:/kyty/p283/p23/pvar_4b7665e5.diff"
OUT = "C:/kyty/p283/p23/pvar_ported.diff"

text = open(SRC, "rb").read().decode("utf-8")
assert "\r" not in text

OLD_ENUM = (
    "\tRtsWrObj,                // rts_wr_obj: values 2/3 - hook calls, whole-object writes\n"
    "\tRtsLost,                 // rts_lost: values 2/3 - records taken at the latch and never given back\n"
    "\tRtsEarly,                // rts_early: values 2/3 - draws that reached place A and not the post\n"
)
NEW_ENUM = (
    "\tBlnRstCpu,               // bln_rst_cpu: generation moves by a clear of a CPU-dirty mask at bindlean 1/2, b2reuse 0\n"
    "\tBlnRstCpuw,              // bln_rst_cpuw: generation moves by an announced CPU write at bindlean 1/2, b2reuse 0\n"
    "\tBlnSraceA,               // bln_srace_a: 2/3, a divergence of part (a) with the witness moved (item 178(b); a row)\n"
)
OLD_LIST = (
    '\t\t\t\t    {"rts_wr_obj", FS::Counter::RtsWrObj, false},\n'
    '\t\t\t\t    {"rts_lost", FS::Counter::RtsLost, false},\n'
    '\t\t\t\t    {"rts_early", FS::Counter::RtsEarly, false},\n'
)


def ctx(block):
    return "".join(" " + line + "\n" for line in block.split("\n")[:-1])


# The three list lines before "};" on the FS2 tree.
wt = open("C:/kyty/p283/p23/wt/src/graphics/presentation/videoOut.cpp", "rb").read().decode("utf-8")
anchor = '\t\t\t\t    {"bln_srace_a", FS::Counter::BlnSraceA, false},\n\t\t\t\t};\n\t\t\t\tstd::string text;\n'
assert wt.count(anchor) == 1, "list anchor"
pos = wt.index(anchor)
before = wt[:pos].split("\n")[-3:-1]
NEW_LIST = before[0] + "\n" + before[1] + "\n" + '\t\t\t\t    {"bln_srace_a", FS::Counter::BlnSraceA, false},\n'

fs = open("C:/kyty/p283/p23/wt/src/common/frameStats.h", "rb").read().decode("utf-8")
assert fs.count(NEW_ENUM + "\tCount\n};\n") == 1, "enum anchor"

for old, new in ((OLD_ENUM, NEW_ENUM), (OLD_LIST, NEW_LIST)):
    o, n = ctx(old), ctx(new)
    assert text.count(o) == 1, "diff context " + old[:30]
    text = text.replace(o, n)

open(OUT, "wb").write(text.encode("utf-8"))
print("ported diff written", OUT)

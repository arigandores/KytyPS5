# F3a (HPP-308): build docs/track-f/f3a-b1b.md from f3a_body.md - reference map by anchor with
# the +1 control at a pinned commit, and asserts on every sum / count the text names.
import sys, os, re, json, subprocess, hashlib

if os.path.exists("C:/kyty/SEALED_RUN.lock"):
    sys.exit(3)
D = "C:/kyty/f287/f3a/"
REPO = "C:/kyty/KytyPS5"
GIT = "C:/Program Files/Git/cmd/git.exe"
COMMIT = "20b39318"
S = "src/graphics/"
REFS = [
    # key, commit, path, line, anchor
    ("native_base", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", 2216, "const auto base = DeviceAddressFromWords(state, desc0, Binary(state, OpBitwiseAnd, u32t, desc1, U(0xffffu)));"),
    ("native_add", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", 2219, "node_addr       = Binary(state, OpIAdd, addrt, base, off);"),
    ("ir_base", COMMIT, S + "shader/recompiler/frontend/translate/Memory.cpp", 872, "const IR::U64 base64 = ir.ConstructU64(desc0, ir.BitwiseAnd(desc1, U32C(0xffffu)));"),
    ("ir_comment", COMMIT, S + "shader/recompiler/frontend/translate/Memory.cpp", 833, "//   dword0        = base_address[31:0]"),
    ("stub", COMMIT, S + "shader/recompiler/frontend/translate/Memory.cpp", 714, 'static const bool stub = Common::EnvFlagOn("KYTY_BVH_STUB");'),
    ("is_tri", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", 2223, "const auto is_tri   = Binary(state, OpULessThan, boolt, node_type, U(2u));"),
    ("nullpage", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", 2035, "const auto base = Select(state, type, missing, null_base, loaded);"),
    ("trip_emit", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterMemory.cpp", 1938, "void EmitLoopCapTrip(EmitterState& state, uint32_t budget) {"),
    ("cap_default", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterProgram.cpp", 568, "constexpr uint64_t BvhLoopCapDefaultHash = 0x380bb9d636390baeull;"),
    ("cap_token", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterProgram.cpp", 599, 'result.token = ":bvhcap" + std::to_string(result.cap);'),
    ("guard_cmp", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterProgram.cpp", 207, "state.builder.AddFunction(spv::OpUGreaterThan, TypeBool(state), over, next,"),
    ("guard_abort", COMMIT, S + "shader/recompiler/backend/spirv/spirvEmitterProgram.cpp", 222, "EmitLoopCapTrip(state, next);"),
    ("trip_log", COMMIT, S + "host_gpu/renderer/cache/faultManager.cpp", 204, 'LOGF("BvhLoopCapTrip: trips=+%u total=%u near=+%u near_total=%u max_spent=%u "'),
    ("fault_find", COMMIT, S + "host_gpu/renderer/cache/faultManager.cpp", 220, "(void)m_buffer_cache.FindBuffer(start, end - start);"),
    ("memcpy", COMMIT, S + "host_gpu/renderer/cache/bufferCache.cpp", 270, "std::memcpy(staging, reinterpret_cast<const void*>(vaddr), static_cast<size_t>(size));"),
    ("pagebits", COMMIT, S + "host_gpu/renderer/cache/bufferCache.h", 53, "static constexpr uint32_t CACHING_PAGEBITS  = 14;"),
    ("uses_dma", COMMIT, S + "shader/recompiler/ir/passes/ResourceTracking.cpp", 905, "if (op == ValueOpcode::BvhIntersectRay) {"),
    ("strap", COMMIT, S + "shader/recompiler/frontend/translate/Scalar.cpp", None, "case O::S_TRAP: EmitControlNop(); return true;"),
    ("rtskip", COMMIT, "src/common/gates.h", 672, 'RtSkip,           // KYTY_RT_SKIP,     file name "rtskip" (0 off, 1 skip, 2 self-check'),
    ("dumpcs", COMMIT, S + "host_gpu/renderer/renderCompute.cpp", 630, 'static const char* dump_cs      = std::getenv("KYTY_DUMP_CS");'),
    ("dumpcs_size", COMMIT, S + "host_gpu/renderer/renderCompute.cpp", 778, "if (base == 0 || size == 0 || size > (64u << 10)) {"),
    ("skipcs", COMMIT, S + "host_gpu/renderer/renderCompute.cpp", 521, 'static const char* skip_cs = std::getenv("KYTY_SKIP_CS");'),
    ("p237d", "57729aed", "docs/ROADMAP.md", 12609, "(д) **F3 = Б1б (+ Б1а)**"),
    ("s98", COMMIT, "docs/local-session-98.md", 110, "`cs=0x380bb9d636390bae args=1,2048,1"),
]


def show(commit, path):
    r = subprocess.run([GIT, "-C", REPO, "show", commit + ":" + path], capture_output=True)
    assert r.returncode == 0, (commit, path, r.stderr[:200])
    return r.stdout.decode("utf-8").split("\n")


cache = {}
ref_text = {}
map_lines = []
for key, commit, path, line, anchor in REFS:
    lines = cache.setdefault((commit, path), show(commit, path))
    if line is None:
        hits = [i + 1 for i, l in enumerate(lines) if anchor in l]
        assert len(hits) == 1, (key, hits)
        line = hits[0]
    got = lines[line - 1].strip()
    assert anchor in got, (key, line, got)
    plus = lines[line].strip()
    short = anchor if len(anchor) <= 70 else anchor[:70] + "…"
    ref_text[key] = "`%s:%s:%d` «%s»" % (commit, path, line, short.replace("|", "\\|"))
    map_lines.append("| `%s:%s:%d` | %s | %s |" % (commit, path, line, anchor.replace("|", "\\|")[:110], plus.replace("|", "\\|")[:80]))
refmap = "| ссылка | якорь (строка содержит) | контроль +1 (начало следующей строки) |\n|---|---|---|\n" + "\n".join(map_lines)

# ---- numeric checks
checks = 0


def ok(cond, what):
    global checks
    assert cond, what
    checks += 1


scan = open(D + "scan_f3a.out.txt", encoding="utf-8").read()
t02 = [int(x) for x in re.findall(r"trips=\+(\d+) total=\d+", scan.split("===== c142_09")[0].split("-- FrameTrace-x")[0])]
t09 = [int(x) for x in re.findall(r"trips=\+(\d+) total=\d+", scan.split("===== c142_09")[1].split("-- FrameTrace-x")[0])]
ok(t02 == [131072, 129024, 128000, 122880, 122848, 117760] and sum(t02) == 751584, "c142_02 trips")
ok(t09 == [131072] * 6 and sum(t09) == 786432, "c142_09 trips")
ok(131072 == 2048 * 64 and 131072 * 65536 == 8589934592, "dispatch size")
ok(abs(117760 / 131072 - 0.898) < 0.001, "share")
view = open(D + "view_f3a.out.txt", encoding="utf-8").read()
v02, v09 = view.split("===== c142_09")[0], view.split("===== c142_09")[1]


def dts(text, lo, hi):
    return [int(d) for n, d in re.findall(r"F \d+ n=(\d+) dt_us=(\d+)", text) if lo <= int(n) <= hi]


ok(dts(v02, 332, 337) == [299442, 299580, 284617, 300409, 298800, 299220], "dt c142_02")
ok(dts(v09, 182, 187) == [316631, 283174, 266420, 285526, 298651, 283939], "dt c142_09")
ok(min(dts(v02, 332, 337) + dts(v09, 182, 187)) == 266420 and max(dts(v02, 332, 337) + dts(v09, 182, 187)) == 316631, "range 266-317")
rows = json.load(open(D + "sky_f3a.json", encoding="utf-8"))


def band(s):
    return 0 if s <= 112 else 1 if s <= 126 else 2 if s <= 141 else 3


tab = [[0, 0, 0, 0] for _ in range(4)]
for r in rows:
    b = tab[band(r["ses"])]
    b[0] += 1
    b[1] += 1 if r["trips"] else 0
    b[2] += 1 if r["lows"] else 0
    b[3] += 1 if r["pairs"] else 0
ok(tab == [[151, 17, 151, 151], [61, 5, 61, 61], [72, 0, 71, 71], [2, 0, 2, 2]], "sky table %s" % tab)
ok([sum(c) for c in zip(*tab)] == [286, 22, 285, 285], "sky totals")
ok(tab[0][0] + tab[1][0] == 212 and tab[2][0] + tab[3][0] == 74 and tab[2][3] + tab[3][3] == 73, "212 / 74 / 73")
p74 = (1 - 22 / 212) ** 74
p65 = (1 - 22 / 212) ** sum(1 for r in rows if r["ses"] >= 128)
ok(sum(1 for r in rows if r["ses"] >= 128) == 65 and abs(p74 - 3.0e-4) < 0.05e-4 and abs(p65 - 8.1e-4) < 0.05e-4, "P %g %g" % (p74, p65))
import collections
per = collections.Counter(r["ses"] for r in rows if r["trips"])
ok(dict(per) == {103: 7, 105: 3, 106: 1, 109: 4, 110: 1, 111: 1, 113: 1, 114: 1, 118: 2, 126: 1} and sum(per.values()) == 22, "per session")
x1 = collections.Counter()
for r in rows:
    seq = [(fr, int(a, 16)) for fr, a in r["fault_seq"]]
    first = next((a for fr, a in seq if a > 0x100000000 and any(b == ((a >> 8) & ~0x3fff) for _, b in seq)), None)
    x1[first] += 1
ok(dict(x1) == {0x401c3c000: 285, None: 1}, "X1 %s" % x1)
win = open(D + "win_f3a.out.txt", encoding="utf-8").read().strip().split("\n")
ok(sum(1 for l in win[:-2] if " inside " in l) == 24 and "inside [f1+1, f2+1]: 24 ;" in win[-2] and win[-2].endswith(": 7"), "window 24/24, extra 7")
ok(sum(1 for l in win[:-2] if "max_spent [65537]" in l) == 24 and win[-1].startswith("trip lines 135 "), "max_spent")
nears = [int(re.search(r" near (\d+) ", l).group(1)) for l in win[:-2]]
ok(sum(1 for n in nears if n > 0) == 6 and max(nears) == 387104, "near %s" % nears)
s12 = open(D + "scan12_f3a.out.txt", encoding="utf-8").read()
blocks = s12.split("\n== ")[1:13]
ok(len(blocks) == 12 and sum(1 for b in blocks if "pairs (X, X>>8 page) both faulted: []" not in b) == 11, "pairs 11 of 12")
ok(sum(1 for b in blocks if "low (<4 GiB) fault pages: []" not in b) == 12, "low page 12 of 12")
ok("programs with IMAGE_BVH whose translation dump is in the logs: 1" in s12, "one program")
bfe = open(D + "bfe2_f3a.out.txt", encoding="utf-8").read()
ok("(offset 8, width 40): 40" in bfe and "20 sizes Counter({2: 20})" in bfe, "bfe sites")
ok(((0x401bc0000 >> 8) + 0x100) & ~0x3fff == 0x4018000 and ((0x401c3c000 >> 8) + 0x100) & ~0x3fff == 0x401c000, "page arithmetic")
ok(all(((x >> 8) + 0x100) & ~0x3fff == 0x4024000 for x in (0x40253c000, 0x4024c0000, 0x4024d4000, 0x402478000, 0x402518000, 0x4024e4000)), "X2 pages")
ok((37 & ~7) * 8 == 0x100 and abs(285 * 4096 / 65536 - 17.8) < 0.1, "root offset, cap arithmetic")
import math
ok(math.ceil(math.log(0.05) / math.log(1 - 0.9)) == 2, "N")
asm = open(D + "asm_380b.txt", encoding="utf-8").read().split("\n")
ok(sum(1 for a in asm if a.startswith("0x")) == 1917 and sum(1 for a in asm if "S_MIN_U32" in a) == 8
   and sum(1 for a in asm if "IMAGE_BVH_INTERSECT_RAY" in a) == 3 and sum(1 for a in asm if "S_BFE_U64" in a and "0x00280008" in a) == 2, "asm counts")
ext = open(D + "src_ext/gfx9Device.cpp", encoding="utf-8", errors="replace").read().split("\n")
ok("bvhSrd.base_address = gpuVirtAddr >> 8;" in ext[5333] and "PAL_ASSERT((gpuVirtAddr & 0xFF) == 0);" in ext[5331], "PAL lines")
reg = open(D + "src_ext/gfx10_sq_ko_reg.h", encoding="utf-8", errors="replace").read().split("\n")
ok("union sq_bvh_rsrc_t" in reg[98] and "base_address" in reg[100] and ": 40;" in reg[100] and "type" in reg[109], "PAL header lines")

body = open(D + "f3a_body.md", encoding="utf-8").read()
for key, text in ref_text.items():
    body = body.replace("@@REF:%s@@" % key, text)
left = re.findall(r"@@REF:\w+@@", body)
assert not left, left
body = body.replace("@@REFMAP@@", refmap).replace("@@NSUMS@@", str(checks))
assert "@@" not in body
for bad in open(D + "private_words.txt", encoding="utf-8").read().split():  # local file, not in git
    assert bad not in body, bad
body = body.replace("\r\n", "\n")
out = REPO + "/docs/track-f/f3a-b1b.md"
open(out, "wb").write(body.encode("utf-8"))
open(D + "refs_f3a_map.txt", "wb").write((refmap + "\n").encode("utf-8"))
print("refs", len(REFS), "ALL anchors OK; checks", checks, "; doc bytes", len(body.encode("utf-8")), "sha256", hashlib.sha256(body.encode("utf-8")).hexdigest())
print("ALL OK")

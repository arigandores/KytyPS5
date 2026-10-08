# F29d (HPP-703, Red Team): statement-by-statement comparison of the stand model (tests/B12BdaStampStand.cpp) with the code
# (bufferCache.cpp SynchronizeBuffersByRegion / BeginBdaPass / EndBdaPass, renderContext.cpp PrepareBda ForEach part) at a
# given commit. Code and model are normalized (names of the model, comments and FrameStats/timer lines dropped); the
# remaining differences are printed with difflib and must each be explained in the review.
# Usage: python cmp_model.py <commit_code> <commit_model>
import difflib
import re
import subprocess
import sys

GIT = "C:/Program Files/Git/cmd/git.exe"


def show(commit, path):
    return subprocess.run([GIT, "-C", "C:/kyty/KytyPS5", "show", "%s:%s" % (commit, path)], capture_output=True,
                          check=True).stdout.decode("utf-8")


def body(text, header):
    i = text.index(header)
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]
    raise SystemExit("unbalanced " + header)


REN = [
    (r"m_memory_tracker\.", "tracker."), (r"m_bda_dirty_ranges", "dirty_ranges"),
    (r"m_bda_region_stamps", "region_stamps"), (r"m_bda_stamp_generation", "stamp_generation"),
    (r"m_bda_bits_generation", "bits_generation"), (r"m_bda_map_generation", "map_generation"),
    (r"m_bda_narrow_check", "narrow_check"), (r"m_bda_pass_open", "bda_pass_open"), (r"m_bda_pass", "bda_pass"),
    (r"m_b12_rewalk", "rewalk"), (r"m_b12_rwd", "rwd"), (r"m_b12_lskip", "lskip"),
    (r"SynchronizeBuffersOfDirtyRanges\(\)", "OfDirtyRanges()"), (r"Libs::Graphics::", ""),
    (r"MemoryTracker::RegionCount", "MemoryTracker::RegionCount"),
]
DROP = [r"FrameStats::", r"bda_split", r"bda_walk_scope", r"bda_scan_t", r"LapScope", r"m_bda_scan_thread",
        r"Counter::", r"^\s*\}\s*$", r"^\s*$", r"bits_check", r"BdaBitsVerify", r"logged", r"LOGF",
        r"static_cast<unsigned long long>", r"range_address = 0", r"DirtyRangesTouchBuffers\(&"]
STAND_ONLY = [r"\bskipped\+\+", r"bit_skipped\+\+", r"scanned\+\+", r"nwould\+\+", r"nmiss\+\+", r"nrace\+\+"]


def norm(src, extra_drop=()):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    out = []
    for line in src.split("\n"):
        line = re.sub(r"//.*$", "", line).rstrip()
        for a, b in REN:
            line = re.sub(a, b, line)
        if any(re.search(p, line) for p in list(DROP) + list(extra_drop)):
            continue
        line = re.sub(r"\s+", " ", line).strip()
        line = line.replace("auto& ", "auto& ").replace("const auto ", "const auto ")
        out.append(line)
    return out


def main():
    cc, cm = sys.argv[1], sys.argv[2]
    code = show(cc, "src/graphics/host_gpu/renderer/cache/bufferCache.cpp")
    ctx = show(cc, "src/graphics/host_gpu/renderer/renderContext.cpp")
    model = show(cm, "tests/B12BdaStampStand.cpp")
    pairs = [
        ("ByRegion", body(code, "void BufferCache::SynchronizeBuffersByRegion("), body(model, "void ByRegion(")),
    ]
    if "BeginBdaPass" in code:
        pairs.append(("BeginBdaPass", body(code, "void BufferCache::BeginBdaPass()"), body(model, "void BeginBdaPass()")))
        pairs.append(("EndBdaPass(first stmt)", body(code, "void BufferCache::EndBdaPass()").split(";")[0] + ";",
                      body(model, "void EndBdaPass()").split(";")[0] + ";"))
    pc = body(ctx, "void RenderContext::PrepareBda()")
    pm = body(model, "void Prepare()")
    a = pc[pc.index("const bool fix_b12") if "fix_b12" in pc else pc.index("m_mapped_ranges.ForEach"):]
    a = a[:a.index("m_bda_cpu_epoch")]
    b = pm[pm.index("const bool fix_b12") if "fix_b12" in pm else pm.index("mapped_ranges.ForEach"):]
    b = b[:b.index("bda_cpu_epoch")]
    pairs.append(("PrepareBda(pass part)", a.replace("m_buffer_cache.", "cache.").replace("m_mapped_ranges", "mapped_ranges")
                  .replace("SynchronizeBuffersInRange", "InRange"), b))
    total = 0
    for name, c, m in pairs:
        nc, nm = norm(c), norm(m, STAND_ONLY + [r"hook", r"fire\(", r"auto\* fire"])
        d = [x for x in difflib.unified_diff(nc, nm, "code:" + cc, "model:" + cm, lineterm="", n=1)]
        print("=== %s: code %d lines, model %d lines, diff lines %d" % (name, len(nc), len(nm), len(d)))
        for x in d:
            print(x)
        total += len(d)
    print("TOTAL DIFF LINES", total)


main()

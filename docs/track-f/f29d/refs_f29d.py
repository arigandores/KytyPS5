# F29d (HPP-703, Red Team): the <commit>:<path>:<line> references of docs/track-f/f29d-review.md (general rule 24(1)) - each
# by its anchor line (the whole stripped line must equal the anchor) and the +1 line; the line number is checked, not
# searched. --negctl shifts every line by +1 and must print FAILED.
# Usage: python refs_f29d.py [--negctl]
import subprocess
import sys

GIT = "C:/Program Files/Git/cmd/git.exe"
BC = "src/graphics/host_gpu/renderer/cache/bufferCache.cpp"
REFS = [
    ("726e751e", BC, 3529, "const bool b12_pass = m_bda_pass_open;", "for (auto cursor = scan_begin; cursor < scan_end;) {"),
    ("726e751e", BC, 3545, "if (b12_pass && m_bda_region_stamps[index].walked_pass == m_bda_pass) {",
     "m_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);"),
    ("726e751e", BC, 3562, "if (b12_pass && m_bda_region_stamps[index].skipped_pass == m_bda_pass) {",
     "const auto& late = m_bda_region_stamps[index];"),
    ("726e751e", BC, 3565, "!(use_bits && BdaRegionWritePending(index))) {", "cursor += bytes;"),
    ("726e751e", BC, 3576, "const bool bit_clear = use_bits && !BdaTakeRegionWrite(index);",
     "if (bit_clear && m_bda_region_stamps[index].generation == m_bda_stamp_generation) {"),
    ("726e751e", BC, 3599, "m_bda_region_stamps[index].skipped_pass = m_bda_pass;", "}"),
    ("726e751e", BC, 3610, "seen.skipped_pass = m_bda_pass;", "}"),
    ("726e751e", BC, 3617, "seen = {stamp, m_bda_stamp_generation};", "if (b12_pass) {"),
    ("726e751e", BC, 3620, "seen.walked_pass = m_bda_pass;", "}"),
    ("726e751e", BC, 3447, "m_bda_region_stamps[index].generation = 0; // never the current generation: the next pass walks it",
     "Common::FrameStats::Add(Common::FrameStats::Counter::BdaRegionInv, 1);"),
    ("726e751e", "src/graphics/host_gpu/renderer/renderContext.cpp", 384, "m_buffer_cache.BeginBdaPass();", "}"),
    ("726e751e", "src/graphics/host_gpu/renderer/renderContext.cpp", 390, "m_buffer_cache.EndBdaPass();", "}"),
    ("726e751e", "src/graphics/host_gpu/regionDefinitions.h", 34, "inline bool BdaRegionWritePending(uint64_t index) noexcept {",
     "const auto word = index / 64u;"),
    ("726e751e", "src/graphics/host_gpu/renderer/cache/bufferCache.h", 389, "uint64_t                   skipped_pass = 0;", "};"),
    ("726e751e", "tests/B12BdaStampStand.cpp", 228, "if (b12_pass && region_stamps[index].skipped_pass == bda_pass) {",
     "const auto& late = region_stamps[index];"),
    ("726e751e", "tests/B12BdaStampStand.cpp", 231, "!(use_bits && Libs::Graphics::BdaRegionWritePending(index))) {",
     "cursor += bytes;"),
    ("726e751e", "tests/B12BdaStampStand.cpp", 534,
     "s->tracker->MarkRegionAsCpuModified(s->address, s->size); // the real ChangeState<Cpu, true>", "};"),
    ("726e751e", "src/graphics/presentation/videoOut.cpp", 2723, "{\"bda_b12_lskip\", FS::Counter::BdaB12Lskip, false},",
     "{\"prio_unsub\", FS::Counter::PrioUnsub, false},"),
    ("726e751e", "src/graphics/presentation/videoOut.cpp", 3566,
     "text += std::to_string(counter.micros ? dus(counter.counter) : d(counter.counter));", "}"),
]


def main():
    shift = 1 if "--negctl" in sys.argv else 0
    cache = {}
    bad = 0
    for commit, path, line, anchor, nxt in REFS:
        key = (commit, path)
        if key not in cache:
            cache[key] = subprocess.run([GIT, "-C", "C:/kyty/KytyPS5", "show", "%s:%s" % key], capture_output=True,
                                        check=True).stdout.decode("utf-8").split(chr(10))
        lines = cache[key]
        n = line + shift
        a = lines[n - 1].strip() if n - 1 < len(lines) else ""
        b = lines[n].strip() if n < len(lines) else ""
        ok = a == anchor and b == nxt
        bad += 0 if ok else 1
        print("%s %s:%s:%d" % ("OK  " if ok else "BAD ", commit, path, n))
    print("REFS %d, %s" % (len(REFS), "ALL OK" if bad == 0 else "FAILED %d" % bad))


main()

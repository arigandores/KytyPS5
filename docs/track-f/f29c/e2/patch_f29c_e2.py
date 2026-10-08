# F29c edition 2 (HPP-702, ROADMAP s122 item 641(v)): KYTY_FIX_B12=1 - the first visit of a pass that SKIPS marks the
# region (skipped_pass); a late visit after a skip takes no bit, writes no witness, sets no mark: it skips only when the
# witness of the current generation equals RegionWriteStamp and (with use_bits) the bit is not pending, otherwise it
# collects its piece and synchronizes. Counter bda_b12_lskip, field lskip= of FixB12Stat:. Code + stand model branch.
# Anchors are whole lines; LF in, LF out (CR stripped and restored if present).
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "C:/kyty/KytyPS5"


def patch(rel, edits):
    path = ROOT + "/" + rel
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            print("ANCHOR COUNT %d in %s:\n%s" % (n, rel, old))
            sys.exit(1)
        text = text.replace(old, new)
    if crlf:
        text = text.replace("\n", "\r\n")
    open(path, "wb").write(text.encode("utf-8"))
    print("patched", rel)


NL = chr(10)


def L(*lines):
    return NL.join(lines) + NL


# ---------------------------------------------------------------- frameStats.h
patch("src/common/frameStats.h", [(
    L("\tBdaB12Rwd,               // bda_b12_rwd"),
    L("\tBdaB12Rwd,               // bda_b12_rwd",
      "\t// Track F, F29c edition 2 (KYTY_FIX_B12=1, ROADMAP s122 item 641(v)(3)): late visits of a region in a BDA pass whose",
      "\t// first visit skipped it, that found the witness or the bit moved and collected their piece.  Raw count; decides nothing.",
      "\tBdaB12Lskip,             // bda_b12_lskip"),
)])

# ---------------------------------------------------------------- videoOut.cpp
patch("src/graphics/presentation/videoOut.cpp", [(
    L("\t\t\t\t    {\"bda_b12_rwd\", FS::Counter::BdaB12Rwd, false},"),
    L("\t\t\t\t    {\"bda_b12_rwd\", FS::Counter::BdaB12Rwd, false},",
      "\t\t\t\t    {\"bda_b12_lskip\", FS::Counter::BdaB12Lskip, false},"),
)])

# ---------------------------------------------------------------- bufferCache.h
patch("src/graphics/host_gpu/renderer/cache/bufferCache.h", [
    (L("\t\t// Written and read at KYTY_FIX_B12=1 only.",
       "\t\tuint64_t                   walked_pass = 0;"),
     L("\t\t// Written and read at KYTY_FIX_B12=1 only.",
       "\t\tuint64_t                   walked_pass = 0;",
       "\t\t// F29c edition 2 (item 641(v)(1)): the BDA pass whose FIRST visit of this region skipped it (by the bit or by the",
       "\t\t// witness); 0 - none. Never changes stamp or generation. Written and read at KYTY_FIX_B12=1 only.",
       "\t\tuint64_t                   skipped_pass = 0;")),
    (L("\tuint64_t                                           m_b12_rwd       = 0;"),
     L("\tuint64_t                                           m_b12_rwd       = 0;",
       "\tuint64_t                                           m_b12_lskip     = 0; // F29c edition 2, item 641(v)(3)")),
    (L("\tuint64_t                                           m_b12_stat_rwd    = 0;"),
     L("\tuint64_t                                           m_b12_stat_rwd    = 0;",
       "\tuint64_t                                           m_b12_stat_lskip  = 0;")),
])

# ---------------------------------------------------------------- bufferCache.cpp
patch("src/graphics/host_gpu/renderer/cache/bufferCache.cpp", [
    (L("\tif (m_bda_pass == m_b12_stat_pass && m_b12_rewalk == m_b12_stat_rewalk && m_b12_rwd == m_b12_stat_rwd) {"),
     L("\tif (m_bda_pass == m_b12_stat_pass && m_b12_rewalk == m_b12_stat_rewalk && m_b12_rwd == m_b12_stat_rwd &&",
       "\t    m_b12_lskip == m_b12_stat_lskip) {")),
    (L("\tm_b12_stat_rwd    = m_b12_rwd;",
       "\tLOGF(\"FixB12Stat: passes=%llu rewalk=%llu rwd=%llu\\n\", static_cast<unsigned long long>(m_bda_pass),",
       "\t     static_cast<unsigned long long>(m_b12_rewalk), static_cast<unsigned long long>(m_b12_rwd));"),
     L("\tm_b12_stat_rwd    = m_b12_rwd;",
       "\tm_b12_stat_lskip  = m_b12_lskip;",
       "\tLOGF(\"FixB12Stat: passes=%llu rewalk=%llu rwd=%llu lskip=%llu\\n\", static_cast<unsigned long long>(m_bda_pass),",
       "\t     static_cast<unsigned long long>(m_b12_rewalk), static_cast<unsigned long long>(m_b12_rwd),",
       "\t     static_cast<unsigned long long>(m_b12_lskip));")),
    (L("\t\t\tSynchronizeBuffersOfDirtyRanges();",
       "\t\t\tcursor += bytes;",
       "\t\t\tcontinue;",
       "\t\t}",
       "\t\tconst bool bit_clear = use_bits && !BdaTakeRegionWrite(index);"),
     L("\t\t\tSynchronizeBuffersOfDirtyRanges();",
       "\t\t\tcursor += bytes;",
       "\t\t\tcontinue;",
       "\t\t}",
       "\t\t// F29c edition 2 (KYTY_FIX_B12=1, ROADMAP s122 item 641(v)(2)): the first visit of this pass SKIPPED the region. This",
       "\t\t// late visit takes no bit, writes no witness and sets no mark - so a write that landed after the first visit (in",
       "\t\t// this piece or another) is still announced to the next pass by the bit and the stamp. It skips only on the same",
       "\t\t// condition as the first visit's (witness of the current generation equal to the stamp, and no pending bit when",
       "\t\t// the bits are used); otherwise it collects and synchronizes its own piece.",
       "\t\tif (b12_pass && m_bda_region_stamps[index].skipped_pass == m_bda_pass) {",
       "\t\t\tconst auto& late = m_bda_region_stamps[index];",
       "\t\t\tif (late.generation == m_bda_stamp_generation && late.stamp == m_memory_tracker.RegionWriteStamp(index) &&",
       "\t\t\t    !(use_bits && BdaRegionWritePending(index))) {",
       "\t\t\t\tcursor += bytes;",
       "\t\t\t\tcontinue;",
       "\t\t\t}",
       "\t\t\tm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);",
       "\t\t\tm_b12_lskip++;",
       "\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BdaB12Lskip, 1);",
       "\t\t\tSynchronizeBuffersOfDirtyRanges();",
       "\t\t\tcursor += bytes;",
       "\t\t\tcontinue;",
       "\t\t}",
       "\t\tconst bool bit_clear = use_bits && !BdaTakeRegionWrite(index);")),
    (L("\t\t\t\t\t}",
       "\t\t\t\t}",
       "\t\t\t}",
       "\t\t\tcursor += bytes;",
       "\t\t\tcontinue;",
       "\t\t}",
       "\t\tconst auto stamp = m_memory_tracker.RegionWriteStamp(index);"),
     L("\t\t\t\t\t}",
       "\t\t\t\t}",
       "\t\t\t}",
       "\t\t\tif (b12_pass) {",
       "\t\t\t\t// Item 641(v)(1): the first visit of this pass skipped the region by the bit.",
       "\t\t\t\tm_bda_region_stamps[index].skipped_pass = m_bda_pass;",
       "\t\t\t}",
       "\t\t\tcursor += bytes;",
       "\t\t\tcontinue;",
       "\t\t}",
       "\t\tconst auto stamp = m_memory_tracker.RegionWriteStamp(index);")),
    (L("\t\tif (seen.generation == m_bda_stamp_generation && seen.stamp == stamp) {",
       "\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsSkipped, 1);",
       "\t\t\tcursor += bytes;"),
     L("\t\tif (seen.generation == m_bda_stamp_generation && seen.stamp == stamp) {",
       "\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BdaRegionsSkipped, 1);",
       "\t\t\tif (b12_pass) {",
       "\t\t\t\t// Item 641(v)(1): the first visit of this pass skipped the region by the witness.",
       "\t\t\t\tseen.skipped_pass = m_bda_pass;",
       "\t\t\t}",
       "\t\t\tcursor += bytes;")),
])

# ---------------------------------------------------------------- stand model (tests/B12BdaStampStand.cpp)
patch("tests/B12BdaStampStand.cpp", [
    (L("\t\tuint64_t                   walked_pass = 0; // F29c: KYTY_FIX_B12=1 only"),
     L("\t\tuint64_t                   walked_pass = 0; // F29c: KYTY_FIX_B12=1 only",
       "\t\tuint64_t                   skipped_pass = 0; // F29c edition 2: KYTY_FIX_B12=1 only")),
    (L("\tuint64_t                    rewalk = 0, rwd = 0;         // m_b12_rewalk, m_b12_rwd (F29c)"),
     L("\tuint64_t                    rewalk = 0, rwd = 0;         // m_b12_rewalk, m_b12_rwd (F29c)",
       "\tuint64_t                    lskip = 0;                   // m_b12_lskip (F29c edition 2)")),
    (L("\t\t\t\tOfDirtyRanges();",
       "\t\t\t\tcursor += bytes;",
       "\t\t\t\tcontinue;",
       "\t\t\t}",
       "\t\t\tconst bool bit_clear = use_bits && !Libs::Graphics::BdaTakeRegionWrite(index);",
       "\t\t\tif (bit_clear && region_stamps[index].generation == stamp_generation) {",
       "\t\t\t\tbit_skipped++;",
       "\t\t\t\tskipped++;",
       "\t\t\t\tcursor += bytes;"),
     L("\t\t\t\tOfDirtyRanges();",
       "\t\t\t\tcursor += bytes;",
       "\t\t\t\tcontinue;",
       "\t\t\t}",
       "\t\t\tif (b12_pass && region_stamps[index].skipped_pass == bda_pass) {",
       "\t\t\t\tconst auto& late = region_stamps[index];",
       "\t\t\t\tif (late.generation == stamp_generation && late.stamp == tracker.RegionWriteStamp(index) &&",
       "\t\t\t\t    !(use_bits && Libs::Graphics::BdaRegionWritePending(index))) {",
       "\t\t\t\t\tcursor += bytes;",
       "\t\t\t\t\tcontinue;",
       "\t\t\t\t}",
       "\t\t\t\ttracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);",
       "\t\t\t\tlskip++;",
       "\t\t\t\tOfDirtyRanges();",
       "\t\t\t\tcursor += bytes;",
       "\t\t\t\tcontinue;",
       "\t\t\t}",
       "\t\t\tconst bool bit_clear = use_bits && !Libs::Graphics::BdaTakeRegionWrite(index);",
       "\t\t\tif (bit_clear && region_stamps[index].generation == stamp_generation) {",
       "\t\t\t\tbit_skipped++;",
       "\t\t\t\tskipped++;",
       "\t\t\t\tif (b12_pass) {",
       "\t\t\t\t\tregion_stamps[index].skipped_pass = bda_pass;",
       "\t\t\t\t}",
       "\t\t\t\tcursor += bytes;")),
    (L("\t\t\tif (seen.generation == stamp_generation && seen.stamp == stamp) {",
       "\t\t\t\tskipped++;",
       "\t\t\t\tcursor += bytes;"),
     L("\t\t\tif (seen.generation == stamp_generation && seen.stamp == stamp) {",
       "\t\t\t\tskipped++;",
       "\t\t\t\tif (b12_pass) {",
       "\t\t\t\t\tseen.skipped_pass = bda_pass;",
       "\t\t\t\t}",
       "\t\t\t\tcursor += bytes;")),
    (L("\tconst auto     rwd0    = cache.rwd;"),
     L("\tconst auto     rwd0    = cache.rwd;",
       "\tconst auto     lskip0  = cache.lskip;",
       "\tuint64_t       late_lskips = 0;")),
    (L("\t\t\tconst auto r0 = cache.rewalk;"),
     L("\t\t\tconst auto r0 = cache.rewalk;",
       "\t\t\tconst auto l0 = cache.lskip;")),
    (L("\t\t\t\tlate_rewalks += dr;"),
     L("\t\t\t\tlate_rewalks += dr;",
       "\t\t\t\tlate_lskips += cache.lskip - l0;")),
    (L("\t            \"scan_passes=%llu rw_min=%llu rw_max=%llu late_scans=%llu late_rewalks=%llu\\n\","),
     L("\t            \"scan_passes=%llu rw_min=%llu rw_max=%llu late_scans=%llu late_rewalks=%llu lskip=%llu late_lskips=%llu\\n\",")),
    (L("\t            static_cast<unsigned long long>(late_scans), static_cast<unsigned long long>(late_rewalks));"),
     L("\t            static_cast<unsigned long long>(late_scans), static_cast<unsigned long long>(late_rewalks),",
       "\t            static_cast<unsigned long long>(cache.lskip - lskip0), static_cast<unsigned long long>(late_lskips));")),
    (L("// buffer (rwd); per iteration: scans and revisits in the passes after the first (late_*), and the minimum and",
       "// maximum of revisits over the passes that scanned at least one region (rw_min / rw_max; scan_passes of them)."),
     L("// buffer (rwd); per iteration: scans and revisits in the passes after the first (late_*), and the minimum and",
       "// maximum of revisits over the passes that scanned at least one region (rw_min / rw_max; scan_passes of them).",
       "// Edition 2 (ROADMAP s122 item 641(v)): skipped_pass - the first visit of the pass skipped the region; a late visit",
       "// after a skip takes no bit and writes no witness, skips on the first visit's condition, else collects its piece",
       "// (lskip; late_lskips - those in the passes after the first).")),
])
print("ALL PATCHED")

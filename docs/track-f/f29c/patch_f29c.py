# Track F, F29c (HPP-702, ROADMAP s122 item 639(d)): KYTY_FIX_B12 - the code. Anchors are whole lines; each must occur once.
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "C:/kyty/KytyPS5"
NL = chr(10)


def edit(rel, pairs):
    path = ROOT + "/" + rel
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", NL)
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            print("ANCHOR x%d in %s: %r" % (n, rel, old[:90]))
            sys.exit(1)
        text = text.replace(old, new)
    if crlf:
        text = text.replace(NL, "\r\n")
    open(path, "wb").write(text.encode("utf-8"))
    print("patched", rel)


def L(*lines):
    return NL.join(lines) + NL


# 1. The knob, next to KYTY_FIX_B13 (the stand reads the same function).
edit("src/graphics/host_gpu/regionManager.h", [(
    L("[[nodiscard]] inline bool FixB13Enabled() noexcept {",
      "\tstatic const bool on = [] {",
      "\t\tconst char* value = std::getenv(\"KYTY_FIX_B13\");",
      "\t\treturn value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
      "\t}();",
      "\treturn on;",
      "}"),
    L("[[nodiscard]] inline bool FixB13Enabled() noexcept {",
      "\tstatic const bool on = [] {",
      "\t\tconst char* value = std::getenv(\"KYTY_FIX_B13\");",
      "\t\treturn value == nullptr || value[0] == '\\0' || Common::EnvValueOn(value);",
      "\t}();",
      "\treturn on;",
      "}",
      "",
      "// Track F, F29c (HPP-702, ROADMAP s122 item 639(d)): knob KYTY_FIX_B12, read once per process; default OFF - unset, \"\",",
      "// 0/false/off/no = OFF (Common::EnvValueOn). At 1 the incremental BDA scan numbers its passes (RenderContext::PrepareBda),",
      "// and a tracking region already walked in the current pass by another mapped range is walked again for the piece of",
      "// this range (BufferCache::SynchronizeBuffersByRegion) - B12: the witness of the whole 4 MiB region was written by the",
      "// walk of the first range while only that range's piece was collected, so the second range skipped the region.",
      "// BufferCache's constructor prints \"FixB12: mode=<0|1>\" once per process.",
      "[[nodiscard]] inline bool FixB12Enabled() noexcept {",
      "\tstatic const bool on = Common::EnvValueOn(std::getenv(\"KYTY_FIX_B12\"));",
      "\treturn on;",
      "}"),
)])

# 2. BufferCache: the pass, the field of the witness, the counters of the line.
edit("src/graphics/host_gpu/renderer/cache/bufferCache.h", [
    (L("#include <atomic>"), L("#include <atomic>", "#include <chrono>")),
    (L("\tvoid               SetBdaNarrowCheck(bool check) noexcept { m_bda_narrow_check = check; }"),
     L("\tvoid               SetBdaNarrowCheck(bool check) noexcept { m_bda_narrow_check = check; }",
       "\t// Track F, F29c (KYTY_FIX_B12, ROADMAP s122 item 639(d), (g)(3)): called by PrepareBda at 1 only, around its",
       "\t// m_mapped_ranges.ForEach - the pass is open between the two calls and nowhere else, so a walk outside it is the",
       "\t// path of 0. EndBdaPass also prints \"FixB12Stat:\" (item 639(g)(5)).",
       "\tvoid               BeginBdaPass() noexcept;",
       "\tvoid               EndBdaPass();")),
    (L("\tstruct BdaRegionStamp {",
       "\t\tMemoryTracker::RegionStamp stamp;",
       "\t\tuint64_t                   generation = 0;",
       "\t};"),
     L("\tstruct BdaRegionStamp {",
       "\t\tMemoryTracker::RegionStamp stamp;",
       "\t\tuint64_t                   generation = 0;",
       "\t\t// Track F, F29c (KYTY_FIX_B12): the BDA pass (m_bda_pass) whose scanning visit last wrote this witness; 0 - none.",
       "\t\t// Written and read at KYTY_FIX_B12=1 only.",
       "\t\tuint64_t                   walked_pass = 0;",
       "\t};")),
    (L("\tstd::thread::id                                    m_bda_scan_thread {};"),
     L("\tstd::thread::id                                    m_bda_scan_thread {};",
       "\t// Track F, F29c (KYTY_FIX_B12, ROADMAP s122 item 639(d)): the number of the current BDA pass and whether it is open",
       "\t// (BeginBdaPass .. EndBdaPass); the running totals of the \"FixB12Stat:\" line (revisits; revisits whose collected",
       "\t// piece overlaps a registered buffer) and the values and time of its last print. Render mutex (PrepareBda) only.",
       "\tuint64_t                                           m_bda_pass      = 0;",
       "\tbool                                               m_bda_pass_open = false;",
       "\tuint64_t                                           m_b12_rewalk    = 0;",
       "\tuint64_t                                           m_b12_rwd       = 0;",
       "\tuint64_t                                           m_b12_stat_pass   = 0;",
       "\tuint64_t                                           m_b12_stat_rewalk = 0;",
       "\tuint64_t                                           m_b12_stat_rwd    = 0;",
       "\tstd::chrono::steady_clock::time_point              m_b12_stat_time {};")),
])

# 3. BufferCache: the line of the knob, the pass, the revisit.
edit("src/graphics/host_gpu/renderer/cache/bufferCache.cpp", [
    (L("\tLOGF(\"BufferGc: budget=%llu trigger=%llu critical=%llu shift_mb=%llu\\n\", static_cast<unsigned long long>(budget),",
       "\t     static_cast<unsigned long long>(m_trigger_gc_memory), static_cast<unsigned long long>(m_critical_gc_memory),",
       "\t     static_cast<unsigned long long>(shift_mb));",
       "}"),
     L("\tLOGF(\"BufferGc: budget=%llu trigger=%llu critical=%llu shift_mb=%llu\\n\", static_cast<unsigned long long>(budget),",
       "\t     static_cast<unsigned long long>(m_trigger_gc_memory), static_cast<unsigned long long>(m_critical_gc_memory),",
       "\t     static_cast<unsigned long long>(shift_mb));",
       "\t// Track F, F29c (KYTY_FIX_B12, ROADMAP s122 item 639(d)): the knob is read here, once per process, and printed once.",
       "\tstatic std::atomic<bool> fix_b12_logged {false};",
       "\tconst bool               fix_b12 = FixB12Enabled();",
       "\tif (!fix_b12_logged.exchange(true, std::memory_order_relaxed)) {",
       "\t\tLOGF(\"FixB12: mode=%d\\n\", fix_b12 ? 1 : 0);",
       "\t}",
       "}")),
    (L("// Incremental variant (gate \"bdastamp\"): only regions that announced a CPU write since the last",
       "// scan are locked and walked. The witness is read and stored BEFORE the region is scanned, so a",
       "// write racing with the scan is seen by the next preparation instead of being lost."),
     L("void BufferCache::BeginBdaPass() noexcept {",
       "\tm_bda_pass++;",
       "\tm_bda_pass_open = true;",
       "}",
       "",
       "void BufferCache::EndBdaPass() {",
       "\tm_bda_pass_open = false;",
       "\t// Item 639(g)(5): the running totals, at most once in 10 s of host time and only when one of them moved.",
       "\tif (m_bda_pass == m_b12_stat_pass && m_b12_rewalk == m_b12_stat_rewalk && m_b12_rwd == m_b12_stat_rwd) {",
       "\t\treturn;",
       "\t}",
       "\tconst auto now = std::chrono::steady_clock::now();",
       "\tif (m_b12_stat_pass != 0 && now - m_b12_stat_time < std::chrono::seconds(10)) {",
       "\t\treturn;",
       "\t}",
       "\tm_b12_stat_time   = now;",
       "\tm_b12_stat_pass   = m_bda_pass;",
       "\tm_b12_stat_rewalk = m_b12_rewalk;",
       "\tm_b12_stat_rwd    = m_b12_rwd;",
       "\tLOGF(\"FixB12Stat: passes=%llu rewalk=%llu rwd=%llu\\n\", static_cast<unsigned long long>(m_bda_pass),",
       "\t     static_cast<unsigned long long>(m_b12_rewalk), static_cast<unsigned long long>(m_b12_rwd));",
       "}",
       "",
       "// Incremental variant (gate \"bdastamp\"): only regions that announced a CPU write since the last",
       "// scan are locked and walked. The witness is read and stored BEFORE the region is scanned, so a",
       "// write racing with the scan is seen by the next preparation instead of being lost.")),
    (L("\tconst bool bits_check = use_bits && Common::Gates::Enabled(Common::Gates::Gate::BdaWriteBitsVerify);",
       "\tm_bda_bits_generation = m_bda_stamp_generation;"),
     L("\tconst bool bits_check = use_bits && Common::Gates::Enabled(Common::Gates::Gate::BdaWriteBitsVerify);",
       "\tm_bda_bits_generation = m_bda_stamp_generation;",
       "\t// Track F, F29c (KYTY_FIX_B12=1, ROADMAP s122 item 639(d), (g)(3)): true only inside an open pass of PrepareBda.",
       "\tconst bool b12_pass = m_bda_pass_open;")),
    (L("\t\tconst bool bit_clear = use_bits && !BdaTakeRegionWrite(index);"),
     L("\t\t// Track F, F29c (KYTY_FIX_B12=1, ROADMAP s122 item 639(d), (g)(1)): another mapped range walked this region in this",
       "\t\t// pass and wrote its witness, but collected only its own piece. This piece is collected and synchronized now -",
       "\t\t// without the bit (taking it would drop a write announced after the first visit's collect, and the next pass",
       "\t\t// would skip the region on a clear bit), without the witness test and without writing the witness: a write",
       "\t\t// after the first visit's stamp read moved the stamp, so the next pass walks the region again.",
       "\t\tif (b12_pass && m_bda_region_stamps[index].walked_pass == m_bda_pass) {",
       "\t\t\tm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);",
       "\t\t\tm_b12_rewalk++;",
       "\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BdaB12Rewalk, 1);",
       "\t\t\tif (DirtyRangesTouchBuffers()) {",
       "\t\t\t\tm_b12_rwd++;",
       "\t\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BdaB12Rwd, 1);",
       "\t\t\t}",
       "\t\t\tSynchronizeBuffersOfDirtyRanges();",
       "\t\t\tcursor += bytes;",
       "\t\t\tcontinue;",
       "\t\t}",
       "\t\tconst bool bit_clear = use_bits && !BdaTakeRegionWrite(index);")),
    (L("\t\tseen = {stamp, m_bda_stamp_generation};"),
     L("\t\tseen = {stamp, m_bda_stamp_generation};",
       "\t\tif (b12_pass) {",
       "\t\t\t// Item 639(g)(2): after the assignment above, which resets the field; the skips above never set it.",
       "\t\t\tseen.walked_pass = m_bda_pass;",
       "\t\t}")),
])

# 4. PrepareBda: the pass around the walk, at 1 only.
edit("src/graphics/host_gpu/renderer/renderContext.cpp", [
    (L("\tm_mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {",
       "\t\tm_buffer_cache.SynchronizeBuffersInRange(start, end - start);",
       "\t});"),
     L("\t// Track F, F29c (KYTY_FIX_B12, ROADMAP s122 item 639(d)): at 1 the walk below is one numbered pass, open only for",
       "\t// the ForEach; at 0 neither call is made.",
       "\tconst bool fix_b12 = FixB12Enabled();",
       "\tif (fix_b12) {",
       "\t\tm_buffer_cache.BeginBdaPass();",
       "\t}",
       "\tm_mapped_ranges.ForEach([this](uint64_t start, uint64_t end) {",
       "\t\tm_buffer_cache.SynchronizeBuffersInRange(start, end - start);",
       "\t});",
       "\tif (fix_b12) {",
       "\t\tm_buffer_cache.EndBdaPass();",
       "\t}")),
])

# 5. The counters, where the other bda_* of the BDA scan are declared and printed.
edit("src/common/frameStats.h", [
    (L("\tBdaNarrowRace,           // bda_nrace"),
     L("\tBdaNarrowRace,           // bda_nrace",
       "\t// Track F, F29c (KYTY_FIX_B12=1, ROADMAP s122 item 639(g)(4)): revisits of a region in the same BDA pass, and those",
       "\t// whose collected piece gave a dirty range overlapping a registered buffer (pages the path of 0 would not have",
       "\t// collected by the BDA scan).  Raw counts; they decide nothing.",
       "\tBdaB12Rewalk,            // bda_b12_rewalk",
       "\tBdaB12Rwd,               // bda_b12_rwd")),
])
edit("src/graphics/presentation/videoOut.cpp", [
    (L("\t\t\t\t    {\"bda_nrace\", FS::Counter::BdaNarrowRace, false},"),
     L("\t\t\t\t    {\"bda_nrace\", FS::Counter::BdaNarrowRace, false},",
       "\t\t\t\t    {\"bda_b12_rewalk\", FS::Counter::BdaB12Rewalk, false},",
       "\t\t\t\t    {\"bda_b12_rwd\", FS::Counter::BdaB12Rwd, false},")),
])
print("ALL OK")

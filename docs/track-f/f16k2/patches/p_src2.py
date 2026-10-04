"""F16k2 (HPP-590, ROADMAP s122 item 496(b)(1)-(6)): RC1-RC5 of the F16l review in the KYTY_FIX_F5CMU / KYTY_DIAG_F5ID code.

    python p_src2.py <repo root>

Files: renderer/diagF5.h/.cpp, cache/bufferCache.h/.cpp, cache/textureCache.h/.cpp, pipeline/descriptors.cpp,
renderCompute.cpp. LF in, LF out (a CR is an error). Every anchor is whole lines and must occur exactly once. No file of
the translation signature set (CMakeLists.txt:156: src/graphics/shader/**, shaderTranslationCache.cpp, gpu_format.h,
gpu_defs.h, imageInfo.h) is touched - checked at the end.
"""
import sys

ROOT = sys.argv[1]
R = ROOT + "/src/graphics/host_gpu/renderer/"
FILES = {}


def load(path):
    if path not in FILES:
        data = open(path, "rb").read()
        if b"\r" in data:
            raise SystemExit("CR in " + path)
        FILES[path] = data.decode("utf-8")
    return FILES[path]


def sub(path, old, new):
    t = load(path)
    n = t.count(old)
    if n != 1:
        raise SystemExit("anchor count %d in %s for %r" % (n, path, old[:100]))
    FILES[path] = t.replace(old, new)


SIGNATURE = ("/src/graphics/shader/", "shaderTranslationCache.cpp", "gpu_format.h", "gpu_defs.h", "imageInfo.h")

# ---------------------------------------------------------------- diagF5.h
P = R + "diagF5.h"
sub(P, "\tCmaskRtBucketOnly,\n\tCount\n};\n",
    "\tCmaskRtBucketOnly,\n"
    "\t// Track F, F16k2 (RC4, ROADMAP s122 item 496(b)(4)): the f5cmu_exact_stale decisions set by a CPU-modified page of the\n"
    "\t// fill (PendingDccFillStale's cpu_written; the event line says why=cpu): f5cmu_exact_cpu <= f5cmu_exact_stale.\n"
    "\tF5CmuExactCpu,\n"
    "\tCount\n};\n")
sub(P, "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer };\n",
    "// Track F, F16k2 (RC4, item 496(b)(4)): Cpu - an ExactStale decision set by a CPU write (a CPU-modified page of the\n"
    "// fill), not by a crossing GPU write.\n"
    "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu };\n")
sub(P, "\tbool fallback      = false;\n};\n[[nodiscard]] inline bool StaleBucketOnly(const StaleProbe& probe) {\n",
    "\tbool fallback      = false;\n"
    "\t// Track F, F16k2 (RC4): exact_stale was set by cpu_written (a CPU-modified page of the fill), not by a GPU write.\n"
    "\tbool cpu           = false;\n"
    "};\n[[nodiscard]] inline bool StaleBucketOnly(const StaleProbe& probe) {\n")
sub(P, "bool                      NoteCmuEvent(const CmuEventLine& line);\n",
    "bool                      NoteCmuEvent(const CmuEventLine& line);\n"
    "// Track F, F16k2 (RC5, ROADMAP s122 item 496(b)(5)): the event line of a decision of the FCE acquisition that has no\n"
    "// cmask_fce line (no B42 hit: the target carried CMASK metadata already - FixB42Probe answered None - or a drawn\n"
    "// fill), KYTY_DIAG_F5=1 and fix not off / fresh: \"DiagF5Ev: cmask_fce_nohit n=<k> b42=<none|drawn> present=<n>\n"
    "// gpu=<n> image=0x... cmask=0x... extent=<w>x<h> fix=<..> [why=<..>]\" (`applied` is not printed); its own limit -\n"
    "// the first 64 (k = 1..64), counted after.\n"
    "[[nodiscard]] std::string FormatCmuNoHit(uint64_t n, const CmuEventLine& line, bool drawn);\n"
    "bool                      NoteCmuNoHit(const CmuEventLine& line, bool drawn);\n")
sub(P, "enum class WrAfter : uint8_t { None, Exact, Fallback, Na };\n",
    "// Track F, F16k2 (RC1, item 496(b)(1)): Large - no recorded bucket write crosses the range after `since`, but a GPU\n"
    "// write larger than 16 MB (no bucket, no ring, any address) is newer than `since`.\n"
    "enum class WrAfter : uint8_t { None, Exact, Fallback, Na, Large };\n")
sub(P, "// The fill's GPU write sequence (StampPendingDccFill's answer for any entry type), for wr_after.\n"
       "void     NoteFillSeq(uint64_t address, uint64_t seq);\n"
       "[[nodiscard]] uint64_t FillSeq(uint64_t address);\n",
    "// The fill's GPU write sequence (StampPendingDccFill's answer for any entry type), for wr_after; Track F, F16k2 (RC2,\n"
    "// item 496(b)(2)): with the CPU write epoch of the fill range at the stamp (MemoryTracker::RangeWriteEpoch; 0 - not\n"
    "// tracked), for cpu_mod. FillCpuEpoch: false - no fill was stamped at `address`.\n"
    "void     NoteFillSeq(uint64_t address, uint64_t seq, uint64_t cpu_epoch);\n"
    "[[nodiscard]] uint64_t FillSeq(uint64_t address);\n"
    "[[nodiscard]] bool     FillCpuEpoch(uint64_t address, uint64_t* cpu_epoch);\n"
    "// Track F, F16k2 (RC3, item 496(b)(3)): a fill stamp its dispatch left untaken (TextureCache::F5IdNoteStampLate at the\n"
    "// end of DispatchDirect, or TrackDccFill over it) - the counter stamp_late of the sum line, once per stamp.\n"
    "void NoteStampLate();\n")

# ---------------------------------------------------------------- diagF5.cpp
P = R + "diagF5.cpp"
sub(P, "    \"cmask_rt_bucket_only\",\n};\nstatic_assert(std::size(F5Names)",
    "    \"cmask_rt_bucket_only\",\n    \"f5cmu_exact_cpu\",\n};\nstatic_assert(std::size(F5Names)")
sub(P, "    \"next_overflow\", \"keys_fce\",   \"keys_cs\",      \"overflow_fce\", \"overflow_cs\",\n};\n",
    "    \"next_overflow\", \"keys_fce\",   \"keys_cs\",      \"overflow_fce\", \"overflow_cs\",\n    \"stamp_late\",\n};\n")
sub(P, "\tkOverflowCs,\n\tkIdCount\n};\n", "\tkOverflowCs,\n\tkStampLate, // Track F, F16k2 (RC3)\n\tkIdCount\n};\n")
sub(P, "\tstd::map<uint64_t, uint64_t>    fill_seq;\n",
    "\tstd::map<uint64_t, uint64_t>    fill_seq;\n"
    "\tstd::map<uint64_t, uint64_t>    fill_cpu_epoch; // Track F, F16k2 (RC2): RangeWriteEpoch of the fill at its stamp\n")
sub(P, "\t\tcase Id::WrAfter::Na: return \"na\";\n",
    "\t\tcase Id::WrAfter::Na: return \"na\";\n\t\tcase Id::WrAfter::Large: return \"large\";\n")
sub(P, "\t\tcase CmuWhy::NoLayer: return \"nolayer\";\n",
    "\t\tcase CmuWhy::NoLayer: return \"nolayer\";\n\t\tcase CmuWhy::Cpu: return \"cpu\";\n")
sub(P, "std::atomic<uint64_t> g_cmu_events {0};\n} // namespace\n",
    "std::atomic<uint64_t> g_cmu_events {0};\n"
    "std::atomic<uint64_t> g_cmu_nohit_events {0}; // Track F, F16k2 (RC5): the lines cmask_fce_nohit\n"
    "} // namespace\n")
sub(P, "\tEmitLine(FormatCmuEvent(n, line));\n\treturn true;\n}\n",
    "\tEmitLine(FormatCmuEvent(n, line));\n\treturn true;\n}\n"
    "\n"
    "std::string FormatCmuNoHit(uint64_t n, const CmuEventLine& line, bool drawn) {\n"
    "\tauto text = fmt::format(\"DiagF5Ev: cmask_fce_nohit n={} b42={} present={} gpu={} image=0x{:016x} cmask=0x{:016x} \"\n"
    "\t                        \"extent={}x{} fix={}\",\n"
    "\t                        n, drawn ? \"drawn\" : \"none\", line.present, line.gpu, line.image, line.cmask, line.width,\n"
    "\t                        line.height, CmuFixName(line.event.fix));\n"
    "\tif (line.event.why != CmuWhy::None) {\n"
    "\t\ttext += fmt::format(\" why={}\", CmuWhyName(line.event.why));\n"
    "\t}\n"
    "\treturn text;\n"
    "}\n"
    "\n"
    "bool NoteCmuNoHit(const CmuEventLine& line, bool drawn) {\n"
    "\tconst auto n = g_cmu_nohit_events.fetch_add(1, std::memory_order_relaxed) + 1;\n"
    "\tif (n > 64) {\n"
    "\t\treturn false;\n"
    "\t}\n"
    "\tEmitLine(FormatCmuNoHit(n, line, drawn));\n"
    "\treturn true;\n"
    "}\n")
sub(P, "void NoteFillSeq(uint64_t address, uint64_t seq) {\n"
       "\tauto&            s = IdS();\n"
       "\tstd::scoped_lock lock {s.mutex};\n"
       "\ts.fill_seq[address] = seq;\n"
       "}\n",
    "void NoteFillSeq(uint64_t address, uint64_t seq, uint64_t cpu_epoch) {\n"
    "\tauto&            s = IdS();\n"
    "\tstd::scoped_lock lock {s.mutex};\n"
    "\ts.fill_seq[address]       = seq;\n"
    "\ts.fill_cpu_epoch[address] = cpu_epoch;\n"
    "}\n")
sub(P, "\tconst auto       found = s.fill_seq.find(address);\n"
       "\treturn found == s.fill_seq.end() ? 0 : found->second;\n"
       "}\n",
    "\tconst auto       found = s.fill_seq.find(address);\n"
    "\treturn found == s.fill_seq.end() ? 0 : found->second;\n"
    "}\n"
    "\n"
    "bool FillCpuEpoch(uint64_t address, uint64_t* cpu_epoch) {\n"
    "\tauto&            s = IdS();\n"
    "\tstd::scoped_lock lock {s.mutex};\n"
    "\tconst auto       found = s.fill_cpu_epoch.find(address);\n"
    "\tif (found == s.fill_cpu_epoch.end()) {\n"
    "\t\treturn false;\n"
    "\t}\n"
    "\t*cpu_epoch = found->second;\n"
    "\treturn true;\n"
    "}\n"
    "\n"
    "void NoteStampLate() {\n"
    "\tauto&            s = IdS();\n"
    "\tstd::scoped_lock lock {s.mutex};\n"
    "\ts.cnt[kStampLate]++;\n"
    "}\n")
sub(P, "\ts.fill_seq.clear();\n\ts.stale_lines = 0;\n",
    "\ts.fill_seq.clear();\n\ts.fill_cpu_epoch.clear();\n\ts.stale_lines = 0;\n")

# ---------------------------------------------------------------- bufferCache.h / .cpp
P = R + "cache/bufferCache.h"
sub(P, "\t[[nodiscard]] ExactWriteSeq LastGpuWriteSeqExact(uint64_t vaddr, uint64_t size, uint64_t since) const;\n",
    "\t[[nodiscard]] ExactWriteSeq LastGpuWriteSeqExact(uint64_t vaddr, uint64_t size, uint64_t since) const;\n"
    "\t// Track F, F16k2 (KYTY_DIAG_F5ID, ROADMAP s122 item 496(b)(1)-(2)): the sequence number of the last GPU write larger\n"
    "\t// than 16 MB (m_large_write_seq: no bucket, no ring, any address), and MemoryTracker::RangeWriteEpoch of a range\n"
    "\t// (0 - an empty or invalid range, or a region not tracked; lock free). Measurement only: no decision reads them.\n"
    "\t[[nodiscard]] uint64_t LargeGpuWriteSeq() const noexcept { return m_large_write_seq; }\n"
    "\t[[nodiscard]] uint64_t F5IdRangeWriteEpoch(uint64_t vaddr, uint64_t size);\n")
P = R + "cache/bufferCache.cpp"
sub(P, "\t\tif (ring->second.count > ExactRing::K && oldest > since) {\n"
       "\t\t\tanswer.fallback = true;\n"
       "\t\t}\n"
       "\t}\n"
       "\treturn answer;\n"
       "}\n",
    "\t\tif (ring->second.count > ExactRing::K && oldest > since) {\n"
    "\t\t\tanswer.fallback = true;\n"
    "\t\t}\n"
    "\t}\n"
    "\treturn answer;\n"
    "}\n"
    "\n"
    "uint64_t BufferCache::F5IdRangeWriteEpoch(uint64_t vaddr, uint64_t size) {\n"
    "\t// Track F, F16k2 (item 496(b)(2)): never the EXIT of MemoryTracker::ValidateRange on a range made from registers.\n"
    "\tif (size == 0 || !GuestRange {vaddr, size}.Valid()) {\n"
    "\t\treturn 0;\n"
    "\t}\n"
    "\treturn m_memory_tracker.RangeWriteEpoch(vaddr, size);\n"
    "}\n")

# ---------------------------------------------------------------- textureCache.h / .cpp
P = R + "cache/textureCache.h"
sub(P, "\tvoid StampPendingDccFill();\n",
    "\tvoid StampPendingDccFill();\n"
    "\t// Track F, F16k2 (KYTY_DIAG_F5ID, RC3, ROADMAP s122 item 496(b)(3)): called at the end of DispatchDirect (its\n"
    "\t// F5IdCsHolder): a fill stamp TrackDccFill left and StampPendingDccFill has not taken (the dispatch returned before\n"
    "\t// it) counts stamp_late once; the stamp itself is unchanged. Nothing without DiagF5Id::On().\n"
    "\tvoid F5IdNoteStampLate();\n")
sub(P, "\tuint64_t                                          m_f5id_stamp_size    = 0;\n",
    "\tuint64_t                                          m_f5id_stamp_size    = 0;\n"
    "\tbool                                              m_f5id_stamp_late    = false; // F16k2: stamp_late counted\n")
P = R + "cache/textureCache.cpp"
sub(P, "\t\tif (DiagF5Id::On()) [[unlikely]] {\n"
       "\t\t\tDiagF5Id::NoteFill(address);\n"
       "\t\t\tm_f5id_stamp_address = address;\n"
       "\t\t\tm_f5id_stamp_size    = size;\n"
       "\t\t}\n",
    "\t\tif (DiagF5Id::On()) [[unlikely]] {\n"
    "\t\t\tDiagF5Id::NoteFill(address);\n"
    "\t\t\t// Track F, F16k2 (RC3): the stamp of an earlier fill was not taken by its dispatch and not counted at its end.\n"
    "\t\t\tif (m_f5id_stamp_address != 0 && !m_f5id_stamp_late) {\n"
    "\t\t\t\tDiagF5Id::NoteStampLate();\n"
    "\t\t\t}\n"
    "\t\t\tm_f5id_stamp_address = address;\n"
    "\t\t\tm_f5id_stamp_size    = size;\n"
    "\t\t\tm_f5id_stamp_late    = false;\n"
    "\t\t}\n")
sub(P, "\t\tDiagF5Id::NoteFillSeq(m_f5id_stamp_address,\n"
       "\t\t                      m_buffer_cache.LastGpuWriteSeq(m_f5id_stamp_address, m_f5id_stamp_size, false));\n"
       "\t\tm_f5id_stamp_address = 0;\n"
       "\t\tm_f5id_stamp_size    = 0;\n"
       "\t}\n",
    "\t\t// Track F, F16k2 (RC2): with the CPU write epoch of the fill range at this stamp (cpu_mod).\n"
    "\t\tDiagF5Id::NoteFillSeq(m_f5id_stamp_address,\n"
    "\t\t                      m_buffer_cache.LastGpuWriteSeq(m_f5id_stamp_address, m_f5id_stamp_size, false),\n"
    "\t\t                      m_buffer_cache.F5IdRangeWriteEpoch(m_f5id_stamp_address, m_f5id_stamp_size));\n"
    "\t\tm_f5id_stamp_address = 0;\n"
    "\t\tm_f5id_stamp_size    = 0;\n"
    "\t\tm_f5id_stamp_late    = false;\n"
    "\t}\n")
sub(P, "\tm_fill_stamp_address = 0;\n\tm_fill_stamp_size    = 0;\n}\n\nbool TextureCache::PendingDccFillStale(",
    "\tm_fill_stamp_address = 0;\n\tm_fill_stamp_size    = 0;\n}\n"
    "\n"
    "void TextureCache::F5IdNoteStampLate() {\n"
    "\tif (!DiagF5Id::On()) {\n"
    "\t\treturn;\n"
    "\t}\n"
    "\tstd::scoped_lock lock {m_lock};\n"
    "\tif (m_f5id_stamp_address != 0 && !m_f5id_stamp_late) {\n"
    "\t\tm_f5id_stamp_late = true;\n"
    "\t\tDiagF5Id::NoteStampLate();\n"
    "\t}\n"
    "}\n"
    "\nbool TextureCache::PendingDccFillStale(")
sub(P, "\t\tif (cpu_written) {\n\t\t\tf5_probe->exact_stale = true;\n\t\t} else {\n",
    "\t\tif (cpu_written) {\n\t\t\tf5_probe->exact_stale = true;\n"
    "\t\t\tf5_probe->cpu         = true; // Track F, F16k2 (RC4): why=cpu\n\t\t} else {\n")
sub(P, "\t\t\t\tcase DiagF5::CmuFix::ExactStale: DiagF5::Add(DiagF5::Counter::F5CmuExactStale); break;\n",
    "\t\t\t\tcase DiagF5::CmuFix::ExactStale:\n"
    "\t\t\t\t\tDiagF5::Add(DiagF5::Counter::F5CmuExactStale);\n"
    "\t\t\t\t\tif (m_probe.cpu) {\n"
    "\t\t\t\t\t\tDiagF5::Add(DiagF5::Counter::F5CmuExactCpu); // Track F, F16k2 (RC4)\n"
    "\t\t\t\t\t}\n"
    "\t\t\t\t\tbreak;\n")
sub(P, "\t\t\tm_out->why = fix == DiagF5::CmuFix::Kept\n"
       "\t\t\t                 ? (m_why != DiagF5::CmuWhy::None ? m_why : DiagF5::CmuWhy::NoLayer)\n"
       "\t\t\t                 : DiagF5::CmuWhy::None;\n",
    "\t\t\t// Track F, F16k2 (RC4): an exact_stale decision set by a CPU-modified page says why=cpu.\n"
    "\t\t\tm_out->why = fix == DiagF5::CmuFix::Kept\n"
    "\t\t\t                 ? (m_why != DiagF5::CmuWhy::None ? m_why : DiagF5::CmuWhy::NoLayer)\n"
    "\t\t\t             : fix == DiagF5::CmuFix::ExactStale && m_probe.cpu ? DiagF5::CmuWhy::Cpu\n"
    "\t\t\t                                                                 : DiagF5::CmuWhy::None;\n")

# ---------------------------------------------------------------- descriptors.cpp
P = R + "pipeline/descriptors.cpp"
sub(P, "\t\tconst auto exact = buffers.LastGpuWriteSeqExact(e.dcc, e.dcc_size, since);\n"
       "\t\te.wr_after       = exact.seq != 0    ? DiagF5Id::WrAfter::Exact\n"
       "\t\t                   : exact.fallback ? DiagF5Id::WrAfter::Fallback\n"
       "\t\t                                    : DiagF5Id::WrAfter::None;\n"
       "\t\te.cpu_mod        = buffers.IsRegionCpuModified(e.dcc, e.dcc_size) ? 1 : 0;\n"
       "\t}\n",
    "\t\tconst auto exact = buffers.LastGpuWriteSeqExact(e.dcc, e.dcc_size, since);\n"
    "\t\t// Track F, F16k2 (RC1, ROADMAP s122 item 496(b)(1)): no crossing bucket write after `since`, but a GPU write larger\n"
    "\t\t// than 16 MB (no bucket, no ring, any address) is newer than `since` - wr_after=large.\n"
    "\t\tconst bool large = exact.seq == 0 && buffers.LargeGpuWriteSeq() > since;\n"
    "\t\te.wr_after       = exact.seq != 0    ? DiagF5Id::WrAfter::Exact\n"
    "\t\t                   : large          ? DiagF5Id::WrAfter::Large\n"
    "\t\t                   : exact.fallback ? DiagF5Id::WrAfter::Fallback\n"
    "\t\t                                    : DiagF5Id::WrAfter::None;\n"
    "\t\t// Track F, F16k2 (RC2, item 496(b)(2)): CPU-modified now, or the CPU write epoch of the range moved since the epoch\n"
    "\t\t// stamped with the last fill at `dcc`; no fill stamped there, or an untracked range at the stamp - 1 (the tracker\n"
    "\t\t// has no epoch of the process start: a region is created lazily with every page CPU-dirty).\n"
    "\t\tuint64_t   fill_epoch = 0;\n"
    "\t\tconst bool seen       = DiagF5Id::FillCpuEpoch(e.dcc, &fill_epoch);\n"
    "\t\tconst bool cpu_now    = buffers.IsRegionCpuModified(e.dcc, e.dcc_size);\n"
    "\t\te.cpu_mod = cpu_now || !seen || fill_epoch == 0 || buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch\n"
    "\t\t                ? 1\n"
    "\t\t                : 0;\n"
    "\t}\n")
sub(P, "\t\t\t\t                ? DiagF5::Counter::CmaskFceLayout\n"
       "\t\t\t\t                : DiagF5::Counter::CmaskFceNoFill);\n"
       "\t\t\t}\n"
       "\t\t\tcontinue;\n"
       "\t\t}\n",
    "\t\t\t\t                ? DiagF5::Counter::CmaskFceLayout\n"
    "\t\t\t\t                : DiagF5::Counter::CmaskFceNoFill);\n"
    "\t\t\t}\n"
    "\t\t\t// Track F, F16k2 (RC5, ROADMAP s122 item 496(b)(5)): a decision of the FCE acquisition above without a B42 hit (no\n"
    "\t\t\t// cmask_fce line): the target carried CMASK metadata already (FixB42Probe answered None) or a drawn fill; printed\n"
    "\t\t\t// when the decision is not off / fresh, under its own limit of 64.\n"
    "\t\t\tif (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&\n"
    "\t\t\t    f5_cmu.fix != DiagF5::CmuFix::Fresh) [[unlikely]] {\n"
    "\t\t\t\t(void)DiagF5::NoteCmuNoHit({.present = DiagF5::Present(),\n"
    "\t\t\t\t                            .gpu     = GpuTimeProfiler::Frame(),\n"
    "\t\t\t\t                            .image   = color.desc.info.data.address,\n"
    "\t\t\t\t                            .cmask   = rt.cmask.addr,\n"
    "\t\t\t\t                            .width   = color.desc.info.extent.width,\n"
    "\t\t\t\t                            .height  = color.desc.info.extent.height,\n"
    "\t\t\t\t                            .applied = false,\n"
    "\t\t\t\t                            .event   = f5_cmu},\n"
    "\t\t\t\t                           b42.kind == FixB42Kind::Drawn);\n"
    "\t\t\t}\n"
    "\t\t\tcontinue;\n"
    "\t\t}\n")

# ---------------------------------------------------------------- renderCompute.cpp
P = R + "renderCompute.cpp"
sub(P, "\t~F5IdCsHolder() {\n"
       "\t\tif (m_d) [[unlikely]] {\n"
       "\t\t\tDiagF5Id::Emit(*m_d, m_refusals);\n"
       "\t\t}\n"
       "\t}\n",
    "\t~F5IdCsHolder() {\n"
    "\t\tif (m_d) [[unlikely]] {\n"
    "\t\t\tDiagF5Id::Emit(*m_d, m_refusals);\n"
    "\t\t\t// Track F, F16k2 (RC3, ROADMAP s122 item 496(b)(3)): the end of DispatchDirect - a fill stamp this dispatch left\n"
    "\t\t\t// untaken (a return before StampPendingDccFill) counts stamp_late (m_lock after the render mutex, as the stamp).\n"
    "\t\t\tm_cache->F5IdNoteStampLate();\n"
    "\t\t}\n"
    "\t}\n")
sub(P, "\tvoid Arm(const ShaderComputeInputInfo& input) {\n\t\tm_d.emplace();\n",
    "\tvoid Arm(const ShaderComputeInputInfo& input, TextureCache& cache) {\n\t\tm_cache = &cache;\n\t\tm_d.emplace();\n")
sub(P, "\tconst DiagF5::CsRefusals&           m_refusals;\n\tstd::optional<DiagF5Id::CsDispatch> m_d;\n};\n",
    "\tconst DiagF5::CsRefusals&           m_refusals;\n\tstd::optional<DiagF5Id::CsDispatch> m_d;\n"
    "\tTextureCache*                       m_cache = nullptr; // Track F, F16k2: set by Arm\n};\n")
sub(P, "\t\tf5id.Arm(input_info);\n", "\t\tf5id.Arm(input_info, m_context.GetTextureCache());\n")

for path, text in FILES.items():
    norm = path.replace("\\", "/")
    if any(s in norm for s in SIGNATURE):
        raise SystemExit("signature set file touched: " + path)
    open(path, "wb").write(text.encode("utf-8"))
    print("patched", path[len(ROOT):])
print("P_SRC2 OK")

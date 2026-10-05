"""Track F, F16o (HPP-595, ROADMAP s122 item 504(e)(1)-(6)): KYTY_FIX_F26 and the cmask_fce line limit 1024.

    python p_src_f16o.py <repo root>

Every anchor is a run of whole lines and must occur exactly once (else nothing is written). CRLF files: the CR are
removed before the search and put back on write; files written with write_bytes. Refuses to touch the translation
signature set (CMakeLists.txt, src/graphics/shader/**, shaderTranslationCache.cpp, gpu_format.h, gpu_defs.h,
imageInfo.h).
"""
import os
import sys

ROOT = sys.argv[1].rstrip("/") + "/"
R = "src/graphics/host_gpu/renderer/"
FORBIDDEN = ("CMakeLists.txt", "src/graphics/shader/", "shaderTranslationCache.cpp", "gpu_format.h", "gpu_defs.h",
             "imageInfo.h")

EDITS = []


def edit(path, old, new):
    EDITS.append((path, old, new))


# ---------------------------------------------------------------- diagF5.h
H = R + "diagF5.h"
edit(H,
     "// counters). The new counter names are the last rows of the table.\n",
     "// counters). The new counter names are the last rows of the table.\n"
     "// Track F, F16o (HPP-595, ROADMAP s122 item 504(e)): KYTY_FIX_F26 - default 0, read once: the exact check decides the\n"
     "// stale question of a pending DCC fill at PrepareDccClear and AdoptPendingDccForTexture (row F26); the FCE acquisition and\n"
     "// every other PrepareCmaskClear do not read it. Its counters f26_* and the event line DiagF5Ev dcc_stale (KYTY_DIAG_F5).\n")
edit(H,
     "\tF5CmuExactCpu,\n"
     "\tCount\n",
     "\tF5CmuExactCpu,\n"
     "\t// Track F, F16o (item 504(e)(4)): KYTY_FIX_F26 at PrepareDccClear / AdoptPendingDccForTexture, where the bucket check\n"
     "\t// said stale - kept (the exact check did not; kept_applied - and the same call applied the fill: >= 1 layer cleared at\n"
     "\t// prepare, a non-zero clear mask adopted at adopt; kept_applied <= kept), stale by the exact check too, the ring could\n"
     "\t// not answer (fallback). With KYTY_DIAG_F5ID: f26_kept = dcc_stale_bucket_only, f26_fallback = dcc_stale_fallback.\n"
     "\tF26Kept,\n"
     "\tF26KeptApplied,\n"
     "\tF26ExactStale,\n"
     "\tF26Fallback,\n"
     "\tCount\n")
edit(H,
     "// BufferCache writes its exact write journal (the ring of item 492(v)(3)) while this holds: FixCmuOn() or\n"
     "// DiagF5Id::On(). Both are read once, so the journal holds every write since the process start or none.\n",
     "// BufferCache writes its exact write journal (the ring of item 492(v)(3)) while this holds: FixCmuOn(), FixF26On()\n"
     "// (Track F, F16o) or DiagF5Id::On(). All are read once, so the journal holds every write since the process start or\n"
     "// none.\n")
edit(H,
     "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu };\n",
     "// Track F, F16o (item 504(e)(3)): Levels - PrepareDccClear's return on an image with more than one level (the line\n"
     "// dcc_stale only).\n"
     "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu, Levels };\n")
edit(H,
     "// The probe of TextureCache::PendingDccFillStale (nullptr = the old call). In: `exact_decides` - the exact answer is\n"
     "// the answer (KYTY_FIX_F5CMU at the FCE acquisition). Out, written only when the old check reached its comparison:\n",
     "// The probe of TextureCache::PendingDccFillStale (nullptr = the old call). In: `exact_decides` - the exact answer is\n"
     "// the answer (KYTY_FIX_F5CMU at the FCE acquisition; Track F, F16o: KYTY_FIX_F26 at PrepareDccClear and\n"
     "// AdoptPendingDccForTexture). Out, written only when the old check reached its comparison:\n")
edit(H,
     "// [why=<..>]\"; printed for the first 64 events (k = 1..64), counted after (the hits are cmask_fce_b42 +\n"
     "// cmask_fce_unapplied).\n",
     "// [why=<..>]\"; printed for the first 1024 events (k = 1..1024; Track F, F16o, item 504(e)(5): was 64), counted after\n"
     "// (the hits are cmask_fce_b42 + cmask_fce_unapplied).\n")
edit(H,
     "bool                      NoteCmuNoHit(const CmuEventLine& line, bool drawn);\n",
     "bool                      NoteCmuNoHit(const CmuEventLine& line, bool drawn);\n"
     "\n"
     "// ---- Track F, F16o (HPP-595, ROADMAP s122 item 504(e)): KYTY_FIX_F26.\n"
     "// The knob (default 0, read once: unset or \"\" = OFF, otherwise Common::EnvValueOn).\n"
     "[[nodiscard]] bool FixF26On();\n"
     "// \"FixF26: mode=1\" once per process when FixF26On() (device creation); true when this call printed it.\n"
     "bool LogFixF26Mode();\n"
     "// The event line (item 504(e)(3)), KYTY_DIAG_F5=1, one per decision of PrepareDccClear / AdoptPendingDccForTexture\n"
     "// where the bucket check said stale: \"DiagF5Ev: dcc_stale site=<prepare|adopt> n=<k> present=<n> gpu=<n> image=0x...\n"
     "// dcc=0x... extent=<w>x<h> exact=<stale|fresh|fallback|na> fix=<off|exact_stale|kept|kept_applied|fallback>\n"
     "// [why=<..>]\"; `exact` - the ring's answer (na: the ring is not written); `fix` - off: KYTY_FIX_F26 is 0; kept: kept\n"
     "// and not applied in the same call (`why`); kept_applied: kept and applied in the same call; `present` - as cmask_fce\n"
     "// (Present()); printed for the first 256 (k = 1..256), counted after.\n"
     "enum class DccSite : uint8_t { Prepare, Adopt };\n"
     "enum class DccExact : uint8_t { Na, Stale, Fresh, Fallback };\n"
     "[[nodiscard]] const char* DccSiteName(DccSite site);\n"
     "[[nodiscard]] const char* DccExactName(DccExact exact);\n"
     "struct DccStaleLine {\n"
     "\tDccSite  site    = DccSite::Prepare;\n"
     "\tuint32_t present = 0;\n"
     "\tuint32_t gpu     = 0;\n"
     "\tuint64_t image   = 0;\n"
     "\tuint64_t dcc     = 0;\n"
     "\tuint32_t width   = 0;\n"
     "\tuint32_t height  = 0;\n"
     "\tDccExact exact   = DccExact::Na;\n"
     "\tCmuEvent event;\n"
     "};\n"
     "[[nodiscard]] std::string FormatDccStale(uint64_t n, const DccStaleLine& line);\n"
     "bool                      NoteDccStale(const DccStaleLine& line);\n")

# ---------------------------------------------------------------- diagF5.cpp
C = R + "diagF5.cpp"
edit(C,
     "    \"f5cmu_exact_cpu\",\n"
     "};\n",
     "    \"f5cmu_exact_cpu\",\n"
     "    \"f26_kept\",\n"
     "    \"f26_kept_applied\",\n"
     "    \"f26_exact_stale\",\n"
     "    \"f26_fallback\",\n"
     "};\n")
edit(C,
     "\tEmitLine(\"FixF5Cmu: mode=1\");\n"
     "\treturn true;\n"
     "}\n"
     "\n"
     "bool ExactRingOn() {\n"
     "\tstatic const bool on = FixCmuOn() || DiagF5Id::On();\n"
     "\treturn on;\n"
     "}\n",
     "\tEmitLine(\"FixF5Cmu: mode=1\");\n"
     "\treturn true;\n"
     "}\n"
     "\n"
     "// ---- Track F, F16o (HPP-595, ROADMAP s122 item 504(e)(1)): KYTY_FIX_F26.\n"
     "bool FixF26On() {\n"
     "\tstatic const bool on = Common::EnvValueOn(std::getenv(\"KYTY_FIX_F26\"));\n"
     "\treturn on;\n"
     "}\n"
     "\n"
     "bool LogFixF26Mode() {\n"
     "\tstatic std::atomic<bool> logged {false};\n"
     "\tif (!FixF26On() || logged.exchange(true, std::memory_order_relaxed)) {\n"
     "\t\treturn false;\n"
     "\t}\n"
     "\tEmitLine(\"FixF26: mode=1\");\n"
     "\treturn true;\n"
     "}\n"
     "\n"
     "bool ExactRingOn() {\n"
     "\tstatic const bool on = FixCmuOn() || FixF26On() || DiagF5Id::On(); // Track F, F16o: KYTY_FIX_F26 too\n"
     "\treturn on;\n"
     "}\n")
edit(C,
     "\t\tcase CmuWhy::Cpu: return \"cpu\";\n",
     "\t\tcase CmuWhy::Cpu: return \"cpu\";\n"
     "\t\tcase CmuWhy::Levels: return \"levels\"; // Track F, F16o\n")
edit(C,
     "std::atomic<uint64_t> g_cmu_nohit_events {0}; // Track F, F16k2 (RC5): the lines cmask_fce_nohit\n",
     "std::atomic<uint64_t> g_cmu_nohit_events {0}; // Track F, F16k2 (RC5): the lines cmask_fce_nohit\n"
     "std::atomic<uint64_t> g_dcc_stale_events {0}; // Track F, F16o (item 504(e)(3)): the lines dcc_stale\n")
edit(C,
     "\tconst auto n = g_cmu_events.fetch_add(1, std::memory_order_relaxed) + 1;\n"
     "\tif (n > 64) {\n",
     "\tconst auto n = g_cmu_events.fetch_add(1, std::memory_order_relaxed) + 1;\n"
     "\tif (n > 1024) { // Track F, F16o (item 504(e)(5)): was 64; output of the measurement only\n")
edit(C,
     "\tEmitLine(FormatCmuNoHit(n, line, drawn));\n"
     "\treturn true;\n"
     "}\n",
     "\tEmitLine(FormatCmuNoHit(n, line, drawn));\n"
     "\treturn true;\n"
     "}\n"
     "\n"
     "// ---- Track F, F16o (HPP-595, ROADMAP s122 item 504(e)(3)): the line dcc_stale.\n"
     "const char* DccSiteName(DccSite site) {\n"
     "\treturn site == DccSite::Adopt ? \"adopt\" : \"prepare\";\n"
     "}\n"
     "\n"
     "const char* DccExactName(DccExact exact) {\n"
     "\tswitch (exact) {\n"
     "\t\tcase DccExact::Na: return \"na\";\n"
     "\t\tcase DccExact::Stale: return \"stale\";\n"
     "\t\tcase DccExact::Fresh: return \"fresh\";\n"
     "\t\tcase DccExact::Fallback: return \"fallback\";\n"
     "\t}\n"
     "\treturn \"na\";\n"
     "}\n"
     "\n"
     "std::string FormatDccStale(uint64_t n, const DccStaleLine& line) {\n"
     "\tauto text = fmt::format(\"DiagF5Ev: dcc_stale site={} n={} present={} gpu={} image=0x{:016x} dcc=0x{:016x} \"\n"
     "\t                        \"extent={}x{} exact={} fix={}\",\n"
     "\t                        DccSiteName(line.site), n, line.present, line.gpu, line.image, line.dcc, line.width,\n"
     "\t                        line.height, DccExactName(line.exact), CmuFixName(line.event.fix));\n"
     "\tif (line.event.why != CmuWhy::None) {\n"
     "\t\ttext += fmt::format(\" why={}\", CmuWhyName(line.event.why));\n"
     "\t}\n"
     "\treturn text;\n"
     "}\n"
     "\n"
     "bool NoteDccStale(const DccStaleLine& line) {\n"
     "\tconst auto n = g_dcc_stale_events.fetch_add(1, std::memory_order_relaxed) + 1;\n"
     "\tif (n > 256) {\n"
     "\t\treturn false;\n"
     "\t}\n"
     "\tEmitLine(FormatDccStale(n, line));\n"
     "\treturn true;\n"
     "}\n")

# ---------------------------------------------------------------- textureCache.h
TH = R + "cache/textureCache.h"
edit(TH,
     "\t// changes only with f5_probe->exact_decides (KYTY_FIX_F5CMU at the FCE acquisition).\n",
     "\t// changes only with f5_probe->exact_decides (KYTY_FIX_F5CMU at the FCE acquisition; Track F, F16o: KYTY_FIX_F26 at\n"
     "\t// PrepareDccClear and AdoptPendingDccForTexture).\n")

# ---------------------------------------------------------------- textureCache.cpp
T = R + "cache/textureCache.cpp"
edit(T,
     "\tbool               m_cleared = false;\n"
     "};\n"
     "\n"
     "} // namespace\n"
     "\n"
     "void TextureCache::PrepareDccClear(ImageId id, const ImageDesc& desc) {\n"
     "\tif (desc.info.metadata.kind != ImageMetadataKind::Dcc) {\n"
     "\t\treturn;\n"
     "\t}\n",
     "\tbool               m_cleared = false;\n"
     "};\n"
     "\n"
     "// Track F, F16o (KYTY_FIX_F26, ROADMAP s122 item 504(e)(2)-(4)): one PendingDccFillStale decision of PrepareDccClear or\n"
     "// AdoptPendingDccForTexture. Arm() - the probe of the call: passed when the ring is written and KYTY_DIAG_F5 or\n"
     "// KYTY_FIX_F26 is on (KYTY_DIAG_F5ID implies both), `exact_decides` = KYTY_FIX_F26; otherwise nullptr (the old call).\n"
     "// Decided() - after the call: with KYTY_DIAG_F5 and a stale bucket answer (the probe's; without a probe the answer\n"
     "// itself, which is then the bucket one) the decision is reported when the scope leaves (every later return of the\n"
     "// site): the counters f26_* (with the knob) and the line DiagF5Ev dcc_stale. Why() / Applied() - whether a kept fill was\n"
     "// applied in the same call. Neither knob: Arm() returns nullptr and nothing is reported. Not called: inert.\n"
     "class F26Scope {\n"
     "public:\n"
     "\texplicit F26Scope(DiagF5::DccSite site): m_site(site) {}\n"
     "\t~F26Scope() {\n"
     "\t\tif (m_report) [[unlikely]] {\n"
     "\t\t\tReport();\n"
     "\t\t}\n"
     "\t}\n"
     "\tF26Scope(const F26Scope&)            = delete;\n"
     "\tF26Scope& operator=(const F26Scope&) = delete;\n"
     "\n"
     "\t[[nodiscard]] DiagF5::StaleProbe* Arm() {\n"
     "\t\tm_fix                 = DiagF5::FixF26On();\n"
     "\t\tm_probe_on            = DiagF5::ExactRingOn() && (DiagF5::On() || m_fix);\n"
     "\t\tm_probe.exact_decides = m_fix;\n"
     "\t\treturn m_probe_on ? &m_probe : nullptr;\n"
     "\t}\n"
     "\tvoid Decided(bool stale, uint64_t image, uint64_t dcc, uint32_t width, uint32_t height) {\n"
     "\t\tif (DiagF5::On() && (m_probe_on ? m_probe.bucket_stale : stale)) [[unlikely]] {\n"
     "\t\t\tm_report = true;\n"
     "\t\t\tm_line   = {.site    = m_site,\n"
     "\t\t\t            .present = DiagF5::Present(),\n"
     "\t\t\t            .gpu     = GpuTimeProfiler::Frame(),\n"
     "\t\t\t            .image   = image,\n"
     "\t\t\t            .dcc     = dcc,\n"
     "\t\t\t            .width   = width,\n"
     "\t\t\t            .height  = height};\n"
     "\t\t}\n"
     "\t}\n"
     "\t[[nodiscard]] const DiagF5::StaleProbe& Probe() const { return m_probe; }\n"
     "\t[[nodiscard]] bool                      Reported() const { return m_report; }\n"
     "\t// The return of a kept fill without applying it.\n"
     "\tvoid Why(DiagF5::CmuWhy why) { m_why = why; }\n"
     "\t// After the site applied (or not) a kept fill; `why_not` - when not applied and no Why() was given.\n"
     "\tvoid Applied(bool applied, DiagF5::CmuWhy why_not) {\n"
     "\t\tm_applied = applied;\n"
     "\t\tif (!applied && m_why == DiagF5::CmuWhy::None) {\n"
     "\t\t\tm_why = why_not;\n"
     "\t\t}\n"
     "\t}\n"
     "\n"
     "private:\n"
     "\tvoid Report() {\n"
     "\t\tusing F    = DiagF5::CmuFix;\n"
     "\t\tauto& e    = m_line.event;\n"
     "\t\te.fix      = !m_fix                 ? F::Off\n"
     "\t\t            : m_probe.exact_stale  ? F::ExactStale\n"
     "\t\t            : m_probe.fallback     ? F::Fallback\n"
     "\t\t            : m_applied            ? F::KeptApplied\n"
     "\t\t                                   : F::Kept;\n"
     "\t\tm_line.exact = !m_probe_on            ? DiagF5::DccExact::Na\n"
     "\t\t               : m_probe.exact_stale ? DiagF5::DccExact::Stale\n"
     "\t\t               : m_probe.fallback    ? DiagF5::DccExact::Fallback\n"
     "\t\t                                     : DiagF5::DccExact::Fresh;\n"
     "\t\te.why = e.fix == F::Kept ? (m_why != DiagF5::CmuWhy::None ? m_why : DiagF5::CmuWhy::NoLayer)\n"
     "\t\t        : m_probe.cpu    ? DiagF5::CmuWhy::Cpu\n"
     "\t\t                         : DiagF5::CmuWhy::None;\n"
     "\t\tif (m_fix) {\n"
     "\t\t\tswitch (e.fix) {\n"
     "\t\t\t\tcase F::Kept: DiagF5::Add(DiagF5::Counter::F26Kept); break;\n"
     "\t\t\t\tcase F::KeptApplied:\n"
     "\t\t\t\t\tDiagF5::Add(DiagF5::Counter::F26Kept);\n"
     "\t\t\t\t\tDiagF5::Add(DiagF5::Counter::F26KeptApplied);\n"
     "\t\t\t\t\tbreak;\n"
     "\t\t\t\tcase F::ExactStale: DiagF5::Add(DiagF5::Counter::F26ExactStale); break;\n"
     "\t\t\t\tcase F::Fallback: DiagF5::Add(DiagF5::Counter::F26Fallback); break;\n"
     "\t\t\t\tdefault: break;\n"
     "\t\t\t}\n"
     "\t\t}\n"
     "\t\t(void)DiagF5::NoteDccStale(m_line);\n"
     "\t}\n"
     "\n"
     "\tDiagF5::DccSite      m_site;\n"
     "\tbool                 m_fix      = false;\n"
     "\tbool                 m_probe_on = false;\n"
     "\tbool                 m_report   = false;\n"
     "\tbool                 m_applied  = false;\n"
     "\tDiagF5::CmuWhy       m_why      = DiagF5::CmuWhy::None;\n"
     "\tDiagF5::StaleProbe   m_probe {};\n"
     "\tDiagF5::DccStaleLine m_line {};\n"
     "};\n"
     "\n"
     "} // namespace\n"
     "\n"
     "void TextureCache::PrepareDccClear(ImageId id, const ImageDesc& desc) {\n"
     "\tif (desc.info.metadata.kind != ImageMetadataKind::Dcc) {\n"
     "\t\treturn;\n"
     "\t}\n"
     "\t// Track F, F16o (KYTY_FIX_F26, item 504(e)(2)-(3)): the decision of the PendingDcc branch below; reported at return.\n"
     "\tF26Scope f26 {DiagF5::DccSite::Prepare};\n")
edit(T,
     "\t\t// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(5), F26): the probe only counts - the decision is the old one.\n"
     "\t\tDiagF5::StaleProbe f5_probe {};\n"
     "\t\tconst bool         f5id = DiagF5Id::On();\n"
     "\t\tif (PendingDccFillStale(desc.info.metadata.range.address, metadata,\n"
     "\t\t                        image.info.data.address, f5id ? &f5_probe : nullptr)) {\n"
     "\t\t\tmetadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};\n",
     "\t\t// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(5), F26): the probe counts dcc_stale_*. Track F, F16o (KYTY_FIX_F26,\n"
     "\t\t// item 504(e)(2)): with the knob the exact answer decides - a kept fill stays and is cleared below.\n"
     "\t\tconst bool f5id     = DiagF5Id::On();\n"
     "\t\tconst bool f5_stale = PendingDccFillStale(desc.info.metadata.range.address, metadata,\n"
     "\t\t                                          image.info.data.address, f26.Arm());\n"
     "\t\tf26.Decided(f5_stale, image.info.data.address, desc.info.metadata.range.address, desc.info.extent.width,\n"
     "\t\t            desc.info.extent.height);\n"
     "\t\tif (f5_stale) {\n"
     "\t\t\tmetadata = MetaDataInfo {.type = MetaDataInfo::Type::Dcc};\n")
edit(T,
     "\t\t} else if (DiagF5::On()) [[unlikely]] {\n"
     "\t\t\tDiagF5::NoteDccFill(metadata.fill_value); // Track F, F16d: PendingDcc -> Dcc by the stored code (RC3)\n"
     "\t\t}\n"
     "\t\tif (f5id) [[unlikely]] {\n"
     "\t\t\tDiagF5::NoteDccStaleProbe(f5_probe);\n"
     "\t\t}\n"
     "\t\tmetadata.type = MetaDataInfo::Type::Dcc;\n",
     "\t\t} else if (DiagF5::On()) [[unlikely]] {\n"
     "\t\t\tDiagF5::NoteDccFill(metadata.fill_value); // Track F, F16d: PendingDcc -> Dcc by the stored code (RC3)\n"
     "\t\t}\n"
     "\t\tif (f5id) [[unlikely]] {\n"
     "\t\t\tDiagF5::NoteDccStaleProbe(f26.Probe());\n"
     "\t\t}\n"
     "\t\tmetadata.type = MetaDataInfo::Type::Dcc;\n")
edit(T,
     "\t\t\tDiagF5::Add(image.info.resources.levels != 1 ? DiagF5::Counter::DccRtSkipLevels\n"
     "\t\t\t                                             : DiagF5::Counter::DccRtSkipPartial);\n"
     "\t\t}\n"
     "\t\treturn;\n",
     "\t\t\tDiagF5::Add(image.info.resources.levels != 1 ? DiagF5::Counter::DccRtSkipLevels\n"
     "\t\t\t                                             : DiagF5::Counter::DccRtSkipPartial);\n"
     "\t\t}\n"
     "\t\tif (f26.Reported()) [[unlikely]] {\n"
     "\t\t\tf26.Why(metadata.clear_mask == 0                ? DiagF5::CmuWhy::Mask\n"
     "\t\t\t        : image.info.resources.levels != 1      ? DiagF5::CmuWhy::Levels\n"
     "\t\t\t        : desc.info.metadata.range.size == 0    ? DiagF5::CmuWhy::Range\n"
     "\t\t\t                                                : DiagF5::CmuWhy::Partial);\n"
     "\t\t}\n"
     "\t\treturn;\n")
edit(T,
     "\t\t\tDiagF5::Add(DiagF5::Counter::DccRtSkipDecode);\n"
     "\t\t}\n"
     "\t\treturn;\n",
     "\t\t\tDiagF5::Add(DiagF5::Counter::DccRtSkipDecode);\n"
     "\t\t}\n"
     "\t\tf26.Why(DiagF5::CmuWhy::Decode); // Track F, F16o\n"
     "\t\treturn;\n")
edit(T,
     "\t\t\tDiagF5::Add(DiagF5::Counter::DccRtSkipLayers);\n"
     "\t\t}\n"
     "\t\treturn;\n",
     "\t\t\tDiagF5::Add(DiagF5::Counter::DccRtSkipLayers);\n"
     "\t\t}\n"
     "\t\tf26.Why(DiagF5::CmuWhy::Layers); // Track F, F16o\n"
     "\t\treturn;\n")
edit(T,
     "\t// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)-(3)): a clear ran here - a stale mark, `cleared` of an open record.\n"
     "\tif (DiagF5Id::On() && metadata.clear_mask != f5id_mask0) [[unlikely]] {\n"
     "\t\tDiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::DccRt, desc.info.metadata.range.address,\n",
     "\t// Track F, F16o (item 504(e)(3)): a kept fill is kept_applied when this call cleared >= 1 layer.\n"
     "\tf26.Applied(metadata.clear_mask != f5id_mask0, DiagF5::CmuWhy::NoLayer);\n"
     "\t// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(2)-(3)): a clear ran here - a stale mark, `cleared` of an open record.\n"
     "\tif (DiagF5Id::On() && metadata.clear_mask != f5id_mask0) [[unlikely]] {\n"
     "\t\tDiagF5Id::NoteClearApplied(DiagF5Id::ApplySite::DccRt, desc.info.metadata.range.address,\n")
edit(T,
     "\t// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(5), F26): the probe only counts - the decision is the old one.\n"
     "\tDiagF5::StaleProbe f5_probe {};\n"
     "\tconst bool         f5id     = DiagF5Id::On();\n"
     "\tconst bool         f5_stale = PendingDccFillStale(metadata_address, found->second, image->info.data.address,\n"
     "\t                                                  f5id ? &f5_probe : nullptr);\n"
     "\tif (f5id) [[unlikely]] {\n"
     "\t\tDiagF5::NoteDccStaleProbe(f5_probe);\n"
     "\t}\n",
     "\t// Track F, F16k (KYTY_DIAG_F5ID, item 492(g)(5), F26): the probe counts dcc_stale_*. Track F, F16o (KYTY_FIX_F26,\n"
     "\t// item 504(e)(2)): with the knob the exact answer decides - a kept fill is adopted below. The scope reports when it\n"
     "\t// leaves (each return below, m_lock still held: it is declared after the lock).\n"
     "\tF26Scope   f26 {DiagF5::DccSite::Adopt};\n"
     "\tconst bool f5id     = DiagF5Id::On();\n"
     "\tconst bool f5_stale = PendingDccFillStale(metadata_address, found->second, image->info.data.address, f26.Arm());\n"
     "\tf26.Decided(f5_stale, image->info.data.address, metadata_address, image->info.extent.width,\n"
     "\t            image->info.extent.height);\n"
     "\tif (f5id) [[unlikely]] {\n"
     "\t\tDiagF5::NoteDccStaleProbe(f26.Probe());\n"
     "\t}\n")
edit(T,
     "\tfound->second.type                 = MetaDataInfo::Type::Dcc;\n",
     "\tfound->second.type                 = MetaDataInfo::Type::Dcc;\n"
     "\t// Track F, F16o (item 504(e)(3)): a kept fill is kept_applied when it is adopted with a clear (a non-zero mask).\n"
     "\tf26.Applied(found->second.clear_mask != 0, DiagF5::CmuWhy::Mask);\n")

# ---------------------------------------------------------------- vulkanWindow.cpp
V = "src/graphics/presentation/window/vulkanWindow.cpp"
edit(V,
     "\t(void)DiagF5::LogFixCmuMode();\n",
     "\t(void)DiagF5::LogFixCmuMode();\n"
     "\t(void)DiagF5::LogFixF26Mode(); // Track F, F16o (item 504(e)(1)): \"FixF26: mode=1\" once, same point\n")


def main():
    files = {}
    for path, old, new in EDITS:
        if any(f in path for f in FORBIDDEN):
            print("REFUSED: signature set file", path)
            return 2
        if path not in files:
            raw = open(ROOT + path, "rb").read()
            crlf = b"\r\n" in raw
            files[path] = [raw.decode("utf-8").replace("\r\n", "\n"), crlf]
        text = files[path][0]
        n = text.count(old)
        if n != 1:
            print("ANCHOR COUNT %d in %s: %r" % (n, path, old[:120]))
            return 1
        files[path][0] = text.replace(old, new)
    for path, (text, crlf) in files.items():
        data = text.replace("\n", "\r\n") if crlf else text
        open(ROOT + path, "wb").write(data.encode("utf-8"))
        print("patched", path, "crlf" if crlf else "lf")
    print("EDITS", len(EDITS), "ALL OK")
    return 0


sys.exit(main())

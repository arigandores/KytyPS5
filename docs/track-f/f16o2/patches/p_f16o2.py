"""Track F, F16o2 (HPP-599, RC1 of F16p, ROADMAP s122 item 507(b)(1)-(6)): AdoptPendingDccForTexture's kept fill with a
clear is kept why=deferred; a one-shot mark on the image (TextureCache, under m_lock, event number n) is taken by
RenderExecutor::MaterializeDeferredDccClear, which reports the line dcc_stale_apply result=<cleared|declined> and counts
f26_kept_applied / f26_deferred_declined (new, last). Test site: D4 (0x40, cleared), D4e (0x20 without a slot, declined),
identities of item 507(b)(4), the line limit.

    python p_f16o2.py <repo root>

Every anchor is a run of whole lines and must occur exactly once (else nothing is written). CRLF files: the CR are
removed before the search and put back on write; files written with write_bytes. Refuses to touch the translation
signature set (CMakeLists.txt, src/graphics/shader/**, shaderTranslationCache.cpp, gpu_format.h, gpu_defs.h,
imageInfo.h).
"""
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
     "\t// said stale - kept (the exact check did not; kept_applied - and the same call applied the fill: >= 1 layer cleared at\n"
     "\t// prepare, a non-zero clear mask adopted at adopt; kept_applied <= kept), stale by the exact check too, the ring could\n",
     "\t// said stale - kept (the exact check did not; kept_applied - and the fill was applied: >= 1 layer cleared by the call\n"
     "\t// at prepare; at adopt (Track F, F16o2) >= 1 layer cleared by the MaterializeDeferredDccClear that took the deferred\n"
     "\t// mark; kept_applied <= kept), stale by the exact check too, the ring could\n")
edit(H,
     "\tF26ExactStale,\n"
     "\tF26Fallback,\n"
     "\tCount\n",
     "\tF26ExactStale,\n"
     "\tF26Fallback,\n"
     "\t// Track F, F16o2 (RC1 of F16p, item 507(b)(3)-(4)): a deferred clear of an adoption (fix=kept why=deferred) that\n"
     "\t// RenderExecutor::MaterializeDeferredDccClear took and did not clear (result=declined); one it cleared counts\n"
     "\t// f26_kept_applied. f26_kept_applied + f26_deferred_declined <= f26_kept.\n"
     "\tF26DeferredDeclined,\n"
     "\tCount\n")
edit(H,
     "// Track F, F16o (item 504(e)(3)): Levels - PrepareDccClear's return on an image with more than one level (the line\n"
     "// dcc_stale only).\n"
     "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu, Levels };\n",
     "// Track F, F16o (item 504(e)(3)): Levels - PrepareDccClear's return on an image with more than one level (the line\n"
     "// dcc_stale only). Track F, F16o2 (item 507(b)(1)): Deferred - AdoptPendingDccForTexture adopted the fill with a clear\n"
     "// the call does not apply (the line dcc_stale only; the outcome - the line dcc_stale_apply of the same n).\n"
     "enum class CmuWhy : uint8_t { None, Value, Mask, Range, Partial, Decode, Layers, NoLayer, Cpu, Levels, Deferred };\n")
edit(H,
     "[[nodiscard]] std::string FormatDccStale(uint64_t n, const DccStaleLine& line);\n"
     "bool                      NoteDccStale(const DccStaleLine& line);\n",
     "[[nodiscard]] std::string FormatDccStale(uint64_t n, const DccStaleLine& line);\n"
     "// Track F, F16o2: `n_out` (optional) receives the event number k (past the limit too).\n"
     "bool                      NoteDccStale(const DccStaleLine& line, uint64_t* n_out = nullptr);\n"
     "\n"
     "// ---- Track F, F16o2 (HPP-599, RC1 of F16p, ROADMAP s122 item 507(b)): the deferred clear of an adoption (the\n"
     "// one-shot mark the event fix=kept why=deferred of AdoptPendingDccForTexture leaves on the image -\n"
     "// TextureCache::F26Deferred, under m_lock).\n"
     "// The outcome line of RenderExecutor::MaterializeDeferredDccClear on an image with the mark (the call takes the mark\n"
     "// whatever its outcome), KYTY_DIAG_F5=1: \"DiagF5Ev: dcc_stale_apply n=<n> present=<n> gpu=<n> image=0x... dcc=0x...\n"
     "// result=<cleared|declined> layers=0x<mask>\"; n, image, dcc - of the adopt's dcc_stale line; present / gpu - at the\n"
     "// outcome (sources as dcc_stale); cleared - >= 1 layer cleared; declined - any return without a clear; layers - the\n"
     "// pending layer mask the call read (0 when it returned before reading it). The limit of dcc_stale: printed when\n"
     "// n <= 256 (the adopt's own line was printed). Counting (f26_kept_applied / f26_deferred_declined) is the caller's.\n"
     "struct DccApplyLine {\n"
     "\tuint64_t n       = 0;\n"
     "\tuint32_t present = 0;\n"
     "\tuint32_t gpu     = 0;\n"
     "\tuint64_t image   = 0;\n"
     "\tuint64_t dcc     = 0;\n"
     "\tbool     cleared = false;\n"
     "\tuint32_t layers  = 0;\n"
     "};\n"
     "[[nodiscard]] std::string FormatDccStaleApply(const DccApplyLine& line);\n"
     "bool                      NoteDccStaleApply(const DccApplyLine& line);\n")

# ---------------------------------------------------------------- diagF5.cpp
D = R + "diagF5.cpp"
edit(D,
     "    \"f26_fallback\",\n"
     "};\n",
     "    \"f26_fallback\",\n"
     "    \"f26_deferred_declined\", // Track F, F16o2 (item 507(b)(3))\n"
     "};\n")
edit(D,
     "\t\tcase CmuWhy::Levels: return \"levels\"; // Track F, F16o\n",
     "\t\tcase CmuWhy::Levels: return \"levels\"; // Track F, F16o\n"
     "\t\tcase CmuWhy::Deferred: return \"deferred\"; // Track F, F16o2\n")
edit(D,
     "bool NoteDccStale(const DccStaleLine& line) {\n"
     "\tconst auto n = g_dcc_stale_events.fetch_add(1, std::memory_order_relaxed) + 1;\n"
     "\tif (n > 256) {\n",
     "bool NoteDccStale(const DccStaleLine& line, uint64_t* n_out) {\n"
     "\tconst auto n = g_dcc_stale_events.fetch_add(1, std::memory_order_relaxed) + 1;\n"
     "\tif (n_out != nullptr) {\n"
     "\t\t*n_out = n; // Track F, F16o2: the deferred mark of an adoption carries it\n"
     "\t}\n"
     "\tif (n > 256) {\n")
edit(D,
     "std::vector<std::string> RecentLines() {\n",
     "// ---- Track F, F16o2 (HPP-599, ROADMAP s122 item 507(b)(3)): the line dcc_stale_apply.\n"
     "std::string FormatDccStaleApply(const DccApplyLine& line) {\n"
     "\treturn fmt::format(\"DiagF5Ev: dcc_stale_apply n={} present={} gpu={} image=0x{:016x} dcc=0x{:016x} result={} \"\n"
     "\t                   \"layers=0x{:08x}\",\n"
     "\t                   line.n, line.present, line.gpu, line.image, line.dcc, line.cleared ? \"cleared\" : \"declined\",\n"
     "\t                   line.layers);\n"
     "}\n"
     "\n"
     "bool NoteDccStaleApply(const DccApplyLine& line) {\n"
     "\tif (line.n == 0 || line.n > 256) { // the limit of dcc_stale: only when the adopt's line n was printed\n"
     "\t\treturn false;\n"
     "\t}\n"
     "\tEmitLine(FormatDccStaleApply(line));\n"
     "\treturn true;\n"
     "}\n"
     "\n"
     "std::vector<std::string> RecentLines() {\n")

# ---------------------------------------------------------------- textureCache.h
TH = R + "cache/textureCache.h"
edit(TH,
     "\t[[nodiscard]] bool AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address,\n"
     "\t                                             DiagF5Id::DccMiss* f5id_miss = nullptr);\n",
     "\t[[nodiscard]] bool AdoptPendingDccForTexture(ImageId id, uint64_t metadata_address,\n"
     "\t                                             DiagF5Id::DccMiss* f5id_miss = nullptr);\n"
     "\t// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(2)-(3)): the one-shot deferred mark of an\n"
     "\t// image. NoteF26DeferredLocked - caller holds m_lock (the F26Scope of AdoptPendingDccForTexture, event fix=kept\n"
     "\t// why=deferred); a second such event on the image overwrites the mark. TakeF26Deferred - takes m_lock itself (as\n"
     "\t// MetaClearMask; RenderExecutor::MaterializeDeferredDccClear holds no texture cache lock), removes and returns the\n"
     "\t// mark; false without one (and without taking the lock while no image has a mark). DeleteImage drops a mark without\n"
     "\t// a line. No mark exists with KYTY_FIX_F26 = 0.\n"
     "\tstruct F26Deferred {\n"
     "\t\tuint64_t n     = 0; // the event number of the adopt's dcc_stale line\n"
     "\t\tuint64_t image = 0; // image / dcc of that line\n"
     "\t\tuint64_t dcc   = 0;\n"
     "\t};\n"
     "\tvoid               NoteF26DeferredLocked(ImageId id, const F26Deferred& mark);\n"
     "\t[[nodiscard]] bool TakeF26Deferred(ImageId id, F26Deferred* mark);\n")
edit(TH,
     "\tstd::unordered_map<ImageId, uint64_t>             m_b42_draw_seq;\n",
     "\tstd::unordered_map<ImageId, uint64_t>             m_b42_draw_seq;\n"
     "\t// Track F, F16o2 (item 507(b)(2)): the deferred marks, under m_lock; their number - written under m_lock, read\n"
     "\t// without it by TakeF26Deferred (0: the lock is not taken).\n"
     "\tstd::unordered_map<ImageId, F26Deferred>          m_f26_deferred;\n"
     "\tstd::atomic<uint32_t>                             m_f26_deferred_count {0};\n")

# ---------------------------------------------------------------- textureCache.cpp
T = R + "cache/textureCache.cpp"
edit(T,
     "\tm_b42_draw_seq.erase(id); // Track F, F9e2b (KYTY_FIX_B42): a recycled slot id starts without a draw stamp\n",
     "\tm_b42_draw_seq.erase(id); // Track F, F9e2b (KYTY_FIX_B42): a recycled slot id starts without a draw stamp\n"
     "\t// Track F, F16o2 (item 507(b)(2)): the deferred mark of a deleted image is dropped without a line.\n"
     "\tif (m_f26_deferred_count.load(std::memory_order_relaxed) != 0 && m_f26_deferred.erase(id) != 0) [[unlikely]] {\n"
     "\t\tm_f26_deferred_count.fetch_sub(1, std::memory_order_relaxed);\n"
     "\t}\n")
edit(T,
     "\tvoid Applied(bool applied, DiagF5::CmuWhy why_not) {\n"
     "\t\tm_applied = applied;\n"
     "\t\tif (!applied && m_why == DiagF5::CmuWhy::None) {\n"
     "\t\t\tm_why = why_not;\n"
     "\t\t}\n"
     "\t}\n",
     "\tvoid Applied(bool applied, DiagF5::CmuWhy why_not) {\n"
     "\t\tm_applied = applied;\n"
     "\t\tif (!applied && m_why == DiagF5::CmuWhy::None) {\n"
     "\t\t\tm_why = why_not;\n"
     "\t\t}\n"
     "\t}\n"
     "\t// Track F, F16o2 (RC1 of F16p, item 507(b)(1)-(2)): AdoptPendingDccForTexture adopted the kept fill with a clear the\n"
     "\t// call does not apply (RenderExecutor::MaterializeDeferredDccClear clears it later or declines): kept why=deferred;\n"
     "\t// when Report() reports it as kept (KYTY_FIX_F26, KYTY_DIAG_F5), the mark of `id` in `cache` with the line's n (the\n"
     "\t// scope is declared after cache->m_lock is taken and leaves before it is released).\n"
     "\tvoid Deferred(TextureCache* cache, ImageId id) {\n"
     "\t\tm_why         = DiagF5::CmuWhy::Deferred;\n"
     "\t\tm_applied     = false;\n"
     "\t\tm_defer_cache = cache;\n"
     "\t\tm_defer_id    = id;\n"
     "\t}\n")
edit(T,
     "\t\t(void)DiagF5::NoteDccStale(m_line);\n"
     "\t}\n",
     "\t\tuint64_t n = 0;\n"
     "\t\t(void)DiagF5::NoteDccStale(m_line, &n);\n"
     "\t\tif (m_fix && e.fix == F::Kept && e.why == DiagF5::CmuWhy::Deferred && m_defer_cache != nullptr) {\n"
     "\t\t\tm_defer_cache->NoteF26DeferredLocked(m_defer_id, {.n = n, .image = m_line.image, .dcc = m_line.dcc});\n"
     "\t\t}\n"
     "\t}\n")
edit(T,
     "\tDiagF5::DccStaleLine m_line {};\n"
     "};\n",
     "\tDiagF5::DccStaleLine m_line {};\n"
     "\tTextureCache*        m_defer_cache = nullptr; // Track F, F16o2: Deferred()\n"
     "\tImageId              m_defer_id {};\n"
     "};\n")
edit(T,
     "\t// Track F, F16o (item 504(e)(3)): a kept fill is kept_applied when it is adopted with a clear (a non-zero mask).\n"
     "\tf26.Applied(found->second.clear_mask != 0, DiagF5::CmuWhy::Mask);\n",
     "\t// Track F, F16o (item 504(e)(3)): a kept fill adopted without a clear (mask 0) is kept why=mask. Track F, F16o2 (RC1\n"
     "\t// of F16p, item 507(b)(1)): one adopted with a clear is kept why=deferred - this call clears nothing; the clear is\n"
     "\t// RenderExecutor::MaterializeDeferredDccClear's, which reports it (dcc_stale_apply) by the mark Deferred() leaves.\n"
     "\tif (found->second.clear_mask != 0) {\n"
     "\t\tf26.Deferred(this, id);\n"
     "\t} else {\n"
     "\t\tf26.Applied(false, DiagF5::CmuWhy::Mask);\n"
     "\t}\n")
edit(T,
     "bool TextureCache::TouchMeta(uint64_t address, uint32_t slice, bool is_clear) {\n",
     "// Track F, F16o2 (KYTY_FIX_F26, item 507(b)(2)): caller holds m_lock.\n"
     "void TextureCache::NoteF26DeferredLocked(ImageId id, const F26Deferred& mark) {\n"
     "\tif (m_f26_deferred.insert_or_assign(id, mark).second) {\n"
     "\t\tm_f26_deferred_count.fetch_add(1, std::memory_order_relaxed);\n"
     "\t}\n"
     "}\n"
     "\n"
     "// Track F, F16o2 (item 507(b)(3)): takes m_lock itself, as MetaClearMask; while no image has a mark the lock is not\n"
     "// taken (the count is written under m_lock by the same GPU thread that calls this [I]).\n"
     "bool TextureCache::TakeF26Deferred(ImageId id, F26Deferred* mark) {\n"
     "\tif (m_f26_deferred_count.load(std::memory_order_relaxed) == 0) {\n"
     "\t\treturn false;\n"
     "\t}\n"
     "\tstd::scoped_lock lock {m_lock};\n"
     "\tconst auto       found = m_f26_deferred.find(id);\n"
     "\tif (found == m_f26_deferred.end()) {\n"
     "\t\treturn false;\n"
     "\t}\n"
     "\t*mark = found->second;\n"
     "\tm_f26_deferred.erase(found);\n"
     "\tm_f26_deferred_count.fetch_sub(1, std::memory_order_relaxed);\n"
     "\treturn true;\n"
     "}\n"
     "\n"
     "bool TextureCache::TouchMeta(uint64_t address, uint32_t slice, bool is_clear) {\n")

# ---------------------------------------------------------------- descriptors.cpp
P = R + "pipeline/descriptors.cpp"
edit(P,
     "private:\n"
     "\tvk::Format m_saved;\n"
     "};\n"
     "\n"
     "} // namespace\n"
     "\n"
     "// A guest DCC fast clear only rewrites metadata, and the attachment path materializes it as a\n",
     "private:\n"
     "\tvk::Format m_saved;\n"
     "};\n"
     "\n"
     "// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(3)): one MaterializeDeferredDccClear call on an\n"
     "// image that carries the deferred mark of AdoptPendingDccForTexture (event fix=kept why=deferred). The constructor\n"
     "// takes the mark (TextureCache::TakeF26Deferred - m_lock taken inside, as MetaClearMask; the call holds no cache\n"
     "// lock), so it is removed whatever the outcome; the destructor (every return of the call) reports it: cleared (>= 1\n"
     "// layer cleared) - f26_kept_applied, declined (any return without a clear) - f26_deferred_declined, and the line\n"
     "// DiagF5Ev dcc_stale_apply. Without KYTY_FIX_F26 nothing is taken (no mark exists) and nothing is reported.\n"
     "class F26ApplyScope {\n"
     "public:\n"
     "\tF26ApplyScope(TextureCache& cache, ImageId id) {\n"
     "\t\tif (DiagF5::FixF26On()) [[unlikely]] {\n"
     "\t\t\tm_armed = cache.TakeF26Deferred(id, &m_mark);\n"
     "\t\t}\n"
     "\t}\n"
     "\t~F26ApplyScope() {\n"
     "\t\tif (m_armed) [[unlikely]] {\n"
     "\t\t\tDiagF5::Add(m_cleared ? DiagF5::Counter::F26KeptApplied : DiagF5::Counter::F26DeferredDeclined);\n"
     "\t\t\t(void)DiagF5::NoteDccStaleApply({.n       = m_mark.n,\n"
     "\t\t\t                                   .present = DiagF5::Present(),\n"
     "\t\t\t                                   .gpu     = GpuTimeProfiler::Frame(),\n"
     "\t\t\t                                   .image   = m_mark.image,\n"
     "\t\t\t                                   .dcc     = m_mark.dcc,\n"
     "\t\t\t                                   .cleared = m_cleared,\n"
     "\t\t\t                                   .layers  = m_layers});\n"
     "\t\t}\n"
     "\t}\n"
     "\tF26ApplyScope(const F26ApplyScope&)            = delete;\n"
     "\tF26ApplyScope& operator=(const F26ApplyScope&) = delete;\n"
     "\n"
     "\t// The pending layer mask the call read.\n"
     "\tvoid Layers(uint32_t mask) { m_layers = mask; }\n"
     "\t// Every layer of that mask was cleared.\n"
     "\tvoid Cleared() { m_cleared = true; }\n"
     "\n"
     "private:\n"
     "\tTextureCache::F26Deferred m_mark {};\n"
     "\tbool                      m_armed   = false;\n"
     "\tbool                      m_cleared = false;\n"
     "\tuint32_t                  m_layers  = 0;\n"
     "};\n"
     "\n"
     "} // namespace\n"
     "\n"
     "// A guest DCC fast clear only rewrites metadata, and the attachment path materializes it as a\n")
edit(P,
     "void RenderExecutor::MaterializeDeferredDccClear(CommandBuffer& buffer, ImageId id, Image& image) {\n"
     "\tauto& cache = m_context.GetTextureCache();\n",
     "void RenderExecutor::MaterializeDeferredDccClear(CommandBuffer& buffer, ImageId id, Image& image) {\n"
     "\tauto& cache = m_context.GetTextureCache();\n"
     "\t// Track F, F16o2 (KYTY_FIX_F26, RC1 of F16p, ROADMAP s122 item 507(b)(3)): the deferred mark of an adoption is\n"
     "\t// taken here, before any return; the outcome (dcc_stale_apply) is reported when the call returns. Nothing without\n"
     "\t// the knob.\n"
     "\tF26ApplyScope f26_apply {cache, id};\n")
edit(P,
     "\tif (mask == 0) {\n"
     "\t\treturn;\n"
     "\t}\n"
     "\tif (DiagF5::On()) [[unlikely]] {\n"
     "\t\tDiagF5::Add(DiagF5::Counter::DccMatPending); // Track F, F16d (item 427(b), RC4): a pending layer mask\n",
     "\tf26_apply.Layers(mask); // Track F, F16o2\n"
     "\tif (mask == 0) {\n"
     "\t\treturn;\n"
     "\t}\n"
     "\tif (DiagF5::On()) [[unlikely]] {\n"
     "\t\tDiagF5::Add(DiagF5::Counter::DccMatPending); // Track F, F16d (item 427(b), RC4): a pending layer mask\n")
edit(P,
     "\t// Session 124, knob \"skipceil\" = 3 (closure census, ROADMAP s122 item 47(b)): the materialized layers (every level).\n",
     "\tf26_apply.Cleared(); // Track F, F16o2: every layer of the mask was cleared above\n"
     "\t// Session 124, knob \"skipceil\" = 3 (closure census, ROADMAP s122 item 47(b)): the materialized layers (every level).\n")

# ---------------------------------------------------------------- tests
X = "tests/ShaderRecompilerComputeTests.cpp"
edit(X,
     "  static void F16kEraseMeta(TextureCache &cache, uint64_t address) {\n"
     "    std::lock_guard lock(cache.m_lock);\n"
     "    cache.m_surface_metas.erase(address);\n"
     "  }\n",
     "  static void F16kEraseMeta(TextureCache &cache, uint64_t address) {\n"
     "    std::lock_guard lock(cache.m_lock);\n"
     "    cache.m_surface_metas.erase(address);\n"
     "  }\n"
     "  // Track F, F16o2 (HPP-599): the number of deferred marks (KYTY_FIX_F26).\n"
     "  static size_t F16o2Marks(TextureCache &cache) {\n"
     "    std::lock_guard lock(cache.m_lock);\n"
     "    return cache.m_f26_deferred.size();\n"
     "  }\n")
edit(X,
     "                  static_cast<uint32_t>(C::F26Fallback) + 1 == static_cast<uint32_t>(C::Count) &&\n",
     "                  static_cast<uint32_t>(C::F26Fallback) + 2 == static_cast<uint32_t>(C::Count) && // F16o2: +1 row\n")
edit(X,
     "      F16kOk(\"F16o pure helpers (names, f26_* last, dcc_stale line form)\");\n",
     "      F16kOk(\"F16o pure helpers (names, f26_* last, dcc_stale line form)\");\n"
     "      // Track F, F16o2 (item 507(b)(1), (3)): why=deferred last, f26_deferred_declined last, the line dcc_stale_apply.\n"
     "      Require(name, \"F16o2 names\",\n"
     "              std::string(DiagF5::CmuWhyName(W::Deferred)) == \"deferred\" &&\n"
     "                  static_cast<uint32_t>(W::Deferred) == static_cast<uint32_t>(W::Levels) + 1 &&\n"
     "                  std::string(DiagF5::Name(C::F26DeferredDeclined)) == \"f26_deferred_declined\" &&\n"
     "                  static_cast<uint32_t>(C::F26DeferredDeclined) == static_cast<uint32_t>(C::F26Fallback) + 1 &&\n"
     "                  static_cast<uint32_t>(C::F26DeferredDeclined) + 1 == static_cast<uint32_t>(C::Count),\n"
     "              \"a name of F16o2\");\n"
     "      const auto da1 = DiagF5::FormatDccStaleApply({.n = 4, .present = 7, .gpu = 9, .image = 0x10, .dcc = 0x20,\n"
     "                                                     .cleared = true, .layers = 1});\n"
     "      const auto da2 = DiagF5::FormatDccStaleApply({.n = 5, .present = 1, .gpu = 2, .image = 0x10, .dcc = 0x20,\n"
     "                                                     .cleared = false, .layers = 0});\n"
     "      const auto ds4 = DiagF5::FormatDccStale(6, {.site = DS::Adopt, .present = 1, .gpu = 2, .image = 0x10, .dcc = 0x20,\n"
     "                                                  .width = 64, .height = 64, .exact = DX::Fresh,\n"
     "                                                  .event = {F::Kept, W::Deferred}});\n"
     "      Require(name, \"F16o2 dcc_stale_apply line form\",\n"
     "              da1 == \"DiagF5Ev: dcc_stale_apply n=4 present=7 gpu=9 image=0x0000000000000010 dcc=0x0000000000000020 \"\n"
     "                     \"result=cleared layers=0x00000001\" &&\n"
     "                  da2 == \"DiagF5Ev: dcc_stale_apply n=5 present=1 gpu=2 image=0x0000000000000010 \"\n"
     "                         \"dcc=0x0000000000000020 result=declined layers=0x00000000\" &&\n"
     "                  ds4 == \"DiagF5Ev: dcc_stale site=adopt n=6 present=1 gpu=2 image=0x0000000000000010 \"\n"
     "                         \"dcc=0x0000000000000020 extent=64x64 exact=fresh fix=kept why=deferred\",\n"
     "              \"the dcc_stale_apply line: \" + da1 + \" | \" + da2 + \" | \" + ds4);\n"
     "      F16kOk(\"F16o2 pure helpers (why=deferred, f26_deferred_declined last, dcc_stale_apply line form)\");\n")
edit(X,
     "        for (const auto counter : {C::F26Kept, C::F26KeptApplied, C::F26ExactStale, C::F26Fallback}) {\n",
     "        for (const auto counter :\n"
     "             {C::F26Kept, C::F26KeptApplied, C::F26ExactStale, C::F26Fallback, C::F26DeferredDeclined}) {\n")
edit(X,
     "                   {C::F26ExactStale, 0}, {C::F26Fallback, 0}});\n",
     "                   {C::F26ExactStale, 0}, {C::F26Fallback, 0}, {C::F26DeferredDeclined, 0}});\n")
edit(X,
     "                 {C::F26Fallback, 0}});\n",
     "                 {C::F26Fallback, 0}, {C::F26DeferredDeclined, 0}});\n")
edit(X,
     "                     {C::F26Fallback, k5 && d.f26_counter == C::F26Fallback ? 1u : 0u}});\n",
     "                     {C::F26Fallback, k5 && d.f26_counter == C::F26Fallback ? 1u : 0u},\n"
     "                     {C::F26DeferredDeclined, 0}});\n")
edit(X,
     "        // erased; Track F, F16o: with it the neighbour's fill is adopted - kept_applied with a clear code, kept why=mask\n",
     "        // erased; Track F, F16o: with it the neighbour's fill is adopted - kept why=deferred with a clear code (Track F,\n"
     "        // F16o2: the clear is MaterializeDeferredDccClear's - D4 cleared, D4e declined), kept why=mask\n")
edit(X,
     "          C f26_counter;\n"
     "        };\n"
     "        const ACase acases[] = {\n"
     "            {\"D4f adoption, no write after the fill: no line\", 0, 0x40404040u, \"-\", \"-\", \"-\", true, 0, 0, C::Count},\n"
     "            {\"D4 adoption, neighbour\", 1, 0x40404040u, \"fresh\", \"kept_applied\", \"<none>\", true, 1, 0, C::F26KeptApplied},\n"
     "            {\"D4b adoption, neighbour, no clear code\", 1, 0x12345678u, \"fresh\", \"kept\", \"mask\", true, 1, 0, C::F26Kept},\n",
     "          C f26_counter;\n"
     "          bool mat;           // Track F, F16o2: MaterializeDeferredDccClear after the adoption\n"
     "          const char *result; // Track F, F16o2: of dcc_stale_apply (with the mark)\n"
     "        };\n"
     "        const ACase acases[] = {\n"
     "            {\"D4f adoption, no write after the fill: no line\", 0, 0x40404040u, \"-\", \"-\", \"-\", true, 0, 0, C::Count,\n"
     "             false, \"-\"},\n"
     "            {\"D4 adoption, neighbour, code 0x40: deferred, then cleared\", 1, 0x40404040u, \"fresh\", \"kept\", \"deferred\",\n"
     "             true, 1, 0, C::F26Kept, true, \"cleared\"},\n"
     "            {\"D4b adoption, neighbour, no clear code\", 1, 0x12345678u, \"fresh\", \"kept\", \"mask\", true, 1, 0, C::F26Kept,\n"
     "             false, \"-\"},\n"
     "            {\"D4e adoption, neighbour, code 0x20 without a slot: deferred, then declined\", 1, 0x20202020u, \"fresh\",\n"
     "             \"kept\", \"deferred\", true, 1, 0, C::F26Kept, true, \"declined\"},\n")
edit(X,
     "            {\"D4c adoption, crossing\", 2, 0x40404040u, \"stale\", \"exact_stale\", \"<none>\", false, 0, 0, C::F26ExactStale},\n"
     "            {\"D4d adoption, K+1\", 3, 0x40404040u, \"fallback\", \"fallback\", \"<none>\", false, 0, 1, C::F26Fallback},\n",
     "            {\"D4c adoption, crossing\", 2, 0x40404040u, \"stale\", \"exact_stale\", \"<none>\", false, 0, 0, C::F26ExactStale,\n"
     "             false, \"-\"},\n"
     "            {\"D4d adoption, K+1\", 3, 0x40404040u, \"fallback\", \"fallback\", \"<none>\", false, 0, 1, C::F26Fallback,\n"
     "             false, \"-\"},\n")
edit(X,
     "                     {C::F26Fallback, k5 && a.f26_counter == C::F26Fallback ? 1u : 0u}});\n",
     "                     {C::F26Fallback, k5 && a.f26_counter == C::F26Fallback ? 1u : 0u},\n"
     "                     {C::F26DeferredDeclined, 0}});\n")
edit(X,
     "          pimage0.info.metadata = pmeta0;\n"
     "          TTA::F16kEraseMeta(cache, pending);\n"
     "          F16kOk(a.stage);\n",
     "          // Track F, F16o2 (RC1 of F16p, item 507(b)(1)-(5)): an adoption kept with a clear leaves the deferred mark (only\n"
     "          // with KYTY_FIX_F26 and KYTY_DIAG_F5 - the decision reported as kept why=deferred); MaterializeDeferredDccClear\n"
     "          // takes it and reports dcc_stale_apply of the adopt line's n - cleared (code 0x40) or declined (code 0x20: no\n"
     "          // colour slot addresses the surface). Without the knob: no mark, no line; the materialization as before.\n"
     "          const bool marked = k5 && !fresh && kept && std::string(a.why) == \"deferred\";\n"
     "          Require(name, a.stage, TTA::F16o2Marks(cache) == (marked ? 1u : 0u),\n"
     "                  fmt::format(\"deferred marks {} (expected {})\", TTA::F16o2Marks(cache), marked ? 1 : 0));\n"
     "          if (a.mat) {\n"
     "            const auto adopt_n = F16kField(F16kLast(\"DiagF5Ev: dcc_stale \"), \"n\");\n"
     "            const auto mlines = F16kCount(\"DiagF5Ev:\");\n"
     "            const auto mbefore = F16kRead();\n"
     "            RTA::F16dMaterialize(executor, scheduler.Current(), pid);\n"
     "            const bool cleared = std::string(a.result) == \"cleared\";\n"
     "            F16kDelta(a.stage, mbefore,\n"
     "                      {{C::F26Kept, 0},\n"
     "                       {C::F26KeptApplied, marked && cleared ? 1u : 0u},\n"
     "                       {C::F26DeferredDeclined, marked && !cleared ? 1u : 0u},\n"
     "                       {C::DccMatCleared, f5 && kept && cleared ? 1u : 0u},\n"
     "                       {C::DccMatUndecoded, f5 && kept && !cleared ? 1u : 0u}});\n"
     "            Require(name, a.stage, TTA::F16o2Marks(cache) == 0, \"the deferred mark was not taken\");\n"
     "            if (marked) {\n"
     "              const auto line = F16kLast(\"DiagF5Ev: dcc_stale_apply \");\n"
     "              Require(name, a.stage,\n"
     "                      F16kCount(\"DiagF5Ev:\") == mlines + 1 && F16kField(line, \"n\") == adopt_n &&\n"
     "                          F16kField(line, \"result\") == a.result && F16kField(line, \"layers\") == \"0x00000001\" &&\n"
     "                          F16kField(line, \"image\") == fmt::format(\"0x{:016x}\", plain) &&\n"
     "                          F16kField(line, \"dcc\") == fmt::format(\"0x{:016x}\", pending) &&\n"
     "                          F16kField(line, \"present\") != \"<none>\" && F16kField(line, \"gpu\") != \"<none>\",\n"
     "                      \"the dcc_stale_apply line: \" + line);\n"
     "              std::printf(\"[f16k]      %s\\n[f16k]      %s\\n\", F16kLast(\"DiagF5Ev: dcc_stale \").c_str(), line.c_str());\n"
     "            } else {\n"
     "              Require(name, a.stage, F16kCount(\"DiagF5Ev:\") == mlines, \"a dcc_stale_apply line without a mark\");\n"
     "            }\n"
     "          }\n"
     "          pimage0.info.metadata = pmeta0;\n"
     "          TTA::F16kEraseMeta(cache, pending);\n"
     "          F16kOk(a.stage);\n")
edit(X,
     "                              g(C::F26Fallback) == 0),\n",
     "                              g(C::F26Fallback) == 0 && g(C::F26DeferredDeclined) == 0),\n")
edit(X,
     "      Require(name, \"Z identity f26_kept_applied <= f26_kept\", g(C::F26KeptApplied) <= g(C::F26Kept),\n"
     "              \"f26_kept_applied > f26_kept\");\n",
     "      // Track F, F16o2 (item 507(b)(4)): f26_kept_applied + f26_deferred_declined <= f26_kept.\n"
     "      Require(name, \"Z identity f26_kept_applied + f26_deferred_declined <= f26_kept\",\n"
     "              g(C::F26KeptApplied) + g(C::F26DeferredDeclined) <= g(C::F26Kept),\n"
     "              \"f26_kept_applied + f26_deferred_declined > f26_kept\");\n")
edit(X,
     "        uint64_t all = 0, off = 0, kept = 0, kept_applied = 0, exact_stale = 0, fallback = 0;\n"
     "        for (const auto &line : DiagF5::RecentLines()) {\n"
     "          if (line.rfind(\"DiagF5Ev: dcc_stale \", 0) != 0) {\n"
     "            continue;\n"
     "          }\n"
     "          const auto fix = F16kField(line, \"fix\");\n"
     "          all++;\n"
     "          off += fix == \"off\" ? 1 : 0;\n"
     "          kept += fix == \"kept\" || fix == \"kept_applied\" ? 1 : 0;\n"
     "          kept_applied += fix == \"kept_applied\" ? 1 : 0;\n"
     "          exact_stale += fix == \"exact_stale\" ? 1 : 0;\n"
     "          fallback += fix == \"fallback\" ? 1 : 0;\n"
     "        }\n"
     "        Require(name, \"Z print identity dcc_stale lines by fix = f26_*\",\n"
     "                !f5 ? all == 0\n"
     "                : f26 ? all == 8 && off == 0 && kept == g(C::F26Kept) && kept_applied == g(C::F26KeptApplied) &&\n"
     "                            exact_stale == g(C::F26ExactStale) && fallback == g(C::F26Fallback)\n"
     "                      : all == 8 && off == all,\n"
     "                fmt::format(\"lines {} off {} kept {} kept_applied {} exact_stale {} fallback {}\", all, off, kept,\n"
     "                            kept_applied, exact_stale, fallback));\n",
     "        // Track F, F16o2 (item 507(b)(4)): lines fix=kept_applied (prepare only) + result=cleared = f26_kept_applied;\n"
     "        // fix=kept + fix=kept_applied = f26_kept; result=declined = f26_deferred_declined; adopt fix=kept_applied 0.\n"
     "        uint64_t all = 0, off = 0, kept = 0, kept_applied = 0, exact_stale = 0, fallback = 0, adopt_applied = 0;\n"
     "        uint64_t cleared = 0, declined = 0;\n"
     "        for (const auto &line : DiagF5::RecentLines()) {\n"
     "          if (line.rfind(\"DiagF5Ev: dcc_stale_apply \", 0) == 0) {\n"
     "            const auto result = F16kField(line, \"result\");\n"
     "            cleared += result == \"cleared\" ? 1 : 0;\n"
     "            declined += result == \"declined\" ? 1 : 0;\n"
     "            continue;\n"
     "          }\n"
     "          if (line.rfind(\"DiagF5Ev: dcc_stale \", 0) != 0) {\n"
     "            continue;\n"
     "          }\n"
     "          const auto fix = F16kField(line, \"fix\");\n"
     "          all++;\n"
     "          off += fix == \"off\" ? 1 : 0;\n"
     "          kept += fix == \"kept\" || fix == \"kept_applied\" ? 1 : 0;\n"
     "          kept_applied += fix == \"kept_applied\" ? 1 : 0;\n"
     "          exact_stale += fix == \"exact_stale\" ? 1 : 0;\n"
     "          fallback += fix == \"fallback\" ? 1 : 0;\n"
     "          adopt_applied += fix == \"kept_applied\" && F16kField(line, \"site\") == \"adopt\" ? 1 : 0;\n"
     "        }\n"
     "        Require(name, \"Z print identity dcc_stale lines by fix, dcc_stale_apply lines by result = f26_*\",\n"
     "                !f5 ? all == 0 && cleared == 0 && declined == 0\n"
     "                : f26 ? all == 9 && off == 0 && kept == g(C::F26Kept) &&\n"
     "                            kept_applied + cleared == g(C::F26KeptApplied) &&\n"
     "                            declined == g(C::F26DeferredDeclined) && adopt_applied == 0 && cleared == 1 &&\n"
     "                            declined == 1 && exact_stale == g(C::F26ExactStale) && fallback == g(C::F26Fallback)\n"
     "                      : all == 9 && off == all && cleared == 0 && declined == 0,\n"
     "                fmt::format(\"lines {} off {} kept {} kept_applied {} (adopt {}) exact_stale {} fallback {} cleared {} \"\n"
     "                            \"declined {}\",\n"
     "                            all, off, kept, kept_applied, adopt_applied, exact_stale, fallback, cleared, declined));\n")
edit(X,
     "      F16kOk(\"L line limits: cmask_fce 1024, cmask_fce_nohit 64, dcc_stale 256\");\n",
     "      F16kOk(\"L line limits: cmask_fce 1024, cmask_fce_nohit 64, dcc_stale 256\");\n"
     "      // Track F, F16o2 (item 507(b)(3)): dcc_stale_apply is printed under the limit of dcc_stale - for n <= 256.\n"
     "      const auto apply0 = F16kCount(\"DiagF5Ev: dcc_stale_apply \");\n"
     "      const bool a256 = DiagF5::NoteDccStaleApply({.n = 256});\n"
     "      const bool a257 = DiagF5::NoteDccStaleApply({.n = 257});\n"
     "      Require(name, \"L dcc_stale_apply limit\",\n"
     "              a256 && !a257 && F16kCount(\"DiagF5Ev: dcc_stale_apply \") == apply0 + 1 &&\n"
     "                  F16kField(F16kLast(\"DiagF5Ev: dcc_stale_apply \"), \"n\") == \"256\",\n"
     "              fmt::format(\"n=256 printed {} n=257 printed {}\", a256, a257));\n"
     "      F16kOk(\"L F16o2 dcc_stale_apply limit (n <= 256)\");\n")


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

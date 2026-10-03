# F9e2 (HPP-426, ROADMAP s122 item 351(v)(1)-(3)): KYTY_FIX_B42 variant M2c.
# Usage: python patch_f9e2.py <repo root>
# Anchors are whole lines; every anchor must occur exactly once. CRLF files keep CRLF; output written with write_bytes.
import sys, pathlib

ROOT = pathlib.Path(sys.argv[1])
NL = chr(10)


def patch(rel, edits):
    p = ROOT / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", NL)
    lines = text.split(NL)
    for anchor, mode, new in edits:
        idx = [i for i, l in enumerate(lines) if l == anchor]
        if len(idx) != 1:
            raise SystemExit("%s: anchor found %d times: %r" % (rel, len(idx), anchor))
        i = idx[0]
        new_lines = new.split(NL)
        if mode == "after":
            lines[i + 1:i + 1] = new_lines
        elif mode == "before":
            lines[i:i] = new_lines
        elif mode == "replace":
            lines[i:i + 1] = new_lines
        else:
            raise SystemExit("bad mode")
    out = NL.join(lines)
    if crlf:
        out = out.replace(NL, "\r\n")
    p.write_bytes(out.encode("utf-8"))
    print("patched", rel, "crlf" if crlf else "lf")


# ---- textureCache.h: the read-only query
H_ANCHOR = "\t[[nodiscard]] bool IsMeta(uint64_t address);"
H_NEW = NL.join([
    "\t// Track F, F9e2 (KYTY_FIX_B42, ROADMAP s122 item 351(v)(1)): a read-only copy of the metadata entry at `address`,",
    "\t// taken under m_lock. Nothing is inserted, bumped, stamped or consumed - the answer is the same with and without",
    "\t// the fix. `pending`: the entry is a PendingDcc fill (TrackDccFill) no image binding has classified yet; `cmask`:",
    "\t// a binding classified it as CMASK (PrepareCmaskClear).",
    "\tstruct MetaFillQuery {",
    "\t\tbool     found      = false;",
    "\t\tbool     pending    = false;",
    "\t\tbool     cmask      = false;",
    "\t\tuint32_t clear_mask = 0;",
    "\t\tuint32_t fill_value = 0xffffffffu;",
    "\t\tuint64_t fill_size  = 0;",
    "\t};",
    "\t[[nodiscard]] MetaFillQuery QueryMetaFill(uint64_t address);",
])

# ---- textureCache.cpp: its definition, right after IsMeta
C_ANCHOR = "uint32_t TextureCache::MetaClearMask(uint64_t address, uint32_t* fill_value) {"
C_NEW = NL.join([
    "// Track F, F9e2 (KYTY_FIX_B42, ROADMAP s122 item 351(v)(1)): read-only, see textureCache.h.",
    "TextureCache::MetaFillQuery TextureCache::QueryMetaFill(uint64_t address) {",
    "\tstd::scoped_lock lock {m_lock};",
    "\tMetaFillQuery    answer {};",
    "\tconst auto       found = m_surface_metas.find(address);",
    "\tif (found == m_surface_metas.end()) {",
    "\t\treturn answer;",
    "\t}",
    "\tanswer.found      = true;",
    "\tanswer.pending    = found->second.type == MetaDataInfo::Type::PendingDcc;",
    "\tanswer.cmask      = found->second.type == MetaDataInfo::Type::CMask;",
    "\tanswer.clear_mask = found->second.clear_mask;",
    "\tanswer.fill_value = found->second.fill_value;",
    "\tanswer.fill_size  = found->second.fill_size;",
    "\treturn answer;",
    "}",
    "",
])

# ---- descriptors.cpp: helpers before MaterializeBoundTargetDccClears, and the CMASK branch
D_HELPER_ANCHOR = "// A fast-clear-eliminate / DCC-decompress draw (CB_COLOR_CONTROL.MODE 2/6) binds the surface as"
D_HELPER_NEW = NL.join([
    "namespace {",
    "",
    "// Track F, F9e2 (B42, ROADMAP s122 item 351(v)(1)-(3)), KYTY_FIX_B42 (default 0: unset, \"\", 0/false/off/no = OFF).",
    "// colorRenderTarget.cpp gives a single-sample CMASK target metadata only when its width and height are multiples of",
    "// 1024, so the fast-clear-eliminate register scan below never materializes the CMASK fast clear of a smaller target",
    "// (the Sky Garden water input T6, 960x540 / 480x270): the image keeps whatever guest memory or buffer bytes it was",
    "// created from. `hit`: a CMASK fast-clear target the old path skips (no DCC, one sample, one level, not a volume,",
    "// not both axes 1024-multiples) whose CMASK address holds a PendingDcc fill of value 0 covering",
    "// width*height*layers/128 bytes - a code-0 CMASK in every tile, i.e. the whole surface is the clear colour whatever",
    "// the tile layout. Counted with the fix on and off. ON: the target's descriptor gets the CMASK metadata the 1024",
    "// branch of colorRenderTarget.cpp would give it, and the existing FindRenderTarget -> PrepareCmaskClear clears it.",
    "// `applied` grows only when PrepareCmaskClear cleared at least one layer (a clear-mask bit consumed while the fill",
    "// value stayed 0: that bit is dropped only right after ClearImage). OFF: the query and the line only - the old path.",
    "bool FixB42Enabled() {",
    "\tstatic const bool enabled = Common::EnvFlagOn(\"KYTY_FIX_B42\");",
    "\treturn enabled;",
    "}",
    "",
    "struct FixB42Hit {",
    "\tbool     hit        = false;",
    "\tuint64_t cmask_size = 0;",
    "\tuint32_t clear_mask = 0; // PendingDcc clear mask seen before the acquisition",
    "};",
    "",
    "FixB42Hit FixB42Probe(TextureCache& cache, const HW::RenderTarget& rt, const RenderColorInfo& color) {",
    "\tFixB42Hit   probe {};",
    "\tconst auto& info = color.desc.info;",
    "\tif (!color.image_id || info.metadata.kind != ImageMetadataKind::None || info.samples != 1 ||",
    "\t    info.resources.levels != 1 || info.IsVolume() ||",
    "\t    (info.extent.width % 1024u == 0 && info.extent.height % 1024u == 0)) {",
    "\t\treturn probe;",
    "\t}",
    "\tconst auto size = static_cast<uint64_t>(info.extent.width) * info.extent.height * info.resources.layers / 128u;",
    "\tconst auto fill = cache.QueryMetaFill(rt.cmask.addr);",
    "\tif (size == 0 || !fill.found || !fill.pending || fill.fill_value != 0 || fill.fill_size < size) {",
    "\t\treturn probe;",
    "\t}",
    "\tprobe.hit        = true;",
    "\tprobe.cmask_size = size;",
    "\tprobe.clear_mask = fill.clear_mask;",
    "\treturn probe;",
    "}",
    "",
    "// The line: on every hit for the first 256 lines, then at most once per 600 frames (still only on a hit).",
    "void FixB42Note(bool applied, uint32_t width, uint32_t height, uint64_t cmask, uint32_t word0, uint32_t word1) {",
    "\tstatic std::mutex m;",
    "\tstatic uint64_t   hits         = 0;",
    "\tstatic uint64_t   applies      = 0;",
    "\tstatic uint32_t   lines        = 0;",
    "\tstatic uint32_t   printed_at   = 0;",
    "\tconst auto        frame        = GpuTimeProfiler::Frame();",
    "\tstd::scoped_lock  lock {m};",
    "\thits++;",
    "\tif (applied) {",
    "\t\tapplies++;",
    "\t}",
    "\tif (lines >= 256 && frame - printed_at < 600u) {",
    "\t\treturn;",
    "\t}",
    "\tlines++;",
    "\tprinted_at = frame;",
    "\tLOGF(\"FixB42: mode=%d hit=%\" PRIu64 \" applied=%\" PRIu64 \" last_frame=%u extent=%ux%u cmask=0x%\" PRIx64",
    "\t     \" clear=%08x/%08x\\n\",",
    "\t     FixB42Enabled() ? 1 : 0, hits, applies, frame, width, height, cmask, word0, word1);",
    "}",
    "",
    "} // namespace",
    "",
])

D_BRANCH_OLD_FIRST = "\t\t\tResolveRenderColorTarget(buffer, color, 0, slot, true, true);"
D_BRANCH_NEW_FIRST = NL.join([
    "\t\t\tResolveRenderColorTarget(buffer, color, 0, slot, true, true);",
    "\t\t\t// Track F, F9e2 (B42): see FixB42Probe. With the fix off nothing below changes.",
    "\t\t\tconst auto b42 = FixB42Probe(cache, rt, color);",
    "\t\t\tif (b42.hit && FixB42Enabled()) {",
    "\t\t\t\tcolor.desc.info.metadata.kind              = ImageMetadataKind::Cmask;",
    "\t\t\t\tcolor.desc.info.metadata.range             = {rt.cmask.addr, b42.cmask_size};",
    "\t\t\t\tcolor.desc.info.metadata.cmask_clear_words = {rt.clear_word0.word0, rt.clear_word1.word1};",
    "\t\t\t}",
])

D_BRANCH_CONTINUE_OLD = NL.join([
    "\t\t\t\t        (rt.dcc.dcc_clear_key_enable ? TextureCache::kRegColorDccKey : 0u));",
    "\t\t\t}",
    "\t\t\tcontinue;",
])


def patch_descriptors():
    rel = "src/graphics/host_gpu/renderer/pipeline/descriptors.cpp"
    p = ROOT / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", NL)
    # helper block
    lines = text.split(NL)
    idx = [i for i, l in enumerate(lines) if l == D_HELPER_ANCHOR]
    if len(idx) != 1:
        raise SystemExit("helper anchor %d" % len(idx))
    lines[idx[0]:idx[0]] = D_HELPER_NEW.split(NL)
    # first line of the branch
    idx = [i for i, l in enumerate(lines) if l == D_BRANCH_OLD_FIRST]
    if len(idx) != 1:
        raise SystemExit("branch anchor %d" % len(idx))
    lines[idx[0]:idx[0] + 1] = D_BRANCH_NEW_FIRST.split(NL)
    text = NL.join(lines)
    # the tail of the branch (three whole lines, once)
    if text.count(D_BRANCH_CONTINUE_OLD) != 1:
        raise SystemExit("continue anchor %d" % text.count(D_BRANCH_CONTINUE_OLD))
    tail_new = NL.join([
        "\t\t\t\t        (rt.dcc.dcc_clear_key_enable ? TextureCache::kRegColorDccKey : 0u));",
        "\t\t\t}",
        "\t\t\tif (b42.hit) {",
        "\t\t\t\tbool applied = false;",
        "\t\t\t\tif (FixB42Enabled()) {",
        "\t\t\t\t\tconst auto after = cache.QueryMetaFill(rt.cmask.addr);",
        "\t\t\t\t\tapplied = after.found && after.cmask && after.fill_value == 0 &&",
        "\t\t\t\t\t          (b42.clear_mask & ~after.clear_mask) != 0;",
        "\t\t\t\t}",
        "\t\t\t\tFixB42Note(applied, color.desc.info.extent.width, color.desc.info.extent.height, rt.cmask.addr,",
        "\t\t\t\t           rt.clear_word0.word0, rt.clear_word1.word1);",
        "\t\t\t}",
        "\t\t\tcontinue;",
    ])
    text = text.replace(D_BRANCH_CONTINUE_OLD, tail_new)
    if crlf:
        text = text.replace(NL, "\r\n")
    p.write_bytes(text.encode("utf-8"))
    print("patched", rel, "crlf" if crlf else "lf")


patch("src/graphics/host_gpu/renderer/cache/textureCache.h", [(H_ANCHOR, "after", H_NEW)])
patch("src/graphics/host_gpu/renderer/cache/textureCache.cpp", [(C_ANCHOR, "before", C_NEW)])
patch_descriptors()
print("PATCH OK")

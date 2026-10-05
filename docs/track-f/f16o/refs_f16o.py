"""Track F, F16o (HPP-595): every code reference of docs/track-f/f16o.md checked by anchor at <commit>:<path>:<line> (general
rule 24(1)); the decision reference with its +1 line. Every full reference d5cbcbe2:<path>:<line> of the report must be in
the list. Run in C:/kyty/KytyPS5:

    python refs_f16o.py <report.md> <out.txt>

The last line is ALL OK / NOT OK.
"""
import re
import subprocess
import sys

C = "d5cbcbe2"
TC = "src/graphics/host_gpu/renderer/cache/textureCache.cpp"
DC = "src/graphics/host_gpu/renderer/diagF5.cpp"
DH = "src/graphics/host_gpu/renderer/diagF5.h"
VW = "src/graphics/presentation/window/vulkanWindow.cpp"
BC = "src/graphics/host_gpu/renderer/cache/bufferCache.cpp"
SS = "src/graphics/presentation/window/screenshot.cpp"
T = "tests/ShaderRecompilerComputeTests.cpp"
REFS = [
    (DC, 595, "bool FixF26On() {"), (DC, 600, "bool LogFixF26Mode() {"), (DC, 605, "EmitLine(\"FixF26: mode=1\");"),
    (DC, 610, "FixCmuOn() || FixF26On() || DiagF5Id::On()"), (DC, 637, "case CmuWhy::Levels"),
    (DC, 653, "g_dcc_stale_events {0}"), (DC, 660, "uint32_t Present() {"), (DC, 677, "if (n > 1024)"),
    (DC, 697, "if (n > 64)"), (DC, 719, "std::string FormatDccStale("), (DC, 730, "bool NoteDccStale("),
    (DC, 732, "if (n > 256)"), (DC, 219, "\"f26_kept\","), (DC, 222, "\"f26_fallback\","), (DC, 238, "void EmitLine("),
    (DH, 278, "bool FixF26On();"), (DH, 287, "enum class DccSite"), (DH, 288, "enum class DccExact"),
    (DH, 291, "struct DccStaleLine"), (DH, 218, "enum class CmuWhy"), (DH, 254, "printed for the first 1024"),
    (DH, 135, "F26Kept,"), (DH, 138, "F26Fallback,"),
    (VW, 684, "DiagF5::LogFixF26Mode()"), (BC, 2866, "if (DiagF5::ExactRingOn())"),
    (SS, 243, "DiagF5::NotePresent(m_presents);"),
    (TC, 1889, "m_decide(fce && DiagF5::FixCmuOn())"), (TC, 1960, "class F26Scope {"), (TC, 1963, "~F26Scope() {"),
    (TC, 1971, "DiagF5::StaleProbe* Arm() {"), (TC, 1977, "void Decided(bool stale"), (TC, 2002, "void Report() {"),
    (TC, 2029, "(void)DiagF5::NoteDccStale(m_line);"), (TC, 2044, "void TextureCache::PrepareDccClear("),
    (TC, 2046, "return;"), (TC, 2049, "F26Scope f26 {DiagF5::DccSite::Prepare};"), (TC, 2075, "f26.Arm());"),
    (TC, 2076, "f26.Decided(f5_stale, image.info.data.address"), (TC, 2087, "DiagF5::NoteDccStaleProbe(f26.Probe());"),
    (TC, 2131, "f26.Why(metadata.clear_mask == 0"), (TC, 2136, "return;"), (TC, 2146, "f26.Why(DiagF5::CmuWhy::Decode);"),
    (TC, 2147, "return;"), (TC, 2162, "f26.Why(DiagF5::CmuWhy::Layers);"), (TC, 2163, "return;"),
    (TC, 2181, "ClearImage(m_scheduler.Current(), id, view.format,"),
    (TC, 2189, "f26.Applied(metadata.clear_mask != f5id_mask0, DiagF5::CmuWhy::NoLayer);"), (TC, 2195, "}"),
    (TC, 2556, "std::scoped_lock lock {m_lock};"), (TC, 2578, "PrepareDccClear(id, desc);"),
    (TC, 2633, "std::scoped_lock lock {m_lock};"), (TC, 2702, "PrepareDccClear(id, desc);"),
    (TC, 3642, "if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {"),
    (TC, 3711, "bool TextureCache::AdoptPendingDccForTexture("), (TC, 3712, "std::scoped_lock lock {m_lock};"),
    (TC, 3719, "return false;"), (TC, 3725, "return image->info.metadata.range.address == metadata_address;"),
    (TC, 3731, "return false;"), (TC, 3742, "return false;"), (TC, 3747, "F26Scope   f26 {DiagF5::DccSite::Adopt};"),
    (TC, 3749, "f26.Arm());"), (TC, 3750, "f26.Decided(f5_stale, image->info.data.address"),
    (TC, 3753, "DiagF5::NoteDccStaleProbe(f26.Probe());"), (TC, 3765, "return false;"),
    (TC, 3769, "found->second.type                 = MetaDataInfo::Type::Dcc;"),
    (TC, 3771, "f26.Applied(found->second.clear_mask != 0, DiagF5::CmuWhy::Mask);"), (TC, 3792, "return true;"),
    (T, 10461, "const bool f26 = Common::EnvValueOn(std::getenv(\"KYTY_FIX_F26\"));"), (T, 10485, "F16o mode line"),
    (T, 10560, "F16o names"), (T, 10584, "dcc_stale line form"), (T, 10777, "Track F, F16o: the FCE acquisition"),
    (T, 10827, "K1-K8 FCE acquisition: KYTY_FIX_F26"), (T, 10996, "const DCase dcases[] = {"),
    (T, 11086, "const ACase acases[] = {"), (T, 11550, "Z f26_* only"), (T, 11576, "Z print identity"),
    (T, 11610, "L line limits:"), (T, 34837, "\"--f16k-only\""),
]
DECISION = ("c6dd8b0f", "docs/ROADMAP.md", 22853,
            "504. **Звено F16n трека F (`HPP-586`, лид): F16m (`HPP-585`) ПРИНЯТ",
            "(а) **Приёмка строкой. F16m ✓**")


def lines(commit, path):
    out = subprocess.run(["git", "show", "%s:%s" % (commit, path)], capture_output=True)
    return out.stdout.decode("utf-8").split("\n")


def main():
    report, out = sys.argv[1], sys.argv[2]
    cache = {}
    res = []
    ok = True
    for path, n, anchor in REFS:
        if path not in cache:
            cache[path] = lines(C, path)
        text = cache[path][n - 1] if n - 1 < len(cache[path]) else ""
        good = anchor in text
        ok &= good
        nxt = cache[path][n] if n < len(cache[path]) else ""
        res.append("%s %s:%s:%d | %s | +1: %s" % ("OK  " if good else "FAIL", C, path, n, text.strip()[:110], nxt.strip()[:60]))
    c, p, n, a, a1 = DECISION
    dl = lines(c, p)
    good = dl[n - 1].startswith(a) and dl[n].strip().startswith(a1)
    ok &= good
    res.append("%s %s:%s:%d anchor and +1" % ("OK  " if good else "FAIL", c, p, n))
    listed = {(p, n) for p, n, _ in REFS}
    text = open(report, encoding="utf-8").read()
    full = re.findall(C + r":([\w/.]+):(\d+)", text)
    for p, n in full:
        good = (p, int(n)) in listed
        ok &= good
        if not good:
            res.append("FAIL report reference not in the list: %s:%s:%s" % (C, p, n))
    res.append("references in the list %d, full references in the report %d (all listed: %s)" % (
        len(REFS), len(full), all((p, int(n)) in listed for p, n in full)))
    res.append("ALL OK" if ok else "NOT OK")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(res) + "\n")
    print("\n".join(res[-4:]))
    return 0 if ok else 1


sys.exit(main())

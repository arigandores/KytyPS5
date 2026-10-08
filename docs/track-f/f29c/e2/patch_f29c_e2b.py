# F29c edition 2, stand only (HPP-702, ROADMAP s122 item 641(g), (d)): field hlost1 of the B12c line - the hook page was not
# synchronized within the pass in which the hook fired (a reference field: the late visit after a skip that skips without
# the witness check delays a write to the next pass, which hlost over 2 passes does not see). Whole-line anchors, LF.
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "C:/kyty/KytyPS5"
NL = chr(10)


def L(*lines):
    return NL.join(lines) + NL


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


patch("tests/B12BdaStampStand.cpp", [
    (L("// (lskip; late_lskips - those in the passes after the first)."),
     L("// (lskip; late_lskips - those in the passes after the first). hlost1 - the hook page was not synchronized within the",
       "// pass in which the hook fired (reference: a write delayed to the next pass is not lost over the passes).")),
    (L("\tuint64_t       hlost = 0, hdirty = 0, hboth = 0, hfired = 0, late_scans = 0, late_rewalks = 0;"),
     L("\tuint64_t       hlost = 0, hdirty = 0, hboth = 0, hfired = 0, late_scans = 0, late_rewalks = 0, hlost1 = 0;")),
    (L("\t\tbool           fired;",
       "\t} hs {&tracker, 0, page, 0, &cache, false};"),
     L("\t\tbool           fired;",
       "\t\tsize_t         synced_end; // the end of the pieces of the pass in which the hook fired",
       "\t\tbool           pass_done;",
       "\t} hs {&tracker, 0, page, 0, &cache, false, 0, false};")),
    (L("\t\t\ths.fired   = false;"),
     L("\t\t\ths.fired   = false;",
       "\t\t\ths.pass_done = false;")),
    (L("\t\t\tcontext.Prepare();",
       "\t\t\tconst auto ds = cache.scanned - s0;"),
     L("\t\t\tcontext.Prepare();",
       "\t\t\tif (h_any && hs.fired && !hs.pass_done) {",
       "\t\t\t\ths.synced_end = cache.synced.size();",
       "\t\t\t\ths.pass_done  = true;",
       "\t\t\t}",
       "\t\t\tconst auto ds = cache.scanned - s0;")),
    (L("\t\t\t\tconst bool h_dirty = tracker.IsRegionCpuModified(hs.address, page);"),
     L("\t\t\t\tconst bool h_dirty = tracker.IsRegionCpuModified(hs.address, page);",
       "\t\t\t\tconst std::vector<GuestRange> in_pass(cache.synced.begin() + static_cast<std::ptrdiff_t>(hs.synced_at),",
       "\t\t\t\t                                      cache.synced.begin() + static_cast<std::ptrdiff_t>(hs.synced_end));",
       "\t\t\t\thlost1 += Covered(in_pass, hs.address, page) ? 0 : 1;")),
    (L("\t            \"scan_passes=%llu rw_min=%llu rw_max=%llu late_scans=%llu late_rewalks=%llu lskip=%llu late_lskips=%llu\\n\","),
     L("\t            \"scan_passes=%llu rw_min=%llu rw_max=%llu late_scans=%llu late_rewalks=%llu lskip=%llu late_lskips=%llu \"",
       "\t            \"hlost1=%llu\\n\",")),
    (L("\t            static_cast<unsigned long long>(cache.lskip - lskip0), static_cast<unsigned long long>(late_lskips));"),
     L("\t            static_cast<unsigned long long>(cache.lskip - lskip0), static_cast<unsigned long long>(late_lskips),",
       "\t            static_cast<unsigned long long>(hlost1));")),
])
print("ALL PATCHED")

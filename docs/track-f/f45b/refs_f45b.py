# refs_f45b.py - track F, link F45b (HPP-796, Red Team): every <commit>:<path>:<line> of f45b-review.md with anchor and +1 control.
# Usage: python refs_f45b.py [repo]          - check every ref (anchor at line n, its +1 at line n+1)
#        python refs_f45b.py text <review>   - every <commit>:<short|path>:<n> of the review is a checked ref
#        python refs_f45b.py neg             - negative control: every ref shifted by +1 must fail
import re, subprocess, sys

SHORT = {"tc": "src/graphics/host_gpu/renderer/cache/textureCache.cpp",
         "ds": "src/graphics/host_gpu/renderer/pipeline/descriptors.cpp",
         "rd5": "docs/track-f/f16m/runs/f5id_sg/read.txt"}
MODE = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("text", "neg") else "check"
REPO = sys.argv[1] if MODE == "check" and len(sys.argv) > 1 else "C:/kyty/KytyPS5"
TC, DS, RD5 = SHORT["tc"], SHORT["ds"], SHORT["rd5"]
F16M = "cfcfbb46"
REFS = [
    ("730ed40a", TC, 1897, "metadata.type = MetaDataInfo::Type::Dcc;", "} else if (metadata.type != MetaDataInfo::Type::Dcc) {"),
    ("730ed40a", TC, 1941, "for (uint32_t layer = first; layer < first + count;) {", "if ((metadata.clear_mask & (1u << layer)) == 0) {"),
    ("730ed40a", TC, 3227, "const auto found = m_surface_metas.try_emplace(address).first;", "if (found->second.type == MetaDataInfo::Type::PendingDcc ||"),
    ("730ed40a", TC, 3228, "if (found->second.type == MetaDataInfo::Type::PendingDcc ||", "found->second.type == MetaDataInfo::Type::Dcc || found->second.type == MetaDataInfo::Type::CMask) {"),
    ("730ed40a", TC, 3242, "if (found->second.type == MetaDataInfo::Type::PendingDcc) {", "found->second.fill_seq = 0;"),
    ("730ed40a", TC, 3268, "// A streamed texture's metadata is filled when its mips are allocated and rewritten (DMA of", "// the real metadata, or CPU) before the texture is bound: adopting that fill would clear the"),
    ("730ed40a", DS, 3138, "// registers DCC), the host image keeps stale memory instead of the (0,0,0,1) clear and", "// the composite pass overwrites the whole scene with it (black cutscene frames)."),
    ("730ed40a", DS, 3142, "(void)texture_cache.AdoptPendingDccForTexture(id, descriptor.MetaAddr() << 8u);", "}"),
    ("730ed40a", DS, 3268, "(void)texture_cache.AdoptPendingDccForTexture(memo_slot.image_id, meta_address);", "}"),
    ("730ed40a", DS, 3547, "if (rt.base.addr == image.info.data.address && rt.dcc_addr.addr == address &&", "DecodePackedColorClear(format, rt.clear_word0.word0, rt.clear_word1.word1,"),
    ("730ed40a", DS, 3571, "if (dcc_trace || log_count++ < 32) {", 'LOGF("MaterializeDeferredDccClear: image=0x%016" PRIx64 " dcc=0x%016" PRIx64'),
    (F16M, RD5, 84, "B2KEY base=0x0000000510d10000 dcc=0x000000056d898000 reason=r1", "B2KEY"),
    (F16M, RD5, 86, "B2KEY base=0x0000000511650000 dcc=0x0000000570aee000 reason=r2", "B2KEY"),
    (F16M, RD5, 91, "B3KEY shader=0xa572ee17a880e71c addr=0x000000056d898000 class=tracked n=9345", "B3KEY"),
    (F16M, RD5, 117, "B3KEY shader=0xa572ee17a880e71c addr=0x0000000570b24000 class=tracked n=10", "B3KEY"),
    (F16M, RD5, 118, "B3KEY shader=0xa572ee17a880e71c addr=0x0000000570aee000 class=tracked n=10", "B3KEY"),
    (F16M, RD5, 126, "B3KEY shader=0xa572ee17a880e71c addr=0x0000000571006000 class=tracked n=10", "B3KEY"),
]


def show(cache, c, p):
    key = c + ":" + p
    if key not in cache:
        out = subprocess.run(["git", "-C", REPO, "show", key], capture_output=True)
        cache[key] = out.stdout.decode("utf-8").split(chr(10)) if out.returncode == 0 else None
    return cache[key]


def ok_at(lines, n, anchor, nxt):
    return lines is not None and len(lines) > n and lines[n - 1].strip().startswith(anchor) and lines[n].strip().startswith(nxt)


def main():
    cache = {}
    if MODE == "text":
        text = open(sys.argv[2], encoding="utf-8").read()
        have = {(c, p, n) for c, p, n, _, _ in REFS}
        missing = 0
        found = re.findall(r"`([0-9a-f]{8}):([A-Za-z0-9_./]+):(\d+)`", text)
        for c, p, n in found:
            p = SHORT.get(p, p)
            if (c, p, int(n)) not in have:
                print("MISSING", c, p, n)
                missing += 1
        print("text links", len(found), "missing", missing)
        print("ALL OK" if missing == 0 and found else "FAILED")
        return 0 if missing == 0 and found else 1
    bad = 0
    for c, p, n, anchor, nxt in REFS:
        lines = show(cache, c, p)
        good = ok_at(lines, n, anchor, nxt)
        if MODE == "neg":
            good = not ok_at(lines, n + 1, anchor, nxt)
        print(("OK  " if good else "BAD ") + c + ":" + p + ":" + str(n))
        bad += 0 if good else 1
    print(("neg " if MODE == "neg" else "") + "links", len(REFS), "bad", bad)
    print("ALL OK" if bad == 0 else "FAILED")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

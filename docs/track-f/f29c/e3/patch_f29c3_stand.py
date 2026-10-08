# F29c3 (HPP-713, ROADMAP s122 item 645(v)): stand arm B12-9b - the hook form hook=bitonly (between the walks of the first
# and the second mapped range the region bit is announced, Libs::Graphics::BdaNoteRegionWrite, with NO page write and NO
# stamp move), the fields bit1 (region bit still pending right after the first pass, bitonly arms) and late_bit_skips
# (first-visit skips by a clear bit in the passes after the first, every arm). Form of the hook - the demonstration
# 7417f704:docs/track-f/f29d/demo_bitonly.py. Only tests/B12BdaStampStand.cpp; the model lines 1-397 keep their numbers
# (line 48 is replaced in place) so that the anchors of 7417f704:docs/track-f/f29d/mut_f29d.py stay valid.
# Usage: python patch_f29c3_stand.py <file>   LF in, LF out (write_bytes); every anchor must match exactly once.
import hashlib
import sys

T = "\t"
NL = "\n"
F = sys.argv[1]
raw = open(F, "rb").read()
if b"\r" in raw:
    print("CR in the file - refuse")
    sys.exit(1)
text = raw.decode("utf-8")
before = text.split(NL)

EDITS = [
    # usage line of the header comment, replaced in place (no line count change)
    ("// Usage: b12_bdastamp_stand <hole|nob1|split|touch> <upper|lower|none> <passes> <iters> [hook=<upper|lower>]",
     "// Usage: b12_bdastamp_stand <hole|nob1|split|touch> <upper|lower|none> <passes> <iters> [hook=<upper|lower|bitonly>]"),
    # description of the new form, before main (after the model)
    ("} // namespace" + NL + NL + "int main(int argc, char** argv) {",
     "} // namespace" + NL + NL +
     "// Track F, F29c3 (HPP-713, ROADMAP s122 item 645(v)): hook=bitonly (layout hole, write none only) - the hook announces the" + NL +
     "// region bit (Libs::Graphics::BdaNoteRegionWrite, the bit of the real ChangeState<Cpu, true>) with NO page write and NO" + NL +
     "// stamp move: at the late visit after a skip the state is \"witness equal to the stamp, bit set\" (in the emulator - the" + NL +
     "// window of a guest write whose bit is visible before its region epoch). bit1 - iterations whose region bit is still" + NL +
     "// pending right after the first pass (bitonly arms); late_bit_skips - first visits skipped by a clear bit in the passes" + NL +
     "// after the first (every arm). For bitonly no page is written: hlost / hdirty / hlost1 are not counted (0)." + NL +
     "int main(int argc, char** argv) {"),
    ("\"[hook=<upper|lower>]", "\"[hook=<upper|lower|bitonly>]"),
    (T + "const bool     h_low  = std::strcmp(hook_s, \"hook=lower\") == 0;",
     T + "const bool     h_low  = std::strcmp(hook_s, \"hook=lower\") == 0;" + NL +
     T + "const bool     h_bit  = std::strcmp(hook_s, \"hook=bitonly\") == 0; // F29c3"),
    (T + "const bool     h_any  = h_up || h_low;", T + "const bool     h_any  = h_up || h_low || h_bit;"),
    (T + "if ((argc == 6 && !h_any) || (none && !h_any) || (nob1 && h_low)) {",
     T + "if ((argc == 6 && !h_any) || (none && !h_any) || (nob1 && h_low) || (h_bit && (!hole || !none))) {"),
    (T + "uint64_t       scan_passes = 0, rw_min = UINT64_MAX, rw_max = 0;",
     T + "uint64_t       scan_passes = 0, rw_min = UINT64_MAX, rw_max = 0;" + NL +
     T + "uint64_t       bit1 = 0, late_bit_skips = 0; // F29c3"),
    (T * 2 + "bool           pass_done;", T * 2 + "bool           pass_done;" + NL + T * 2 + "bool           bit_only; // F29c3"),
    ("} hs {&tracker, 0, page, 0, &cache, false, 0, false};", "} hs {&tracker, 0, page, 0, &cache, false, 0, false, h_bit};"),
    (T * 4 + "s->tracker->MarkRegionAsCpuModified(s->address, s->size); // the real ChangeState<Cpu, true>",
     T * 4 + "if (s->bit_only) { // F29c3: the bit alone, no page write, no stamp move" + NL +
     T * 5 + "Libs::Graphics::BdaNoteRegionWrite(s->address / TRACKER_REGION_SIZE);" + NL +
     T * 4 + "} else {" + NL +
     T * 5 + "s->tracker->MarkRegionAsCpuModified(s->address, s->size); // the real ChangeState<Cpu, true>" + NL +
     T * 4 + "}"),
    (T * 3 + "const auto l0 = cache.lskip;" + NL + T * 3 + "context.Prepare();",
     T * 3 + "const auto l0 = cache.lskip;" + NL + T * 3 + "const auto b0 = cache.bit_skipped;" + NL + T * 3 + "context.Prepare();" + NL +
     T * 3 + "if (p == 0 && h_bit && Libs::Graphics::BdaRegionWritePending(hs.address / TRACKER_REGION_SIZE)) {" + NL +
     T * 4 + "bit1++;" + NL + T * 3 + "}"),
    (T * 4 + "late_lskips += cache.lskip - l0;",
     T * 4 + "late_lskips += cache.lskip - l0;" + NL + T * 4 + "late_bit_skips += cache.bit_skipped - b0;"),
    (T * 3 + "if (hs.fired) {" + NL + T * 4 + "hfired++;",
     T * 3 + "if (hs.fired && h_bit) {" + NL + T * 4 + "hfired++;" + NL + T * 3 + "} else if (hs.fired) {" + NL + T * 4 + "hfired++;"),
    ("\"hlost1=%llu", "\"hlost1=%llu bit1=%llu late_bit_skips=%llu"),
    (T + " " * 12 + "static_cast<unsigned long long>(hlost1));",
     T + " " * 12 + "static_cast<unsigned long long>(hlost1), static_cast<unsigned long long>(bit1)," + NL +
     T + " " * 12 + "static_cast<unsigned long long>(late_bit_skips));"),
]

for old, new in EDITS:
    n = text.count(old)
    if n != 1:
        print("ANCHOR COUNT %d: %r" % (n, old[:100]))
        sys.exit(1)
    text = text.replace(old, new)

after = text.split(NL)
# the model and the header keep their line numbers: lines 1..408 equal except line 48
diff_lines = [i + 1 for i in range(408) if before[i] != after[i]]
if diff_lines != [48]:
    print("MODEL LINES MOVED OR CHANGED:", diff_lines[:20])
    sys.exit(1)
open(F, "wb").write(text.encode("utf-8"))
print("PATCH OK edits %d lines %d -> %d sha256 %s -> %s" % (len(EDITS), len(before), len(after),
      hashlib.sha256(raw).hexdigest()[:16], hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]))

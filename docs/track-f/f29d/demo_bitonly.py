# F29d (HPP-703, Red Team): DEMONSTRATION ONLY (not a proposed patch, never committed) that the uncaught mutant
# l2a_late_takes_bit_at_check is observable in the stand MODEL. In the worktree C:/kyty/f287/f29d/wt (726e751e) the stand
# gets a hook form "hook=bitonly" - between the walks of the first and the second mapped range the region bit is announced
# (Libs::Graphics::BdaNoteRegionWrite) with NO page write and NO stamp move: the state "witness equal to the stamp, bit
# set" at the late visit, which in the emulator is the window of a guest write whose bit is visible before its region
# epoch is (a stamp read that precedes the epoch store). A field bit1 counts the iterations whose region bit is still
# pending right after the first pass. Then: build the clean+demo stand, and the demo + mutant l2a stand; run the arm
# hole none 2 <iters> hook=bitonly with KYTY_FIX_B12=1, KYTY_BDA_WRITE_BITS=1, KYTY_BDA_EPOCH_CACHE=0; restore the file.
# Usage: python demo_bitonly.py <iters>
import os
import re
import shutil
import subprocess
import sys

WT = "C:/kyty/f287/f29d/wt"
F = WT + "/tests/B12BdaStampStand.cpp"
D = "C:/kyty/f287/f29d"
OUT = D + "/demo"
NL = chr(10)
T = chr(9)
BS = chr(92)

EDITS = [
    # argument parsing: hook=bitonly is a hook form
    (T + "const bool     h_low  = std::strcmp(hook_s, \"hook=lower\") == 0;",
     T + "const bool     h_low  = std::strcmp(hook_s, \"hook=lower\") == 0;" + NL +
     T + "const bool     h_bit  = std::strcmp(hook_s, \"hook=bitonly\") == 0;"),
    (T + "const bool     h_any  = h_up || h_low;", T + "const bool     h_any  = h_up || h_low || h_bit;"),
    # the hook state carries the form
    (T + T + "bool           pass_done;", T + T + "bool           pass_done;" + NL + T + T + "bool           bit_only;"),
    ("} hs {&tracker, 0, page, 0, &cache, false, 0, false};", "} hs {&tracker, 0, page, 0, &cache, false, 0, false, h_bit};"),
    (T * 4 + "s->tracker->MarkRegionAsCpuModified(s->address, s->size); // the real ChangeState<Cpu, true>",
     T * 4 + "if (s->bit_only) {" + NL + T * 5 + "Libs::Graphics::BdaNoteRegionWrite(s->address / TRACKER_REGION_SIZE);" + NL +
     T * 4 + "} else {" + NL + T * 5 + "s->tracker->MarkRegionAsCpuModified(s->address, s->size);" + NL + T * 4 + "}"),
    # bit1: the region bit still pending right after the first pass
    (T * 3 + "context.Prepare();" + NL + T * 3 + "if (h_any && hs.fired && !hs.pass_done) {",
     T * 3 + "context.Prepare();" + NL + T * 3 + "if (p == 0 && h_bit && Libs::Graphics::BdaRegionWritePending(BASE / TRACKER_REGION_SIZE)) {" +
     NL + T * 4 + "bit1++;" + NL + T * 3 + "}" + NL + T * 3 + "if (h_any && hs.fired && !hs.pass_done) {"),
    (T + "uint64_t       scan_passes = 0, rw_min = UINT64_MAX, rw_max = 0;",
     T + "uint64_t       scan_passes = 0, rw_min = UINT64_MAX, rw_max = 0;" + NL + T + "uint64_t       bit1 = 0;"),
    (T + "std::fflush(stdout);", T + "std::printf(\"B12demo bit1=%llu\" \"" + BS + "n\", static_cast<unsigned long long>(bit1));" + NL +
     T + "std::fflush(stdout);"),
]
MUT_L2A = (T * 4 + "    !(use_bits && Libs::Graphics::BdaRegionWritePending(index))) {",
           T * 4 + "    !(use_bits && Libs::Graphics::BdaTakeRegionWrite(index))) {")


def build():
    env = dict(os.environ)
    env["F29D_WT"] = "C:" + BS + "kyty" + BS + "f287" + BS + "f29d" + BS + "wt"
    env["F29D_BUILD"] = "C:" + BS + "kyty" + BS + "f287" + BS + "f29d" + BS + "build"
    r = subprocess.run(["cmd", "/c", D.replace("/", BS) + BS + "build_f29d.cmd", "target", "b12_bdastamp_stand"],
                       capture_output=True, env=env, timeout=600)
    return r.returncode, r.stdout.decode("utf-8", "replace")[-600:]


def run(exe, iters):
    e = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
    e.update({"KYTY_FIX_B12": "1", "KYTY_BDA_WRITE_BITS": "1", "KYTY_BDA_EPOCH_CACHE": "0"})
    r = subprocess.run([exe, "hole", "none", "2", iters, "hook=bitonly"], capture_output=True, env=e, timeout=300)
    out = r.stdout.decode("utf-8", "replace")
    kv = dict(re.findall(r"(\w+)=([^ " + NL + "]+)", out))
    keys = ["fix_b12", "hook_fired", "lskip", "late_lskips", "bit_skips", "region_skips", "region_scans", "rewalk", "bit1"]
    return r.returncode, " ".join("%s=%s" % (k, kv.get(k, "?")) for k in keys)


def main():
    iters = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    orig = open(F, "rb").read()
    text = orig.decode("utf-8")
    for old, new in EDITS:
        if text.count(old) != 1:
            print("ANCHOR COUNT %d: %r" % (text.count(old), old[:80]))
            sys.exit(1)
        text = text.replace(old, new)
    try:
        for name, src in (("demo_clean", text), ("demo_l2a", text.replace(MUT_L2A[0], MUT_L2A[1]))):
            if name == "demo_l2a" and src == text:
                print("MUTANT ANCHOR NOT FOUND")
                sys.exit(1)
            open(F, "wb").write(src.encode("utf-8"))
            rc, tail = build()
            if rc != 0:
                print(name, "BUILD FAILED", tail)
                continue
            exe = OUT + "/" + name + ".exe"
            shutil.copyfile(D + "/build/b12_bdastamp_stand.exe", exe)
            rc, line = run(exe, iters)
            print("%s rc=%d %s" % (name, rc, line))
    finally:
        open(F, "wb").write(orig)
    assert open(F, "rb").read() == orig
    rc, tail = build()
    print("restored, clean stand rebuilt rc", rc)


main()

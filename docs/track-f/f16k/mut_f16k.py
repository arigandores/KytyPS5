"""Track F, F16k (HPP-583): mutants of the F16k code against the test site --f16k-only (each must be caught - some arm
FAILs). For each mutant: replace one exact string in one worktree file (count must be 1), build the test target with
build_f16k.cmd, run run_tests_f16k.py f16k into mut/<name>.txt, restore the file byte for byte. Run under the watchdog
by the caller; one mutant per call:

    python mut_f16k.py <name>

The last line of mut/<name>.result is CAUGHT / NOT CAUGHT / ERROR.
"""
import os
import shutil
import subprocess
import sys

WT = "C:/kyty/f287/f16k/wt/"
R = WT + "src/graphics/host_gpu/renderer/"
MUTANTS = {
    # the exact answer never decides (the old bucket answer at the FCE acquisition)
    "m1_no_decide": (R + "cache/textureCache.cpp",
                     "if (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {",
                     "if (false && f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {"),
    # the ring is written with both knobs off
    "m2_ring_always": (R + "cache/bufferCache.cpp",
                       "if (DiagF5::ExactRingOn()) [[unlikely]] {\n\t\tfor (auto bucket = first; bucket <= last; bucket++) {\n\t\t\tauto& ring",
                       "if (true) [[unlikely]] {\n\t\tfor (auto bucket = first; bucket <= last; bucket++) {\n\t\t\tauto& ring"),
    # the exact check decides on a draw acquisition too
    "m3_decide_draw": (R + "cache/textureCache.cpp",
                       ": m_out(out), m_decide(fce && DiagF5::FixCmuOn()), m_rt_count(!fce && DiagF5Id::On()) {",
                       ": m_out(out), m_decide(DiagF5::FixCmuOn()), m_rt_count(!fce && DiagF5Id::On()) {"),
    # tracked and tracked_other swapped
    "m4_tracked_swap": (R + "diagF5.cpp",
                        ": addr == d.tracked        ? CsClass::Tracked\n\t\t                                             : CsClass::TrackedOther;",
                        ": addr == d.tracked        ? CsClass::TrackedOther\n\t\t                                             : CsClass::Tracked;"),
    # K = 8 fallback test off by one (count >= K)
    "m5_ring_offbyone": (R + "cache/bufferCache.cpp",
                         "if (ring->second.count > ExactRing::K && oldest > since) {",
                         "if (ring->second.count >= ExactRing::K && oldest > since) {"),
    # kept_applied not distinguished from kept
    "m6_no_applied": (R + "cache/textureCache.cpp",
                      "\t\tf5.Cleared(); // Track F, F16k: kept_applied\n",
                      "\n"),
    # the reason R5 / R6 swapped in the adoption
    "m7_r5_r6": (R + "cache/textureCache.cpp",
                 "? DiagF5Id::DccMiss {DiagF5Id::Miss::R5, 0}",
                 "? DiagF5Id::DccMiss {DiagF5Id::Miss::R6, 0}"),
}


def main():
    name = sys.argv[1]
    path, old, new = MUTANTS[name]
    os.makedirs("mut", exist_ok=True)
    original = open(path, "rb").read()
    text = original.decode("utf-8")
    if text.count(old) != 1:
        open("mut/%s.result" % name, "w").write("anchor count %d\nERROR\n" % text.count(old))
        print("ERROR anchor", text.count(old))
        return 2
    try:
        open(path, "wb").write(text.replace(old, new).encode("utf-8"))
        b = subprocess.run(["cmd", "/c", "C:\\kyty\\f287\\f16k\\build_f16k.cmd", "target",
                            "shader_recompiler_compute_tests"], capture_output=True, text=True, errors="replace")
        if b.returncode != 0:
            open("mut/%s.result" % name, "w").write(b.stdout[-3000:] + b.stderr[-2000:] + "\nERROR\n")
            print("ERROR build")
            return 2
        exe = "mut/%s/shader_recompiler_compute_tests.exe" % name
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        shutil.copy("build/shader_recompiler_compute_tests.exe", exe)
        r = subprocess.run([sys.executable, "run_tests_f16k.py", "f16k", exe, "mut/%s.txt" % name],
                           capture_output=True, text=True, errors="replace")
        caught = r.returncode != 0
        fails = [l for l in open("mut/%s.txt" % name, encoding="utf-8").read().splitlines()
                 if "FAIL" in l or "failed at" in l]
        open("mut/%s.result" % name, "w", encoding="utf-8", newline="\n").write(
            "\n".join(fails[:12]) + "\n" + ("CAUGHT" if caught else "NOT CAUGHT") + "\n")
        print(name, "CAUGHT" if caught else "NOT CAUGHT")
        for l in fails[:6]:
            print("  ", l[:200])
        return 0
    finally:
        open(path, "wb").write(original)


sys.exit(main())

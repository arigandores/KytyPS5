"""Track F, F16k2 (HPP-590, ROADMAP s122 item 496(b)): mutants of the F16k2 code against the test site --f16k-only, one per
new case (each must be caught - some arm FAILs). Copy of f16k/mut_f16k.py with the F16k2 mutants. For each mutant: replace
one exact string in one worktree file (count must be 1), build the test target with build_f16k2.cmd, run
run_tests_f16k2.py f16k into mut/<name>.txt, restore the file byte for byte. Run under the watchdog by the caller; one
mutant per call:

    python mut_f16k2.py <name>

The last line of mut/<name>.result is CAUGHT / NOT CAUGHT / ERROR.
"""
import os
import shutil
import subprocess
import sys

WT = "C:/kyty/f287/f16k/wt/"
R = WT + "src/graphics/host_gpu/renderer/"
MUTANTS = {
    # RC1: wr_after=large never set (D18)
    "m8_no_large": (R + "pipeline/descriptors.cpp",
                    "\t\tconst bool large = exact.seq == 0 && buffers.LargeGpuWriteSeq() > since;\n",
                    "\t\tconst bool large = false && exact.seq == 0 && buffers.LargeGpuWriteSeq() > since;\n"),
    # RC2: cpu_mod without the epoch since the fill - the old "dirty now" (D19: a CPU write uploaded after the fill)
    "m9_cpu_now_only": (R + "pipeline/descriptors.cpp",
                        "\t\te.cpu_mod = cpu_now || !seen || fill_epoch == 0 || "
                        "buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch\n",
                        "\t\te.cpu_mod = cpu_now\n"),
    # RC2: no fill seen reads 0 (D19: the address without a fill)
    "m10_nofill_zero": (R + "pipeline/descriptors.cpp",
                        "\t\te.cpu_mod = cpu_now || !seen || fill_epoch == 0 || "
                        "buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch\n",
                        "\t\te.cpu_mod = cpu_now || (seen && buffers.F5IdRangeWriteEpoch(e.dcc, e.dcc_size) != fill_epoch)\n"),
    # RC2: cpu_mod always 1 (D19: no CPU write after the fill reads 0)
    "m11_cpu_always": (R + "pipeline/descriptors.cpp",
                       "\t\t                ? 1\n\t\t                : 0;\n",
                       "\t\t                ? 1\n\t\t                : 1;\n"),
    # RC3: the end of the dispatch does not count stamp_late (D20)
    "m12_no_stamp_late": (R + "cache/textureCache.cpp",
                          "\t\tm_f5id_stamp_late = true;\n\t\tDiagF5Id::NoteStampLate();\n",
                          "\t\tm_f5id_stamp_late = true;\n"),
    # RC4: the probe does not say cpu (K8: why=cpu)
    "m13_no_why_cpu": (R + "cache/textureCache.cpp",
                       "\t\t\tf5_probe->cpu         = true; // Track F, F16k2 (RC4): why=cpu\n",
                       "\n"),
    # RC4: f5cmu_exact_cpu not counted (K8 counter delta)
    "m14_no_exact_cpu": (R + "cache/textureCache.cpp",
                         "\t\t\t\t\t\tDiagF5::Add(DiagF5::Counter::F5CmuExactCpu); // Track F, F16k2 (RC4)\n",
                         "\n"),
    # RC5: no cmask_fce_nohit line (K7 with KYTY_FIX_F5CMU)
    "m15_no_nohit": (R + "pipeline/descriptors.cpp",
                     "\t\t\tif (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&\n",
                     "\t\t\tif (false && DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&\n"),
    # RC5: the line printed for off / fresh too (K7 without KYTY_FIX_F5CMU: no line)
    "m16_nohit_off": (R + "pipeline/descriptors.cpp",
                      "\t\t\tif (DiagF5::On() && b42.kind != FixB42Kind::Hit && f5_cmu.fix != DiagF5::CmuFix::Off &&\n"
                      "\t\t\t    f5_cmu.fix != DiagF5::CmuFix::Fresh) [[unlikely]] {\n",
                      "\t\t\tif (DiagF5::On() && b42.kind != FixB42Kind::Hit) [[unlikely]] {\n"),
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
        b = subprocess.run(["cmd", "/c", "C:\\kyty\\f287\\f16k2\\build_f16k2.cmd", "target",
                            "shader_recompiler_compute_tests"], capture_output=True, text=True, errors="replace")
        if b.returncode != 0:
            open("mut/%s.result" % name, "w").write(b.stdout[-3000:] + b.stderr[-2000:] + "\nERROR\n")
            print("ERROR build")
            return 2
        exe = "mut/%s/shader_recompiler_compute_tests.exe" % name
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        shutil.copy("C:/kyty/f287/f16k/build/shader_recompiler_compute_tests.exe", exe)
        r = subprocess.run([sys.executable, "run_tests_f16k2.py", "f16k", exe, "mut/%s.txt" % name],
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

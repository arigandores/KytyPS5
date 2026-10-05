"""Track F, F16o2 (HPP-599, ROADMAP s122 item 507(b)(5)): mutants of the deferred-clear code (RC1 of F16p) against the
test site --f16k-only (eleven arms of run_tests_f16o2.py) - each must be caught (some arm FAILs). Copy of
f16o/mut_f16o.py with the F16o2 mutants. For each mutant: replace one exact string in one worktree file (count must be
1), build the test target with build_f16o2.cmd, run run_tests_f16o2.py f16k into mut/<name>.txt, restore the file byte
for byte. Run under the watchdog by the caller (mrun.sh); one mutant per call:

    python mut_f16o2.py <name>

The last line of mut/<name>.result is CAUGHT / NOT CAUGHT / ERROR.
"""
import os
import shutil
import subprocess
import sys

WT = "C:/kyty/f287/f16k/wt/"
R = WT + "src/graphics/host_gpu/renderer/"
TC = R + "cache/textureCache.cpp"
DC = R + "diagF5.cpp"
DS = R + "pipeline/descriptors.cpp"
MUTANTS = {
    # (1) the old adopt reading (RC1): kept_applied at the adoption (D4, D4e: fix=kept why=deferred)
    "m31_adopt_applied": (TC, "\t\tf26.Deferred(this, id);\n", "\t\tf26.Applied(true, DiagF5::CmuWhy::Mask);\n"),
    # (2) no mark left by the reported kept why=deferred event (D4, D4e: one mark)
    "m32_no_mark": (TC, "\t\tif (m_fix && e.fix == F::Kept && e.why == DiagF5::CmuWhy::Deferred && m_defer_cache != nullptr) {\n",
                    "\t\tif (false) {\n"),
    # (3) the mark is not removed when taken (D4: the mark was not taken)
    "m33_mark_kept_after_take": (TC, "\tm_f26_deferred.erase(found);\n\tm_f26_deferred_count.fetch_sub(1, std::memory_order_relaxed);\n\treturn true;\n",
                                 "\treturn true;\n"),
    # (3) a declined outcome counted as cleared (D4e: f26_deferred_declined 1, f26_kept_applied 0)
    "m34_declined_as_cleared": (DS, "\t\t\tDiagF5::Add(m_cleared ? DiagF5::Counter::F26KeptApplied : DiagF5::Counter::F26DeferredDeclined);\n",
                                "\t\t\tDiagF5::Add(DiagF5::Counter::F26KeptApplied);\n"),
    # (3) the clear is not reported as cleared (D4: result=cleared)
    "m35_no_cleared": (DS, "\tf26_apply.Cleared(); // Track F, F16o2: every layer of the mask was cleared above\n", ""),
    # (3) no dcc_stale_apply line (D4, D4e lines; Z print identity)
    "m36_no_apply_line": (DC, "\tEmitLine(FormatDccStaleApply(line));\n", "\t(void)line;\n"),
    # (3) the line limit of dcc_stale_apply not n <= 256 (L)
    "m37_apply_limit": (DC, "\tif (line.n == 0 || line.n > 256) { // the limit of dcc_stale: only when the adopt's line n was printed\n",
                        "\tif (line.n == 0 || line.n > 257) { // the limit of dcc_stale: only when the adopt's line n was printed\n"),
    # (3) the layer mask not reported (D4, D4e: layers=0x00000001)
    "m38_no_layers": (DS, "\tf26_apply.Layers(mask); // Track F, F16o2\n", ""),
    # (3) the count's fast path never takes (D4: the mark was not taken)
    "m39_fast_path_never": (TC, "\tif (m_f26_deferred_count.load(std::memory_order_relaxed) == 0) {\n\t\treturn false;\n\t}\n\tstd::scoped_lock lock {m_lock};\n",
                            "\tif (true) {\n\t\treturn false;\n\t}\n\tstd::scoped_lock lock {m_lock};\n"),
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
        b = subprocess.run(["cmd", "/c", "C:\\kyty\\f287\\f16o2\\build_f16o2.cmd", "target",
                            "shader_recompiler_compute_tests"], capture_output=True, text=True, errors="replace")
        if b.returncode != 0:
            open("mut/%s.result" % name, "w").write(b.stdout[-3000:] + b.stderr[-2000:] + "\nERROR\n")
            print("ERROR build")
            return 2
        exe = "mut/%s/shader_recompiler_compute_tests.exe" % name
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        shutil.copy("C:/kyty/f287/f16k/build/shader_recompiler_compute_tests.exe", exe)
        r = subprocess.run([sys.executable, "run_tests_f16o2.py", "f16k", exe, "mut/%s.txt" % name],
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

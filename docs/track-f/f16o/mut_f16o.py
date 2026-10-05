"""Track F, F16o (HPP-595, ROADMAP s122 item 504(e)(6)): mutants of the KYTY_FIX_F26 code against the test site --f16k-only
(eleven arms of run_tests_f16o.py), one per new case - each must be caught (some arm FAILs). Copy of
f16k2/mut_f16k2.py with the F16o mutants. For each mutant: replace one exact string in one worktree file (count must be
1), build the test target with build_f16o.cmd, run run_tests_f16o.py f16k into mut/<name>.txt, restore the file byte for
byte. Run under the watchdog by the caller (mrun.sh); one mutant per call:

    python mut_f16o.py <name>

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
MUTANTS = {
    # (2) the exact answer never decides at the DCC sites (D1, D1b, D4, D4b with KYTY_FIX_F26: kept expected)
    "m17_no_decide": (TC, "\t\tm_probe.exact_decides = m_fix;\n", "\t\tm_probe.exact_decides = false;\n"),
    # (2) the exact answer decides without the knob (=0 path: D1, D4 in the arms with a ring and KYTY_FIX_F26 0)
    "m18_decide_always": (TC, "\t\tm_probe.exact_decides = m_fix;\n", "\t\tm_probe.exact_decides = true;\n"),
    # (2) the ring is not written with KYTY_FIX_F26 alone (knob read; D1 would be a fallback)
    "m19_ring_no_f26": (DC, "\tstatic const bool on = FixCmuOn() || FixF26On() || DiagF5Id::On(); // Track F, F16o: KYTY_FIX_F26 too\n",
                        "\tstatic const bool on = FixCmuOn() || DiagF5Id::On(); // Track F, F16o: KYTY_FIX_F26 too\n"),
    # (2) the FCE acquisition reads KYTY_FIX_F26 (K2: the old decision expected with KYTY_FIX_F5CMU 0)
    "m20_fce_reads_f26": (TC, "\t    : m_out(out), m_decide(fce && DiagF5::FixCmuOn()), m_rt_count(!fce && DiagF5Id::On()) {\n",
                          "\t    : m_out(out), m_decide(fce && (DiagF5::FixCmuOn() || DiagF5::FixF26On())), m_rt_count(!fce && DiagF5Id::On()) {\n"),
    # (2) a crossing write kept (D3, D4c: exact_stale - dropped)
    "m21_crossing_kept": (TC, "\t\tif (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {\n",
                          "\t\tif (f5_probe->exact_decides && !f5_probe->fallback) {\n"),
    # (2) a fallback kept (D2, D4d: fallback - dropped)
    "m22_fallback_kept": (TC, "\t\tif (f5_probe->exact_decides && !f5_probe->exact_stale && !f5_probe->fallback) {\n",
                          "\t\tif (f5_probe->exact_decides && !f5_probe->exact_stale) {\n"),
    # (2) the adopt site without the scope's probe (D4: kept expected with KYTY_FIX_F26)
    "m23_adopt_no_probe": (TC, "\tconst bool f5_stale = PendingDccFillStale(metadata_address, found->second, image->info.data.address, f26.Arm());\n",
                           "\tconst bool f5_stale = PendingDccFillStale(metadata_address, found->second, image->info.data.address, nullptr);\n"),
    # (3) prepare: kept_applied never (D1: fix=kept_applied)
    "m24_prepare_never_applied": (TC, "\tf26.Applied(metadata.clear_mask != f5id_mask0, DiagF5::CmuWhy::NoLayer);\n",
                                  "\tf26.Applied(false, DiagF5::CmuWhy::NoLayer);\n"),
    # (3) adopt: kept_applied always (D4b: fix=kept why=mask)
    "m25_adopt_always_applied": (TC, "\tf26.Applied(found->second.clear_mask != 0, DiagF5::CmuWhy::Mask);\n",
                                 "\tf26.Applied(true, DiagF5::CmuWhy::Mask);\n"),
    # (3) no dcc_stale line (D1-D4 lines, Z print identity)
    "m26_no_line": (DC, "\tEmitLine(FormatDccStale(n, line));\n", "\t(void)line;\n"),
    # (3) a line on a decision the bucket check did not call stale (D0f, D4f: no line)
    "m27_line_on_fresh": (TC, "\t\tif (DiagF5::On() && (m_probe_on ? m_probe.bucket_stale : stale)) [[unlikely]] {\n",
                          "\t\tif (DiagF5::On()) [[unlikely]] {\n"),
    # (4) the f26_* counters not counted (D1-D4 deltas, Z identity)
    "m28_no_counters": (TC, "\t\tif (m_fix) {\n\t\t\tswitch (e.fix) {\n", "\t\tif (false) {\n\t\t\tswitch (e.fix) {\n"),
    # (5) the cmask_fce limit back to 64 (L)
    "m29_cmask_limit_64": (DC, "\tif (n > 1024) { // Track F, F16o (item 504(e)(5)): was 64; output of the measurement only\n",
                           "\tif (n > 64) { // Track F, F16o (item 504(e)(5)): was 64; output of the measurement only\n"),
    # (3) the dcc_stale limit not 256 (L)
    "m30_dcc_limit_64": (DC, "\tconst auto n = g_dcc_stale_events.fetch_add(1, std::memory_order_relaxed) + 1;\n\tif (n > 256) {\n",
                         "\tconst auto n = g_dcc_stale_events.fetch_add(1, std::memory_order_relaxed) + 1;\n\tif (n > 64) {\n"),
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
        b = subprocess.run(["cmd", "/c", "C:\\kyty\\f287\\f16o\\build_f16o.cmd", "target",
                            "shader_recompiler_compute_tests"], capture_output=True, text=True, errors="replace")
        if b.returncode != 0:
            open("mut/%s.result" % name, "w").write(b.stdout[-3000:] + b.stderr[-2000:] + "\nERROR\n")
            print("ERROR build")
            return 2
        exe = "mut/%s/shader_recompiler_compute_tests.exe" % name
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        shutil.copy("C:/kyty/f287/f16k/build/shader_recompiler_compute_tests.exe", exe)
        r = subprocess.run([sys.executable, "run_tests_f16o.py", "f16k", exe, "mut/%s.txt" % name],
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

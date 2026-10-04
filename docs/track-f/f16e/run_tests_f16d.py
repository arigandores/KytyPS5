"""Track F, F16d (HPP-521): test runs of the KYTY_DIAG_F5 / KYTY_DIAG_F6 code (no game).

    python run_tests_f16d.py site   <shader_recompiler_compute_tests.exe> <out.txt>
    python run_tests_f16d.py modes  <shader_recompiler_compute_tests.exe> <out.txt>
    python run_tests_f16d.py cfg    <shader_cfg_tests.exe> <out.txt>

site  - the test site --diag-f5-only three times: KYTY_DIAG_F5 / KYTY_DIAG_F6 unset, =0, =1 (all other KYTY_* removed);
        each arm must exit 0 and print 'DiagF5F6 test site: ALL OK'; the last line of the file is ALL OK / NOT OK.
modes - the existing texture-cache / metadata modes of the same binary with every KYTY_* removed (base vs patched
        comparison: rc and the last output line per mode).
cfg   - shader_cfg_tests with KYTY_TESTS_CONTINUE=1 KYTY_TESTS_VERBOSE=1 (every other KYTY_* removed); the failing
        test names are listed (compared with the base by the caller).
The working directory of every run is the directory of the executable. Output: one block per run (sha256 of the exe
first).
"""
import hashlib
import os
import subprocess
import sys

MODES = ["--cmask-clear-only", "--dcc-clear-only", "--compute-meta-clear-only", "--htile-clear-only",
         "--image-overlap-only", "--compute-meta-classification-only"]


def clean_env(extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
    env.update(extra)
    return env


def run(exe, args, env, timeout=900):
    p = subprocess.run([exe] + args, cwd=os.path.dirname(exe), env=env, capture_output=True, text=True,
                       errors="replace", timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def main():
    what, exe, out = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    lines = ["exe %s sha256 %s" % (exe.replace("\\", "/"), hashlib.sha256(open(exe, "rb").read()).hexdigest())]
    ok = True
    if what == "site":
        for label, extra in (("unset", {}), ("zero", {"KYTY_DIAG_F5": "0", "KYTY_DIAG_F6": "0"}),
                             ("one", {"KYTY_DIAG_F5": "1", "KYTY_DIAG_F6": "1"})):
            rc, text = run(exe, ["--diag-f5-only"], clean_env(extra))
            good = rc == 0 and "DiagF5F6 test site: ALL OK" in text
            ok &= good
            lines.append("=== arm %s rc=%d %s" % (label, rc, "OK" if good else "FAIL"))
            lines += [l for l in text.splitlines() if l.startswith(("[f16d]", "DiagF5F6", "ShaderRecompilerComputeTests"))]
    elif what == "modes":
        for mode in MODES:
            rc, text = run(exe, [mode], clean_env({}))
            tail = [l for l in text.splitlines() if l.strip()][-1:] or ["<no output>"]
            lines.append("mode %s rc=%d last=%s" % (mode, rc, tail[0][:200]))
            ok &= rc == 0
    elif what == "cfg":
        rc, text = run(exe, [], clean_env({"KYTY_TESTS_CONTINUE": "1", "KYTY_TESTS_VERBOSE": "1"}), timeout=1800)
        fails = sorted(set(l.strip() for l in text.splitlines() if "FAIL" in l or "failed" in l.lower()))
        lines.append("rc=%d failing-lines=%d" % (rc, len(fails)))
        lines += fails
        lines += [l for l in text.splitlines() if l.strip()][-3:]
        ok = True  # compared with the base list by the caller
    lines.append("ALL OK" if ok else "NOT OK")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines[-12:]))
    return 0 if ok else 1


sys.exit(main())

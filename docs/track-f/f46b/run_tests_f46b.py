"""Track F, F46b (HPP-799, ROADMAP s122 item 702(e)(5)): copy of f16o2/run_tests_f16o2.py with six KYTY_F26_TINT arms
(the dcc / pending addresses of the D block of CheckF16k: 0x207400000, 0x207c00000) - seventeen arms of --f16k-only.
Was: Track F, F16o (HPP-595, ROADMAP s122 item 504(e)(6)): copy of f16k2/run_tests_f16k2.py with four KYTY_FIX_F26 arms
(f5_f26, f5_f26_id, f5_fix_f26, f26_only) - eleven arms of --f16k-only. Was: Track F, F16k (HPP-583, ROADMAP s122 item 492(z)(2)-(3)): test runs of the KYTY_FIX_F5CMU / KYTY_DIAG_F5ID code (no game).
Copy of docs/track-f/f16d/run_tests_f16d.py (modes site / modes / cfg unchanged) with two more modes.

    python run_tests_f16k.py site   <shader_recompiler_compute_tests.exe> <out.txt>
    python run_tests_f16k.py f16k   <shader_recompiler_compute_tests.exe> <out.txt>
    python run_tests_f16k.py same   <site out A> <site out B> <out.txt>
    python run_tests_f16k.py modes  <shader_recompiler_compute_tests.exe> <out.txt>
    python run_tests_f16k.py cfg    <shader_cfg_tests.exe> <out.txt>

site  - the F16d test site --diag-f5-only three times: KYTY_DIAG_F5 / KYTY_DIAG_F6 unset, =0, =1 (every other KYTY_*
        removed - so KYTY_FIX_F5CMU and KYTY_DIAG_F5ID are unset, item 492(z)(3)); each arm must exit 0 and print
        'DiagF5F6 test site: ALL OK'.
f16k  - the F16k test site --f16k-only in seven arms (every other KYTY_* removed): none; F5; F5+FIX; F5+ID; F5+FIX+ID;
        ID without F5; FIX without F5. Each arm must exit 0 and print 'F16k test site: ALL OK'.
same  - item 492(z)(3): the two site outputs are equal byte for byte after their first line (the exe path and sha256).
The working directory of every run is the directory of the executable. The last line of every output file is
ALL OK / NOT OK.
"""
import hashlib
import os
import subprocess
import sys

MODES = ["--cmask-clear-only", "--dcc-clear-only", "--compute-meta-clear-only", "--htile-clear-only",
         "--image-overlap-only", "--compute-meta-classification-only"]

F16K_ARMS = (
    ("none", {}),
    ("f5", {"KYTY_DIAG_F5": "1"}),
    ("f5_fix", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F5CMU": "1"}),
    ("f5_id", {"KYTY_DIAG_F5": "1", "KYTY_DIAG_F5ID": "1"}),
    ("f5_fix_id", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F5CMU": "1", "KYTY_DIAG_F5ID": "1"}),
    ("id_only", {"KYTY_DIAG_F5ID": "1"}),
    ("fix_only", {"KYTY_FIX_F5CMU": "1"}),
    # Track F, F16o (HPP-595, ROADMAP s122 item 504(e)(6)): KYTY_FIX_F26 arms
    ("f5_f26", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F26": "1"}),
    ("f5_f26_id", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F26": "1", "KYTY_DIAG_F5ID": "1"}),
    ("f5_fix_f26", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F5CMU": "1", "KYTY_FIX_F26": "1"}),
    ("f26_only", {"KYTY_FIX_F26": "1"}),
    # Track F, F46b (HPP-799, ROADMAP s122 item 702(e)(4)-(5)): KYTY_F26_TINT arms, keyed by the D block's dcc / pending
    ("f5_f26_id_t1d", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F26": "1", "KYTY_DIAG_F5ID": "1", "KYTY_F26_TINT": "1",
                       "KYTY_F26_TINT_DCC": "0x207400000"}),
    ("f5_f26_id_t1p", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F26": "1", "KYTY_DIAG_F5ID": "1", "KYTY_F26_TINT": "1",
                       "KYTY_F26_TINT_DCC": "0x207c00000"}),
    ("f5_f26_id_t2d", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F26": "1", "KYTY_DIAG_F5ID": "1", "KYTY_F26_TINT": "2",
                       "KYTY_F26_TINT_DCC": "0x207400000"}),
    ("f5_f26_id_t2p", {"KYTY_DIAG_F5": "1", "KYTY_FIX_F26": "1", "KYTY_DIAG_F5ID": "1", "KYTY_F26_TINT": "2",
                       "KYTY_F26_TINT_DCC": "0x207c00000"}),
    ("f5_id_t2p", {"KYTY_DIAG_F5": "1", "KYTY_DIAG_F5ID": "1", "KYTY_F26_TINT": "2", "KYTY_F26_TINT_DCC": "0x207c00000"}),
    ("f26_t1d", {"KYTY_FIX_F26": "1", "KYTY_F26_TINT": "1", "KYTY_F26_TINT_DCC": "0x207400000"}),
)


def clean_env(extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
    env.update(extra)
    return env


def run(exe, args, env, timeout=900):
    p = subprocess.run([exe] + args, cwd=os.path.dirname(exe), env=env, capture_output=True, text=True,
                       errors="replace", timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def head(exe):
    return "exe %s sha256 %s" % (exe.replace("\\", "/"), hashlib.sha256(open(exe, "rb").read()).hexdigest())


def main():
    what = sys.argv[1]
    if what == "same":
        a, b, out = sys.argv[2], sys.argv[3], sys.argv[4]
        la = open(a, "rb").read().split(b"\n")
        lb = open(b, "rb").read().split(b"\n")
        same = la[1:] == lb[1:]
        lines = ["A %s" % a, "  %s" % la[0].decode(), "B %s" % b, "  %s" % lb[0].decode(),
                 "lines after the first: A %d B %d; byte for byte equal: %s" % (len(la) - 1, len(lb) - 1, same)]
        if not same:
            for i, (x, y) in enumerate(zip(la[1:], lb[1:])):
                if x != y:
                    lines.append("first difference at line %d: A %r B %r" % (i + 2, x[:160], y[:160]))
                    break
        lines.append("ALL OK" if same else "NOT OK")
        open(out, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        print("\n".join(lines))
        return 0 if same else 1
    exe, out = os.path.abspath(sys.argv[2]), sys.argv[3]
    lines = [head(exe)]
    ok = True
    if what == "site":
        for label, extra in (("unset", {}), ("zero", {"KYTY_DIAG_F5": "0", "KYTY_DIAG_F6": "0"}),
                             ("one", {"KYTY_DIAG_F5": "1", "KYTY_DIAG_F6": "1"})):
            rc, text = run(exe, ["--diag-f5-only"], clean_env(extra))
            good = rc == 0 and "DiagF5F6 test site: ALL OK" in text
            ok &= good
            lines.append("=== arm %s rc=%d %s" % (label, rc, "OK" if good else "FAIL"))
            lines += [l for l in text.splitlines() if l.startswith(("[f16d]", "DiagF5F6", "ShaderRecompilerComputeTests"))]
    elif what == "f16k":
        for label, extra in F16K_ARMS:
            rc, text = run(exe, ["--f16k-only"], clean_env(extra))
            good = rc == 0 and "F16k test site: ALL OK" in text
            ok &= good
            lines.append("=== arm %s (%s) rc=%d %s" % (label, " ".join("%s=%s" % kv for kv in sorted(extra.items())),
                                                       rc, "OK" if good else "FAIL"))
            keep = [l for l in text.splitlines() if l.startswith(("[f16k]", "F16k", "ShaderRecompilerComputeTests"))]
            lines += keep
            if not good:
                lines += ["  | " + l for l in text.splitlines()[-25:] if l not in keep]
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
    print("\n".join(lines[-14:]))
    return 0 if ok else 1


sys.exit(main())

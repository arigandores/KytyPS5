# FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): memory_tracker_tests and shader_cfg_tests of the worktree build
# C:/kyty/f287/fs9a/build at the defaults (every KYTY_* removed from the environment; KYTY_TESTS_CONTINUE=1,
# KYTY_TESTS_VERBOSE=1). Phase "base" - the build at 0005e11f (before the cherry-picks), phase "fs9" - the build at the
# FS9 HEAD; for fs9 also KYTY_FIX_B13=0 and =1 (reference, not members). Outputs to tests/<phase>/<exe>_<knob>.txt.
#   python run_tests_fs9a.py run <phase>      run the phase
#   python run_tests_fs9a.py compare          member: at the defaults the lines with "failed" (multiset), the
#                                             "ShaderCfgTests: failed:" count, the [test] list and the mtt verdict of
#                                             fs9 = base; FixB13 line of fs9 at defaults = "FixB13: mode=1" for
#                                             memory_tracker_tests (shader_cfg_tests: none, as base); prints ALL OK.
import collections
import hashlib
import os
import subprocess
import sys

DIR = "C:/kyty/f287/fs9a"
BUILD = DIR + "/build"
EXES = ("memory_tracker_tests", "shader_cfg_tests")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run(phase):
    knobs = [None] if phase == "base" else [None, "0", "1"]
    os.makedirs("%s/tests/%s" % (DIR, phase), exist_ok=True)
    for exe in EXES:
        path = "%s/%s.exe" % (BUILD, exe)
        print("exe %s %s sha256 %s" % (phase, exe, sha(path)), flush=True)
        for k in knobs:
            env = {n: v for n, v in os.environ.items() if not n.upper().startswith("KYTY_")}
            env["KYTY_TESTS_CONTINUE"] = "1"
            env["KYTY_TESTS_VERBOSE"] = "1"
            if k is not None:
                env["KYTY_FIX_B13"] = k
            r = subprocess.run([path], cwd=BUILD, env=env, capture_output=True, timeout=500)
            out = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
            name = "%s/tests/%s/%s_%s.txt" % (DIR, phase, exe, "unset" if k is None else k)
            open(name, "w", encoding="utf-8", newline="\n").write("rc: %d\n%s" % (r.returncode, out))
            print("%s %s KYTY_FIX_B13=%s rc %d -> %s" % (phase, exe, "unset" if k is None else k, r.returncode, name), flush=True)


def summary(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    rc = lines[0]
    failed = collections.Counter(l for l in lines if "failed" in l and not l.startswith("FixB13"))
    tests = [l for l in lines if l.startswith("[test]")]
    sct_failed = sum(1 for l in lines if "ShaderCfgTests: failed:" in l)
    mtt = [l for l in lines if l.startswith("MemoryTrackerTests:")]
    fix = [l for l in lines if l.startswith("FixB13: mode=")]
    return rc, failed, tests, sct_failed, mtt, fix


def compare():
    ok = True
    for exe in EXES:
        b = summary("%s/tests/base/%s_unset.txt" % (DIR, exe))
        f = summary("%s/tests/fs9/%s_unset.txt" % (DIR, exe))
        eq = b[0] == f[0] and b[1] == f[1] and b[2] == f[2] and b[3] == f[3] and b[4] == f[4]
        # shader_cfg_tests constructs no MemoryTracker - no FixB13 line (as base); memory_tracker_tests - one line, mode=1.
        fixok = f[5] == (["FixB13: mode=1"] if exe == "memory_tracker_tests" else b[5])
        print("%s defaults: base %s, failed-lines %d, ShaderCfgTests failed %d, tests %d, mtt %s, FixB13 %s | fs9 %s, failed-lines %d, ShaderCfgTests failed %d, tests %d, mtt %s, FixB13 %s | equal %s, fs9 FixB13 mode=1 %s"
              % (exe, b[0], sum(b[1].values()), b[3], len(b[2]), b[4], b[5] or "none", f[0], sum(f[1].values()), f[3], len(f[2]), f[4], f[5], eq, fixok))
        ok &= eq and fixok
        for k in ("0", "1"):
            r = summary("%s/tests/fs9/%s_%s.txt" % (DIR, exe, k))
            print("  reference fs9 KYTY_FIX_B13=%s: %s, failed-lines %d, ShaderCfgTests failed %d, tests %d, mtt %s, FixB13 %s, failed-lines = base %s"
                  % (k, r[0], sum(r[1].values()), r[3], len(r[2]), r[4], r[5], r[1] == b[1]))
    print("ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2])
    else:
        sys.exit(compare())

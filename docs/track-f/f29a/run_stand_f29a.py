# F29a (HPP-699, ROADMAP s122 item 638(g)(2)): the matrix of the B12 stand of the worktree build C:/kyty/f287/f29a/build,
# one process per arm, outputs to runs/<arm>.txt, the summary to runs/summary.txt. Members - p0_f29a.md (sealed before any
# data, sha256 in C:/kyty/f287/f29a/times.txt). Every knob of an arm is set explicitly; the rest of the environment is
# cleared of KYTY_* so that only the arm's values are read.
# Usage: python run_stand_f29a.py [--iters N]   Prints the summary and ALL OK when every member B12-1..B12-7 holds.
import argparse
import hashlib
import os
import re
import subprocess
import time

DIR = "C:/kyty/f287/f29a"
EXE = DIR + "/build/b12_bdastamp_stand.exe"
RUNS = DIR + "/runs"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(name, args, env_add, timeout=600):
    env = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
    env.update(env_add)
    t0 = time.time()
    res = subprocess.run([EXE] + args, capture_output=True, timeout=timeout, env=env)
    out = res.stdout.decode("utf-8", "replace").strip()
    open("%s/%s.txt" % (RUNS, name), "w", encoding="utf-8", newline="\n").write(
        "args: %s\nenv: %s\nrc: %d\nseconds: %.1f\n%s\n%s\n" % (" ".join(args), env_add, res.returncode, time.time() - t0,
                                                               out, res.stderr.decode("utf-8", "replace")))
    line = [l for l in out.split("\n") if l.startswith("B12 ")]
    if res.returncode != 0 or len(line) != 1:
        return None
    return line[0]


def fields(line):
    return dict(re.findall(r"(\w+)=([^ ]+)", line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=10000)
    a = parser.parse_args()
    it = str(a.iters)
    os.makedirs(RUNS, exist_ok=True)
    lines = ["exe b12_bdastamp_stand sha256 %s" % sha(EXE), "iters %s" % it]
    ok = True
    res = {}

    def arm(name, layout, write, passes, env):
        nonlocal ok
        line = run(name, [layout, write, str(passes), it], env)
        if line is None:
            lines.append("ARM FAILED %s" % name)
            res[name] = None
            return None
        lines.append("%s: %s" % (name, line))
        f = fields(line)
        res[name] = f
        return f

    def full(f, want, layout):
        # lost == dirty == want, and the common invariants of p0_f29a.md
        if f is None:
            return False
        same = "0" if layout == "split" else "1"
        mapped = "1" if layout == "touch" else "2"
        return (f["lost"] == want and f["dirty"] == want and f["clean_before_bad"] == "0" and
                f["same_region"] == same and f["mapped_ranges"] == mapped)

    m1 = m2 = m8 = True
    for bits in ("0", "1"):
        for narrow in ("0", "1", "2"):
            for b13 in ("0", "1"):
                env = {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_NARROW_STAMPS": narrow, "KYTY_FIX_B13": b13}
                tag = "b%s_n%s_f%s" % (bits, narrow, b13)
                f = arm("hole_upper_" + tag, "hole", "upper", 1, env)
                m1 &= full(f, it, "hole") and f["gate_bdabits"] == bits and f["bdanarrow"] == narrow and f["fix_b13"] == b13
                if narrow == "2":
                    m8 &= f is not None and f["nmiss"] == "0"
                g = arm("hole_lower_" + tag, "hole", "lower", 1, env)
                m2 &= full(g, "0", "hole") and g["gate_bdabits"] == bits and g["bdanarrow"] == narrow
    lines.append("MEMBER B12-1 hole/upper lost = dirty = iters in 12 arms: %s" % ("PASS" if m1 else "FAIL"))
    lines.append("MEMBER B12-2 hole/lower (forced negative control) lost = dirty = 0 in 12 arms: %s" % ("PASS" if m2 else "FAIL"))
    ok &= m1 and m2

    for num, layout in (("3", "nob1"), ("4", "split"), ("5", "touch")):
        m = True
        for bits in ("0", "1"):
            f = arm("%s_upper_b%s" % (layout, bits), layout, "upper", 1, {"KYTY_BDA_WRITE_BITS": bits})
            m &= full(f, "0", layout)
        lines.append("MEMBER B12-%s %s/upper lost = dirty = 0 (bits 0, 1): %s" % (num, layout, "PASS" if m else "FAIL"))
        ok &= m

    f = arm("hole_upper_stamps0", "hole", "upper", 1, {"KYTY_BDA_REGION_STAMPS": "0"})
    m6 = full(f, "0", "hole") and f["gate_bdastamp"] == "0"
    lines.append("MEMBER B12-6 hole/upper KYTY_BDA_REGION_STAMPS=0 lost = dirty = 0: %s" % ("PASS" if m6 else "FAIL"))
    ok &= m6

    f = arm("hole_upper_p8", "hole", "upper", 8, {})
    m7 = full(f, it, "hole")
    lines.append("MEMBER B12-7 hole/upper passes 8 lost = dirty = iters: %s" % ("PASS" if m7 else "FAIL"))
    ok &= m7

    lines.append("INFO B12-8 bdanarrow 2 arms of B12-1: nmiss = 0 (the check does not see the hole): %s" % ("yes" if m8 else "no"))
    lines.append("STAND REPRODUCES THE HOLE (B12-1..B12-7): %s" % ("ALL OK" if ok else "FAILED"))
    txt = "\n".join(lines) + "\n"
    open(RUNS + "/summary.txt", "w", encoding="utf-8", newline="\n").write(txt)
    print(txt)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

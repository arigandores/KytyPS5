# F24a (HPP-658, ROADMAP s122 item 593(d)(1), (e)): the full matrix of the B13 and B27 stands of the worktree build
# C:/kyty/f287/f24a/build, one process per arm, outputs to runs/<arm>.txt, the summary to runs/summary.txt.
# Members (named in p0_f24a.md before any data):
#   B13-1 order of the code, forced at hook point 1, bdabits 0: lost == iters (the window loses the region every time)
#   B13-2 reversed order (test build), the same arm: lost == 0 (the stand tells the two orders apart)
#   B13-5 controls before / after, both orders: lost == 0 (the reader model scans a completed write)
#   B13-3, B13-4, B13-6: reported, not members of the outcome
#   B27-1 inject none, 3 seeds: takes >= 10^6 each, hits >= 1, I1..I5 == 0
#   B27-2 inject draw_noguard: I1+..+I5 >= 1;  B27-3 inject producer_noguard: I1+..+I5 >= 1
#   B27-4 check_b27_copy.py at 707e0d7d, 0005e11f, 0ddca1ee: ALL OK
# Usage: python run_stand_f24a.py [--iters N] [--takes N]   Prints the summary and ALL OK when every member holds.
import argparse
import hashlib
import os
import re
import subprocess
import sys
import time

DIR = "C:/kyty/f287/f24a"
BUILD = DIR + "/build"
RUNS = DIR + "/runs"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(name, args, timeout=300):
    t0 = time.time()
    res = subprocess.run(args, capture_output=True, timeout=timeout)
    out = res.stdout.decode("utf-8", "replace").strip()
    open("%s/%s.txt" % (RUNS, name), "w", encoding="utf-8").write(
        "args: %s\nrc: %d\nseconds: %.1f\n%s\n%s\n" % (" ".join(args), res.returncode, time.time() - t0, out,
                                                        res.stderr.decode("utf-8", "replace")))
    if res.returncode != 0:
        print("ARM FAILED", name, res.returncode, out[:300])
        return None
    return out


def fields(line):
    return dict(re.findall(r"(\w+)=([^ ]+)", line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=1000000)
    parser.add_argument("--takes", type=int, default=500000)
    a = parser.parse_args()
    os.makedirs(RUNS, exist_ok=True)
    lines = []
    ok = True
    exes = {n: "%s/%s.exe" % (BUILD, n) for n in ("b13_epoch_stand", "b13_epoch_stand_swap", "b27_daslot_stand")}
    for n, p in exes.items():
        lines.append("exe %s sha256 %s" % (n, sha(p)))

    # B27-4: the copy of the guard primitives
    res = subprocess.run([sys.executable, DIR + "/check_b27_copy.py", "C:/kyty/f287/f24a/wt/tests/B27DaSlotStand.cpp",
                          "707e0d7d", "0005e11f", "0ddca1ee"], capture_output=True)
    copy_out = res.stdout.decode("utf-8", "replace").strip()
    lines.extend("copy " + l for l in copy_out.split("\n"))
    m = res.returncode == 0 and copy_out.endswith("ALL OK")
    ok &= m
    lines.append("MEMBER B27-4 copy of the guard primitives = code at 707e0d7d, 0005e11f, 0ddca1ee: %s" % ("PASS" if m else "FAIL"))

    # B13 matrix
    b13 = {}
    for build in ("code", "swap"):
        exe = exes["b13_epoch_stand" if build == "code" else "b13_epoch_stand_swap"]
        for mode, point, bits in (("forced", 1, 0), ("forced", 1, 1), ("forced", 2, 0), ("forced", 2, 1),
                                  ("before", 1, 0), ("after", 1, 0), ("free", 1, 0), ("free", 1, 1)):
            name = "b13_%s_%s_p%d_b%d" % (build, mode, point, bits)
            out = run(name, [exe, mode, str(point), str(bits), str(a.iters)])
            if out is None:
                ok = False
                continue
            lines.append(out)
            b13[(build, mode, point, bits)] = fields(out)

    def lost(key):
        f = b13.get(key)
        return None if f is None else int(f["lost"])

    m = lost(("code", "forced", 1, 0)) == a.iters
    ok &= m
    lines.append("MEMBER B13-1 order of the code, forced point 1, bdabits 0: lost %s of %d: %s" %
                 (lost(("code", "forced", 1, 0)), a.iters, "PASS" if m else "FAIL"))
    m = lost(("swap", "forced", 1, 0)) == 0
    ok &= m
    lines.append("MEMBER B13-2 reversed order, forced point 1, bdabits 0: lost %s: %s" %
                 (lost(("swap", "forced", 1, 0)), "PASS" if m else "FAIL"))
    ctl = [(k, lost(k)) for k in (("code", "before", 1, 0), ("code", "after", 1, 0), ("swap", "before", 1, 0),
                                  ("swap", "after", 1, 0))]
    m = all(v == 0 for _, v in ctl)
    ok &= m
    lines.append("MEMBER B13-5 controls before/after, both orders: lost %s: %s" %
                 (",".join(str(v) for _, v in ctl), "PASS" if m else "FAIL"))
    for key in (("code", "forced", 2, 0), ("swap", "forced", 2, 0), ("code", "forced", 1, 1), ("swap", "forced", 1, 1),
                ("code", "forced", 2, 1), ("swap", "forced", 2, 1), ("code", "free", 1, 0), ("swap", "free", 1, 0),
                ("code", "free", 1, 1), ("swap", "free", 1, 1)):
        lines.append("REPORT B13 %s %s point %d bdabits %d: lost %s of %d" % (key[0], key[1], key[2], key[3], lost(key),
                                                                              a.iters))

    # B27 matrix
    b27 = {}
    for inject, seeds in (("none", (1, 2, 3)), ("draw_noguard", (1,)), ("producer_noguard", (1,))):
        for seed in seeds:
            name = "b27_%s_s%d" % (inject, seed)
            out = run(name, [exes["b27_daslot_stand"], inject, str(a.takes), str(seed)])
            if out is None:
                ok = False
                continue
            lines.append(out)
            b27[(inject, seed)] = fields(out)

    def fails(f):
        return sum(int(f["I%d" % i]) for i in range(1, 6))

    clean = [(s, b27.get(("none", s))) for s in (1, 2, 3)]
    m = all(f is not None and int(f["takes"]) >= 1000000 and int(f["hits"]) >= 1 and fails(f) == 0 for _, f in clean)
    ok &= m
    lines.append("MEMBER B27-1 inject none, 3 seeds: takes %s hits %s failures %s: %s" % (
        ",".join(f["takes"] if f else "-" for _, f in clean), ",".join(f["hits"] if f else "-" for _, f in clean),
        ",".join(str(fails(f)) if f else "-" for _, f in clean), "PASS" if m else "FAIL"))
    for inject, member in (("draw_noguard", "B27-2"), ("producer_noguard", "B27-3")):
        f = b27.get((inject, 1))
        m = f is not None and fails(f) >= 1
        ok &= m
        lines.append("MEMBER %s inject %s: failures %s (I1..I5 %s): %s" % (
            member, inject, fails(f) if f else "-",
            ",".join(f["I%d" % i] for i in range(1, 6)) if f else "-", "PASS" if m else "FAIL"))
    lines.append("ALL OK" if ok else "FAILED")
    text = "\n".join(lines) + "\n"
    open(RUNS + "/summary.txt", "w", encoding="utf-8").write(text)
    print(text, end="")
    sys.exit(0 if ok else 1)


main()

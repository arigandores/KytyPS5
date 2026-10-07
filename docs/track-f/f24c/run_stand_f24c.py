# F24c (HPP-662, ROADMAP s122 item 595(e)(1)): the B13 stand matrix of the worktree build C:/kyty/f287/f24c/buildM (the
# stand of the commit of the fix) with the knob KYTY_FIX_B13 of the code under test; one process per arm, outputs to
# runs/<arm>.txt, the summary to runs/summary.txt. Copy of docs/track-f/f24a/run_stand_f24a.py (B13 part) with the knob
# arms. Members (named in p0_f24c.md and item 595(e)(1) before any data):
#   E1-a KYTY_FIX_B13=1, forced, every hook point (11, 12, 13) x bdabits 0 and 1: lost 0
#   E1-b KYTY_FIX_B13=1, free, points 11 and 12 x bdabits 0 and 1: lost 0
#   E1-c KYTY_FIX_B13=1, controls before / after x bdabits 0 and 1: lost 0
#   E1-d KYTY_FIX_B13=0 (same build), forced point 1, bdabits 0: lost >= 1
#   E1-e every arm of KYTY_FIX_B13=1 ends with rc 0 and its result line (no EXIT, STALL or crash)
#   E2-c every arm prints "FixB13: mode=<v>" by the value of the knob (unset - 0) and fix_b13=<v> in its result line
# Reported, not members: =0 free point 1 bdabits 0 and 1; =0 forced points 1/2 x bdabits; =0 controls; unset forced
# point 1 bdabits 0; swap build at =0 forced point 1 bdabits 0 and controls.
# Usage: python run_stand_f24c.py [--iters N]   Prints the summary and ALL OK when every member holds.
import argparse
import hashlib
import os
import re
import subprocess
import sys
import time

DIR = "C:/kyty/f287/f24c"
BUILD = DIR + "/buildM"
RUNS = DIR + "/runs"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(name, args, knob, timeout=300):
    env = dict(os.environ)
    env.pop("KYTY_FIX_B13", None)
    if knob is not None:
        env["KYTY_FIX_B13"] = knob
    t0 = time.time()
    try:
        res = subprocess.run(args, capture_output=True, timeout=timeout, env=env)
        rc, out, err = res.returncode, res.stdout.decode("utf-8", "replace").strip(), res.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc, out, err = -999, "", "TIMEOUT"
    open("%s/%s.txt" % (RUNS, name), "w", encoding="utf-8").write(
        "args: %s\nKYTY_FIX_B13: %s\nrc: %d\nseconds: %.1f\n%s\n%s\n" % (
            " ".join(args), "unset" if knob is None else knob, rc, time.time() - t0, out, err))
    return rc, out


def fields(line):
    return dict(re.findall(r"(\w+)=([^ ]+)", line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=1000000)
    a = parser.parse_args()
    os.makedirs(RUNS, exist_ok=True)
    lines = []
    ok = True
    exes = {n: "%s/%s.exe" % (BUILD, n) for n in ("b13_epoch_stand", "b13_epoch_stand_swap")}
    for n, p in exes.items():
        lines.append("exe %s sha256 %s" % (n, sha(p)))

    arms = []  # (knob, build, mode, point, bits)
    for point in (11, 12, 13):
        for bits in (0, 1):
            arms.append(("1", "code", "forced", point, bits))
    for point in (11, 12):
        for bits in (0, 1):
            arms.append(("1", "code", "free", point, bits))
    for mode in ("before", "after"):
        for bits in (0, 1):
            arms.append(("1", "code", mode, 11, bits))
    for point in (1, 2):
        for bits in (0, 1):
            arms.append(("0", "code", "forced", point, bits))
    for mode in ("before", "after"):
        arms.append(("0", "code", mode, 1, 0))
    for bits in (0, 1):
        arms.append(("0", "code", "free", 1, bits))
    arms.append((None, "code", "forced", 1, 0))
    arms.append(("0", "swap", "forced", 1, 0))
    arms.append(("0", "swap", "before", 1, 0))
    arms.append(("0", "swap", "after", 1, 0))

    res = {}
    bad_rc = []
    bad_mode = []
    for knob, build, mode, point, bits in arms:
        kname = "u" if knob is None else knob
        name = "b13_k%s_%s_%s_p%d_b%d" % (kname, build, mode, point, bits)
        exe = exes["b13_epoch_stand" if build == "code" else "b13_epoch_stand_swap"]
        rc, out = run(name, [exe, mode, str(point), str(bits), str(a.iters)], knob)
        result = [l for l in out.split("\n") if l.startswith("B13 ")]
        want = "1" if knob == "1" else "0"
        mode_lines = re.findall(r"FixB13: mode=(\d)", out)
        if rc != 0 or len(result) != 1:
            bad_rc.append("%s rc=%d" % (name, rc))
            lines.append("ARM FAILED %s rc %d %s" % (name, rc, out[:200].replace("\n", " | ")))
            continue
        f = fields(result[0])
        if mode_lines != [want] or f.get("fix_b13") != want:
            bad_mode.append("%s FixB13=%s fix_b13=%s" % (name, ",".join(mode_lines), f.get("fix_b13")))
        lines.append("%s | %s" % (name, result[0]))
        res[(kname, build, mode, point, bits)] = f

    def lost(key):
        f = res.get(key)
        return None if f is None else int(f["lost"])

    forced1 = [("1", "code", "forced", p, b) for p in (11, 12, 13) for b in (0, 1)]
    m = all(lost(k) == 0 for k in forced1)
    ok &= m
    lines.append("MEMBER E1-a =1 forced points 11/12/13 x bdabits 0/1: lost %s: %s" % (
        ",".join(str(lost(k)) for k in forced1), "PASS" if m else "FAIL"))
    free1 = [("1", "code", "free", p, b) for p in (11, 12) for b in (0, 1)]
    m = all(lost(k) == 0 for k in free1)
    ok &= m
    lines.append("MEMBER E1-b =1 free points 11/12 x bdabits 0/1: lost %s: %s" % (
        ",".join(str(lost(k)) for k in free1), "PASS" if m else "FAIL"))
    ctl1 = [("1", "code", md, 11, b) for md in ("before", "after") for b in (0, 1)]
    m = all(lost(k) == 0 for k in ctl1)
    ok &= m
    lines.append("MEMBER E1-c =1 controls before/after x bdabits 0/1: lost %s: %s" % (
        ",".join(str(lost(k)) for k in ctl1), "PASS" if m else "FAIL"))
    k0 = ("0", "code", "forced", 1, 0)
    m = lost(k0) is not None and lost(k0) >= 1
    ok &= m
    lines.append("MEMBER E1-d =0 forced point 1 bdabits 0: lost %s of %d: %s" % (lost(k0), a.iters, "PASS" if m else "FAIL"))
    m = not [x for x in bad_rc if "_k1_" in x]
    ok &= m
    lines.append("MEMBER E1-e =1 arms rc 0 with a result line: failed %s: %s" % (
        ",".join(x for x in bad_rc if "_k1_" in x) or "none", "PASS" if m else "FAIL"))
    m = not bad_mode and not bad_rc
    ok &= m
    lines.append("MEMBER E2-c FixB13 line and fix_b13 field by the knob value in every arm: mismatches %s, failed arms %s: %s" % (
        ";".join(bad_mode) or "none", ";".join(bad_rc) or "none", "PASS" if m else "FAIL"))
    for key in (("0", "code", "free", 1, 0), ("0", "code", "free", 1, 1), ("0", "code", "forced", 1, 1),
                ("0", "code", "forced", 2, 0), ("0", "code", "forced", 2, 1), ("0", "code", "before", 1, 0),
                ("0", "code", "after", 1, 0), ("u", "code", "forced", 1, 0), ("0", "swap", "forced", 1, 0),
                ("0", "swap", "before", 1, 0), ("0", "swap", "after", 1, 0)):
        lines.append("REPORT B13 knob %s %s %s point %d bdabits %d: lost %s of %d" % (
            key[0], key[1], key[2], key[3], key[4], lost(key), a.iters))
    lines.append("ALL OK" if ok else "FAILED")
    text = "\n".join(lines) + "\n"
    open(RUNS + "/summary.txt", "w", encoding="utf-8").write(text)
    print(text, end="")
    sys.exit(0 if ok else 1)


main()

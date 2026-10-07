# FS9a (HPP-671, ROADMAP s122 item 604(d)(1)): the B13 stand of the FS9 worktree build C:/kyty/f287/fs9a/build (the
# targets b13_epoch_stand, b13_epoch_stand_swap of the worktree 0005e11f + 1570d110 + 21f8ca76 + FS9a) with the knob
# KYTY_FIX_B13 UNSET (the default of FS9) and =0 (control). Copy of run_stand_f24c.py (F24c) with the arms of item
# 604(d)(1); one process per arm, outputs to runs_stand/<arm>.txt, the summary to runs_stand/summary.txt.
# Members (item 604(d)(1), named before any data):
#   S1 unset, forced, points 11/12/13 x bdabits 0/1: lost 0
#   S2 unset, free, points 11/12 x bdabits 0/1: lost 0
#   S3 unset, controls before/after x bdabits 0/1: lost 0
#   S4 every unset arm: rc 0, one result line, "FixB13: mode=1" and fix_b13=1 (the =1 expectations), no EXIT/STALL
#   S5 KYTY_FIX_B13=0, forced point 1, bdabits 0: lost >= 1, "FixB13: mode=0" and fix_b13=0
# Reported, not members: unset forced point 1 bdabits 0 (a point of the =0 order - refused, exit 2, since unset is =1 now);
# =0 free point 1 bdabits 0; =1 forced point 11 bdabits 0.
# Usage: python run_stand_fs9a.py [--iters N]   Prints the summary and ALL OK when every member holds.
import argparse
import hashlib
import os
import re
import subprocess
import sys
import time

DIR = "C:/kyty/f287/fs9a"
BUILD = DIR + "/build"
RUNS = DIR + "/runs_stand"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run(name, args, knob, timeout=300):
    env = {n: v for n, v in os.environ.items() if not n.upper().startswith("KYTY_")}
    if knob is not None:
        env["KYTY_FIX_B13"] = knob
    t0 = time.time()
    try:
        res = subprocess.run(args, capture_output=True, timeout=timeout, env=env)
        rc, out, err = res.returncode, res.stdout.decode("utf-8", "replace").strip(), res.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        rc, out, err = -999, "", "TIMEOUT"
    open("%s/%s.txt" % (RUNS, name), "w", encoding="utf-8", newline="\n").write(
        "args: %s\nKYTY_FIX_B13: %s\nrc: %d\nseconds: %.1f\n%s\n%s\n" % (
            " ".join(args), "unset" if knob is None else knob, rc, time.time() - t0, out, err))
    return rc, out


def fields(line):
    return dict(re.findall(r"(\w+)=([^ ]+)", line))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=100000)
    a = parser.parse_args()
    os.makedirs(RUNS, exist_ok=True)
    lines = []
    ok = True
    exes = {n: "%s/%s.exe" % (BUILD, n) for n in ("b13_epoch_stand", "b13_epoch_stand_swap")}
    for n, p in exes.items():
        lines.append("exe %s sha256 %s" % (n, sha(p)))

    arms = []  # (knob, mode, point, bits)
    for point in (11, 12, 13):
        for bits in (0, 1):
            arms.append((None, "forced", point, bits))
    for point in (11, 12):
        for bits in (0, 1):
            arms.append((None, "free", point, bits))
    for mode in ("before", "after"):
        for bits in (0, 1):
            arms.append((None, mode, 11, bits))
    arms.append(("0", "forced", 1, 0))
    ref = [(None, "forced", 1, 0), ("0", "free", 1, 0), ("1", "forced", 11, 0)]

    res, raw = {}, {}
    for knob, mode, point, bits in arms + ref:
        kname = "u" if knob is None else knob
        name = "b13_k%s_code_%s_p%d_b%d" % (kname, mode, point, bits)
        rc, out = run(name, [exes["b13_epoch_stand"], mode, str(point), str(bits), str(a.iters)], knob)
        result = [l for l in out.split("\n") if l.startswith("B13 ")]
        mode_lines = re.findall(r"FixB13: mode=(\d)", out)
        bad = [l for l in out.split("\n") if l.startswith("EXIT") or l.startswith("STALL")]
        raw[(kname, mode, point, bits)] = (rc, mode_lines, result, bad)
        if rc == 0 and len(result) == 1:
            res[(kname, mode, point, bits)] = fields(result[0])
            lines.append("%s | rc 0 | FixB13 %s | %s" % (name, ",".join(mode_lines), result[0]))
        else:
            lines.append("%s | rc %d | FixB13 %s | %s" % (name, rc, ",".join(mode_lines), out[:200].replace("\n", " | ")))

    def lost(key):
        f = res.get(key)
        return None if f is None else int(f["lost"])

    def member(tag, keys, cond, text):
        nonlocal ok
        m = all(cond(k) for k in keys)
        ok &= m
        lines.append("MEMBER %s %s: lost %s: %s" % (tag, text, ",".join(str(lost(k)) for k in keys), "PASS" if m else "FAIL"))

    s1 = [("u", "forced", p, b) for p in (11, 12, 13) for b in (0, 1)]
    member("S1", s1, lambda k: lost(k) == 0, "unset forced points 11/12/13 x bdabits 0/1")
    s2 = [("u", "free", p, b) for p in (11, 12) for b in (0, 1)]
    member("S2", s2, lambda k: lost(k) == 0, "unset free points 11/12 x bdabits 0/1")
    s3 = [("u", md, 11, b) for md in ("before", "after") for b in (0, 1)]
    member("S3", s3, lambda k: lost(k) == 0, "unset controls before/after x bdabits 0/1")
    bad4 = []
    for k in s1 + s2 + s3:
        rc, ml, result, bad = raw[k]
        if rc != 0 or len(result) != 1 or ml != ["1"] or res.get(k, {}).get("fix_b13") != "1" or bad:
            bad4.append("%s rc=%d FixB13=%s" % ("_".join(map(str, k)), rc, ",".join(ml)))
    m = not bad4
    ok &= m
    lines.append("MEMBER S4 every unset arm rc 0, one result line, FixB13: mode=1, fix_b13=1, no EXIT/STALL: bad %s: %s" % (
        ";".join(bad4) or "none", "PASS" if m else "FAIL"))
    k0 = ("0", "forced", 1, 0)
    rc, ml, result, bad = raw[k0]
    m = lost(k0) is not None and lost(k0) >= 1 and ml == ["0"] and res[k0].get("fix_b13") == "0"
    ok &= m
    lines.append("MEMBER S5 =0 forced point 1 bdabits 0: lost %s of %d, FixB13 %s: %s" % (
        lost(k0), a.iters, ",".join(ml), "PASS" if m else "FAIL"))
    for k in ref:
        kk = ("u" if k[0] is None else k[0],) + k[1:]
        rc, ml, result, bad = raw[kk]
        lines.append("REPORT knob %s %s point %d bdabits %d: rc %d FixB13 %s lost %s" % (
            k[0] if k[0] else "unset", k[1], k[2], k[3], rc, ",".join(ml) or "none", lost(kk)))
    lines.append("ALL OK" if ok else "FAILED")
    text = "\n".join(lines) + "\n"
    open(RUNS + "/summary.txt", "w", encoding="utf-8", newline="\n").write(text)
    print(text, end="")
    sys.exit(0 if ok else 1)


main()

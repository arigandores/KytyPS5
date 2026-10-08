# F29c3 (HPP-713, ROADMAP s122 item 645(v)): copy of 851674a1:docs/track-f/f29c/e2/run_stand_f29c_e2.py (the e2 form of the
# member (e)(1)) + B12-9n hlost1 = 0 (item 642(v)) + B12-9b; outputs to C:/kyty/f287/f29c3/runs_e2form. Was:
# F29c edition 2 (HPP-702, ROADMAP s122 item 641(g)): copy of run_stand_f29c.py with the members of e2/p0_f29c_e2.md -
# B12-10n / B12-9n gates at 1, the =0 control of B12-10n, lskip = 0 in B12-11; outputs to e2/runs. Was:
# F29c (HPP-702, ROADMAP s122 item 639(e)(1)): the matrix of the B12 stand at KYTY_FIX_B12=1 and the control at 0, built from
# the fix commit c94c49e0 in the clean worktree C:/kyty/f287/f29c/wt; one process per arm, outputs to runs/<arm>.txt, the
# summary to runs/summary.txt. Members - p0_f29c.md (sealed before the matrix, sha256 in C:/kyty/f287/f29c/times.txt). Copy of
# the F29a run_stand_f29a.py with the arms of p0_f29c.md; every knob of an arm is set explicitly, the rest of KYTY_* cleared.
# Usage: python run_stand_f29c.py [--iters N] [--exe PATH]   Prints the summary and ALL OK when member (e)(1) holds.
import argparse
import hashlib
import os
import re
import subprocess
import time

DIR = "C:/kyty/f287/f29c"
RUNS = "C:/kyty/f287/f29c3/runs_e2form"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def fields(text):
    return dict(re.findall(r"(\w+)=([^ ]+)", text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=10000)
    parser.add_argument("--exe", default="C:/kyty/f287/f29c3/exe/b12_stand_e3.exe")
    a = parser.parse_args()
    exe = a.exe
    it = str(a.iters)
    os.makedirs(RUNS, exist_ok=True)
    lines = ["exe %s sha256 %s" % (os.path.basename(exe), sha(exe)), "iters %s" % it]
    t_all = time.time()

    def arm(name, layout, write, passes, env, hook=None):
        env = dict(env)
        full_env = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
        full_env.update(env)
        args = [layout, write, str(passes), it] + (["hook=" + hook] if hook else [])
        t0 = time.time()
        try:
            res = subprocess.run([exe] + args, capture_output=True, timeout=900, env=full_env)
            rc, out, err = res.returncode, res.stdout.decode("utf-8", "replace").strip(), res.stderr.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            rc, out, err = -999, "", "TIMEOUT"
        open("%s/%s.txt" % (RUNS, name), "w", encoding="utf-8", newline="\n").write(
            "args: %s\nenv: %s\nrc: %d\nseconds: %.1f\n%s\n%s\n" % (" ".join(args), env, rc, time.time() - t0, out, err))
        l1 = [l for l in out.split("\n") if l.startswith("B12 ")]
        l2 = [l for l in out.split("\n") if l.startswith("B12c ")]
        if rc != 0 or len(l1) != 1 or len(l2) != 1:
            lines.append("ARM FAILED %s rc=%d" % (name, rc))
            return None
        f = fields(l1[0])
        f.update(fields(l2[0]))
        lines.append("%s: %s | %s" % (name, l1[0][4:].split(" gate_bdastamp")[0], l2[0][5:]))
        return f

    def common(f, layout, fix):
        if f is None:
            return False
        same = "0" if layout == "split" else "1"
        mapped = "1" if layout == "touch" else "2"
        return (f["fix_b12"] == fix and f["clean_before_bad"] == "0" and f["same_region"] == same and
                f["mapped_ranges"] == mapped)

    def zero(f, layout, fix="1"):
        return common(f, layout, fix) and f["lost"] == "0" and f["dirty"] == "0"

    ok = True
    m = {k: True for k in ("1", "2", "3", "4", "5", "6", "7", "9", "10", "11", "12", "10n", "9n", "c1", "c10n", "9nh1", "9b")}
    for bits in ("0", "1"):
        for narrow in ("0", "1", "2"):
            for b13 in ("0", "1"):
                tag = "b%s_n%s_f%s" % (bits, narrow, b13)
                base = {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_NARROW_STAMPS": narrow, "KYTY_FIX_B13": b13}
                f = arm("x1_hole_upper_" + tag, "hole", "upper", 1, dict(base, KYTY_FIX_B12="1"))
                m["1"] &= (zero(f, "hole") and f["gate_bdabits"] == bits and f["bdanarrow"] == narrow and
                           f["fix_b13"] == b13)
                m["12"] &= f is not None and f["rw_min"] == "1" and f["rw_max"] == "1" and int(f["scan_passes"]) >= 1
                g = arm("x1_hole_lower_" + tag, "hole", "lower", 1, dict(base, KYTY_FIX_B12="1"))
                m["2"] &= zero(g, "hole") and g["gate_bdabits"] == bits and g["bdanarrow"] == narrow
                c = arm("x0_hole_upper_" + tag, "hole", "upper", 1, dict(base, KYTY_FIX_B12="0"))
                m["c1"] &= (common(c, "hole", "0") and int(c["lost"]) >= 1 and int(c["dirty"]) >= 1 and
                            c["rewalk"] == "0")
    for num, layout in (("3", "nob1"), ("4", "split"), ("5", "touch")):
        for bits in ("0", "1"):
            f = arm("x1_%s_upper_b%s" % (layout, bits), layout, "upper", 1, {"KYTY_BDA_WRITE_BITS": bits, "KYTY_FIX_B12": "1"})
            m[num] &= zero(f, layout)
            m["12"] &= f is not None and f["rw_max"] == "0" and f["rewalk"] == "0"
    f = arm("x1_hole_upper_stamps0", "hole", "upper", 1, {"KYTY_BDA_REGION_STAMPS": "0", "KYTY_FIX_B12": "1"})
    m["6"] &= zero(f, "hole") and f["gate_bdastamp"] == "0"
    f = arm("x1_hole_upper_p8", "hole", "upper", 8, {"KYTY_FIX_B12": "1"})
    m["7"] &= zero(f, "hole")
    info0 = []
    for hook, num in (("upper", "9"), ("lower", "10")):
        for write in ("upper", "lower"):
            for bits in ("0", "1"):
                for fix in ("1", "0"):
                    name = "x%s_hole_%s_hook%s_b%s" % (fix, write, hook, bits)
                    f = arm(name, "hole", write, 2, {"KYTY_BDA_WRITE_BITS": bits, "KYTY_FIX_B12": fix}, hook)
                    if fix == "1":
                        m[num] &= (zero(f, "hole") and f["hook_fired"] == it and f["hlost"] == "0" and f["hdirty"] == "0")
                    else:
                        info0.append("%s: lost=%s dirty=%s hlost=%s hdirty=%s" % (
                            name, *(("-",) * 4 if f is None else (f["lost"], f["dirty"], f["hlost"], f["hdirty"]))))
    for bits in ("0", "1"):
        f = arm("x1_hole_upper_p8_cache0_b%s" % bits, "hole", "upper", 8,
                {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_EPOCH_CACHE": "0", "KYTY_FIX_B12": "1"})
        m["11"] &= (zero(f, "hole") and f["late_scans"] == "0" and f["late_rewalks"] == "0" and f["lskip"] == "0")
    info_n = []
    for hook in ("lower", "upper"):
        for bits in ("0", "1"):
            for fix in ("1", "0"):
                name = "x%s_hole_none_hook%s_b%s_cache0" % (fix, hook, bits)
                f = arm(name, "hole", "none", 2,
                        {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_EPOCH_CACHE": "0", "KYTY_FIX_B12": fix}, hook)
                info_n.append("%s: hook_fired=%s hlost=%s hdirty=%s hlost1=%s lskip=%s rc_ok=%s" % (
                    name, *(("-",) * 5 if f is None else (f["hook_fired"], f["hlost"], f["hdirty"], f["hlost1"],
                                                          f["lskip"])), f is not None))
                ok &= f is not None and common(f, "hole", fix)
                num = "10n" if hook == "lower" else "9n"
                if fix == "1":
                    m[num] &= (common(f, "hole", "1") and f["hook_fired"] == it and f["hlost"] == "0" and
                               f["hdirty"] == "0")
                    if hook == "upper":  # F29c3: the member of item 642(v)
                        m["9nh1"] &= f["hlost1"] == "0"
                elif hook == "lower":
                    m["c10n"] &= common(f, "hole", "0") and int(f["hlost"]) >= 1 and f["lskip"] == "0"

    info_b = []  # F29c3 (item 645(v)): B12-9b
    for fix in ("1", "0"):
        name = "x%s_hole_none_hookbitonly_b1_cache0" % fix
        f = arm(name, "hole", "none", 2, {"KYTY_BDA_WRITE_BITS": "1", "KYTY_BDA_EPOCH_CACHE": "0", "KYTY_FIX_B12": fix}, "bitonly")
        ok &= f is not None and common(f, "hole", fix)
        info_b.append("%s: hook_fired=%s bit1=%s late_bit_skips=%s bit_skips=%s" % (
            name, *(("-",) * 4 if f is None else (f["hook_fired"], f["bit1"], f["late_bit_skips"], f["bit_skips"]))))
        if fix == "1":
            m["9b"] &= (f is not None and common(f, "hole", "1") and f["hook_fired"] == it and f["bit1"] == it and
                        f["late_bit_skips"] == "0")
    names = {"1": "B12-1 hole/upper lost = dirty = 0 (12 arms)", "2": "B12-2 hole/lower lost = dirty = 0 (12 arms)",
             "3": "B12-3 nob1/upper lost = dirty = 0", "4": "B12-4 split/upper lost = dirty = 0",
             "5": "B12-5 touch/upper lost = dirty = 0", "6": "B12-6 bdastamp=0 lost = dirty = 0",
             "7": "B12-7 passes 8 lost = dirty = 0", "9": "B12-9 hook=upper between the visits, hlost = hdirty = 0 (4 arms)",
             "10": "B12-10 hook=lower between the visits, hlost = hdirty = 0 (4 arms)",
             "11": "B12-11 epoch cache 0, passes 2-8: late_scans = late_rewalks = 0, lskip = 0 (2 arms)",
             "10n": "B12-10n first visit skips, hook=lower, hlost = hdirty = 0 (2 arms)",
             "9n": "B12-9n first visit skips, hook=upper, hlost = hdirty = 0 (2 arms)",
             "c10n": "CONTROL KYTY_FIX_B12=0: B12-10n hlost >= 1 in each of 2 arms, lskip 0",
             "12": "B12-12 revisits per scanning pass: hole 1, nob1/split/touch 0",
             "c1": "CONTROL KYTY_FIX_B12=0: B12-1 lost >= 1 and dirty >= 1 in each of 12 arms, rewalk 0",
             "9nh1": "B12-9n hlost1 = 0 in both bdabits arms (item 642(v))",
             "9b": "B12-9b hook=bitonly, bdabits 1, cache 0: hook_fired = bit1 = iters, late_bit_skips = 0 (item 645(v))"}
    for k in ("1", "2", "3", "4", "5", "6", "7", "9", "10", "11", "12", "10n", "9n", "c1", "c10n", "9nh1", "9b"):
        lines.append("MEMBER %s: %s" % (names[k], "PASS" if m[k] else "FAIL"))
        ok &= m[k]
    lines.append("INFO KYTY_FIX_B12=0, B12-9/B12-10 arms (report line, not a gate):")
    lines += ["  " + s for s in info0]
    lines.append("B12-10n / B12-9n arms (gates at 1 and the =0 control of B12-10n above; hlost1 - reference):")
    lines += ["  " + s for s in info_n]
    lines.append("B12-9b arms (gate at 1 above; =0 - reference line, not a gate):")
    lines += ["  " + s for s in info_b]
    lines.append("INFO B12-13 (three pieces): the model holds two ranges in a region - no arm (item 641(g))")
    lines.append("wall %.1f s" % (time.time() - t_all))
    lines.append("MEMBER (e)(1) AT KYTY_FIX_B12=1 WITH THE CONTROL AT 0: %s" % ("ALL OK" if ok else "FAILED"))
    txt = "\n".join(lines) + "\n"
    open(RUNS + "/summary.txt", "w", encoding="utf-8", newline="\n").write(txt)
    print(txt)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

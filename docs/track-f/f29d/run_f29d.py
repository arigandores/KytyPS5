# F29d (HPP-703, Red Team): own run of the B12 stand (ROADMAP s122 items 639(e)(1), 641(g), 642(v)) - written by the
# reviewer, not a copy of run_stand_f29c*.py. Members are fixed in this file BEFORE the first run (its sha256 goes to
# C:/kyty/f287/f29d/times.txt before the matrix):
#   at KYTY_FIX_B12=1, every arm: rc 0, fix_b12=1, clean_before_bad=0;
#   B12-1  hole/upper, KYTY_BDA_WRITE_BITS {0,1} x KYTY_BDA_NARROW_STAMPS {0,1,2} x KYTY_FIX_B13 {0,1} (12 arms): lost=dirty=0;
#          B12-12 on the same arms: rw_min=rw_max=1, scan_passes>=1;
#   B12-2  hole/lower, the same 12 arms: lost=dirty=0;
#   B12-3/4/5 nob1/split/touch, upper, bits {0,1}: lost=dirty=0; B12-12: rw_max=0, rewalk=0;
#   B12-6  hole/upper, KYTY_BDA_REGION_STAMPS=0: lost=dirty=0;
#   B12-7  hole/upper, passes 8: lost=dirty=0;
#   B12-9  hole, write {upper,lower}, hook=upper, passes 2, bits {0,1} (4 arms): hook_fired=iters, hlost=hdirty=0, lost=dirty=0;
#   B12-10 the same with hook=lower (4 arms);
#   B12-11 hole/upper, passes 8, KYTY_BDA_EPOCH_CACHE=0, bits {0,1}: late_scans=late_rewalks=0, lskip=0, lost=dirty=0;
#   B12-10n hole, write none, hook=lower, passes 2, KYTY_BDA_EPOCH_CACHE=0, bits {0,1}: hook_fired=iters, hlost=hdirty=0;
#   B12-9n  the same with hook=upper: hook_fired=iters, hlost=hdirty=0 and (item 642(v)) hlost1=0;
#   control at KYTY_FIX_B12=0 (same build): B12-1 12 arms lost>=1, dirty>=1, rewalk=0, fix_b12=0; B12-10n 2 arms hlost>=1,
#          lskip=0. Reference lines (not members): B12-9, B12-10, B12-9n at 0; hlost1 of B12-10n at 1.
# Every KYTY_* variable of the environment is removed; each arm sets KYTY_FIX_B12 explicitly.
# Usage: python run_f29d.py <stand.exe> <iters> <out.txt>     exit 0 always; last line "MEMBERS ALL OK" or "MEMBERS FAILED: ..."
import os
import re
import subprocess
import sys


def run(exe, args, env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
    e.update(env)
    try:
        r = subprocess.run([exe] + args, capture_output=True, timeout=300, env=e)
    except subprocess.TimeoutExpired:
        return -999, {}, "TIMEOUT"
    out = r.stdout.decode("utf-8", "replace")
    kv = dict(re.findall(r"(\w+)=([^ \n]+)", out))
    return r.returncode, kv, out


def main():
    exe, iters, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    n = int(iters)
    rows = []
    fails = []

    def arm(name, fix, layout, write, passes, env, hook=None):
        args = [layout, write, str(passes), iters] + ([hook] if hook else [])
        env = dict(env)
        env["KYTY_FIX_B12"] = fix
        rc, kv, raw = run(exe, args, env)
        rows.append("%s rc=%d %s" % (name, rc, " ".join("%s=%s" % x for x in sorted(kv.items()))))
        return rc, kv

    def g(kv, k):
        return int(kv.get(k, "-1"))

    def member(label, ok):
        if not ok:
            fails.append(label)

    def base_ok(name, rc, kv, fix):
        member(name + " rc/fix/cbb", rc == 0 and g(kv, "fix_b12") == int(fix) and g(kv, "clean_before_bad") == 0)

    for fix in ("1", "0"):
        for bits in ("0", "1"):
            for narrow in ("0", "1", "2"):
                for b13 in ("0", "1"):
                    env = {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_NARROW_STAMPS": narrow, "KYTY_FIX_B13": b13}
                    tag = "b%s_n%s_f%s" % (bits, narrow, b13)
                    rc, kv = arm("x%s_B12-1_%s" % (fix, tag), fix, "hole", "upper", 1, env)
                    base_ok("x%s_B12-1_%s" % (fix, tag), rc, kv, fix)
                    if fix == "1":
                        member("B12-1 " + tag, g(kv, "lost") == 0 and g(kv, "dirty") == 0)
                        member("B12-12 hole " + tag, g(kv, "rw_min") == 1 and g(kv, "rw_max") == 1 and g(kv, "scan_passes") >= 1)
                        rc, kv = arm("x1_B12-2_" + tag, fix, "hole", "lower", 1, env)
                        base_ok("x1_B12-2_" + tag, rc, kv, fix)
                        member("B12-2 " + tag, g(kv, "lost") == 0 and g(kv, "dirty") == 0)
                    else:
                        member("CONTROL0 B12-1 " + tag, g(kv, "lost") >= 1 and g(kv, "dirty") >= 1 and g(kv, "rewalk") == 0)
    for layout in ("nob1", "split", "touch"):
        for bits in ("0", "1"):
            name = "x1_%s_b%s" % (layout, bits)
            rc, kv = arm(name, "1", layout, "upper", 1, {"KYTY_BDA_WRITE_BITS": bits})
            base_ok(name, rc, kv, "1")
            member("B12-3/4/5 " + name, g(kv, "lost") == 0 and g(kv, "dirty") == 0)
            member("B12-12 " + name, g(kv, "rw_max") == 0 and g(kv, "rewalk") == 0)
    rc, kv = arm("x1_B12-6_stamps0", "1", "hole", "upper", 1, {"KYTY_BDA_REGION_STAMPS": "0"})
    base_ok("x1_B12-6", rc, kv, "1")
    member("B12-6", g(kv, "lost") == 0 and g(kv, "dirty") == 0)
    rc, kv = arm("x1_B12-7_p8", "1", "hole", "upper", 8, {})
    base_ok("x1_B12-7", rc, kv, "1")
    member("B12-7", g(kv, "lost") == 0 and g(kv, "dirty") == 0)
    for fix in ("1", "0"):
        for hook in ("upper", "lower"):
            for write in ("upper", "lower"):
                for bits in ("0", "1"):
                    name = "x%s_B12-%s_%s_b%s" % (fix, "9" if hook == "upper" else "10", write, bits)
                    rc, kv = arm(name, fix, "hole", write, 2, {"KYTY_BDA_WRITE_BITS": bits}, "hook=" + hook)
                    base_ok(name, rc, kv, fix)
                    if fix == "1":
                        member(name, g(kv, "hook_fired") == n and g(kv, "hlost") == 0 and g(kv, "hdirty") == 0 and
                               g(kv, "lost") == 0 and g(kv, "dirty") == 0)
    for bits in ("0", "1"):
        name = "x1_B12-11_b" + bits
        rc, kv = arm(name, "1", "hole", "upper", 8, {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_EPOCH_CACHE": "0"})
        base_ok(name, rc, kv, "1")
        member(name, g(kv, "late_scans") == 0 and g(kv, "late_rewalks") == 0 and g(kv, "lskip") == 0 and
               g(kv, "late_lskips") == 0 and g(kv, "lost") == 0 and g(kv, "dirty") == 0)
    for fix in ("1", "0"):
        for hook in ("lower", "upper"):
            for bits in ("0", "1"):
                name = "x%s_B12-%sn_b%s" % (fix, "10" if hook == "lower" else "9", bits)
                rc, kv = arm(name, fix, "hole", "none", 2, {"KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_EPOCH_CACHE": "0"},
                             "hook=" + hook)
                base_ok(name, rc, kv, fix)
                if fix == "1":
                    ok = g(kv, "hook_fired") == n and g(kv, "hlost") == 0 and g(kv, "hdirty") == 0
                    member(name, ok)
                    if hook == "upper":
                        member(name + " hlost1 (642(v))", g(kv, "hlost1") == 0)
                elif hook == "lower":
                    member("CONTROL0 " + name, g(kv, "hlost") >= 1 and g(kv, "lskip") == 0)
    rows.append("MEMBERS ALL OK" if not fails else "MEMBERS FAILED: " + "; ".join(fails))
    open(out_path, "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
    print("arms", len(rows) - 1, rows[-1])


main()

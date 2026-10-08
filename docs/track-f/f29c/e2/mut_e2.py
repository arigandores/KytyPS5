# F29c edition 2 (HPP-702): self-check of the executor (not the F29d member) - the mutants of ROADMAP s122 item 641(d) applied
# to the =1 branch of the stand MODEL in the worktree C:/kyty/f287/f29c/wt (726e751e), one build per mutant, the arms of
# B12-10n / B12-9n / B12-11 run at 10 000 iterations; the worktree file is restored by git after each mutant.
# Usage: python mut_e2.py   (prints one line per mutant and the table; exit 0)
import os
import re
import shutil
import subprocess

WT = "C:/kyty/f287/f29c/wt"
F = WT + "/tests/B12BdaStampStand.cpp"
OUT = "C:/kyty/f287/f29c/e2/mut"
GIT = "C:/Program Files/Git/cmd/git.exe"
NL = chr(10)

LATE_COLLECT = NL.join([
    "\t\t\t\ttracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);",
    "\t\t\t\tlskip++;"])
MUTANTS = {
    # late visit after a skip writes the witness
    "m1_late_writes_witness": (LATE_COLLECT, NL.join([
        "\t\t\t\tregion_stamps[index].stamp = tracker.RegionWriteStamp(index);",
        "\t\t\t\tregion_stamps[index].generation = stamp_generation;",
        LATE_COLLECT])),
    # late visit after a skip takes the bit
    "m2_late_takes_bit": (LATE_COLLECT, NL.join([
        "\t\t\t\t(void)(use_bits && Libs::Graphics::BdaTakeRegionWrite(index));",
        LATE_COLLECT])),
    # late visit after a skip skips without the witness check
    "m3_late_skips_unchecked": (NL.join([
        "\t\t\t\tif (late.generation == stamp_generation && late.stamp == tracker.RegionWriteStamp(index) &&",
        "\t\t\t\t    !(use_bits && Libs::Graphics::BdaRegionWritePending(index))) {"]), NL.join([
        "\t\t\t\tif (true || late.generation == stamp_generation) {"])),
    # a skip does not set the mark (both skip paths)
    "m4_skip_no_mark_bit": ("\t\t\t\t\tregion_stamps[index].skipped_pass = bda_pass;", "\t\t\t\t\t(void)0;"),
    # a skip does not set the mark on either skip path (str.replace replaces both sites)
    "m4b_skip_no_mark_both": ("skipped_pass = bda_pass;", "walked_pass += 0;"),
}


def run(exe, args, env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("KYTY_")}
    e.update(env)
    r = subprocess.run([exe] + args, capture_output=True, timeout=600, env=e)
    out = r.stdout.decode("utf-8", "replace")
    return r.returncode, dict(re.findall(r"(\w+)=([^ \n]+)", out))


def main():
    os.makedirs(OUT, exist_ok=True)
    orig = open(F, "rb").read()
    rows = []
    for name, (old, new) in MUTANTS.items():
        text = orig.decode("utf-8")
        n = text.count(old)
        if n == 0:
            rows.append("%s: ANCHOR NOT FOUND" % name)
            continue
        open(F, "wb").write(text.replace(old, new).encode("utf-8"))
        try:
            b = subprocess.run(["cmd", "/c", "C:\\kyty\\f287\\f29c\\build_f29c.cmd", "target", "b12_bdastamp_stand"],
                               capture_output=True, env=dict(os.environ, F29C_WT="C:\\kyty\\f287\\f29c\\wt",
                                                             F29C_BUILD="C:\\kyty\\f287\\f29c\\build"))
        finally:
            subprocess.run([GIT, "-C", WT, "checkout", "-q", "--", "tests/B12BdaStampStand.cpp"])
        if b.returncode != 0:
            rows.append("%s: BUILD FAILED" % name)
            continue
        exe = "%s/b12_stand_%s.exe" % (OUT, name)
        shutil.copyfile("C:/kyty/f287/f29c/build/b12_bdastamp_stand.exe", exe)
        cells = ["sites %d" % n]
        for hook in ("lower", "upper"):
            for bits in ("0", "1"):
                rc, f = run(exe, ["hole", "none", "2", "10000", "hook=" + hook],
                            {"KYTY_FIX_B12": "1", "KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_EPOCH_CACHE": "0"})
                cells.append("%s b%s rc=%d hlost=%s hdirty=%s hlost1=%s" % (
                    "B12-10n" if hook == "lower" else "B12-9n", bits, rc, f.get("hlost"), f.get("hdirty"), f.get("hlost1")))
        for bits in ("0", "1"):
            rc, f = run(exe, ["hole", "upper", "8", "10000"],
                        {"KYTY_FIX_B12": "1", "KYTY_BDA_WRITE_BITS": bits, "KYTY_BDA_EPOCH_CACHE": "0"})
            cells.append("B12-11 b%s rc=%d lost=%s dirty=%s lskip=%s late_scans=%s" % (
                bits, rc, f.get("lost"), f.get("dirty"), f.get("lskip"), f.get("late_scans")))
        rows.append("%s: %s" % (name, " | ".join(cells)))
        print(rows[-1], flush=True)
    # rebuild the clean stand so that the build dir matches 726e751e again
    subprocess.run(["cmd", "/c", "C:\\kyty\\f287\\f29c\\build_f29c.cmd", "target", "b12_bdastamp_stand"], capture_output=True,
                   env=dict(os.environ, F29C_WT="C:\\kyty\\f287\\f29c\\wt", F29C_BUILD="C:\\kyty\\f287\\f29c\\build"))
    same = open("C:/kyty/f287/f29c/build/b12_bdastamp_stand.exe", "rb").read() == open(
        "C:/kyty/f287/f29c/e2/exe/b12_stand_726e751e.exe", "rb").read()
    rows.append("clean stand rebuilt, equal to e2/exe/b12_stand_726e751e.exe byte for byte: %s" % same)
    open(OUT + "/mut_e2.txt", "w", encoding="utf-8", newline=NL).write(NL.join(rows) + NL)
    print(rows[-1])


if __name__ == "__main__":
    main()

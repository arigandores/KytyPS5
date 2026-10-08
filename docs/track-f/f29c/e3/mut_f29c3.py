# F29c3 (HPP-713, ROADMAP s122 item 645(v)): copy of 7417f704:docs/track-f/f29d/mut_f29d.py - the 13 forms and the 10 line
# anchors unchanged; worktree, build script, out dir and the matrix runner (run_f29c3.py: run_f29d.py + B12-9b) are of F29c3.
# Was:
# F29d (HPP-703, Red Team): own mutants of the =1 branch of the stand MODEL (tests/B12BdaStampStand.cpp of 726e751e) - the
# member of ROADMAP s122 items 639(e)(3) and 641(d). Each mutant is a line edit at a fixed line number of the 726e751e
# file whose content is asserted first (a moved or edited file refuses: ANCHOR MISMATCH). One stand build per mutant in the
# worktree C:/kyty/f287/f29d/wt, the full matrix of run_f29d.py at <iters>, the file restored byte for byte after each.
# Usage: python mut_f29d.py <iters>       prints one line per mutant: caught / NOT CAUGHT and the failing members
import hashlib
import os
import shutil
import subprocess
import sys

WT = "C:/kyty/f287/f29c3/wt"
F = WT + "/tests/B12BdaStampStand.cpp"
D = "C:/kyty/f287/f29c3"
OUT = D + "/mut"
NL = chr(10)
T = chr(9)

# (line number, exact content) anchors of 726e751e:tests/B12BdaStampStand.cpp
A = {
    218: T * 3 + "if (b12_pass && region_stamps[index].walked_pass == bda_pass) {",
    219: T * 4 + "tracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);",
    228: T * 3 + "if (b12_pass && region_stamps[index].skipped_pass == bda_pass) {",
    230: T * 4 + "if (late.generation == stamp_generation && late.stamp == tracker.RegionWriteStamp(index) &&",
    231: T * 4 + "    !(use_bits && Libs::Graphics::BdaRegionWritePending(index))) {",
    235: T * 4 + "tracker.CollectCpuModifiedRanges(cursor, bytes, dirty_ranges);",
    246: T * 5 + "region_stamps[index].skipped_pass = bda_pass;",
    256: T * 5 + "seen.skipped_pass = bda_pass;",
    262: T * 3 + "seen            = {stamp, stamp_generation};",
    264: T * 4 + "seen.walked_pass = bda_pass;",
}
W = T * 4 + "region_stamps[index].stamp = tracker.RegionWriteStamp(index); region_stamps[index].generation = stamp_generation;"
TAKE = T * 4 + "(void)(use_bits && Libs::Graphics::BdaTakeRegionWrite(index));"

# name -> list of (line, kind, text): kind "before" inserts text before the line, "replace" replaces the line
MUTANTS = {
    # 639(e)(3): a revisit (late visit after a scan) writes the witness / takes the bit
    "r1_rewalk_writes_witness": [(219, "before", W)],
    "r2_rewalk_takes_bit": [(219, "before", TAKE)],
    # 639(e)(3): walked_pass is not set by the scan / is set before the aggregate assignment / is set on a skip
    "r3a_scan_no_walked": [(264, "replace", T * 4 + "(void)0;")],
    "r3b_walked_before_assign": [(262, "replace", T * 3 + "if (b12_pass) { seen.walked_pass = bda_pass; }" + NL +
                                  T * 3 + "seen            = {stamp, stamp_generation};"),
                                 (264, "replace", T * 4 + "(void)0;")],
    "r3c_skip_sets_walked": [(246, "replace", A[246] + NL + T * 5 + "region_stamps[index].walked_pass = bda_pass;"),
                             (256, "replace", A[256] + NL + T * 5 + "seen.walked_pass = bda_pass;")],
    # 641(d): a late visit after a skip writes the witness / takes the bit / skips without the stamp check
    "l1_late_writes_witness": [(235, "before", W)],
    "l2a_late_takes_bit_at_check": [(231, "replace", T * 4 + "    !(use_bits && Libs::Graphics::BdaTakeRegionWrite(index))) {")],
    "l2b_late_takes_bit_on_collect": [(235, "before", TAKE)],
    "l3a_late_skips_without_stamp": [(230, "replace", T * 4 + "if (late.generation == stamp_generation &&")],
    "l3b_late_skips_always": [(230, "replace", T * 4 + "if (true ||"), ],
    # 641(d): a skip sets no mark (bit skip / witness skip)
    "l4a_bit_skip_no_mark": [(246, "replace", T * 5 + "(void)0;")],
    "l4b_witness_skip_no_mark": [(256, "replace", T * 5 + "(void)0;")],
    # extra (reference): the late visit after a skip without the generation half of the condition
    "x1_late_without_generation": [(230, "replace", T * 4 + "if (late.stamp == tracker.RegionWriteStamp(index) &&")],
}


def build():
    env = dict(os.environ)
    env["F29C3_WT"] = "C:" + chr(92) + "kyty" + chr(92) + "f287" + chr(92) + "f29c3" + chr(92) + "wt"
    env["F29C3_BUILD"] = "C:" + chr(92) + "kyty" + chr(92) + "f287" + chr(92) + "f29c3" + chr(92) + "build"
    r = subprocess.run(["cmd", "/c", D.replace("/", chr(92)) + chr(92) + "build_f29c3.cmd", "target", "b12_bdastamp_stand"],
                       capture_output=True, env=env, timeout=600)
    return r.returncode, r.stdout.decode("utf-8", "replace")[-400:]


def main():
    iters = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    orig = open(F, "rb").read()
    lines = orig.decode("utf-8").split(NL)
    for k, v in A.items():
        if lines[k - 1] != v:
            print("ANCHOR MISMATCH line %d: %r" % (k, lines[k - 1]))
            sys.exit(1)
    print("anchors 10 of 10 OK, file sha256", hashlib.sha256(orig).hexdigest()[:16], "iters", iters)
    for name, edits in MUTANTS.items():
        new = list(lines)
        for line, kind, text in sorted(edits, key=lambda e: -e[0]):
            if kind == "before":
                new.insert(line - 1, text)
            else:
                new[line - 1] = text
        open(F, "wb").write(NL.join(new).encode("utf-8"))
        try:
            rc, tail = build()
            if rc != 0:
                print("%s: BUILD FAILED %s" % (name, tail))
                continue
            exe = OUT + "/" + name + ".exe"
            shutil.copyfile(WT.replace("/wt", "/build") + "/b12_bdastamp_stand.exe", exe)
            res = OUT + "/" + name + ".txt"
            subprocess.run([sys.executable, D + "/run_f29c3.py", exe, iters, res], capture_output=True, timeout=600)
            last = open(res, encoding="utf-8").read().strip().split(NL)[-1]
            print("%s: %s | %s" % (name, "caught" if last.startswith("MEMBERS FAILED") else "NOT CAUGHT", last[:900]))
        finally:
            open(F, "wb").write(orig)
    assert open(F, "rb").read() == orig
    rc, tail = build()
    print("restored, clean stand rebuilt rc", rc)


main()

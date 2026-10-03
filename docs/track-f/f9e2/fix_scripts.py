# F9e2: retarget the two copied build scripts from P30b paths to F9e2 paths (backslash paths - done in python, not sed).
import pathlib
BS = chr(92)
d = pathlib.Path("C:/kyty/f287/f9/f9e2")
for name, pairs in [
    ("build_f9e2.cmd", [
        ("C:" + BS + "kyty" + BS + "p283" + BS + "p30b" + BS + "wt", "C:" + BS + "kyty" + BS + "f287" + BS + "f9" + BS + "f9e2" + BS + "wt"),
        ("C:" + BS + "kyty" + BS + "p283" + BS + "p30b" + BS + "build", "C:" + BS + "kyty" + BS + "f287" + BS + "f9" + BS + "f9e2" + BS + "build"),
        ("(P30 cd4c2803 + the P30b commit, LF)", "(4414e235 + the F9e2 commit, LF)"),
        ("C:" + BS + "kyty" + BS + "p283" + BS + "p30" + BS + "build_p30.cmd", "C:" + BS + "kyty" + BS + "p283" + BS + "p30b" + BS + "build_p30b.cmd"),
    ]),
    ("lockrun.sh", [
        (BS * 2 + "p283" + BS * 2 + "p30b" + BS * 2 + "build_p30b.cmd", BS * 2 + "f287" + BS * 2 + "f9" + BS * 2 + "f9e2" + BS * 2 + "build_f9e2.cmd"),
    ]),
]:
    p = d / name
    t = p.read_bytes().decode("utf-8")
    for a, b in pairs:
        n = t.count(a)
        print(name, n, a)
        t = t.replace(a, b)
    p.write_bytes(t.encode("utf-8"))

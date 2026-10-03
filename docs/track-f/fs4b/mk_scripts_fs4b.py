# FS4b (HPP-471, Red Team, ROADMAP s122 item 378(g)(2)): mk_wt_fs4b.sh, build_fs4b.cmd, lockrun.sh from my FS3b copies
# with the paths fs3\fs3b -> fs4\fs4b and the worktree commit d515b901 -> 3d0e46da (the FS4a worktree commit); LF out
# (build_fs4b.cmd CRLF as its source). Every replaced anchor must occur exactly once.
import pathlib
A = pathlib.Path("C:/kyty/f287/fs3/fs3b")
B = pathlib.Path("C:/kyty/f287/fs4/fs4b")
BS = chr(92)


def sub(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


wt = (A / "mk_wt_fs3b.sh").read_bytes().decode("utf-8").replace("\r", "")
wt = sub(wt, "WT=C:/kyty/f287/fs3/fs3b/wt", "WT=C:/kyty/f287/fs4/fs4b/wt")
wt = sub(wt, "C=d515b901", "C=3d0e46da")
wt = sub(wt, "#!/bin/bash\n", "#!/bin/bash\n# FS4b (HPP-471, Red Team, ROADMAP s122 item 378(g)(2)): own clean worktree on the FS4a worktree commit 3d0e46da"
         " (d515b901 + 92d11340 + 3d0e46da); copy of my FS3b script with WT and C changed. Was:\n")
(B / "mk_wt_fs4b.sh").write_bytes(wt.encode("utf-8"))

cmd = (A / "build_fs3b.cmd").read_bytes().decode("utf-8").replace("\r", "")
p = BS + "fs3" + BS + "fs3b" + BS
cmd = sub(cmd, "set \"SRC=C:" + BS + "kyty" + BS + "f287" + p + "wt\"", "set \"SRC=C:" + BS + "kyty" + BS + "f287" + BS + "fs4" + BS + "fs4b" + BS + "wt\"")
cmd = sub(cmd, "set \"BUILD=C:" + BS + "kyty" + BS + "f287" + p + "build\"", "set \"BUILD=C:" + BS + "kyty" + BS + "f287" + BS + "fs4" + BS + "fs4b" + BS + "build\"")
cmd = sub(cmd, "@echo off\n", "@echo off\nrem FS4b (HPP-471, Red Team): copy of my build_fs3b.cmd with SRC/BUILD set to fs4" + BS + "fs4b. Was:\n")
(B / "build_fs4b.cmd").write_bytes(cmd.replace("\n", "\r\n").encode("utf-8"))

lr = (A / "lockrun.sh").read_bytes().decode("utf-8").replace("\r", "")
old = "cmd //c \"C:" + BS * 2 + "kyty" + BS * 2 + "f287" + BS * 2 + "fs3" + BS * 2 + "fs3b" + BS * 2 + "build_fs3b.cmd\" $ARG > \"$LOG\" 2>&1 &"
new = "cmd //c \"C:" + BS * 2 + "kyty" + BS * 2 + "f287" + BS * 2 + "fs4" + BS * 2 + "fs4b" + BS * 2 + "build_fs4b.cmd\" $ARG > \"$LOG\" 2>&1 &"
lr = sub(lr, old, new)
lr = sub(lr, "#!/bin/bash\n", "#!/bin/bash\n# FS4b (HPP-471, Red Team): copy of my FS3b lockrun.sh with the build script path changed. Was:\n")
(B / "lockrun.sh").write_bytes(lr.encode("utf-8"))
print("OK")

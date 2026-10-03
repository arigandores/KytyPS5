# FS3b (HPP-448, Red Team): build_fs3b.cmd and lockrun.sh from the FS3a copies with the fs3a -> fs3b paths; LF out.
import pathlib
A = pathlib.Path("C:/kyty/f287/fs3/fs3a")
B = pathlib.Path("C:/kyty/f287/fs3/fs3b")
BS = chr(92)

cmd = (A / "build_fs3a.cmd").read_bytes().decode("utf-8").replace("\r", "")
lines = cmd.split("\n")
src_old = "set \"SRC=C:" + BS + "kyty" + BS + "f287" + BS + "fs3" + BS + "fs3a" + BS + "wt\""
bld_old = "set \"BUILD=C:" + BS + "kyty" + BS + "f287" + BS + "fs3" + BS + "fs3a" + BS + "build\""
assert lines.count(src_old) == 1 and lines.count(bld_old) == 1, "anchors"
lines = [l.replace("fs3a", "fs3b") if l in (src_old, bld_old) else l for l in lines]
lines.insert(1, "rem FS3b (HPP-448, Red Team): copy of build_fs3a.cmd with SRC/BUILD set to fs3" + BS + "fs3b.")
(B / "build_fs3b.cmd").write_bytes("\r\n".join(lines).encode("utf-8"))

lr = (A / "lockrun.sh").read_bytes().decode("utf-8").replace("\r", "")
ll = lr.split("\n")
old = "cmd //c \"C:" + BS * 2 + "kyty" + BS * 2 + "f287" + BS * 2 + "fs3" + BS * 2 + "fs3a" + BS * 2 + "build_fs3a.cmd\" $ARG > \"$LOG\" 2>&1 &"
assert ll.count(old) == 1, "lockrun anchor"
ll = [l.replace("fs3a", "fs3b") if l == old else l for l in ll]
ll.insert(1, "# FS3b (HPP-448, Red Team): copy of the FS3a lockrun.sh with the build script path changed.")
(B / "lockrun.sh").write_bytes("\n".join(ll).encode("utf-8"))
print("OK")

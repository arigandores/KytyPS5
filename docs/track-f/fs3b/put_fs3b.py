# FS3b (HPP-448, Red Team): append the FACTS section from facts_fs3b.tmpl.md (UTF-8, LF kept as the file has it) and copy
# the link files into docs/track-f/fs3b/ (text with LF) plus the report to docs/track-f/fs3b-review.md.
import pathlib, shutil
D = pathlib.Path("C:/kyty/f287/fs3/fs3b")
FACTS = pathlib.Path("C:/kyty/f287/FACTS.md")
tmpl = (D / "facts_fs3b.tmpl.md").read_bytes().decode("utf-8").replace("\r", "")
old = FACTS.read_bytes()
crlf = b"\r\n" in old
assert b"## FS3b (`HPP-448`" not in old, "FACTS section already there"
add = tmpl.replace("\n", "\r\n") if crlf else tmpl
FACTS.write_bytes(old + ("" if old.endswith(b"\n") else "\n").encode() + add.encode("utf-8"))
print("FACTS appended, crlf", crlf)

R = pathlib.Path("C:/kyty/KytyPS5/docs/track-f")
out = R / "fs3b"
out.mkdir(exist_ok=True)
names = ["mk_wt_fs3b.sh", "mk_wt.log", "mk_scripts_fs3b.py", "build_fs3b.cmd", "lockrun.sh", "lineage.out.txt", "sha_fs3b.txt",
         "mk_bincmp_fs3b.py", "bincmp_fs3b.py", "bincmp.out.txt", "fullcmp_fs3b.py", "fullcmp.out.txt", "fullcmp.run1_nopathmap.out.txt",
         "fullcmp.run2_noresidual.out.txt", "mk_knobs_fs3b.py", "knobs_fs3b.py", "knobs_fs3b.out.txt", "cfgtests_defaults.log",
         "gate_order.out.txt", "put_fs3b.py", "facts_fs3b.tmpl.md"]
for n in names:
    b = (D / n).read_bytes().replace(b"\r\n", b"\n")
    (out / n).write_bytes(b)
(R / "fs3b-review.md").write_bytes((D / "fs3b-review.md").read_bytes().replace(b"\r\n", b"\n"))
print("copied", len(names) + 1)

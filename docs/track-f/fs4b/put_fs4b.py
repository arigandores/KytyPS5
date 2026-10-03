# FS4b (HPP-471, Red Team): append the FACTS section from facts_fs4b.tmpl.md (CRLF if FACTS.md has it) and copy the link
# files into docs/track-f/fs4b/ (text with LF) plus the report to docs/track-f/fs4b-review.md. Copy of my put_fs3b.py.
import pathlib
D = pathlib.Path("C:/kyty/f287/fs4/fs4b")
FACTS = pathlib.Path("C:/kyty/f287/FACTS.md")
tmpl = (D / "facts_fs4b.tmpl.md").read_bytes().decode("utf-8").replace("\r", "")
old = FACTS.read_bytes()
crlf = b"\r\n" in old
assert "## FS4b (`HPP-471`".encode("utf-8") not in old, "FACTS section already there"
add = tmpl.replace("\n", "\r\n") if crlf else tmpl
FACTS.write_bytes(old + ("" if old.endswith(b"\n") else "\n").encode() + add.encode("utf-8"))
print("FACTS appended, crlf", crlf)

R = pathlib.Path("C:/kyty/KytyPS5/docs/track-f")
out = R / "fs4b"
out.mkdir(exist_ok=True)
names = ["mk_scripts_fs4b.py", "mk_wt_fs4b.sh", "mk_wt.log", "build_fs4b.cmd", "lockrun.sh", "sha_fs4b.txt", "lineage_fs4b.sh",
         "lineage.out.txt", "fs4_vs_92d11340.diff", "mk_cmp_fs4b.py", "bincmp_fs4b.py", "bincmp.out.txt", "fullcmp_fs4b.py",
         "fullcmp.out.txt", "residual_fs4b.py", "residual.out.txt", "mk_knobs_fs4b.py", "knobs_fs4b.py", "knobs_fs4b.out.txt",
         "knobs_d515b901.out.txt", "cfgtests_defaults.log", "gate_order.out.txt", "mk_fixture_fs4b.py", "fx_3d0e46da.cpp",
         "fx_92d11340.cpp", "build_fx.cmd", "run_fixture_fs4b.py", "fixture.out.txt", "put_fs4b.py", "facts_fs4b.tmpl.md"]
for n in names:
    b = (D / n).read_bytes().replace(b"\r\n", b"\n")
    (out / n).write_bytes(b)
(R / "fs4b-review.md").write_bytes((D / "fs4b-review.md").read_bytes().replace(b"\r\n", b"\n"))
print("copied", len(names) + 1)

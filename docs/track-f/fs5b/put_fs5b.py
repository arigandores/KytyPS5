# FS5b (HPP-510, Red Team): append the FACTS section from facts_fs5b.tmpl.md (CRLF if FACTS.md has it) and copy the link
# files into docs/track-f/fs5b/ (text with LF) plus the report to docs/track-f/fs5b-review.md. Copy of my put_fs4b.py.
import pathlib
D = pathlib.Path("C:/kyty/f287/fs5/fs5b")
FACTS = pathlib.Path("C:/kyty/f287/FACTS.md")
tmpl = (D / "facts_fs5b.tmpl.md").read_bytes().decode("utf-8").replace("\r", "")
old = FACTS.read_bytes()
crlf = b"\r\n" in old
assert "## FS5b (`HPP-510`".encode("utf-8") not in old, "FACTS section already there"
add = tmpl.replace("\n", "\r\n") if crlf else tmpl
FACTS.write_bytes(old + ("" if old.endswith(b"\n") else "\n").encode() + add.encode("utf-8"))
print("FACTS appended, crlf", crlf)

R = pathlib.Path("C:/kyty/KytyPS5/docs/track-f")
out = R / "fs5b"
out.mkdir(exist_ok=True)
names = ["mk_scripts_fs5b.py", "mk_wt_fs5b.sh", "mk_wt.log", "build_fs5b.cmd", "lockrun.sh", "sha_fs5b.txt", "lineage_fs5b.sh",
         "lineage.out.txt", "fs5_vs_3d0e46da_src.diff", "fs5_vs_8a56dc2a.diff", "mk_cmp_fs5b.py", "bincmp_fs5b.py", "bincmp.out.txt",
         "fullcmp_fs5b.py", "fullcmp.out.txt", "residual_fs5b.py", "residual.out.txt", "residual2_fs5b.py", "residual2.out.txt",
         "run_tests_fs5b.sh", "run_tests.out.txt", "cfgtests_defaults.log", "gate_order.out.txt", "mk_fx_scripts_fs5b.py",
         "mk_fixture_fs5b.py", "fx_0e72bc19.cpp", "fx_8a56dc2a.cpp", "build_fx.cmd", "run_fixture_fs5b.py", "fixture.out.txt",
         "knobs_fs5b.py", "knobs_fs5b.out.txt", "knobs_3d0e46da.out.txt", "put_fs5b.py", "facts_fs5b.tmpl.md"]
names += ["gate_f10%s_nat%d.txt" % (f, n) for f in ("unset", "0", "1") for n in (0, 1)]
for n in names:
    b = (D / n).read_bytes().replace(b"\r\n", b"\n")
    (out / n).write_bytes(b)
(R / "fs5b-review.md").write_bytes((D / "fs5b-review.md").read_bytes().replace(b"\r\n", b"\n"))
print("copied", len(names) + 1)

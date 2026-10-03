# FS3b (HPP-448, Red Team): knobs_fs3b.py = my FS2b knobs_fs2b.py (docs/track-f/fs2b/knobs_fs2b.py; independent of the
# FS3a knobs_fs3a.py) with the default commit d515b901 and an expected-set check of item 367(g)(1) appended; LF out.
import pathlib
src = pathlib.Path("C:/kyty/KytyPS5/docs/track-f/fs2b/knobs_fs2b.py").read_bytes().decode("utf-8").replace("\r", "")
rep = [
    ("# FS2b (HPP-382, Red Team): own reading of env knobs in git diff 4fc501f4 <commit> -- src/ (independent of knobs_fs2a.py;",
     "# FS3b (HPP-448, Red Team): port of my FS2b scanner to the FS3 worktree commit d515b901 (independent of knobs_fs3a.py) +\n"
     "# the expected ON set of ROADMAP s122 item 367(g)(1). Was:\n"
     "# FS2b (HPP-382, Red Team): own reading of env knobs in git diff 4fc501f4 <commit> -- src/ (independent of knobs_fs2a.py;", 1),
    ("C = sys.argv[1] if len(sys.argv) > 1 else '9c9d86ae'", "C = sys.argv[1] if len(sys.argv) > 1 else 'd515b901'", 1),
]
for old, new, n in rep:
    c = src.count(old)
    assert c == n, (old, c)
    src = src.replace(old, new)
src = src.rstrip("\n") + "\n" + "\n".join([
    "EXPECTED = {'KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE', 'KYTY_FIX_B9A', 'KYTY_FIX_B42'}",
    "ok = set(on) == EXPECTED and not und",
    "print('ON-IF-UNSET == item 367(g)(1) set:', set(on) == EXPECTED, 'missing', sorted(EXPECTED - set(on)), 'extra', sorted(set(on) - EXPECTED))",
    "print('KNOBS', 'ALL OK' if ok else 'CHECK BY HAND (UNDECIDED or set differs)')",
]) + "\n"
pathlib.Path("C:/kyty/f287/fs3/fs3b/knobs_fs3b.py").write_bytes(src.encode("utf-8"))
print("OK")

# FS4b (HPP-471, Red Team): knobs_fs4b.py = my FS3b knobs_fs3b.py (docs/track-f/fs3b/knobs_fs3b.py; independent of the
# FS4a knobs_fs4a.py) with the default commit 3d0e46da and the expected ON set of item 378(g)(1) (+ KYTY_FIX_SVAL); LF out.
import pathlib
src = pathlib.Path("C:/kyty/KytyPS5/docs/track-f/fs3b/knobs_fs3b.py").read_bytes().decode("utf-8").replace("\r", "")
rep = [
    ("# FS3b (HPP-448, Red Team): port of my FS2b scanner to the FS3 worktree commit d515b901 (independent of knobs_fs3a.py) +",
     "# FS4b (HPP-471, Red Team): port of my FS3b scanner to the FS4 worktree commit 3d0e46da (independent of knobs_fs4a.py) +\n"
     "# the expected ON set of ROADMAP s122 item 378(g)(1). Was:\n"
     "# FS3b (HPP-448, Red Team): port of my FS2b scanner to the FS3 worktree commit d515b901 (independent of knobs_fs3a.py) +", 1),
    ("C = sys.argv[1] if len(sys.argv) > 1 else 'd515b901'", "C = sys.argv[1] if len(sys.argv) > 1 else '3d0e46da'", 1),
    ("EXPECTED = {'KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE', 'KYTY_FIX_B9A', 'KYTY_FIX_B42'}",
     "EXPECTED = {'KYTY_FIX_B26', 'KYTY_FIX_B1B', 'KYTY_FIX_DUALSRC', 'KYTY_FIX_MINIMIZE', 'KYTY_FIX_B9A', 'KYTY_FIX_B42', 'KYTY_FIX_SVAL'}", 1),
    ("print('ON-IF-UNSET == item 367(g)(1) set:'", "print('ON-IF-UNSET == item 378(g)(1) set:'", 1),
]
for old, new, n in rep:
    c = src.count(old)
    assert c == n, (old, c)
    src = src.replace(old, new)
pathlib.Path("C:/kyty/f287/fs4/fs4b/knobs_fs4b.py").write_bytes(src.encode("utf-8"))
print("OK")

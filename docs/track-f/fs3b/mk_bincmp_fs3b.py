# FS3b (HPP-448, Red Team): bincmp_fs3b.py = my FS2b bincmp_fs2b.py (docs/track-f/fs2b/bincmp_fs2b.py) with the
# paths, the expected sha and the worktree-path mapping changed to FS3 (fs3/fs3b -> fs3/fs3a). Every replaced anchor
# must occur the stated number of times; LF out.
import pathlib
src = pathlib.Path("C:/kyty/KytyPS5/docs/track-f/fs2b/bincmp_fs2b.py").read_bytes().decode("utf-8").replace("\r", "")
rep = [
    ("# FS2b (HPP-382, Red Team): independent rebuild check of the FS2 binary by ROADMAP p.286(b) (i)-(iii).",
     "# FS3b (HPP-448, Red Team): independent rebuild check of the FS3 binary 540c035a (ROADMAP s122 item 367(g)(2)); a port of\n"
     "# my FS2b bincmp_fs2b.py with paths fs2b -> fs3/fs3b, fs2a -> fs3/fs3a. Was:\n"
     "# FS2b (HPP-382, Red Team): independent rebuild check of the FS2 binary by ROADMAP p.286(b) (i)-(iii).", 1),
    ("A_PATH = 'C:/kyty/f287/fs2b/build/install/kyty_emulator.exe'", "A_PATH = 'C:/kyty/f287/fs3/fs3b/build/install/kyty_emulator.exe'", 1),
    ("B_PATH = 'C:/kyty/f287/bin/kyty_emulator_bbad499c.exe'", "B_PATH = 'C:/kyty/f287/bin/kyty_emulator_540c035a.exe'", 1),
    ("B_SHA = 'bbad499c56b744dfcef85b7556735c025ebb3db185b6bb9b02e7a0b3a228eb55'",
     "B_SHA = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'", 1),
    ("print('B sha256 == FS2a report', hb == B_SHA)", "print('B sha256 == FS3a report', hb == B_SHA)", 1),
    ("va = gv('C:/kyty/f287/fs2b/build/kytyGitVersion.h')", "va = gv('C:/kyty/f287/fs3/fs3b/build/kytyGitVersion.h')", 1),
    ("vb = gv('C:/kyty/f287/fs2a/build/kytyGitVersion.h')", "vb = gv('C:/kyty/f287/fs3/fs3a/build/kytyGitVersion.h')", 1),
    ("na = A.replace(b'f287' + BS + b'fs2b', b'f287' + BS + b'fs2a').replace(b'f287/fs2b', b'f287/fs2a')",
     "na = A.replace(b'fs3' + BS + b'fs3b', b'fs3' + BS + b'fs3a').replace(b'fs3/fs3b', b'fs3/fs3a')", 1),
]
for old, new, n in rep:
    c = src.count(old)
    assert c == n, (old, c)
    src = src.replace(old, new)
pathlib.Path("C:/kyty/f287/fs3/fs3b/bincmp_fs3b.py").write_bytes(src.encode("utf-8"))
print("OK")

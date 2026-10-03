# FS4b (HPP-471, Red Team): bincmp_fs4b.py and fullcmp_fs4b.py = my FS3b bincmp_fs3b.py / fullcmp_fs3b.py with the paths
# fs3/fs3b -> fs4/fs4b, fs3/fs3a -> fs4/fs4a, the B binary 540c035a -> 31cbfee8 (FS4a report) and the SDL revision strings
# of my build (3d0e46da, configured on it) and of FS4a (configured on 92d11340 before the last cherry-pick). Every replaced
# anchor must occur the stated number of times; LF out.
import pathlib
S = pathlib.Path("C:/kyty/f287/fs3/fs3b")
D = pathlib.Path("C:/kyty/f287/fs4/fs4b")


def port(name_in, name_out, rep):
    src = (S / name_in).read_bytes().decode("utf-8").replace("\r", "")
    for old, new, n in rep:
        c = src.count(old)
        assert c == n, (name_in, old, c)
        src = src.replace(old, new)
    (D / name_out).write_bytes(src.encode("utf-8"))


port("bincmp_fs3b.py", "bincmp_fs4b.py", [
    ("# FS3b (HPP-448, Red Team): independent rebuild check of the FS3 binary 540c035a (ROADMAP s122 item 367(g)(2)); a port of",
     "# FS4b (HPP-471, Red Team): independent rebuild check of the FS4 binary 31cbfee8 (ROADMAP s122 item 378(g)(2)); a port of\n"
     "# my FS3b bincmp_fs3b.py with paths fs3/fs3b -> fs4/fs4b, fs3/fs3a -> fs4/fs4a. Was:\n"
     "# FS3b (HPP-448, Red Team): independent rebuild check of the FS3 binary 540c035a (ROADMAP s122 item 367(g)(2)); a port of", 1),
    ("A_PATH = 'C:/kyty/f287/fs3/fs3b/build/install/kyty_emulator.exe'", "A_PATH = 'C:/kyty/f287/fs4/fs4b/build/install/kyty_emulator.exe'", 1),
    ("B_PATH = 'C:/kyty/f287/bin/kyty_emulator_540c035a.exe'", "B_PATH = 'C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe'", 1),
    ("B_SHA = '540c035ac09f428a5b10617566627c71d79aacbeeafe0c8452db2c7ddd96f4a1'",
     "B_SHA = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'", 1),
    ("print('B sha256 == FS3a report', hb == B_SHA)", "print('B sha256 == FS4a report', hb == B_SHA)", 1),
    ("va = gv('C:/kyty/f287/fs3/fs3b/build/kytyGitVersion.h')", "va = gv('C:/kyty/f287/fs4/fs4b/build/kytyGitVersion.h')", 1),
    ("vb = gv('C:/kyty/f287/fs3/fs3a/build/kytyGitVersion.h')", "vb = gv('C:/kyty/f287/fs4/fs4a/build/kytyGitVersion.h')", 1),
    ("na = A.replace(b'fs3' + BS + b'fs3b', b'fs3' + BS + b'fs3a').replace(b'fs3/fs3b', b'fs3/fs3a')",
     "na = A.replace(b'fs4' + BS + b'fs4b', b'fs4' + BS + b'fs4a').replace(b'fs4/fs4b', b'fs4/fs4a')", 1),
])

port("fullcmp_fs3b.py", "fullcmp_fs4b.py", [
    ("# FS3b (HPP-448, Red Team): every differing byte run of the whole file A (own build) vs B (540c035a), each run named by",
     "# FS4b (HPP-471, Red Team): port of my FS3b fullcmp_fs3b.py to FS4 (B = 31cbfee8, paths fs4/fs4b -> fs4/fs4a). Was:\n"
     "# FS3b (HPP-448, Red Team): every differing byte run of the whole file A (own build) vs B (540c035a), each run named by", 1),
    ("A = open('C:/kyty/f287/fs3/fs3b/build/install/kyty_emulator.exe', 'rb').read()",
     "A = open('C:/kyty/f287/fs4/fs4b/build/install/kyty_emulator.exe', 'rb').read()", 1),
    ("B = open('C:/kyty/f287/bin/kyty_emulator_540c035a.exe', 'rb').read()",
     "B = open('C:/kyty/f287/bin/kyty_emulator_31cbfee8.exe', 'rb').read()", 1),
    ("sa = b'SDL-KytyPS5-2026-09-15-6a2987a-1872-gd515b901'", "sa = b'SDL-KytyPS5-2026-09-15-6a2987a-1874-g3d0e46da'", 1),
    ("sb = b'SDL-KytyPS5-2026-09-15-6a2987a-1871-g722c5e7f'", "sb = b'SDL-KytyPS5-2026-09-15-6a2987a-1873-g92d11340'", 1),
    ("A2 = bytearray(A.replace(sa, sb).replace(b'fs3' + BS + b'fs3b', b'fs3' + BS + b'fs3a').replace(b'fs3/fs3b', b'fs3/fs3a'))",
     "A2 = bytearray(A.replace(sa, sb).replace(b'fs4' + BS + b'fs4b', b'fs4' + BS + b'fs4a').replace(b'fs4/fs4b', b'fs4/fs4a'))", 1),
])
print("OK")

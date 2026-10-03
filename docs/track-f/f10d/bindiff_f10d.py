# F10d (HPP-452, Red Team): byte comparison of the own clean-worktree build against the F10c binary 36e2b042.
# Normalizes the build path (f10d -> f10c, same length), PE TimeDateStamp and CheckSum; prints the remaining diff runs
# grouped, and the counts of both git revisions in each binary. Read-only.
import struct, sys, collections
A = "C:/kyty/f287/f10d/build/install/kyty_emulator.exe"
B = "C:/kyty/f287/f10c/kyty_emulator_36e2b042.exe"
a = bytearray(open(A, "rb").read())
b = bytearray(open(B, "rb").read())
BS = bytes([92])
for x, y in ((b"f287" + BS + b"f10d", b"f287" + BS + b"f10c"), (b"f287/f10d", b"f287/f10c")):
    a = bytearray(bytes(a).replace(x, y))
pe = struct.unpack_from("<I", a, 0x3c)[0]
for x in (a, b):
    x[pe + 8:pe + 12] = b"\0" * 4
    x[pe + 88:pe + 92] = b"\0" * 4
print("len", len(a), len(b))
diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
runs = []
s = p = None
for i in diff:
    if s is None:
        s = p = i
    elif i <= p + 8:
        p = i
    else:
        runs.append((s, p)); s = p = i
if s is not None:
    runs.append((s, p))
print("diff bytes after normalization", len(diff), "runs", len(runs))
kinds = collections.Counter()
for r in runs:
    ctx = bytes(a[max(0, r[0] - 40):r[1] + 40])
    near = bytes(a[max(0, r[0] - 12):r[1] + 2])
    if b"g68602c4f" in ctx or b"1961" in ctx:
        kinds["git version string"] += 1
    elif b"?A0x" in near:
        kinds["anonymous namespace hash ?A0x (path-derived)"] += 1
    elif b"RSDS" in ctx or (r[1] - r[0] < 4 and bytes(a[r[0] - 8:r[0]]) == b"\0" * 8):
        kinds["debug directory: RSDS GUID / timestamp"] += 1
    else:
        kinds["other"] += 1
        if kinds["other"] <= 12:
            print("other", hex(r[0]), r[1] - r[0] + 1, bytes(a[r[0] - 8:r[1] + 8]).hex(), bytes(b[r[0] - 8:r[1] + 8]).hex())
print(dict(kinds))
for s_ in (b"465f0d8e", b"68602c4f", b"1959-g", b"1961-g"):
    print(s_.decode(), "own", a.count(s_), "f10c", b.count(s_))

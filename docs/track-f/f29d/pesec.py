# F29d (HPP-703, Red Team): differing byte runs per PE section, after normalizing the known build-id strings (worktree
# path f29d -> f29c, the SDL_REVISION configure string 1908-g673b780a -> 1907-g61be23e1); the remaining runs are classified
# (PE header, anonymous-namespace hash "?A0x..." of a mangled name, other).
# Usage: python pesec.py <reference.exe> <rebuilt.exe>
import collections
import re
import sys

sys.path.insert(0, ".")
from pediff import sections  # noqa: E402

BS = chr(92).encode()
a = open(sys.argv[1], "rb").read()
b = open(sys.argv[2], "rb").read()
b = b.replace(BS + b"f287" + BS + b"f29d" + BS, BS + b"f287" + BS + b"f29c" + BS)
b = b.replace(b"/f287/f29d/", b"/f287/f29c/").replace(b"1908-g673b780a", b"1907-g61be23e1")
assert len(a) == len(b)
pe, secs = sections(a)
runs = []
i = 0
n = len(a)
while i < n:
    if a[i] != b[i]:
        j = i
        while j < n and a[j] != b[j]:
            j += 1
        runs.append((i, j))
        i = j
    else:
        i += 1
cnt = collections.Counter()
anon = 0
other = []
for i, j in runs:
    sec = [nm for nm, va, vs, raw, rs in secs if raw <= i < raw + rs]
    s = sec[0] if sec else "hdr"
    cnt[s] += 1
    head = a[max(0, i - 14):i]
    if re.search(rb"\?A0x[0-9A-Fa-f]*$", head):
        anon += 1
    elif s != "hdr":
        other.append((hex(i), s, a[max(0, i - 24):j + 8], b[max(0, i - 24):j + 8]))
print("sections", [(nm, hex(raw), rs) for nm, va, vs, raw, rs in secs])
print("runs after normalization", len(runs), "per section", dict(cnt))
print("anonymous-namespace hash runs (?A0x...)", anon)
print("other runs outside the PE header", len(other))
for x in other[:20]:
    print(" ", x)

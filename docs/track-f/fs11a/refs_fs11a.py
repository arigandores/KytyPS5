# FS11a (HPP-714): checks every <commit>:<path>:<line> reference of docs/track-f/fs11a.md (rule 24(1)): the line equals the
# anchor and the line +1 equals the +1 anchor (whole lines, leading/trailing whitespace stripped). Negative control: every
# reference shifted by +1 must fail. Prints REFS <n> ALL OK and "negctl FAILED" (wanted).
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
REFS = [
    ("cb022252", "src/graphics/host_gpu/regionManager.h", 67,
     '// Track F, FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
     '// value as EnvValueOn (the form of FS4a 17adaf80).'),
    ("ee9632be", "src/graphics/host_gpu/regionManager.h", 66,
     '// Track F, FS11a (HPP-714, ROADMAP s122 item 647(d)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
     '// value as EnvValueOn (the form of FS4a 17adaf80).'),
    ("ee9632be", "src/graphics/host_gpu/renderer/cache/bufferCache.cpp", 602,
     'const bool               fix_b12 = FixB12Enabled();',
     'if (!fix_b12_logged.exchange(true, std::memory_order_relaxed)) {'),
    ("ee9632be", "src/graphics/host_gpu/renderer/cache/bufferCache.cpp", 604,
     'LOGF("FixB12: mode=%d\\n", fix_b12 ? 1 : 0);',
     '}'),
    ("ee9632be", "src/graphics/host_gpu/renderer/renderContext.cpp", 382,
     'const bool fix_b12 = FixB12Enabled();',
     'if (fix_b12) {'),
]


def lines(c, p):
    out = subprocess.run([G, "-C", REPO, "show", "%s:%s" % (c, p)], capture_output=True, check=True).stdout
    return out.decode("utf-8").replace("\r\n", "\n").split("\n")


def check(shift):
    ok = True
    for c, p, n, a0, a1 in REFS:
        ls = lines(c, p)
        i = n - 1 + shift
        good = i + 1 < len(ls) and ls[i].strip() == a0 and ls[i + 1].strip() == a1
        if shift == 0:
            print("%s %s:%s:%d" % ("ok  " if good else "BAD ", c, p, n))
        ok &= good
    return ok


ok = check(0)
neg = check(1)
print("REFS %d %s" % (len(REFS), "ALL OK" if ok else "FAILED"))
print("negctl (+1 shift) %s" % ("passed (BAD)" if neg else "FAILED"))
sys.exit(0 if ok and not neg else 1)

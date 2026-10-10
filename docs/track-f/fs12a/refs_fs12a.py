# FS12a (HPP-750): port of fs11a/refs_fs11a.py - checks every <commit>:<path>:<line> reference of docs/track-f/fs12a.md (rule 24(1)): the line equals the
# anchor and the line +1 equals the +1 anchor (whole lines, leading/trailing whitespace stripped). Negative control: every
# reference shifted by +1 must fail. Prints REFS <n> ALL OK and "negctl FAILED" (wanted).
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
REFS = [
    ("cbfe8375", "src/common/subsystems.cpp", 71,
     '// Track F, FS12a (HPP-750, ROADMAP s122 item 683(g)(1)): default ON - unset or "" = ON, 0/false/off/no = OFF, any other',
     '// value as EnvValueOn (the form of FS11a cb022252).'),
    ("730ed40a", "src/common/subsystems.cpp", 74,
     'const char* value = std::getenv("KYTY_FIX_F21");',
     "g_fix_f21  = value == nullptr || value[0] == '\\0' || EnvValueOn(value);"),
    ("730ed40a", "src/common/subsystems.cpp", 80,
     'LOGF("FixF21: mode=%d wait_ms=%u\\n", g_fix_f21 ? 1 : 0, kFixF21WaitMs);',
     '}'),
    ("730ed40a", "src/emulator.cpp", 530,
     'Common::Subsystems::InitFixF21();',
     'Common::Subsystems subsystems(true);'),
    ("730ed40a", "src/common/subsystems.cpp", 129,
     'if (!g_fix_f21) {',
     '// KYTY_FIX_F21=0 with the stand armed: the FS11 sequence - every entry walks - observed.'),
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

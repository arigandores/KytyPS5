# FS5a (HPP-509, ROADMAP s122 p.410(g)(1)): copy of knobs_fs4a.py, the expected set + KYTY_FIX_F10. Was:
# FS4a (HPP-470, ROADMAP s122 p.378(g)(1)): copy of knobs_fs3a.py, the expected set + KYTY_FIX_SVAL. Was:
# FS3a (HPP-447, ROADMAP s122 p.367(g)(1)): copy of knobs_fs2a.py, the expected set + KYTY_FIX_B42. Was:
# FS2a (HPP-381, ROADMAP s122 p.298(v)): every KYTY_* name on an added or removed line of `git diff 4fc501f4 <commit> -- src/`,
# with file:line in <commit> of every line of the new tree that names it (the form of knobs_fsa.py, FSa), plus a mechanical
# default class of each getenv reading site: "DEFAULT-ON" if the reading or one of the next 2 lines takes unset (nullptr)
# as ON (`== nullptr || ... EnvValueOn`; a bare `== nullptr ||` guard returning OFF, as KYTY_TEST_MINIMIZE, is not),
# "default-off" otherwise; KNOB_DEFINITIONS rows - their fallback column. Classification is a
# help for the hand table, the table in fs2a.md is checked by hand against the printed lines.
import re, subprocess, sys, collections

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "4fc501f4"
TIP = sys.argv[1] if len(sys.argv) > 1 else "HEAD"

def git(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")

diff = git("diff", "--ignore-cr-at-eol", "-U0", BASE, TIP, "--", "src/")
rx = re.compile(r'"(KYTY_[A-Z0-9_]+)"')
added, removed = collections.defaultdict(list), collections.defaultdict(list)
cur, ln = None, 0
for line in diff.split("\n"):
    if line.startswith("+++ "):
        cur = line[6:] if line.startswith("+++ b/") else None
        continue
    if line.startswith("--- "):
        continue
    m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
    if m:
        ln = int(m.group(1))
        continue
    if line.startswith("+"):
        for k in rx.findall(line):
            added[k].append(f"{cur}:{ln}")
        ln += 1
    elif line.startswith("-"):
        for k in rx.findall(line):
            removed[k].append("(removed line)")

file_cache = {}
def tip_lines(path):
    if path not in file_cache:
        file_cache[path] = git("show", f"{TIP}:{path}").split("\n")
    return file_cache[path]

def classify(path, lineno, text):
    if "getenv" in text or "EnvFlagOn" in text:
        lines = tip_lines(path)
        window = " ".join(lines[lineno - 1:lineno + 2])
        if "EnvFlagOn" in text:
            return "default-off (EnvFlagOn)"
        if re.search(r"== nullptr \|\|.*EnvValueOn", window):
            return "DEFAULT-ON (unset = ON)"
        return "default-off/other (read by hand)"
    m = re.match(r'\s*\{"KYTY_[A-Z0-9_]+",\s*"[^"]*",\s*(-?\d+)', text)
    if m:
        return f"table row fallback {m.group(1)}"
    return "other (read by hand)"

files = git("diff", "--ignore-cr-at-eol", "--stat", BASE, TIP, "--", "src/").strip().split("\n")[-1]
print("diff", BASE, TIP, ":", files)
names = sorted(set(added) | set(removed))
print("KYTY_* names on +/- lines:", len(names))
on_names = set()
for k in names:
    print(f"{k}  added_lines={len(added[k])} removed_lines={len(removed[k])}")
    for s in added[k]:
        print("   +", s)
    g = git("grep", "-n", f'"{k}"', TIP, "--", "src/")
    for l in g.strip().split("\n"):
        if not l:
            continue
        _, path, lineno, text = l.split(":", 3)
        cls = classify(path, int(lineno), text)
        if cls.startswith("DEFAULT-ON"):
            on_names.add(k)
        print("   tip", f"{path}:{lineno}:{text.strip()}"[:200], "|", cls)
print("DEFAULT-ON names (unset = ON):", " ".join(sorted(on_names)))
expected = {"KYTY_FIX_B26", "KYTY_FIX_B1B", "KYTY_FIX_DUALSRC", "KYTY_FIX_MINIMIZE", "KYTY_FIX_B9A", "KYTY_FIX_B42", "KYTY_FIX_SVAL", "KYTY_FIX_F10"}
print("expected (p.298(v) + p.327(g) + p.367(g)(1) + p.378(g)(1) + p.410(g)(1)):", " ".join(sorted(expected)))
print("DEFAULT-ON == expected:", on_names == expected)
print("ALL OK" if on_names == expected else "MISMATCH")

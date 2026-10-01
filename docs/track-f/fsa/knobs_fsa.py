# FSa (HPP-368, p.282(g)(1)): every KYTY_* name on an added or removed line of `git diff 4fc501f4 <commit> -- src/`,
# with file:line in <commit> of every line of the new tree that names it (reading sites to classify by hand).
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

files = git("diff", "--ignore-cr-at-eol", "--stat", BASE, TIP, "--", "src/").strip().split("\n")[-1]
print("diff", BASE, TIP, ":", files)
names = sorted(set(added) | set(removed))
print("KYTY_* names on +/- lines:", len(names))
for k in names:
    print(f"{k}  added_lines={len(added[k])} removed_lines={len(removed[k])}")
    for s in added[k]:
        print("   +", s)
    # all sites in the tip tree
    g = git("grep", "-n", f'"{k}"', TIP, "--", "src/")
    for l in g.strip().split("\n"):
        if l:
            print("   tip", l.split(":", 1)[1][:200])
print("ALL OK")

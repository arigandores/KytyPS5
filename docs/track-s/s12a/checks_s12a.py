# S12a (HPP-494, ROADMAP s122 item 408(l), 410(g)(6)): source checks of the S12 tip without the game.
# (1) diff of the S12 tip against the base 0e72bc19 (FS5 worktree commit) - files and stat;
# (2) member "contains" in the reading of item 380(b): git cherry -v <tip> <c> <c>^ ('-' = an equal change is in the
#     history of the tip, '+' = absent) for the FS3a..FS5a commits and the S12a commit; track P / F14c / F15a - expected '+';
# (3) S-pcw code of the tip = S-pcw code of binary f3b3aa3b (S6 / S10): f3b3aa3b was built from the tree
#     C:/kyty/s288/wt_s5c = 4fc501f4 + `git diff ae704c5d 2ce6326e -- pipelineCache.{cpp,h}` (FACTS S5c). Check (a): that
#     tree's two files (CR ignored) = 2ce6326e's two files with 4fc501f4's base, i.e. the S-pcw '+' lines of
#     ae704c5d..2ce6326e are all in wt_s5c; check (b): every S-pcw line - a '+' line of `git diff ae704c5d 2ce6326e` - is
#     located in 2ce6326e (line number); every hunk of `git diff 2ce6326e <tip>` on the two files is printed with a flag
#     PCW if its old range overlaps an S-pcw line or it inserts strictly between two S-pcw lines; the PCW hunks are the
#     named differences.
import re, subprocess, sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
TIP = sys.argv[1]
BASE = "0e72bc19"
FILES = ["src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp", "src/graphics/host_gpu/renderer/pipeline/pipelineCache.h"]
WT_S5C = "C:/kyty/s288/wt_s5c"

def git(*a, cwd=REPO):
    return subprocess.run([G, "-C", cwd, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")

ok = True
print("== (1) git diff --stat", BASE, TIP)
st = git("diff", "--stat", BASE, TIP)
print(st.rstrip())
names = git("diff", "--name-only", BASE, TIP).split()
print("files:", names)
ok &= names == [FILES[0]]

print("== (2) git cherry -v", TIP, "<c> <c>^")
want = {"4e72289e": "-", "68602c4f": "-", "17adaf80": "-", "1833ee28": "-", "c3eb8fe8": "-", "c1732d1a": "-",
        "e11a297b": "-", "2ce6326e": "-", "741e3312": "+", "c9b4268e": "+", "fcaf141b": "+", "b64cc8be": "+"}
for c, w in want.items():
    out = git("cherry", "-v", TIP, c, c + "^").strip()
    mark = out[:1] if out else "?"
    if not out:
        # c is an ancestor of TIP: git cherry lists nothing (the commit itself is in the history) - "contains" by ancestry.
        anc = subprocess.run([G, "-C", REPO, "merge-base", "--is-ancestor", c, TIP]).returncode == 0
        mark = "-" if anc else "?"
        out = "(ancestor of tip)" if anc else "(empty, not ancestor)"
    print(f"{c}: {out[:130]} | want {w} -> {'ok' if mark == w else 'FAIL'}")
    ok &= mark == w

print("== (3a) wt_s5c files (f3b3aa3b tree) vs 4fc501f4 + S-pcw patch")
for f in FILES:
    # Line multisets (CR stripped): lines of wt_s5c not in 4fc501f4 must equal the '+' lines of the S-pcw patch not in its
    # '-' lines, and lines of 4fc501f4 not in wt_s5c - the '-' lines not in the '+' lines.
    import collections
    wl = open(f"{WT_S5C}/{f}", "rb").read().replace(b"\r\n", b"\n").decode("utf-8").split("\n")
    bl = git("show", f"4fc501f4:{f}").replace("\r\n", "\n").split("\n")
    patch = git("diff", "-U0", "ae704c5d", "2ce6326e", "--", f)
    plus = collections.Counter(l[1:] for l in patch.split("\n") if l.startswith("+") and not l.startswith("+++"))
    minus = collections.Counter(l[1:] for l in patch.split("\n") if l.startswith("-") and not l.startswith("---"))
    cw, cb = collections.Counter(wl), collections.Counter(bl)
    added, removed = cw - cb, cb - cw
    same = added == plus - minus and removed == minus - plus
    print(f"{f}: wt_s5c vs 4fc501f4 +{sum(added.values())} -{sum(removed.values())}; patch net "
          f"+{sum((plus - minus).values())} -{sum((minus - plus).values())}; equal: {same}")
    ok &= same

print("== (3b) S-pcw lines of 2ce6326e and hunks of git diff 2ce6326e", TIP)
named = 0
for f in FILES:
    patch = git("diff", "-U0", "ae704c5d", "2ce6326e", "--", f)
    pcw = set()
    for line in patch.split("\n"):
        m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if m:
            s = int(m.group(1)); n = int(m.group(2)) if m.group(2) is not None else 1
            pcw.update(range(s, s + n))
    print(f"{f}: S-pcw lines in 2ce6326e: {len(pcw)}")
    d = git("diff", "-U0", "2ce6326e", TIP, "--", f)
    hunks = 0
    named_f = named
    for line in d.split("\n"):
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", line)
        if not m:
            continue
        hunks += 1
        s = int(m.group(1)); n = int(m.group(2)) if m.group(2) is not None else 1
        rng = set(range(s, s + n)) if n else set()
        hit = bool(rng & pcw) or (n == 0 and s in pcw and s + 1 in pcw)
        if hit:
            named += 1
            print(f"  PCW hunk {line[:150]}")
    print(f"  hunks {hunks}, touching S-pcw lines: {named - named_f}")
print("PCW hunks total:", named)
print("ALL OK" if ok else "FAIL")

# FS13a (HPP-787, ROADMAP s122 item 697(g)(1)): source members of the shipping binary FS13 (worktree C:/kyty/f287/fs13a/wt);
# port of fs12a/verify_fs12a.py (FS12a, HPP-750, item 683(g)(1)) with the base FS12 730ed40a and five source commits.
#   V1 every source commit has a worktree commit whose changed lines (+/- lines, file by file, as multisets) equal the
#      source's; git cherry printed. Negative controls: the lines of a28c37d5 against the worktree commit of e9dd8604 must
#      differ; against its own worktree commit with one line spoiled must differ.
#   V1b member "contains" of item 697(g)(1) (rule of item 689(g)): e9dd8604, cbfe8375, 227e1b36, c94c49e0, 726e751e, cb022252
#      - each an ancestor of FS13 or 'git cherry FS13 <c> <c>^' gives '-'. Negative controls (the same rule must say NO):
#      e9dd8604 and the FS13a main commit against the base 730ed40a; cbfe8375 against FS11 ee9632be; the F24 code 5c21c387
#      (F40a, not carried) against FS13.
#   V2 the diff of FS13 against the base 730ed40a - only the files of the five source commits, and its signed multiset of
#      changed lines = the sum of the five commits'. Negative control: the sum without the FS13a commit must differ.
#   V2b member of item 697(g)(1): the paths of the diff outside tests/ and outside the CMake target of the stand - only
#      src/kernel/fileSystem.cpp. The CMakeLists.txt change is only the f25_read_fail_stand target (added lines name it or
#      are its comment / blank; 0 removed lines). The docs/ paths carried by 51c9e38f are printed (not built).
#   V3 default table (own scanner, the form of verify_fs12a.py V3): the knobs whose reading takes unset as ON at FS13 = the
#      base FS12's plus KYTY_FIX_F25 and only it. Negative control: at the worktree commit before FS13a (49aba6a4 carried)
#      the difference is empty (the member would fail there).
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS13 = base (blob), ParseMode returns 3 for unset or "".
#   V5 translation signature set: no path of the diff under src/graphics/shader/.
#   V6 code outside the base not carried: no line added by the diff base..FS13 names KYTY_FIX_F24 / KYTY_FIX_F20 /
#      KYTY_DIAG_B32 / DiagB32 / rts_bad_b (except comments); 5c21c387 (F24 code) and 5f48cc3e (F21 stand edition 1) are
#      not ancestors of FS13.
# Usage: python verify_fs13a.py <FS13 HEAD> <wt 51c9e38f> <wt e9dd8604> <wt a28c37d5> <wt 49aba6a4> <main FS13a> <wt FS13a>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "730ed40a"
HEAD, W1, W2, W3, W4, M5, W5 = sys.argv[1:8]
SRC = [("51c9e38f", W1), ("e9dd8604", W2), ("a28c37d5", W3), ("49aba6a4", W4), (M5, W5)]
CONTAINS = ("e9dd8604", "cbfe8375", "227e1b36", "c94c49e0", "726e751e", "cb022252")


def git(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True, check=True).stdout.decode("utf-8", "replace")


def git_rc(*a):
    return subprocess.run([G, "-C", REPO, *a], capture_output=True).returncode


def changed(diff):
    out = collections.defaultdict(collections.Counter)
    cur = None
    for line in diff.split("\n"):
        if line.startswith("diff --git "):
            cur = line.split(" b/", 1)[1]
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        if line.startswith("+") or line.startswith("-"):
            out[cur][line] += 1
    return {f: c for f, c in out.items()}


def commit_lines(c):
    return changed(git("show", "--format=", "-U0", c))


def signed(d):
    s = collections.defaultdict(collections.Counter)
    for f, c in d.items():
        for line, n in c.items():
            s[f][line[1:]] += n if line[0] == "+" else -n
    return {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in s.items()}


def add(a, b):
    out = collections.defaultdict(collections.Counter)
    for d in (a, b):
        for f, c in d.items():
            for k, v in c.items():
                out[f][k] += v
    return {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in out.items()}


def nonempty(d):
    return {f: c for f, c in d.items() if c}


def contains(tip, c):
    anc = git_rc("merge-base", "--is-ancestor", c, tip) == 0
    ch = git("cherry", tip, c, c + "^").strip()
    return anc or ch.startswith("-"), anc, ch


ok = True
print("FS13 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s" % (
        src, wt, sum(sum(c.values()) for c in a.values()), sum(sum(c.values()) for c in b.values()), eq, ch))
    ok &= eq
neg1 = commit_lines("a28c37d5") == commit_lines(W2)
spoiled = commit_lines(W3)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0 + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("a28c37d5") == spoiled
print("V1 negative controls: a28c37d5 vs %s equal %s (want False); vs its own worktree commit with one line spoiled equal %s (want False)" % (
    W2, neg1, neg2))
ok &= (not neg1) and (not neg2)

# V1b
for c in CONTAINS:
    yes, anc, ch = contains(HEAD, c)
    print("V1b contains %s: %s (ancestor %s, git cherry %s)" % (c, yes, anc, ch))
    ok &= yes
for tip, c, why in ((BASE, "e9dd8604", "code F38a against the base FS12"), (BASE, M5, "FS13a main commit against the base FS12"),
                    ("ee9632be", "cbfe8375", "FS12a against FS11"), ("HEAD", "5c21c387", "F24 code F40a, not carried")):
    t = HEAD if tip == "HEAD" else tip
    yes, anc, ch = contains(t, c)
    print("V1b negative control %s in %s (%s): %s (ancestor %s, git cherry %s) (want False)" % (c, tip, why, yes, anc, ch))
    ok &= not yes

# V2
names = set(git("diff", "--name-only", BASE, HEAD).split())
src_names = set()
by_commit = {}
for src, _ in SRC:
    fs = set(git("show", "--format=", "--name-only", src).split())
    by_commit[src] = fs
    src_names |= fs
print("V2 files of diff %s..FS13 (%d): %s" % (BASE, len(names), " ".join(sorted(names))))
m = names == src_names
total = {}
for src, _ in SRC:
    total = add(total, signed(commit_lines(src)))
d = nonempty(signed(changed(git("diff", "-U0", BASE, HEAD))))
total = nonempty(total)
m2 = d == total
part = {}
for src, _ in SRC[:4]:
    part = add(part, signed(commit_lines(src)))
neg3 = nonempty(part) == d
print("V2 file set = files of the five source commits %s; signed changed lines of the diff = sum of the five commits %s (lines %d); negative control without FS13a equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3

# V2b
docs = sorted(n for n in names if n.startswith("docs/"))
outside = sorted(n for n in names if not n.startswith("tests/") and not n.startswith("docs/"))
print("V2b paths of the diff under docs/ (carried by 51c9e38f, not built): %d: %s" % (len(docs), " ".join(docs)))
print("V2b paths of the diff outside tests/ and docs/: %s" % " ".join(outside))
cm = changed(git("diff", "-U0", BASE, HEAD, "--", "CMakeLists.txt")).get("CMakeLists.txt", collections.Counter())
cm_add = [l[1:] for l in cm.elements() if l.startswith("+")]
cm_del = [l[1:] for l in cm.elements() if l.startswith("-")]
cm_other = [l for l in cm_add if l.strip() and "f25_read_fail_stand" not in l and "F25ReadFailStand" not in l
            and not l.lstrip().startswith("#")]
cm_comment = [l for l in cm_add if l.lstrip().startswith("#")]
print("V2b CMakeLists.txt: added %d (naming the stand %d, comment %d, blank %d, other %d), removed %d" % (
    len(cm_add), sum(1 for l in cm_add if "f25_read_fail_stand" in l or "F25ReadFailStand" in l), len(cm_comment),
    sum(1 for l in cm_add if not l.strip()), len(cm_other), len(cm_del)))
for l in cm_comment:
    print("   comment: %s" % l.strip()[:150])
only = [n for n in outside if n != "CMakeLists.txt"]
m = only == ["src/kernel/fileSystem.cpp"] and not cm_other and not cm_del and len(cm_add) > 0
print("V2b outside tests/, docs/ and the CMake target of the stand - only src/kernel/fileSystem.cpp: %s (%s)" % (m, only))
ok &= m


# V3
def default_on(tip):
    on = set()
    g = git("grep", "-n", "-E", "\"KYTY_[A-Z0-9_]+\"", tip, "--", "src/")
    cache = {}
    for l in g.strip().split("\n"):
        if not l:
            continue
        _, path, lineno, text = l.split(":", 3)
        if "getenv" not in text:
            continue
        if path not in cache:
            cache[path] = git("show", "%s:%s" % (tip, path)).split("\n")
        window = " ".join(cache[path][int(lineno) - 1:int(lineno) + 2])
        if re.search(r"== nullptr \|\|.*EnvValueOn", window):
            for k in re.findall(r'"(KYTY_[A-Z0-9_]+)"', text):
                on.add(k)
    return on


b_on, h_on, w4_on = default_on(BASE), default_on(HEAD), default_on(W4)
print("V3 DEFAULT-ON base (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS13 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == {"KYTY_FIX_F25"} and b_on - h_on == set()
neg4 = w4_on - b_on == {"KYTY_FIX_F25"}
print("V3 FS13 = base + KYTY_FIX_F25 only: %s; negative control at %s (before FS13a): difference %s, member there %s (want False)" % (
    m, W4, sorted(w4_on - b_on) or "empty", neg4))
ok &= m and not neg4

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS13 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4

# V5
sh = [n for n in names if n.startswith("src/graphics/shader/")]
print("V5 paths of the diff under src/graphics/shader/: %s" % (sh or "none"))
ok &= not sh

# V6
added = [l[1:] for l in git("diff", "-U0", BASE, HEAD, "--", "src", "tests", "CMakeLists.txt").split("\n")
         if l.startswith("+") and not l.startswith("+++ ")]
pat = r"KYTY_FIX_F24|KYTY_FIX_F20|DiagB32|diagB32\.h|KYTY_DIAG_B32|rts_bad_b|rts_bad_rx|JoyPump"
code = [l for l in added if re.search(pat, l) and not l.lstrip().startswith("//")]
a1 = git_rc("merge-base", "--is-ancestor", "5c21c387", HEAD) == 0
a2 = git_rc("merge-base", "--is-ancestor", "5f48cc3e", HEAD) == 0
print("V6 added code lines naming F24 / F20 / KYTY_DIAG_B32 / F30d counters: %d; 5c21c387 ancestor of FS13 %s; 5f48cc3e ancestor of FS13 %s" % (
    len(code), a1, a2))
ok &= not code and not a1 and not a2

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)

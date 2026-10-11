# FS14a (HPP-812, ROADMAP s122 item 710(g)(1)): source members of the shipping binary FS14 (worktree C:/kyty/f287/fs14a/wt);
# port of fs13a/verify_fs13a.py (FS13a, HPP-787) with the base FS13 ea6c6e9e and four source commits.
#   V1 every source commit has a worktree commit whose changed lines (+/- lines, file by file, as multisets) equal the
#      source's; git cherry printed. Negative controls: the lines of e3aa4b4d against the worktree commit of 5c21c387 must
#      differ; the lines of 57f9e528 against its own worktree commit with one line spoiled must differ.
#   V1b member "contains" of item 710(g)(1): 5c21c387, 57f9e528, the FS14a main commit, e9dd8604, 3630f116, 227e1b36,
#      cbfe8375, c94c49e0, 726e751e, cb022252 - each an ancestor of FS14 or 'git cherry FS14 <c> <c>^' gives '-'.
#      Negative controls (the same rule must say NO): 5c21c387, 57f9e528 and the FS14a main commit against the base
#      ea6c6e9e; e9dd8604 and 3630f116 against FS12 730ed40a; the F20 code a6342c98 (F42a, not carried) against FS14.
#   V2 the diff of FS14 against the base ea6c6e9e - only the files of the four source commits, and its signed multiset of
#      changed lines = the sum of the four commits'. Negative control: the sum without the FS14a commit must differ.
#   V2b member of item 710(g)(1): the paths of the diff (git diff --stat base FS14) - only files of the three F40 commits
#      and FS14a, all under src/; paths under src/graphics/shader/ - 0 (translation signature set unchanged).
#   V3 default table (own scanner, the form of verify_fs13a.py V3): the knobs whose reading takes unset as ON at FS14 = the
#      base FS13's plus KYTY_FIX_F24 and only it. Negative control: at the worktree commit before FS14a (57f9e528
#      carried) the difference is empty (the member would fail there).
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS14 = base (blob), ParseMode returns 3 for unset or "".
#   V6 code outside the base not carried: no code line added by the diff base..FS14 names KYTY_FIX_F20 / FixF20 /
#      KYTY_DIAG_B32 / DiagB32 / rts_bad_b / KYTY_F26_TINT / F20Stand; a6342c98 (F20 code), 1398d44d (F26 measurement),
#      82570fd2 (F20 stand edition 2) are not ancestors and git cherry gives '+'.
#   V7 (reference for FS14b, not a member of FS14a): the paths of the diff FS14 against the F40a2 tag worktree 7c38e497 under
#      src/ - expected the FS13 code file src/kernel/fileSystem.cpp and the FS14a files joyPump.cpp / joyPump.h only.
# Usage: python verify_fs14a.py <FS14 HEAD> <wt 5c21c387> <wt e3aa4b4d> <wt 57f9e528> <main FS14a> <wt FS14a>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "ea6c6e9e"
HEAD, W1, W2, W3, M4, W4 = sys.argv[1:7]
SRC = [("5c21c387", W1), ("e3aa4b4d", W2), ("57f9e528", W3), (M4, W4)]
CONTAINS = ("5c21c387", "57f9e528", M4, "e9dd8604", "3630f116", "227e1b36", "cbfe8375", "c94c49e0", "726e751e", "cb022252")


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
print("FS14 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s" % (
        src, wt, sum(sum(c.values()) for c in a.values()), sum(sum(c.values()) for c in b.values()), eq, ch))
    ok &= eq
neg1 = commit_lines("e3aa4b4d") == commit_lines(W1)
spoiled = commit_lines(W3)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0 + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("57f9e528") == spoiled
print("V1 negative controls: e3aa4b4d vs %s equal %s (want False); 57f9e528 vs its own worktree commit with one line spoiled equal %s (want False)" % (
    W1, neg1, neg2))
ok &= (not neg1) and (not neg2)

# V1b
for c in CONTAINS:
    yes, anc, ch = contains(HEAD, c)
    print("V1b contains %s: %s (ancestor %s, git cherry %s)" % (c, yes, anc, ch))
    ok &= yes
for tip, c, why in ((BASE, "5c21c387", "code F40a against the base FS13"), (BASE, "57f9e528", "F40a2 against the base FS13"),
                    (BASE, M4, "FS14a main commit against the base FS13"), ("730ed40a", "e9dd8604", "code F38a against FS12"),
                    ("730ed40a", "3630f116", "FS13a against FS12"), ("HEAD", "a6342c98", "F20 code F42a, not carried")):
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
    print("V2 files of %s: %s" % (src, " ".join(sorted(fs))))
print("V2 files of diff %s..FS14 (%d): %s" % (BASE, len(names), " ".join(sorted(names))))
m = names == src_names
total = {}
for src, _ in SRC:
    total = add(total, signed(commit_lines(src)))
d = nonempty(signed(changed(git("diff", "-U0", BASE, HEAD))))
total = nonempty(total)
m2 = d == total
part = {}
for src, _ in SRC[:3]:
    part = add(part, signed(commit_lines(src)))
neg3 = nonempty(part) == d
print("V2 file set = files of the four source commits %s; signed changed lines of the diff = sum of the four commits %s (lines %d); negative control without FS14a equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3

# V2b
print("V2b git diff --stat %s FS14:" % BASE)
for l in git("diff", "--stat", BASE, HEAD).rstrip().split("\n"):
    print("   " + l)
outside = sorted(n for n in names if not n.startswith("src/"))
sh = sorted(n for n in names if n.startswith("src/graphics/shader/"))
m = not outside and not sh and names <= src_names
print("V2b paths outside src/: %s; paths under src/graphics/shader/: %s; member %s" % (outside or "none", sh or "none", m))
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


b_on, h_on, w3_on = default_on(BASE), default_on(HEAD), default_on(W3)
print("V3 DEFAULT-ON base FS13 (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS14 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == {"KYTY_FIX_F24"} and b_on - h_on == set()
neg4 = w3_on - b_on == {"KYTY_FIX_F24"}
print("V3 FS14 = base + KYTY_FIX_F24 only: %s; negative control at %s (before FS14a): difference %s, member there %s (want False)" % (
    m, W3, sorted(w3_on - b_on) or "empty", neg4))
ok &= m and not neg4

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS14 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4

# V6
added = [l[1:] for l in git("diff", "-U0", BASE, HEAD, "--", "src", "tests", "CMakeLists.txt").split("\n")
         if l.startswith("+") and not l.startswith("+++ ")]
pat = r"KYTY_FIX_F20|FixF20|DiagB32|diagB32\.h|KYTY_DIAG_B32|rts_bad_b|rts_bad_rx|KYTY_F26_TINT|F20Stand|KYTY_FIX_F29|KYTY_FIX_F26"
code = [l for l in added if re.search(pat, l) and not l.lstrip().startswith("//")]
print("V6 added code lines naming F20 / F26 / F29 / KYTY_DIAG_B32 / F30d counters: %d" % len(code))
ok &= not code
for c, why in (("a6342c98", "F20 code F42a"), ("1398d44d", "F26 measurement F46a"), ("82570fd2", "F20 stand edition 2 F42a2")):
    yes, anc, ch = contains(HEAD, c)
    print("V6 %s (%s) in FS14: %s (ancestor %s, git cherry %s) (want False)" % (c, why, yes, anc, ch))
    ok &= not yes

# V7 (reference)
v7 = sorted(n for n in git("diff", "--name-only", "7c38e497", HEAD).split() if n.startswith("src/"))
print("V7 (reference) src/ paths of the diff F40a2 worktree 7c38e497 .. FS14: %s" % " ".join(v7))

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)

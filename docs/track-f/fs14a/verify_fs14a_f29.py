# FS14a (HPP-812, ROADMAP s122 item 710(g)(1) amended by item 712(g)(1)): source members of the shipping binary FS14 with F29
# (worktree C:/kyty/f287/fs14a/wt). Port of verify_fs14a.py with six source commits: 5c21c387, e3aa4b4d, 57f9e528, the FS14a
# F24 main commit c8836f14, 15c9d2f2 (code and stand F44a), the FS14a F29 main commit.
#   V1 every source commit has a worktree commit whose changed lines (+/- lines, file by file, as multisets) equal the
#      source's; git cherry printed. Negative controls: e3aa4b4d against the worktree commit of 5c21c387; 57f9e528 against
#      its own worktree commit with one line spoiled; 15c9d2f2 against the worktree commit of the F29 main commit - differ.
#   V1b "contains": 5c21c387, 57f9e528, c8836f14, 15c9d2f2, the F29 main commit, e9dd8604, 3630f116, 227e1b36, cbfe8375,
#      c94c49e0, 726e751e, cb022252 - ancestor of FS14 or 'git cherry FS14 <c> <c>^' gives '-'. Negative controls (want NO):
#      F40/FS14a/F29 commits against the base ea6c6e9e; 15c9d2f2 and the F29 main commit against the intermediate 76c1058f
#      (F24 only); e9dd8604 and 3630f116 against FS12 730ed40a; a6342c98 (F20) against FS14.
#   V2 the diff of FS14 against the base - only the files of the six source commits, signed multiset of changed lines = the
#      sum of the six. Negative control: the sum without the F29 main commit must differ.
#   V2b member of item 712(g)(1): the src/ paths of the diff = the src/ files of the three F40 commits, faultManager.cpp/.h
#      and the FS14a commits, and only they; paths under src/graphics/shader/ - 0. Paths outside src/ are printed - they
#      must all be files of 15c9d2f2 (CMakeLists.txt target f29_fault_stand, tests/F29FaultStand.cpp, docs/track-f/f44a/).
#   V3 default table (own scanner of verify_fs14a.py): DEFAULT-ON at FS14 = the base FS13's + KYTY_FIX_F24 + KYTY_FIX_F29 and
#      only they. Negative controls: at 76c1058f (F24 only) and at the worktree commit of 15c9d2f2 the member fails.
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS14 = base, ParseMode returns 3 for unset or "".
#   V6 code outside the base not carried: no added code line names KYTY_FIX_F20 / FixF20 / KYTY_DIAG_B32 / DiagB32 /
#      rts_bad_b / KYTY_F26_TINT / F20Stand / KYTY_FIX_F26; a6342c98, 1398d44d, 82570fd2 not contained.
#   V7 (reference for FS14b): src/ paths of the diff F40a2 worktree 7c38e497 .. FS14.
# Usage: python verify_fs14a_f29.py <FS14 HEAD> <wt 5c21c387> <wt e3aa4b4d> <wt 57f9e528> <main F24> <wt F24>
#                                   <wt 15c9d2f2> <main F29> <wt F29>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "ea6c6e9e"
MID = "76c1058f"
HEAD, W1, W2, W3, M4, W4, W5, M6, W6 = sys.argv[1:10]
SRC = [("5c21c387", W1), ("e3aa4b4d", W2), ("57f9e528", W3), (M4, W4), ("15c9d2f2", W5), (M6, W6)]
CONTAINS = ("5c21c387", "57f9e528", M4, "15c9d2f2", M6, "e9dd8604", "3630f116", "227e1b36", "cbfe8375", "c94c49e0",
            "726e751e", "cb022252")


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
print("FS14 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip(), "intermediate", git("rev-parse", MID).strip())

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
neg2b = commit_lines("15c9d2f2") == commit_lines(W6)
print("V1 negative controls: e3aa4b4d vs %s equal %s; 57f9e528 vs own worktree commit spoiled equal %s; 15c9d2f2 vs %s equal %s (want False x3)" % (
    W1, neg1, neg2, W6, neg2b))
ok &= (not neg1) and (not neg2) and (not neg2b)

# V1b
for c in CONTAINS:
    yes, anc, ch = contains(HEAD, c)
    print("V1b contains %s: %s (ancestor %s, git cherry %s)" % (c, yes, anc, ch))
    ok &= yes
for tip, c, why in ((BASE, "5c21c387", "code F40a against the base FS13"), (BASE, "57f9e528", "F40a2 against the base FS13"),
                    (BASE, M4, "FS14a F24 main commit against the base FS13"),
                    (BASE, "15c9d2f2", "code F44a against the base FS13"), (BASE, M6, "FS14a F29 main commit against the base FS13"),
                    (MID, "15c9d2f2", "code F44a against the intermediate F24-only 76c1058f"),
                    (MID, M6, "FS14a F29 main commit against the intermediate 76c1058f"),
                    ("730ed40a", "e9dd8604", "code F38a against FS12"),
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
for src, _ in SRC[:5]:
    part = add(part, signed(commit_lines(src)))
neg3 = nonempty(part) == d
print("V2 file set = files of the six source commits %s; signed changed lines of the diff = sum of the six %s (lines %d); negative control without the F29 main commit equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3

# V2b
print("V2b git diff --stat %s FS14:" % BASE)
for l in git("diff", "--stat=200", BASE, HEAD).rstrip().split("\n"):
    print("   " + l)
src_paths = sorted(n for n in names if n.startswith("src/"))
want_src = set()
for c in ("5c21c387", "e3aa4b4d", "57f9e528", M4, M6):
    want_src |= {n for n in by_commit[c] if n.startswith("src/")}
want_src |= {"src/graphics/host_gpu/renderer/cache/faultManager.cpp", "src/graphics/host_gpu/renderer/cache/faultManager.h"}
f44_src = {n for n in by_commit["15c9d2f2"] if n.startswith("src/")}
outside = sorted(n for n in names if not n.startswith("src/"))
sh = [n for n in src_paths if n.startswith("src/graphics/shader/")]
m = set(src_paths) == want_src and f44_src <= want_src and not sh and set(outside) <= by_commit["15c9d2f2"]
print("V2b src/ paths (%d): %s" % (len(src_paths), " ".join(src_paths)))
print("V2b src/ files of 15c9d2f2: %s; paths under src/graphics/shader/: %s; paths outside src/ (all of 15c9d2f2 %s): %s; member %s" % (
    " ".join(sorted(f44_src)), sh or "none", set(outside) <= by_commit["15c9d2f2"], " ".join(outside) or "none", m))
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


WANT = {"KYTY_FIX_F24", "KYTY_FIX_F29"}
b_on, h_on, mid_on, w5_on = default_on(BASE), default_on(HEAD), default_on(MID), default_on(W5)
print("V3 DEFAULT-ON base FS13 (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS14 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == WANT and b_on - h_on == set()
negm = mid_on - b_on == WANT
negw = w5_on - b_on == WANT
print("V3 FS14 = base + KYTY_FIX_F24 + KYTY_FIX_F29 only: %s; negative controls: at %s difference %s member %s, at %s difference %s member %s (want False x2)" % (
    m, MID, sorted(mid_on - b_on) or "empty", negm, W5, sorted(w5_on - b_on) or "empty", negw))
ok &= m and not negm and not negw

# V3b: F29 reading of FS14 - unset or "" = ON, otherwise EnvValueOn; one getenv; one "FixF29: mode=" format
fm = git("show", "%s:src/graphics/host_gpu/renderer/cache/faultManager.cpp" % HEAD)
n_get = fm.count('getenv("KYTY_FIX_F29")')
n_mode = fm.count('"FixF29: mode=%d')
lam = re.search(r"bool FixF29Enabled\(\) \{\s*static const bool enabled = \[\] \{\s*const char\* value = std::getenv\(\"KYTY_FIX_F29\"\);\s*return value == nullptr \|\| value\[0\] == '\\0' \|\| Common::EnvValueOn\(value\);\s*\}\(\);\s*return enabled;\s*\}", fm) is not None
print("V3b faultManager.cpp at FS14: getenv(KYTY_FIX_F29) x%d, format \"FixF29: mode=%%d\" x%d, static const lambda in the form of 3630f116 %s" % (n_get, n_mode, lam))
ok &= n_get == 1 and n_mode == 1 and lam

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
pat = r"KYTY_FIX_F20|FixF20|DiagB32|diagB32\.h|KYTY_DIAG_B32|rts_bad_b|rts_bad_rx|KYTY_F26_TINT|F20Stand|KYTY_FIX_F26"
code = [l for l in added if re.search(pat, l) and not l.lstrip().startswith("//")]
print("V6 added code lines naming F20 / F26 / KYTY_DIAG_B32 / F30d counters: %d" % len(code))
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

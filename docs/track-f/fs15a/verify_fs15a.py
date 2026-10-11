# FS15a (HPP-820, ROADMAP s122 item 730(g)(1)): source members of the shipping binary FS15 (worktree C:/kyty/f287/fs15a/wt,
# base FS14 eb7e8b91). Port of verify_fs14a_f29.py (FS14a) with four source commits: a6342c98 (code F42a), a9d6fd1c (stand
# edition 1), 82570fd2 (CreateCachedModule moved out, getters, stand edition 2, F42a2), the FS15a main commit.
#   V1 every source commit has a worktree commit whose changed lines (+/- lines, file by file, as multisets) equal the
#      source's; git cherry printed. Negative controls: a9d6fd1c against the worktree commit of a6342c98; 82570fd2 against
#      its own worktree commit with one line spoiled; the FS15a main commit against the worktree commit of 82570fd2 - differ.
#   V1b "contains": a6342c98, 82570fd2, the FS15a main commit, 5c21c387, 57f9e528, c8836f14, 15c9d2f2, 78e45af3, e9dd8604,
#      3630f116, 227e1b36, cbfe8375, c94c49e0, 726e751e, cb022252 (+ a9d6fd1c, reference) - ancestor of FS15 or
#      'git cherry FS15 <c> <c>^' gives '-'. Negative controls (want NO): a6342c98, 82570fd2, the FS15a main commit against
#      the base eb7e8b91; the FS15a main commit against the intermediate worktree commit of 82570fd2; 15c9d2f2 and 78e45af3
#      against FS13 ea6c6e9e; 1398d44d (F26 measurement F46a, outside the base) against FS15.
#   V2 the diff of FS15 against the base - only the files of the four source commits, signed multiset of changed lines = the
#      sum of the four. Negative control: the sum without the FS15a main commit must differ.
#   V2b member of item 730(g)(1): the src/ paths of the diff = the src/ files of the three F42 commits and FS15a, and only
#      they; paths under src/graphics/shader/ - 0. Paths outside src/ are printed - they must all be files of a9d6fd1c /
#      82570fd2 (tests/).
#   V3 default table (own scanner of verify_fs14a.py): DEFAULT-ON at FS15 = the base FS14's + KYTY_FIX_F20 and only it.
#      Negative control: at the worktree commit of 82570fd2 (no FS15a) the member fails.
#   V3b fixF20.cpp at FS15: getenv("KYTY_FIX_F20") x1, EnvFlagOn("KYTY_FIX_F20") x0, format "FixF20: mode=%d" x1, format
#      "FixF20Stat: when=%s" x1, the static const lambda in the form of 3630f116 / c8836f14.
#   V4 KYTY_S_REPLAY: shaderReplay.cpp at FS15 = base, ParseMode returns 3 for unset or "".
#   V5 translation signature: KYTY_SHADER_SOURCE_HASH of the FS15 build = the FS14a one (9177b426...).
#   V6 code outside the base not carried: no added code line names KYTY_DIAG_B32 / DiagB32 / rts_bad_b / rts_bad_rx /
#      KYTY_F26_TINT / KYTY_FIX_F26; 1398d44d not contained (V1b).
#   V7 (reference for FS15b): src/ paths of the diff F42a2 worktree 5ccb1d31 .. FS15.
# Usage: python verify_fs15a.py <FS15 HEAD> <wt a6342c98> <wt a9d6fd1c> <wt 82570fd2> <main FS15a> <FS15 kytyGitVersion.h>
#                               <FS14 kytyGitVersion.h>
import collections
import re
import subprocess
import sys

G = "C:/Program Files/Git/cmd/git.exe"
REPO = "C:/kyty/KytyPS5"
BASE = "eb7e8b91"
HEAD, W1, W2, W3, M4, VH15, VH14 = sys.argv[1:8]
W4 = HEAD
SRC = [("a6342c98", W1), ("a9d6fd1c", W2), ("82570fd2", W3), (M4, W4)]
CONTAINS = ("a6342c98", "82570fd2", M4, "5c21c387", "57f9e528", "c8836f14", "15c9d2f2", "78e45af3", "e9dd8604",
            "3630f116", "227e1b36", "cbfe8375", "c94c49e0", "726e751e", "cb022252", "a9d6fd1c")


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
print("FS15 HEAD", git("rev-parse", HEAD).strip(), "base", git("rev-parse", BASE).strip())
print("worktree log base..FS15:")
for l in git("log", "--format=%H %P %s", BASE + ".." + HEAD).rstrip().split("\n"):
    print("   " + l[:170])

# V1
for src, wt in SRC:
    a, b = commit_lines(src), commit_lines(wt)
    eq = a == b
    ch = git("cherry", HEAD, src, src + "^").strip()
    print("V1 %s -> %s: changed lines %d / %d, equal %s; git cherry %s" % (
        src, wt, sum(sum(c.values()) for c in a.values()), sum(sum(c.values()) for c in b.values()), eq, ch))
    ok &= eq
neg1 = commit_lines("a9d6fd1c") == commit_lines(W1)
spoiled = commit_lines(W3)
f0 = sorted(spoiled)[0]
k0 = sorted(spoiled[f0])[0]
spoiled = {f: collections.Counter(c) for f, c in spoiled.items()}
spoiled[f0][k0] -= 1
spoiled[f0][k0 + " x"] += 1
spoiled = {f: collections.Counter({k: v for k, v in c.items() if v}) for f, c in spoiled.items()}
neg2 = commit_lines("82570fd2") == spoiled
neg2b = commit_lines(M4) == commit_lines(W3)
print("V1 negative controls: a9d6fd1c vs %s equal %s; 82570fd2 vs own worktree commit spoiled equal %s; %s vs %s equal %s (want False x3)" % (
    W1, neg1, neg2, M4, W3, neg2b))
ok &= (not neg1) and (not neg2) and (not neg2b)

# V1b
for c in CONTAINS:
    yes, anc, ch = contains(HEAD, c)
    print("V1b contains %s: %s (ancestor %s, git cherry %s)" % (c, yes, anc, ch))
    ok &= yes
for tip, c, why in ((BASE, "a6342c98", "code F42a against the base FS14"),
                    (BASE, "82570fd2", "F42a2 against the base FS14"),
                    (BASE, M4, "FS15a main commit against the base FS14"),
                    (W3, M4, "FS15a main commit against the intermediate worktree commit of 82570fd2"),
                    ("ea6c6e9e", "15c9d2f2", "code F44a against FS13"),
                    ("ea6c6e9e", "78e45af3", "FS14a F29 main commit against FS13"),
                    ("HEAD", "1398d44d", "F26 measurement F46a, not carried")):
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
print("V2 files of diff %s..FS15 (%d): %s" % (BASE, len(names), " ".join(sorted(names))))
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
print("V2 file set = files of the four source commits %s; signed changed lines of the diff = sum of the four %s (lines %d); negative control without the FS15a main commit equal %s (want False)" % (
    m, m2, sum(sum(abs(v) for v in c.values()) for c in d.values()), neg3))
ok &= m and m2 and not neg3

# V2b
print("V2b git diff --stat %s FS15:" % BASE)
for l in git("diff", "--stat=200", BASE, HEAD).rstrip().split("\n"):
    print("   " + l)
src_paths = sorted(n for n in names if n.startswith("src/"))
want_src = set()
for c, _ in SRC:
    want_src |= {n for n in by_commit[c] if n.startswith("src/")}
outside = sorted(n for n in names if not n.startswith("src/"))
tests_files = by_commit["a9d6fd1c"] | by_commit["82570fd2"]
sh = [n for n in src_paths if n.startswith("src/graphics/shader/")]
m = set(src_paths) == want_src and not sh and set(outside) <= tests_files
print("V2b src/ paths (%d): %s" % (len(src_paths), " ".join(src_paths)))
print("V2b paths under src/graphics/shader/: %s; paths outside src/ (all of a9d6fd1c / 82570fd2 %s): %s; member %s" % (
    sh or "none", set(outside) <= tests_files, " ".join(outside) or "none", m))
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


WANT = {"KYTY_FIX_F20"}
b_on, h_on, w3_on = default_on(BASE), default_on(HEAD), default_on(W3)
print("V3 DEFAULT-ON base FS14 (%d): %s" % (len(b_on), " ".join(sorted(b_on))))
print("V3 DEFAULT-ON FS15 (%d): %s" % (len(h_on), " ".join(sorted(h_on))))
m = h_on - b_on == WANT and b_on - h_on == set()
negw = w3_on - b_on == WANT
print("V3 FS15 = base + KYTY_FIX_F20 only: %s; negative control: at %s (no FS15a) difference %s member %s (want False)" % (
    m, W3, sorted(w3_on - b_on) or "empty", negw))
ok &= m and not negw

# V3b
fx = git("show", "%s:src/graphics/host_gpu/renderer/pipeline/fixF20.cpp" % HEAD)
n_get = fx.count('getenv("KYTY_FIX_F20")')
n_flag = fx.count('EnvFlagOn("KYTY_FIX_F20")')
n_mode = fx.count('"FixF20: mode=%d')
n_stat = fx.count('"FixF20Stat: when=%s')
lam = re.search(r"int Mode\(\) \{\s*static const int mode = \[\] \{\s*const char\* env = std::getenv\(\"KYTY_FIX_F20\"\);\s*"
                r"const int value = \(env == nullptr \|\| env\[0\] == '\\0' \|\| Common::EnvValueOn\(env\)\) \? 1 : 0;\s*"
                r"LOGF\(\"FixF20: mode=%d\\n\", value\);\s*return value;\s*\}\(\);\s*return mode;\s*\}", fx) is not None
print("V3b fixF20.cpp at FS15: getenv(KYTY_FIX_F20) x%d, EnvFlagOn(KYTY_FIX_F20) x%d, format \"FixF20: mode=%%d\" x%d, format \"FixF20Stat: when=%%s\" x%d, static const lambda in the form of 3630f116 %s" % (
    n_get, n_flag, n_mode, n_stat, lam))
ok &= n_get == 1 and n_flag == 0 and n_mode == 1 and n_stat == 1 and lam

# V4
p = "src/graphics/host_gpu/renderer/pipeline/shaderReplay.cpp"
bb, hb = git("rev-parse", "%s:%s" % (BASE, p)).strip(), git("rev-parse", "%s:%s" % (HEAD, p)).strip()
txt = git("show", "%s:%s" % (HEAD, p))
m4 = re.search(r"int ParseMode\(const char\* value\) \{.*?if \(value == nullptr \|\| value\[0\] == '\\0'\) \{\s*return 3;", txt, re.S) is not None
print("V4 %s blob base %s FS15 %s equal %s; ParseMode unset/\"\" -> 3: %s" % (p, bb[:12], hb[:12], bb == hb, m4))
ok &= bb == hb and m4


# V5
def sig(path):
    t = open(path, "rb").read().decode("utf-8", "replace")
    mm = re.search(r'#define KYTY_SHADER_SOURCE_HASH "([0-9a-f]+)"', t)
    return mm.group(1) if mm else None


s15, s14 = sig(VH15), sig(VH14)
print("V5 KYTY_SHADER_SOURCE_HASH FS15 %s FS14 %s equal %s" % (s15, s14, s15 == s14 and s15 is not None))
ok &= s15 == s14 and s15 is not None and s15.startswith("9177b426")

# V6
added = [l[1:] for l in git("diff", "-U0", BASE, HEAD, "--", "src", "tests", "CMakeLists.txt").split("\n")
         if l.startswith("+") and not l.startswith("+++ ")]
pat = r"DiagB32|diagB32\.h|KYTY_DIAG_B32|rts_bad_b|rts_bad_rx|KYTY_F26_TINT|KYTY_FIX_F26"
code = [l for l in added if re.search(pat, l) and not l.lstrip().startswith("//")]
print("V6 added code lines naming F26 / KYTY_DIAG_B32 / F30d counters: %d" % len(code))
ok &= not code

# V7 (reference)
try:
    v7 = sorted(n for n in git("diff", "--name-only", "5ccb1d31", HEAD).split() if n.startswith("src/"))
    print("V7 (reference) src/ paths of the diff F42a2 worktree 5ccb1d31 .. FS15: %s" % " ".join(v7))
except subprocess.CalledProcessError as e:
    print("V7 (reference) 5ccb1d31 not readable: %s" % e)

print("ALL OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
